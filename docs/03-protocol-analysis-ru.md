# Анализ протоколов (Русская версия)

## Обзор

VNCI 6154A использует **многослойную протокольную архитектуру**, где PC софт выступает D-PDU API клиентом, а реальная реализация протоколов (DoIP, CAN FD, UDS) находится в **прошивке устройства**.

## Слои протокольного стека

```
┌─────────────────────────────────────────────────────────────┐
│  Application Layer (PC Software)                            │
│  - VCIMngr.exe (Device Manager)                             │
│  - Remote Diagnostic Interface                              │
└─────────────────────┬───────────────────────────────────────┘
                      │ D-PDU API (ISO 22900-1)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  D-PDU API Layer (Bosch Implementation)                     │
│  - MVCI_PDU_API_ROOT v2.2.0                                 │
│  - Множественные VCI драйверы (JLR-DoIP, VW, Ford, etc.)    │
│  - PDUAPI_Loader.dll / PDUAPI_VW.dll / BVTX-VCI-PDU.dll    │
└─────────────────────┬───────────────────────────────────────┘
                      │ Vendor-specific VCI Protocol
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  VNCI 6154A Device Firmware                                 │
│  - Ethernet/USB Interface                                   │
│  - DoIP (ISO 13400) Stack                                   │
│  - CAN/CAN FD Controller                                    │
│  - UDS (ISO 14229) Transport                                │
└─────────────────────┬───────────────────────────────────────┘
                      │ Vehicle Bus
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Vehicle Network                                            │
│  - DoIP over Ethernet (TCP/UDP 13400)                       │
│  - CAN FD (ISO 11898-1)                                     │
│  - Classical CAN                                            │
└─────────────────────────────────────────────────────────────┘
```

## D-PDU API (ISO 22900-1)

**D-PDU API** (Diagnostic Protocol Data Unit API) - стандартизированный интерфейс (ISO 22900-1) для диагностического обмена между PC приложениями и Vehicle Communication Interfaces (VCI).

### Ключевые понятия из D-PDU.xml

1. **MVCI_PDU_API_ROOT**: Корневой элемент v2.2.0
2. **MVCI_PDU_API**: Отдельные записи VCI драйверов
3. **SHORT_NAME**: Уникальный идентификатор (например, "D_PDU_API_Bosch_JLR_DoIP")
4. **LIBRARY_FILE**: VCI vendor DLL (например, BVTX-VCI-PDU.dll)
4. **MODULE_DESCRIPTION_FILE**: MDF - Module Description File (XML)
5. **CABLE_DESCRIPTION_FILE**: CDF - Cable Description File (XML)

### Запись JLR-DoIP (Подтвержденная поддержка DoIP)
```xml
<MVCI_PDU_API>
    <SHORT_NAME>D_PDU_API_Bosch_JLR_DoIP</SHORT_NAME>
    <DESCRIPTION>JLR - JLR-DoIP, D-PDU API by Bosch</DESCRIPTION>
    <SUPPLIER_NAME>Bosch</SUPPLIER_NAME>
    <LIBRARY_FILE URI="file:///C:/Program Files (x86)/Mercedes-Benz/Bosch/VCI Software (Daimler)/Products/MTS6532/Dynamic Link Libraries/BVTX-VCI-PDU.dll"/>
    <MODULE_DESCRIPTION_FILE URI="file:///C:/Program Files (x86)/Mercedes-Benz/Bosch/VCI Software (Daimler)/Products/MTS6532/SupportFiles/MDF_Bosch_MTS6532.xml"/>
    <CABLE_DESCRIPTION_FILE URI="file:///C:/Program Files (x86)/Mercedes-Benz/Bosch/VCI Software (Daimler)/Products/MTS6532/SupportFiles/CDF_Bosch_Daimler.xml"/>
</MVCI_PDU_API>
```

## DoIP (ISO 13400) Реализация

### Детали протокола
- **Стандарт**: ISO 13400 (Diagnostics over Internet Protocol)
- **Транспорт**: TCP/IP и UDP/IP over Ethernet
- **Порт**: 13400 (UDP для discovery, TCP для данных)
- **Payload**: UDS (ISO 14229) сообщения инкапсулированы в DoIP

### Структура DoIP сообщения (Вывод)
```
DoIP Header (8 байт):
├── Protocol Version (1 байт) = 0x02
├── Inverse Protocol Version (1 байт) = 0xFD
├── Payload Type (2 байта)     = 0x0001 (Vehicle Identification Request)
├── Payload Length (4 байта)   = Variable

Payload Types:
├── 0x0000: Generic DoIP Header Negative Acknowledge
├── 0x0001: Vehicle Identification Request (UDP broadcast)
├── 0x0002: Vehicle Identification Response
├── 0x0003: Vehicle Identification Request with EID
├── 0x0004: Vehicle Identification Request with VIN
├── 0x0005: Routing Activation Request
├── 0x0006: Routing Activation Response
├── 0x0007: Alive Check Request
├── 0x0008: Alive Check Response
├── 0x4001: DoIP Entity Status Request
├── 0x4002: DoIP Entity Status Response
├── 0x8001: Diagnostic Message (UDS over DoIP)
├── 0x8002: Diagnostic Message Positive ACK
└── 0x8003: Diagnostic Message Negative ACK
```

### Последовательность инициализации (Стандарт ISO 13400)
```
1. UDP Broadcast (Port 13400): Vehicle Identification Request (0x0001)
   └── Source: Tester/Client
   └── Destination: 255.255.255.255:13400

2. UDP Unicast Response: Vehicle Identification Response (0x0002)
   └── Содержит: VIN, EID, GID, Further Action Required

3. TCP Connection (Port 13400): Client → Vehicle Gateway
   └── SYN → SYN-ACK → ACK

4. Routing Activation (Payload 0x0005):
   └── Source Address (Tester)
   └── Target Address (ECU)
   └── Activation Type (Default/OEM)
   └── OEM Specific Data (если требуется)

5. Routing Activation Response (Payload 0x0006):
   └── Status (0x10 = Success)
   └── OEM Specific Data

6. Diagnostic Communication (Payload 0x8001):
   └── UDS Requests/Responses инкапсулированы

7. Alive Check (Payload 0x0007/0x0008): Периодический keep-alive
```

## CAN FD (ISO 11898-1) Реализация

### Ключевые параметры (Уровень прошивки устройства)
PC софт не содержит строк конфигурации CAN FD baud rate - они настраиваются через D-PDU API вызовы к устройству.

**Типичная конфигурация CAN FD (MEB платформа):**
```
Arbitration Phase:
├── Nominal Bit Rate: 500 kbps (стандарт)
├── Sample Point: 80%
├── SJW: 1-2 TQ
└── Propagation Segment: Настраивается под железо

Data Phase:
├── Data Bit Rate: 2 Mbps / 5 Mbps (MEB поддерживает до 5 Mbps)
├── Sample Point: 75-80%
├── SJW: 1-2 TQ
└── Flexible Data Rate: Включено (FD frames)

Controller Configuration:
├── CAN Controller: Bosch M_CAN или аналог
├── FD Frame Support: ISO 11898-1:2015
├── Bit Rate Switching: Включено (BRS bit)
├── ESI Bit: Error State Indicator
└── DLC Coding: 0-8 (Classic), 9-15 (FD: 12/16/20/24/32/48/64 байт)
```

## UDS (ISO 14229) Транспорт

### Over DoIP
- **Payload Type**: 0x8001 (Diagnostic Message)
- **Source/Target Address**: Логическая адресация (DoIP routing)
- **Max Payload**: 4095 байт (DoIP лимит) → Поддержка длинных UDS сообщений

### Over CAN FD
- **Адресация**: 11-bit или 29-bit CAN IDs
- **Формат фрейма**: CAN FD (FDF bit set)
- **Max Data**: 64 байта на фрейм
- **Сегментация**: ISO 15765-2 (ISO-TP) для multi-frame

## Устройство-к-PC коммуникация

### Интерфейс
- **Основной**: Ethernet (RJ45) - нативный DoIP
- **Вторичный**: USB - D-PDU API туннелирование
- **Discovery**: mDNS/Bonjour или UDP broadcast

### Роль PC софта
VCIMngr.exe - это **инструмент управления и конфигурации**, НЕ диагностический клиент:
1. Обнаружение и перечисление устройств
2. Обновление прошивки (через FTP/HTTPS)
3. Сетевая конфигурация (IP, VLAN, firewall)
4. Управление сертификатами (TLS/SSL)
5. Управление серийным номером / VIN
6. Инициация сессий удаленной диагностики

### Реальный диагностический клиент
Диагностические приложения (ODIS, VAS, кастомные инструменты) используют:
```
Diagnostic App → D-PDU API (ISO 22900) → VNCI 6154A → Vehicle
```

D-PDU API абстрагирует транспорт (DoIP/CAN/USB) от диагностического приложения.
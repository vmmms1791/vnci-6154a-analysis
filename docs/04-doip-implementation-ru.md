# DoIP Implementation Analysis (Русская версия)

## Подтверждение поддержки DoIP

**Статус: ПОДТВЕРЖДЕНО** - VNCI 6154A явно поддерживает DoIP (ISO 13400) для Jaguar Land Rover (JLR) автомобилей через Bosch D-PDU API.

### Доказательства
Из `resource/D-PDU.xml`:
```xml
<MVCI_PDU_API>
    <SHORT_NAME>D_PDU_API_Bosch_JLR_DoIP</SHORT_NAME>
    <DESCRIPTION>JLR - JLR-DoIP, D-PDU API by Bosch</DESCRIPTION>
    <SUPPLIER_NAME>Bosch</SUPPLIER_NAME>
</MVCI_PDU_API>
```

## Расположение DoIP стека

DoIP протокол стек **НЕ в PC софте** (VCIMngr.exe). Он находится в:

1. **Device Firmware** (на железе VNCI 6154A)
2. **D-PDU API Vendor DLL** (BVTX-VCI-PDU.dll) - Загружается диагностическими приложениями
3. **Vehicle Gateway** (OEM реализация)

PC софт только:
- Настраивает сетевые настройки устройства
- Управляет сертификатами для TLS
- Инициализирует сессии удаленной диагностики
- Обрабатывает обновления прошивки

## DoIP Message Flow (С точки зрения Vehicle Gateway)

### Фаза 1: Обнаружение автомобиля (UDP 13400)
```
Client (VNCI)                    Vehicle Gateway
    │                                 │
    ├─ UDP Broadcast ────────────────►│  Port 13400
    │   Payload: 0x0001 (Veh ID Req)  │
    │                                 │
    │◄─ UDP Unicast ──────────────────┤  Payload: 0x0002 (Veh ID Resp)
    │   Содержит: VIN, EID, GID       │
    │                                 │
```

### Фаза 2: TCP Connection & Routing Activation
```
Client (VNCI)                    Vehicle Gateway
    │                                 │
    ├─ TCP SYN ──────────────────────►│  Port 13400
    │◄─ TCP SYN-ACK ──────────────────┤
    ├─ TCP ACK ──────────────────────►│
    │                                 │
    ├─ DoIP: Routing Activation ─────►│  Payload: 0x0005
    │   SA: Tester, TA: ECU           │
    │   Activation Type: 0x00/0x01    │
    │                                 │
    │◄─ DoIP: Routing Activation Resp─┤  Payload: 0x0006
    │   Status: 0x10 (Success)        │
    │                                 │
```

### Фаза 3: Диагностическая коммуникация
```
Client (VNCI)                    Vehicle Gateway
    │                                 │
    ├─ DoIP: Diagnostic Message ─────►│  Payload: 0x8001
    │   UDS Request (например, 0x22)  │
    │                                 │
    │◄─ DoIP: Diagnostic Message ACK ─┤  Payload: 0x8002
    │                                 │
    │◄─ DoIP: Diagnostic Message ─────┤  Payload: 0x8001
    │   UDS Response                  │
    │                                 │
```

### Фаза 4: Alive Check (Keep-Alive)
```
Периодически (обычно 2-5 секунд):
    │                                 │
    ├─ DoIP: Alive Check Request ────►│  Payload: 0x0007
    │                                 │
    │◄─ DoIP: Alive Check Response ───┤  Payload: 0x0008
    │                                 │
```

## DoIP Header Structure (ISO 13400)

| Offset | Size | Field | Value/Description |
|--------|------|-------|-------------------|
| 0 | 1 | Protocol Version | 0x02 (ISO 13400:2012/2019) |
| 1 | 1 | Inverse Protocol Version | 0xFD (bitwise NOT of 0x02) |
| 2-3 | 2 | Payload Type | См. таблицу ниже |
| 4-7 | 4 | Payload Length | Big-endian, байты в payload |

### Payload Types (Ключевые)

| Type | Hex | Direction | Description |
|------|-----|-----------|-------------|
| Generic Negative ACK | 0x0000 | Both | Ошибка протокола |
| Vehicle ID Request | 0x0001 | Client→Vehicle | UDP Broadcast discovery |
| Vehicle ID Response | 0x0002 | Vehicle→Client | Содержит VIN, EID, GID |
| Vehicle ID Req w/ EID | 0x0003 | Client→Vehicle | Целевое discovery |
| Vehicle ID Req w/ VIN | 0x0004 | Client→Vehicle | Целевое discovery |
| Routing Activation Req | 0x0005 | Client→Vehicle | Активация маршрута к ECU |
| Routing Activation Resp | 0x0006 | Vehicle→Client | Статус + OEM данные |
| Alive Check Request | 0x0007 | Both | Keep-alive |
| Alive Check Response | 0x0008 | Both | Keep-alive ACK |
| DoIP Entity Status Req | 0x4001 | Client→Vehicle | Статус узла |
| DoIP Entity Status Resp | 0x4002 | Vehicle→Client | Статус узла |
| Diagnostic Message | 0x8001 | Both | UDS инкапсулирован |
| Diagnostic Message ACK | 0x8002 | Receiver→Sender | Positive ACK |
| Diagnostic Message NACK | 0x8003 | Receiver→Sender | Negative ACK |

## Routing Activation Details

### Request (0x0005)
```
Bytes: [SA:2][TA:2][Activation Type:1][Reserved:1][OEM Data:4][VIN:17] (optional)
```
- **SA** (Source Address): Адрес тестера (например, 0x0E00)
- **TA** (Target Address): Адрес ECU (например, 0x1000)
- **Activation Type**: 0x00=Default, 0x01=OEM Specific
- **OEM Data**: 4 байта OEM-специфичные (JLR использует свой формат)

### Response (0x0006)
```
Bytes: [SA:2][TA:2][Status:1][Reserved:1][OEM Data:4]
```
- **Status**: 0x10=Success, 0x11=Unknown SA, 0x12=Unknown TA, 0x13=Missing OEM Data, 0x14=Invalid OEM Data

## JLR-Specific DoIP Considerations

Исходя из записи D-PDU API "JLR - JLR-DoIP", JLR имеет OEM-специфичные расширения:

1. **Routing Activation**: Требует OEM-специфичные данные (security challenge/response)
2. **VIN Verification**: Gateway проверяет соответствие VIN автомобилю
3. **Security Access**: Может требовать seed/key exchange перед routing activation
4. **TLS/SSL**: Некоторые JLR модели используют TLS на TCP 13400 (DoIP over TLS)

## Сетевая конфигурация (Из setting.ini)

```ini
[FTP]
IPAddr="www.rokwy.com"   # Сервер обновлений прошивки
Dir="./"
```

Устройство вероятно:
1. Подключается к автомобилю через Ethernet (DoIP)
2. Подключается к cloud/backend через HTTPS/TLS (www.rokwy.com) для:
   - Обновлений прошивки
   - Синхронизации конфигурации
   - Авторизации удаленной диагностики
   - Управления сертификатами

## Найденные сертификаты
- `ca_cert.pem` / `ca_cert_b.pem` - CA сертификаты (основной/резерв)
- `server_key.pem` / `server_key_b.pem` - Приватные ключи сервера (основной/резерв)

Используются для: Mutual TLS аутентификация с backend и/или vehicle gateway.

## Мобильные импликации

Для мобильной реализации (Phone ↔ VNCI 6154A):

1. **Direct DoIP**: Phone app реализует DoIP стек → TCP/UDP 13400 к VNCI
2. **Via D-PDU API**: Phone app использует D-PDU API (порт на Android/iOS)
3. **Via VNCI Management API**: Phone app общается с VCIMngr-like сервисом на VNCI

**Рекомендуется**: Вариант 1 (Direct DoIP) - Наиболее переносимый, соответствует стандартам.
- Реализовать ISO 13400 стек на мобильной платформе
- Обрабатывать UDP discovery, TCP connection, routing activation
- Инкапсулировать UDS (ISO 14229) в DoIP 0x8001 payloads
- Обрабатывать alive checks, TLS если требуется
# Структура файлов (Русская версия)

## Установочный пакет

**Файл**: VNCI6154ADevMngrSetup_v4.9.exe
- **Тип**: Inno Setup 6.1.0 (Unicode) установщик
- **Размер**: 47,180,272 байт
- **SHA256**: b57b35a11f349d1f086ef9c1f72ffc198ce31c1c5817af7d78df668e9dde5faa

## Извлеченные компоненты

### Основное приложение
```
app/VNCI 6154A Device Manager/
├── VCIMngr.exe                    # Главный исполняемый файл (3.5 МБ, 3651 процедур, 1505 строк)
├── DuiLib_u.dll                   # Библиотека DirectUI (GUI)
├── event.dll                      # libevent core (154 КБ, 1043 процедуры)
├── event_core.dll                 # libevent core (92 КБ, 701 процедура)  
├── event_openssl.dll              # libevent OpenSSL binding (11 КБ, 281 процедура)
├── libcrypto-1_1.dll              # OpenSSL 1.1 crypto
├── libssl-1_1.dll                 # OpenSSL 1.1 SSL/TLS
├── setting.ini                    # Конфигурация (FTP сервер: www.rokwy.com)
├── ca_cert.pem                    # CA сертификат
├── server_key.pem                 # Приватный ключ сервера
├── ca_cert_b.pem                  # Резервный CA сертификат
├── server_key_b.pem               # Резервный приватный ключ
└── resource/                      # UI ресурсы (XML layouts, изображения)
    ├── D-PDU.xml                  # Конфигурация D-PDU API (КЛЮЧЕВОЕ НАХОЖДЕНИЕ)
    ├── device_manager.xml         # UI менеджера устройств
    ├── remote_diag.xml            # UI удаленной диагностики
    ├── messages.xml               # Определения сообщений
    └── skin.xml                   # UI скин
```

### Компоненты обновлений
```
app/Patch/
├── planet                         # Неизвестный бинарник
├── vc2022redist_x64.exe           # Visual C++ 2022 Redist x64
├── vc2022redist_x86.exe           # Visual C++ 2022 Redist x86
└── ZeroTierOne.msi                # Установщик ZeroTier VPN
```

## Основной исполняемый файл: VCIMngr.exe

- **Формат**: PE32 executable (GUI) Intel 80386
- **Архитектура**: x86 (32-bit)
- **Секции**: 7 (.text, .rdata, .data, .rsrc, .reloc, Headers, tdb)
- **Image Base**: 0x400000
- **Процедуры**: 3,651
- **Строки**: 1,505
- **PDB ссылка**: VCIMngr.pdb (GUID: 4ae042ca-5e71-420f-812d-c50eb56e8298)

### Ключевые импорты
- **KERNEL32.DLL**: Стандартные Windows API
- **WS2_32.DLL**: Winsock2 (WSAEnumNetworkEvents)
- **WININET.DLL**: InternetConnectW
- **WINHTTP.DLL**: WinHttpConnect
- **DUILIB_U.DLL**: Библиотека DirectUI
- **EVENT.DLL / EVENT_CORE.DLL / EVENT_OPENSSL.DLL**: libevent
- **MSVCP140.DLL / VCRUNTIME140.DLL**: Visual C++ Runtime

## XML файлы ресурсов

### D-PDU.xml (Критическое нахождение)
Содержит конфигурацию MVCI_PDU_API_ROOT (v2.2.0) с множественными VCI реализациями:
- **JLR-DoIP**: "JLR - JLR-DoIP, D-PDU API by Bosch" ← **DoIP Подтвержден**
- VW D-PDU API (Volkswagen AG)
- Bosch MTS6532 (Daimler/Mercedes)
- GM MDI/MDI 2
- Ford VCM-II/VCM3/VCMM
- ACTIA I+ME XS
- Opus IVS
- AUTEL
- Mazda VCM-II
- PSA Interface
- Suzuki 6516

Каждая запись содержит:
- LIBRARY_FILE (путь к DLL)
- MODULE_DESCRIPTION_FILE (MDF XML)
- CABLE_DESCRIPTION_FILE (CDF XML)

### setting.ini
```ini
[PREFER]
LanguageIndex=0

[FTP]
IPAddr="www.rokwy.com"
Dir="./"
```

### remote_diag.xml
UI layout для удаленной диагностики с кнопками:
- btn_cpynwid (Копировать Network ID)
- btn_auth (Авторизовать)
- btn_disconnect
- btn_cpyregdata (Копировать регистрационные данные)
- InfoBox (RichEdit для логирования)
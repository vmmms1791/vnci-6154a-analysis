# VNCI 6154A Device Manager - Обратная инженерия (Русская версия)

## Краткое резюме

**Цель**: VNCI 6154A Device Manager (VNCI6154ADevMngrSetup_v4.9.exe)
**SHA256**: b57b35a11f349d1f086ef9c1f72ffc198ce31c1c5817af7d78df668e9dde5faa
**Дата анализа**: 2026-10-20
**Инструменты**: Hermes Agent + REA (Ghidra 12.1.4)

### Ключевые выводы

1. **Архитектура**: 32-битный нативный Windows PE (x86), C++ приложение с использованием:
   - **oatpp** - C++ веб-фреймворк для TCP/HTTP сети
   - **DuiLib** - DirectUI C++ фреймворк для GUI
   - **libevent** - Библиотека асинхронных событий (event.dll, event_core.dll, event_openssl.dll)
   - **OpenSSL 1.1** - TLS/SSL поддержка (libcrypto-1_1.dll, libssl-1_1.dll)

2. **Стек протоколов**:
   ```
   Mobile App / PC Software
         ↓
   D-PDU API (Bosch Standard ISO 22900)
         ↓
   VNCI 6154A Device (Ethernet/USB)
         ↓
   Vehicle Network (DoIP/CAN FD)
   ```

3. **Поддержка DoIP**: **ПОДТВЕРЖДЕНА** - D-PDU.xml явно ссылается на "JLR - JLR-DoIP, D-PDU API by Bosch"

4. **Поддержка CAN FD**: Реализована в прошивке устройства, настраивается через D-PDU API

5. **Сетевое взаимодействие**:
   - TCP клиент/сервер через oatpp (порт настраиваемый)
   - UDP: Не напрямую в PC софте (обрабатывается прошивкой устройства для DoIP discovery на порту 13400)
   - TLS/SSL для безопасного обмена
   - FTP сервер обновлений: www.rokwy.com

### Структура репозитория

```
vnci-6154a-analysis/
├── docs/
│   ├── 01-executive-summary.md
│   ├── 02-file-structure.md
│   ├── 03-protocol-analysis.md
│   ├── 04-doip-implementation.md
│   ├── 05-can-fd-implementation.md
│   ├── 06-d-pdu-api-integration.md
│   ├── 07-network-communication.md
│   └── 08-mobile-port-recommendations.md
├── src/
│   ├── pseudocode/
│   ├── ghidra-scripts/
│   └── extracted-strings/
└── logs/
    ├── static-analysis.log
    ├── string-searches.log
    └── procedure-analysis.log
```
# VNCI 6154A Device Manager - Reverse Engineering Analysis

## Executive Summary

**Target**: VNCI 6154A Device Manager (VNCI6154ADevMngrSetup_v4.9.exe)
**SHA256**: b57b35a11f349d1f086ef9c1f72ffc198ce31c1c5817af7d78df668e9dde5faa
**Analysis Date**: 2026-10-20
**Analyzer**: Hermes Agent with REA (Ghidra 12.1.4)

### Key Findings

1. **Architecture**: 32-bit native Windows PE executable (x86), C++ application using:
   - **oatpp** - C++ web framework for TCP/HTTP networking
   - **DuiLib** - DirectUI C++ framework for GUI
   - **libevent** - Async event notification library (event.dll, event_core.dll, event_openssl.dll)
   - **OpenSSL 1.1** - TLS/SSL support (libcrypto-1_1.dll, libssl-1_1.dll)

2. **Protocol Stack**:
   ```
   Mobile App / PC Software
         ↓
   D-PDU API (Bosch Standard ISO 22900)
         ↓
   VNCI 6154A Device (Ethernet/USB)
         ↓
   Vehicle Network (DoIP/CAN FD)
   ```

3. **DoIP Support**: **Confirmed** - D-PDU.xml explicitly references "JLR - JLR-DoIP, D-PDU API by Bosch"

4. **CAN FD Support**: Implemented in device firmware, configured via D-PDU API

5. **Network Communication**:
   - TCP client/server via oatpp (port configurable)
   - UDP: Not directly in PC software (handled by device firmware for DoIP discovery on port 13400)
   - TLS/SSL for secure communication
   - FTP update server: www.rokwy.com

### Repository Structure

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
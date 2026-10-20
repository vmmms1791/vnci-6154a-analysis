# Protocol Analysis

## Overview

The VNCI 6154A uses a **layered protocol architecture** where the PC software acts as a D-PDU API client, and the actual protocol implementation (DoIP, CAN FD, UDS) resides in the **device firmware**.

## Protocol Stack Layers

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
│  - Multiple VCI drivers (JLR-DoIP, VW, Ford, etc.)          │
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

The **D-PDU API** (Diagnostic Protocol Data Unit API) is a standardized interface (ISO 22900-1) for diagnostic communication between PC applications and Vehicle Communication Interfaces (VCIs).

### Key Concepts from D-PDU.xml

1. **MVCI_PDU_API_ROOT**: Root element v2.2.0
2. **MVCI_PDU_API**: Individual VCI driver entries
3. **SHORT_NAME**: Unique identifier (e.g., "D_PDU_API_Bosch_JLR_DoIP")
4. **LIBRARY_FILE**: VCI vendor DLL (e.g., BVTX-VCI-PDU.dll)
4. **MODULE_DESCRIPTION_FILE**: MDF - Module Description File (XML)
5. **CABLE_DESCRIPTION_FILE**: CDF - Cable Description File (XML)

### JLR-DoIP Entry (Confirmed DoIP Support)
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

## DoIP (ISO 13400) Implementation

### Protocol Details
- **Standard**: ISO 13400 (Diagnostics over Internet Protocol)
- **Transport**: TCP/IP and UDP/IP over Ethernet
- **Port**: 13400 (UDP for discovery, TCP for data)
- **Payload**: UDS (ISO 14229) messages encapsulated in DoIP

### DoIP Message Structure (Inferred)
```
DoIP Header (8 bytes):
├── Protocol Version (1 byte) = 0x02
├── Inverse Protocol Version (1 byte) = 0xFD
├── Payload Type (2 bytes)     = 0x0001 (Vehicle Identification Request)
├── Payload Length (4 bytes)   = Variable

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

### Initialization Sequence (Standard ISO 13400)
```
1. UDP Broadcast (Port 13400): Vehicle Identification Request (0x0001)
   └── Source: Tester/Client
   └── Destination: 255.255.255.255:13400

2. UDP Unicast Response: Vehicle Identification Response (0x0002)
   └── Contains: VIN, EID, GID, Further Action Required

3. TCP Connection (Port 13400): Client → Vehicle Gateway
   └── SYN → SYN-ACK → ACK

4. Routing Activation (Payload 0x0005):
   └── Source Address (Tester)
   └── Target Address (ECU)
   └── Activation Type (Default/OEM)
   └── OEM Specific Data (if required)

5. Routing Activation Response (Payload 0x0006):
   └── Status (0x10 = Success)
   └── OEM Specific Data

6. Diagnostic Communication (Payload 0x8001):
   └── UDS Requests/Responses encapsulated

7. Alive Check (Payload 0x0007/0x0008): Periodic keep-alive
```

## CAN FD (ISO 11898-1) Implementation

### Key Parameters (Device Firmware Level)
The PC software does not contain CAN FD baud rate strings - these are configured via D-PDU API calls to the device.

**Typical CAN FD Configuration (MEB Platform):**
```
Arbitration Phase:
├── Nominal Bit Rate: 500 kbps (standard)
├── Sample Point: 80%
├── SJW: 1-2 TQ
└── Propagation Segment: Configured per hardware

Data Phase:
├── Data Bit Rate: 2 Mbps / 5 Mbps (MEB supports up to 5 Mbps)
├── Sample Point: 75-80%
├── SJW: 1-2 TQ
└── Flexible Data Rate: Enabled (FD frames)

Controller Configuration:
├── CAN Controller: Bosch M_CAN or similar
├── FD Frame Support: ISO 11898-1:2015
├── Bit Rate Switching: Enabled (BRS bit)
├── ESI Bit: Error State Indicator
└── DLC Coding: 0-8 (Classic), 9-15 (FD: 12/16/20/24/32/48/64 bytes)
```

## UDS (ISO 14229) Transport

### Over DoIP
- **Payload Type**: 0x8001 (Diagnostic Message)
- **Source/Target Address**: Logical addressing (DoIP routing)
- **Max Payload**: 4095 bytes (DoIP limit) → Supports UDS long messages

### Over CAN FD
- **Addressing**: 11-bit or 29-bit CAN IDs
- **Frame Format**: CAN FD (FDF bit set)
- **Max Data**: 64 bytes per frame
- **Segmentation**: ISO 15765-2 (ISO-TP) for multi-frame

## Device-to-PC Communication

### Interface
- **Primary**: Ethernet (RJ45) - DoIP native
- **Secondary**: USB - D-PDU API tunneling
- **Discovery**: mDNS/Bonjour or UDP broadcast

### PC Software Role
The VCIMngr.exe is a **management and configuration tool**, not a diagnostic client:
1. Device discovery and enumeration
2. Firmware update (via FTP/HTTPS)
3. Network configuration (IP, VLAN, firewall)
4. Certificate management (TLS/SSL)
5. Serial number / VIN management
6. Remote diagnostic session initiation

### Actual Diagnostic Client
Diagnostic applications (ODIS, VAS, custom tools) use:
```
Diagnostic App → D-PDU API (ISO 22900) → VNCI 6154A → Vehicle
```

The D-PDU API abstracts the transport (DoIP/CAN/USB) from the diagnostic application.
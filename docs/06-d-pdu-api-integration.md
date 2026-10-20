# D-PDU API Integration Analysis

## Overview

The VNCI 6154A Device Manager integrates with the **D-PDU API (ISO 22900-1)**, a standardized interface for diagnostic communication between PC applications and Vehicle Communication Interfaces (VCIs).

## D-PDU API Standard (ISO 22900-1)

### Purpose
- Abstract VCI hardware details from diagnostic applications
- Provide unified API for multiple VCI vendors (Bosch, VW, Ford, etc.)
- Support multiple protocols: DoIP, CAN, CAN FD, K-Line, LIN, FlexRay

### Architecture
```
Diagnostic Application (ODIS, VAS, Custom)
        │
        ▼
D-PDU API Loader (PDUAPI_Loader.dll)
        │
        ├──────────────────────┬──────────────────────┐
        ▼                      ▼                      ▼
Bosch VCI DLL           VW VCI DLL             Ford VCI DLL
(BVTX-VCI-PDU.dll)      (PDUAPI_VW.dll)        (BVTX-VCI-PDU.dll)
        │                      │                      │
        ▼                      ▼                      ▼
VNCI 6154A            VNCI 6154A            VNCI 6154A
(or other VCI)        (or other VCI)        (or other VCI)
```

## D-PDU.xml Configuration Analysis

The `resource/D-PDU.xml` file contains the **MVCI_PDU_API_ROOT** registry (v2.2.0) listing all supported VCI implementations.

### Supported VCI Entries (27 Total)

| SHORT_NAME | Vendor | Protocol | Target |
|------------|--------|----------|--------|
| D_PDU_API_Bosch_JLR_DoIP | Bosch | **DoIP** | JLR |
| D_PDU_API_Bosch_MDI | Bosch | D-PDU | GM MDI |
| D_PDU_API_Bosch_6516-Suzuki | Bosch | D-PDU | Suzuki |
| D_PDU_API_Bosch_MDI_2 | Bosch | D-PDU | GM MDI 2 |
| J2534 | Bosch | J2534 | Generic |
| SELF_LEARNING_MODE | Bosch | VSI Embedded | VSI |
| VW_D_PDU_API_30_3_0 | VW AG | D-PDU | VW Group |
| VW_D_PDU_API_29_0_0 | VW AG | D-PDU | VW Group (legacy) |
| OPUSDPDU | Opus IVS | D-PDU | Opus |
| XS_D_PDU_API_7_0_0 | ACTIA | D-PDU | ACTIA XS |
| XS_D_PDU_API_20_1_8_17 | ACTIA | D-PDU | ACTIA Core XS |
| PSA_Interface_D_PDU_API | ACTIA | D-PDU | PSA |
| D_PDU_API_Bosch_Mazda_VCM_II | Bosch | D-PDU | Mazda |
| AUTEL_D_PDU_API | AUTEL | D-PDU | AUTEL |
| D_PDU_API_Bosch_Ford_VCM_II | Bosch | D-PDU | Ford VCM-II |
| D_PDU_API_Bosch_VCM3 | Bosch | D-PDU | Ford VCM3 |
| D_PDU_API_Bosch_VCMM | Bosch | D-PDU | Ford VCMM |
| D_PDU_API_Bosch_RNM_VI | Bosch | D-PDU | RNM-VI |
| ... | ... | ... | ... |

### Key Files per Entry
Each VCI requires three files:
1. **LIBRARY_FILE**: Vendor DLL (e.g., `BVTX-VCI-PDU.dll`, `PDUAPI_VW.dll`)
2. **MODULE_DESCRIPTION_FILE (MDF)**: XML describing module capabilities
3. **CABLE_DESCRIPTION_FILE (CDF)**: XML describing cable/interface pinout

## JLR-DoIP Specific Entry

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

**Critical Observations:**
1. Uses **BVTX-VCI-PDU.dll** (Bosch VTX VCI PDU library)
2. Shares DLL with Daimler/Mercedes MTS6532
3. MDF/CDF from Bosch MTS6532 support files
4. **Explicitly labeled "JLR-DoIP"** - Confirms DoIP support for JLR

## D-PDU API Core Functions (ISO 22900-1)

### Module Management
```c
PDUGetVersion();                    // API version
PDUGetModuleList();                 // List available VCI modules
PDULoadModule(shortName);           // Load specific VCI module
PDUUnloadModule(hModule);           // Unload module
```

### Channel/Connection Management
```c
PDUCreateChannel(hModule, &hChannel);    // Create communication channel
PDUConnect(hChannel);                     // Connect to VCI
PDUDisconnect(hChannel);                  // Disconnect
PDUDestroyChannel(hChannel);              // Destroy channel
```

### Configuration
```c
PDUSetChannelConfig(hChannel, "KEY", value);
PDUGetChannelConfig(hChannel, "KEY", &value);

// Common CAN FD Keys:
"CAN_FD_ENABLED"           // 0/1
"BITRATE_NOMINAL"          // bps (500000)
"BITRATE_DATA"             // bps (2000000/5000000)
"SAMPLE_POINT_NOMINAL"     // 0.1% units (800 = 80.0%)
"SAMPLE_POINT_DATA"        // 0.1% units (750 = 75.0%)
"SJW_NOMINAL"              // TQ
"SJW_DATA"                 // TQ
"TRANSCEIVER_MODE"         // Normal/Silent/Loopback
```

### Data Transfer
```c
PDUSendData(hChannel, pduData);    // Send diagnostic request
PDUReadData(hChannel, &pduData, timeout);  // Read response
PDUGetStatus(hChannel, &status);   // Get channel status
```

### ISO-TP / UDS Support
```c
PDUStartDiagSession(hChannel, sessionType);
PDUSendDiagRequest(hChannel, request);
PDUReadDiagResponse(hChannel, &response, timeout);
```

## VNCI 6154A Specific Integration

### VCIMngr.exe D-PDU Usage
From string analysis:
- Registry key: `SOFTWARE\\D-PDU API`
- XML Elements: `MVCI_PDU_API_ROOT`, `I_PDU_API`
- Config file reference: `D-PDU API RDF file: "%s"\n`

### PC Software Role
VCIMngr.exe uses D-PDU API for:
1. **Device Enumeration**: List connected VNCI 6154A devices
2. **Configuration**: Network settings, certificates, firmware
3. **Remote Diagnostics**: Initiate/auth diagnostic sessions
4. **Firmware Update**: Via FTP/HTTPS to www.rokwy.com

### Diagnostic Application Role
Actual diagnostic tools (ODIS, VAS, custom) use D-PDU API for:
1. **UDS Communication**: ReadDataByIdentifier, SecurityAccess, etc.
2. **Flash Programming**: Large data transfer via ISO-TP/CAN FD
3. **ECU Variant Coding**: Configuration writes
4. **Live Data**: Periodic data reading

## MDF/CDF File Structure (Inferred)

### MDF (Module Description File)
```xml
<MODULE_DESCRIPTION>
    <MODULE_NAME>VNCI 6154A</MODULE_NAME>
    <VENDOR>Bosch</VENDOR>
    <PROTOCOLS>
        <PROTOCOL name="DoIP" version="13400"/>
        <PROTOCOL name="CAN" version="FD"/>
        <PROTOCOL name="UDS" version="14229"/>
    </PROTOCOLS>
    <CHANNELS>
        <CHANNEL id="0" type="ETHERNET" protocol="DoIP"/>
        <CHANNEL id="1" type="CAN" protocol="CAN_FD"/>
        <CHANNEL id="2" type="USB" protocol="D-PDU"/>
    </CHANNELS>
    <CAPABILITIES>
        <CAN_FD maxBitrate="5000000" maxDataSize="64"/>
        <DoIP maxPayload="4095" routingActivation="OEM"/>
        <TLS versions="1.2,1.3"/>
    </CAPABILITIES>
</MODULE_DESCRIPTION>
```

### CDF (Cable Description File)
```xml
<CABLE_DESCRIPTION>
    <CABLE_NAME>VNCI 6154A</CABLE_NAME>
    <CONNECTORS>
        <CONNECTOR id="ETH" type="RJ45" pins="8" protocol="DoIP">
            <PIN num="1" signal="TX+"/>
            <PIN num="2" signal="TX-"/>
            <PIN num="3" signal="RX+"/>
            <PIN num="6" signal="RX-"/>
            <PIN num="8" signal="WAKEUP"/>  <!-- OBD Pin 8 -->
        </CONNECTOR>
        <CONNECTOR id="OBD" type="J1962" pins="16" protocol="CAN_FD">
            <PIN num="6" signal="CAN_H"/>
            <PIN num="14" signal="CAN_L"/>
            <PIN num="8" signal="WAKEUP_K_LINE"/>
            <PIN num="16" signal="BATTERY+"/>
        </CONNECTOR>
    </CONNECTORS>
</CABLE_DESCRIPTION>
```

## Integration Points for Mobile Development

### Option 1: Embed D-PDU API in Mobile App
- Port D-PDU API loader + vendor DLLs to Android/iOS
- Complex: Native libraries, JNI/FFI, vendor cooperation needed

### Option 2: DoIP Direct (Recommended)
- Bypass D-PDU API entirely
- Implement ISO 13400 (DoIP) directly on mobile
- VNCI 6154A acts as DoIP gateway
- Standard-compliant, no vendor dependencies

### Option 3: VCI Web/REST API
- VNCI 6154A exposes HTTP/WebSocket API
- Mobile app calls REST endpoints
- Requires VNCI firmware support (may exist for remote diag)

### Option 4: Cloud Proxy
- Mobile → Cloud (www.rokwy.com) → VNCI 6154A
- Uses existing remote diagnostic infrastructure
- Requires backend integration
# DoIP Implementation Analysis

## DoIP Support Confirmation

**Status: CONFIRMED** - The VNCI 6154A explicitly supports DoIP (ISO 13400) for Jaguar Land Rover (JLR) vehicles via the Bosch D-PDU API.

### Evidence
From `resource/D-PDU.xml`:
```xml
<MVCI_PDU_API>
    <SHORT_NAME>D_PDU_API_Bosch_JLR_DoIP</SHORT_NAME>
    <DESCRIPTION>JLR - JLR-DoIP, D-PDU API by Bosch</DESCRIPTION>
    <SUPPLIER_NAME>Bosch</SUPPLIER_NAME>
</MVCI_PDU_API>
```

## DoIP Stack Location

The DoIP protocol stack is **NOT in the PC software** (VCIMngr.exe). It resides in:

1. **Device Firmware** (on VNCI 6154A hardware)
2. **D-PDU API Vendor DLL** (BVTX-VCI-PDU.dll) - Loaded by diagnostic apps
3. **Vehicle Gateway** (OEM implementation)

The PC software only:
- Configures the device network settings
- Manages certificates for TLS
- Initiates remote diagnostic sessions
- Handles firmware updates

## DoIP Message Flow (Vehicle Gateway Perspective)

### Phase 1: Vehicle Discovery (UDP 13400)
```
Client (VNCI)                    Vehicle Gateway
    │                                 │
    ├─ UDP Broadcast ────────────────►│  Port 13400
    │   Payload: 0x0001 (Veh ID Req)  │
    │                                 │
    │◄─ UDP Unicast ──────────────────┤  Payload: 0x0002 (Veh ID Resp)
    │   Contains: VIN, EID, GID       │
    │                                 │
```

### Phase 2: TCP Connection & Routing Activation
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

### Phase 3: Diagnostic Communication
```
Client (VNCI)                    Vehicle Gateway
    │                                 │
    ├─ DoIP: Diagnostic Message ─────►│  Payload: 0x8001
    │   UDS Request (e.g., 0x22)      │
    │                                 │
    │◄─ DoIP: Diagnostic Message ACK ─┤  Payload: 0x8002
    │                                 │
    │◄─ DoIP: Diagnostic Message ─────┤  Payload: 0x8001
    │   UDS Response                  │
    │                                 │
```

### Phase 4: Alive Check (Keep-Alive)
```
Periodic (typically 2-5 seconds):
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
| 2-3 | 2 | Payload Type | See table below |
| 4-7 | 4 | Payload Length | Big-endian, bytes in payload |

### Payload Types (Key)

| Type | Hex | Direction | Description |
|------|-----|-----------|-------------|
| Generic Negative ACK | 0x0000 | Both | Protocol error |
| Vehicle ID Request | 0x0001 | Client→Vehicle | UDP Broadcast discovery |
| Vehicle ID Response | 0x0002 | Vehicle→Client | Contains VIN, EID, GID |
| Vehicle ID Req w/ EID | 0x0003 | Client→Vehicle | Targeted discovery |
| Vehicle ID Req w/ VIN | 0x0004 | Client→Vehicle | Targeted discovery |
| Routing Activation Req | 0x0005 | Client→Vehicle | Activate routing to ECU |
| Routing Activation Resp | 0x0006 | Vehicle→Client | Status + OEM data |
| Alive Check Request | 0x0007 | Both | Keep-alive |
| Alive Check Response | 0x0008 | Both | Keep-alive ACK |
| DoIP Entity Status Req | 0x4001 | Client→Vehicle | Node status |
| DoIP Entity Status Resp | 0x4002 | Vehicle→Client | Node status |
| Diagnostic Message | 0x8001 | Both | UDS encapsulated |
| Diagnostic Message ACK | 0x8002 | Receiver→Sender | Positive ACK |
| Diagnostic Message NACK | 0x8003 | Receiver→Sender | Negative ACK |

## Routing Activation Details

### Request (0x0005)
```
Bytes: [SA:2][TA:2][Activation Type:1][Reserved:1][OEM Data:4][VIN:17] (optional)
```
- **SA** (Source Address): Tester logical address (e.g., 0x0E00)
- **TA** (Target Address): ECU logical address (e.g., 0x1000)
- **Activation Type**: 0x00=Default, 0x01=OEM Specific
- **OEM Data**: 4 bytes OEM-specific (JLR uses specific format)

### Response (0x0006)
```
Bytes: [SA:2][TA:2][Status:1][Reserved:1][OEM Data:4]
```
- **Status**: 0x10=Success, 0x11=Unknown SA, 0x12=Unknown TA, 0x13=Missing OEM Data, 0x14=Invalid OEM Data

## JLR-Specific DoIP Considerations

Based on the D-PDU API entry "JLR - JLR-DoIP", JLR (Jaguar Land Rover) has OEM-specific extensions:

1. **Routing Activation**: Requires OEM-specific data (security challenge/response)
2. **VIN Verification**: Gateway validates VIN matches vehicle
3. **Security Access**: May require seed/key exchange before routing activation
4. **TLS/SSL**: Some JLR models use TLS on TCP 13400 (DoIP over TLS)

## Network Configuration (From setting.ini)

```ini
[FTP]
IPAddr="www.rokwy.com"   # Firmware update server
Dir="./"
```

The device likely:
1. Connects to vehicle via Ethernet (DoIP)
2. Connects to cloud/backend via HTTPS/TLS (www.rokwy.com) for:
   - Firmware updates
   - Configuration sync
   - Remote diagnostic authorization
   - Certificate management

## Certificates Found
- `ca_cert.pem` / `ca_cert_b.pem` - CA certificates (backup)
- `server_key.pem` / `server_key_b.pem` - Server private keys (backup)

Used for: Mutual TLS authentication with backend and/or vehicle gateway.

## Mobile Port Implications

For mobile implementation (Phone ↔ VNCI 6154A):

1. **Direct DoIP**: Phone app implements DoIP stack → TCP/UDP 13400 to VNCI
2. **Via D-PDU API**: Phone app uses D-PDU API (port to Android/iOS)
3. **Via VNCI Management API**: Phone app talks to VCIMngr-like service on VNCI

**Recommended**: Option 1 (Direct DoIP) - Most portable, standard-compliant.
- Implement ISO 13400 stack on mobile
- Handle UDP discovery, TCP connection, routing activation
- Encapsulate UDS (ISO 14229) in DoIP 0x8001 payloads
- Handle alive checks, TLS if required
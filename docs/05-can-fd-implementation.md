# CAN FD Implementation Analysis

## CAN FD Support Status

**Status: IMPLEMENTED IN DEVICE FIRMWARE** - The PC software (VCIMngr.exe) does not contain CAN FD configuration strings. CAN FD is handled by the VNCI 6154A device firmware and configured via D-PDU API calls.

## CAN FD Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Diagnostic Application (ODIS, Custom)                          │
│       │                                                         │
│       ▼  ISO 22900-1 (D-PDU API)                                │
│  D-PDU API DLL (BVTX-VCI-PDU.dll, PDUAPI_VW.dll, etc.)         │
│       │                                                         │
│       ▼  VCI Vendor Protocol (Proprietary/Bosch)               │
│  VNCI 6154A Device                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Firmware                                                │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ DoIP Stack   │  │ CAN/CAN FD   │  │ UDS/ISO-TP   │  │   │
│  │  │ (ISO 13400)  │◄─┤ Controller   │◄─┤ (ISO 14229/  │  │   │
│  │  │              │  │ (M_CAN/IP)   │  │  ISO 15765)  │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│       │                                                         │
│       ▼  Physical Layer                                         │
│  Vehicle Network (Ethernet/CAN FD)                              │
└─────────────────────────────────────────────────────────────────┘
```

## CAN FD Controller (Inferred from VW MEB Platform)

The VNCI 6154A targets VW MEB platform vehicles. MEB uses:

### Controller: Bosch M_CAN (or compatible)
- **Standard**: ISO 11898-1:2015 (CAN FD)
- **Clock**: 80 MHz typical
- **Message RAM**: 1600+ words
- **Rx FIFO**: 2x 64 elements
- **Tx Buffers**: 32 dedicated + FIFO

### Bit Timing Configuration (Typical MEB)

#### Arbitration Phase (Nominal)
| Parameter | Value | Notes |
|-----------|-------|-------|
| Bit Rate | 500 kbps | Standard HS-CAN |
| Time Quanta (TQ) | 16-25 | @ 80 MHz |
| Propagation Segment | 1-8 TQ | |
| Phase Segment 1 | 1-8 TQ | |
| Phase Segment 2 | 1-8 TQ | |
| Sample Point | 75-80% | Typical 80% |
| SJW | 1-4 TQ | Sync Jump Width |

#### Data Phase (Fast)
| Parameter | Value | Notes |
|-----------|-------|-------|
| Bit Rate | 2 Mbps / 5 Mbps | MEB supports up to 5 Mbps |
| Time Quanta (TQ) | 10-20 | @ 80 MHz |
| Propagation Segment | 1-8 TQ | |
| Phase Segment 1 | 1-8 TQ | |
| Phase Segment 2 | 1-8 TQ | |
| Sample Point | 75-80% | Typical 75% |
| SJW | 1-4 TQ | |

### CAN FD Frame Format
```
SOF │ arbitration │ FDF │ res │ BRS │ ESI │ DLC │ Data (0-64B) │ CRC │ ACK │ EOF
    │   (11/29b)  │  1  │  1  │  1  │  1  │  4  │              │     │     │
```
- **FDF** (FD Format): 1 = CAN FD frame, 0 = Classic CAN
- **BRS** (Bit Rate Switch): 1 = Bit rate switching in data phase
- **ESI** (Error State Indicator): 0 = Error active, 1 = Error passive
- **DLC**: 0-8 (Classic), 9=12B, 10=16B, 11=20B, 12=24B, 13=32B, 14=48B, 15=64B

## D-PDU API CAN FD Configuration

The D-PDU API (ISO 22900-1) provides standardized functions for CAN FD:

### Key D-PDU API Functions (ISO 22900-1)
```c
// Channel configuration for CAN FD
PDUSetChannelConfig(hChannel, "CAN_FD_ENABLED", 1);
PDUSetChannelConfig(hChannel, "BITRATE_NOMINAL", 500000);
PDUSetChannelConfig(hChannel, "BITRATE_DATA", 2000000);  // or 5000000
PDUSetChannelConfig(hChannel, "SAMPLE_POINT_NOMINAL", 800);  // 80.0%
PDUSetChannelConfig(hChannel, "SAMPLE_POINT_DATA", 750);     // 75.0%
PDUSetChannelConfig(hChannel, "SJW_NOMINAL", 2);
PDUSetChannelConfig(hChannel, "SJW_DATA", 2);

// Transmit CAN FD frame
PDUSendData(hChannel, &pduData);  // pduData contains FD flags, BRS, DLC

// Receive CAN FD frame
PDUReadData(hChannel, &pduData, timeout);
```

### PDU Data Structure for CAN FD
```c
typedef struct {
    uint32_t  id;              // 11-bit (standard) or 29-bit (extended)
    uint8_t   idType;          // 0=11bit, 1=29bit
    uint8_t   fdFlags;         // Bit 0: FDF, Bit 1: BRS, Bit 2: ESI
    uint8_t   dlc;             // 0-15 (FD DLC coding)
    uint8_t   data[64];        // Up to 64 bytes
    uint64_t  timestamp;       // Hardware timestamp
} PDU_DATA_FD;
```

## CAN FD Use Cases in MEB Vehicles

### 1. High-Speed Diagnostics (DoIP over Ethernet → CAN FD Gateway)
```
Phone/PC → DoIP (Ethernet) → Gateway → CAN FD (2/5 Mbps) → ECU
```
- Used for: Flash programming, large data reads, calibration
- Gateway routes DoIP to CAN FD channels

### 2. Direct CAN FD Diagnostics
```
VNCI 6154A (USB/Ethernet) → CAN FD → ECU
```
- Used when: Direct CAN access needed, no gateway routing

### 3. Multi-Bus Access
MEB vehicles have multiple CAN FD buses:
- **CAN FD 1**: Powertrain (2/5 Mbps)
- **CAN FD 2**: Chassis (2/5 Mbps)  
- **CAN FD 3**: Body/Comfort (500 kbps or 2 Mbps)
- **CAN FD 4**: Infotainment (varies)

## ISO-TP over CAN FD (ISO 15765-2)

For UDS messages > 64 bytes (or > 8 bytes classic):

### Single Frame (SF) - ≤ 64 bytes (FD) / ≤ 8 bytes (Classic)
```
PCI: [0x0F] [DLC]  Data...
```

### First Frame (FF) - > 64 bytes
```
PCI: [0x1F] [Length:3 bytes]  Data (up to 59 bytes FD / 6 bytes Classic)
```

### Consecutive Frame (CF)
```
PCI: [0x2F] [SN:1 byte]  Data (up to 63 bytes FD / 7 bytes Classic)
```

### Flow Control (FC)
```
PCI: [0x3F] [FS:1] [BS:1] [STmin:1]
```

## Configuration via PC Software

The VCIMngr.exe provides UI for:
1. **Network Adapter Config** (`/network_adapter.bin`)
2. **Device Firmware Update**
3. **Certificate Management**
4. **Serial Number / VIN Assignment**

Actual CAN FD bit timing is typically:
- **Pre-configured** in device firmware per vehicle platform
- **Auto-negotiated** via gateway
- **Overridable** via D-PDU API channel config (advanced)

## Mobile Implementation Notes

For Phone ↔ VNCI 6154A CAN FD:

### Option A: Direct CAN FD via USB/Bluetooth
- Requires: USB Host/Accessory mode or BLE GATT
- Phone implements: CAN FD controller config, ISO-TP, UDS
- Challenge: Real-time CAN timing on mobile OS

### Option B: DoIP Tunneling (Recommended)
- Phone → DoIP (TCP/UDP 13400) → VNCI → CAN FD → ECU
- Phone only needs: DoIP stack + UDS
- VNCI handles: CAN FD bit timing, ISO-TP segmentation
- Standard-compliant, portable

### Option C: VCI Web API
- VNCI exposes REST/WebSocket API
- Phone → HTTPS/WSS → VNCI → CAN FD
- Vendor-specific, but easiest mobile integration
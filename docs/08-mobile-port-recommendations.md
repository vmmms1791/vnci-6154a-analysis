# Mobile Port Recommendations

## Target Architecture: Phone ↔ VNCI 6154A ↔ Vehicle

### Recommended Stack: Direct DoIP Implementation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MOBILE APPLICATION                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        DIAGNOSTIC LAYER                                  │ │
│  │  • UDS Services (ISO 14229)                                             │ │
│  │    - Diagnostic Session Control (0x10)                                  │ │
│  │    - ECU Reset (0x11)                                                   │ │
│  │    - Security Access (0x27)                                             │ │
│  │    - Communication Control (0x28)                                       │ │
│  │    - Read/Write Data By Identifier (0x22/0x2E)                         │ │
│  │    - Routine Control (0x31)                                             │ │
│  │    - Request Download/Upload (0x34/0x35)                                │ │
│  │    - Transfer Data (0x36)                                               │ │
│  │    - Request Transfer Exit (0x37)                                       │ │
│  │  • ISO-TP Segmentation (ISO 15765-2)                                    │ │
│  │  • Vehicle Database (VIN→ECU mapping, DID definitions)                 │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                        TRANSPORT LAYER                                   │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐  │ │
│  │  │                    DoIP Stack (ISO 13400)                           │  │ │
│  │  │  • Vehicle Discovery (UDP 13400 broadcast)                         │  │ │
│  │  │  • TCP Connection Management (Port 13400)                         │  │ │
│  │  │  • Routing Activation (OEM-specific for JLR/VW)                   │  │ │
│  │  │  • Diagnostic Message Encapsulation (Payload 0x8001)              │  │ │
│  │  │  • Alive Check / Keep-Alive (Payload 0x0007/0x0008)               │  │ │
│  │  │  • TLS Support (DoIP over TLS if required)                        │  │ │
│  │  └────────────────────────────────────────────────────────────────────┘  │ │
│  │  ┌────────────────────────────────────────────────────────────────────┐  │ │
│  │  │              Network Abstraction (Multi-interface)                 │  │ │
│  │  │  • Ethernet (USB-C RJ45 dongle) - Primary                         │  │ │
│  │  │  • WiFi (VNCI AP Mode) - Convenience                              │  │ │
│  │  │  • Bluetooth LE (GATT) - Fallback                                 │  │ │
│  │  │  • Cloud Relay (HTTPS/ZeroTier) - Remote                          │  │ │
│  │  └────────────────────────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Implementation Roadmap

### Phase 1: Core DoIP Stack (Weeks 1-3)
```kotlin/swift
// Android (Kotlin) / iOS (Swift) DoIP Implementation

class DoIPClient {
    // UDP Discovery
    fun discoverVehicles(timeoutMs: Int): List<VehicleInfo>
    
    // TCP Connection
    fun connect(vehicleIp: String, port: Int = 13400): DoIPConnection
    
    // Routing Activation
    fun activateRouting(sourceAddr: Int, targetAddr: Int, 
                       activationType: Int = 0x00, oemData: ByteArray? = null): RoutingActivationResult
    
    // Diagnostic Message
    fun sendDiagnostic(sourceAddr: Int, targetAddr: Int, udsPayload: ByteArray): ByteArray
    
    // Alive Check
    fun startAliveCheck(intervalMs: Int = 2000)
}
```

**Key Classes:**
- `DoIPHeader` - Protocol version, payload type, length
- `VehicleInfo` - VIN, EID, GID, IP, port
- `DoIPConnection` - TCP socket management
- `RoutingActivation` - SA/TA handling, OEM data

### Phase 2: UDS Services (Weeks 3-6)
```kotlin
class UDSClient(doip: DoIPClient) {
    // Session Management
    fun startSession(sessionType: Int = 0x03): UDSResponse  // Extended Diagnostic
    
    // Security Access (Seed/Key)
    fun requestSeed(level: Int): ByteArray
    fun sendKey(level: Int, key: ByteArray): Boolean
    
    // Data Reading
    fun readDataByIdentifier(dids: List<Int>): Map<Int, ByteArray>
    fun readDataByIdentifierPeriodic(dids: List<Int>, rateMs: Int): Flow<Map<Int, ByteArray>>
    
    // Flash Programming
    fun requestDownload(memoryAddress: Long, size: Long): DownloadInfo
    fun transferData(blockSequence: Int, data: ByteArray): TransferResult
    fun requestTransferExit(): Boolean
    
    // ECU Reset
    fun ecuReset(resetType: Int = 0x01): Boolean
}
```

### Phase 3: Vehicle Database (Weeks 4-5)
```kotlin
// JSON/YAML database per vehicle
data class VehicleProfile(
    val vin: String,
    val brand: String,        // "VW", "AUDI", "SKODA", "SEAT", "JLR"
    val platform: String,     // "MEB", "PPE", "MQB", "MLB"
    val ecus: List<ECUProfile>,
    val doipConfig: DoIPConfig
)

data class ECUProfile(
    val name: String,
    val doipTargetAddress: Int,
    val supportedDIDs: Map<Int, DIDDefinition>,
    val securityLevel: Int,
    var flashProcedures: List<FlashProcedure>
)

data class DoIPConfig(
    val useTLS: Boolean = false,
    val activationType: Int = 0x00,
    val oemData: ByteArray? = null,
    val aliveCheckInterval: Int = 2000
)
```

### Phase 4: Multi-Interface Support (Weeks 5-7)
```kotlin
interface DiagnosticTransport {
    fun connect(config: ConnectionConfig): Result<Unit>
    fun send(data: ByteArray): Result<ByteArray>
    fun close()
}

// Implementations:
// - EthernetTransport (USB-C dongle)
// - WiFiTransport (VNCI AP)
// - BLETransport (GATT)
// - CloudTransport (HTTPS/ZeroTier)
```

### Phase 5: Advanced Features (Weeks 7-10)
- Flash programming with progress/resume
- Offline diagnostic caching
- Multi-ECU parallel communication
- OTA firmware update for VNCI
- Diagnostic report generation (PDF/HTML)

## Platform-Specific Considerations

### Android
- **USB Host API**: For USB-C Ethernet dongles
- **NetworkCallback**: WiFi/Ethernet detection
- **NsdManager**: mDNS/Bonjour for VNCI discovery
- **OkHttp/Netty**: TCP/UDP socket management
- **Coroutines/Flow**: Async DoIP/UDS operations

### iOS
- **Network.framework**: Modern TCP/UDP (NWConnection)
- **NetworkExtension**: WiFi configuration (NEHotspotConfiguration)
- **CoreBluetooth**: BLE GATT fallback
- **URLSession**: Cloud REST API
- **Swift Concurrency**: Async/await for DoIP/UDS

## VNCI 6154A Specific Configuration

### Connection Parameters
```json
{
  "vnci6154a": {
    "doipPort": 13400,
    "discoveryTimeoutMs": 3000,
    "connectionTimeoutMs": 5000,
    "routingActivation": {
      "sourceAddress": 0x0E00,
      "defaultTargetAddress": 0x1000,
      "activationType": 0x00,
      "jlrOemData": "REQUIRED_FOR_JLR",
      "vwOemData": "NOT_REQUIRED"
    },
    "aliveCheck": {
      "enabled": true,
      "intervalMs": 2000,
      "timeoutMs": 5000
    },
    "tls": {
      "enabled": false,
      "caCert": "ca_cert.pem",
      "clientCert": "client_cert.pem",
      "clientKey": "client_key.pem"
    }
  }
}
```

### JLR Special Handling
For JLR vehicles (confirmed via D-PDU.xml):
- Routing Activation **requires** OEM-specific data
- May need **Security Access** before Routing Activation
- Some models use **DoIP over TLS** (TCP 13400 + TLS)
- VIN must match gateway records

### VW MEB Special Handling
- Standard Routing Activation (Type 0x00)
- CAN FD at 2/5 Mbps for flash programming
- Multiple gateway ECUs (diagnose each separately)
- Support for **DoIP Entity Status** (0x4001/0x4002)

## Security Considerations

### Certificate Pinning
```kotlin
// Pin VNCI/Cloud certificates
val pinnedCerts = setOf(
    "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
    "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
)
```

### Secure Storage
- **Android**: EncryptedSharedPreferences / Keystore
- **iOS**: Keychain (kSecAttrAccessibleWhenUnlockedThisDeviceOnly)

### Session Security
- Unique session IDs per diagnostic session
- Encrypt diagnostic logs at rest
- Clear sensitive data (seeds, keys, VIN) on app background

## Testing Strategy

### Unit Tests
- DoIP header encoding/decoding
- UDS request/response parsing
- ISO-TP segmentation/reassembly
- Routing activation logic

### Integration Tests
- VNCI 6154A hardware-in-loop
- Vehicle gateway simulator (DoIP)
- Multi-ECU scenarios
- Network interruption handling

### Field Tests
- VW ID.3/ID.4 (MEB) - CAN FD flash
- Audi Q4 e-tron (MEB) - Multi-ECU
- JLR I-PACE - DoIP TLS + OEM activation
- Skoda Enyaq - Standard VW DoIP

## Code Structure (Suggested)

```
mobile-diagnostic/
├── core/
│   ├── doip/
│   │   ├── DoIPClient.kt
│   │   ├── DoIPHeader.kt
│   │   ├── VehicleDiscovery.kt
│   │   ├── RoutingActivation.kt
│   │   └── AliveCheck.kt
│   ├── uds/
│   │   ├── UDSClient.kt
│   │   ├── services/
│   │   │   ├── DiagnosticSession.kt
│   │   │   ├── SecurityAccess.kt
│   │   │   ├── DataByIdentifier.kt
│   │   │   ├── RoutineControl.kt
│   │   │   └── FlashProgramming.kt
│   │   └── isotp/
│   │       ├── ISOtpSender.kt
│   │       └── ISOtpReceiver.kt
│   ├── transport/
│   │   ├── DiagnosticTransport.kt
│   │   ├── EthernetTransport.kt
│   │   ├── WiFiTransport.kt
│   │   ├── BLETransport.kt
│   │   └── CloudTransport.kt
│   └── vehicle/
│       ├── VehicleDatabase.kt
│       ├── VehicleProfile.kt
│       └── ECUProfile.kt
├── android/
│   ├── UsbEthernetManager.kt
│   ├── WifiManager.kt
│   └── NetworkMonitor.kt
├── ios/
│   ├── NetworkExtensionManager.swift
│   ├── BluetoothManager.swift
│   └── NetworkMonitor.swift
└── shared/
    ├── VehicleDatabase.json
    ├── certificates/
    └── config/
```

## Effort Estimation

| Phase | Android | iOS | Shared |
|-------|---------|-----|--------|
| DoIP Stack | 2 weeks | 2 weeks | 3 weeks |
| UDS Services | 3 weeks | 3 weeks | 4 weeks |
| Vehicle DB | 1 week | 1 week | 2 weeks |
| Multi-Transport | 2 weeks | 2 weeks | 2 weeks |
| Advanced Features | 3 weeks | 3 weeks | 3 weeks |
| Testing/Hardware | 2 weeks | 2 weeks | 2 weeks |
| **Total** | **~13 weeks** | **~13 weeks** | **~16 weeks** |

## Alternative: Use Existing D-PDU API

If vendor provides mobile D-PDU API:
```kotlin
// Hypothetical mobile D-PDU API
val dpuApi = DpuApiLoader.load("Bosch_JLR_DoIP")
val channel = dpuApi.createChannel()
channel.connect()
channel.sendData(diagnosticRequest)
val response = channel.readData(timeout)
```
**Pros**: No protocol implementation needed
**Cons**: Vendor dependency, licensing, binary distribution

## Conclusion

**Direct DoIP implementation is recommended** for:
1. **Independence** - No vendor lock-in
2. **Standards compliance** - ISO 13400/14229/15765
3. **Flexibility** - Works with any DoIP gateway
4. **Maintainability** - Open source libraries available
5. **Future-proof** - Supports new vehicles automatically

The VNCI 6154A is a **DoIP gateway** - the mobile app should speak DoIP directly to it.
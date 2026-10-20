# Mobile DoIP Implementation - Detailed Guide

## Direct ISO 13400 Implementation on Mobile

This document provides a comprehensive guide for implementing a **direct DoIP (ISO 13400) stack** on mobile platforms (Android/iOS) to communicate with VNCI 6154A and vehicle gateways, **without vendor D-PDU API dependencies**.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        MOBILE APP                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  UDS LAYER (ISO 14229)                                     │  │
│  │  • Diagnostic Session Control (0x10)                       │  │
│  │  • Security Access (0x27) - Seed/Key                       │  │
│  │  • Read/Write Data By Identifier (0x22/0x2E)              │  │
│  │  • Routine Control (0x31)                                  │  │
│  │  • Request Download/Transfer Data/Exit (0x34/0x36/0x37)   │  │
│  └─────────────────────┬──────────────────────────────────────┘  │
│                        │ ISO-TP (ISO 15765-2)                    │
│  ┌─────────────────────▼──────────────────────────────────────┐  │
│  │  DoIP LAYER (ISO 13400)                                    │  │
│  │  • Vehicle Discovery (UDP 13400 broadcast)                 │  │
│  │  • TCP Connection Management (Port 13400)                  │  │
│  │  • Routing Activation (0x0005/0x0006)                      │  │
│  │  • Diagnostic Message (0x8001/0x8002/0x8003)              │  │
│  │  • Alive Check (0x0007/0x0008)                             │  │
│  │  • TLS Support (optional for JLR)                          │  │
│  └─────────────────────┬──────────────────────────────────────┘  │
│                        │ TCP/UDP Sockets                         │
└────────────────────────┼────────────────────────────────────────┘
                         ▼
              ┌───────────────────────┐
              │   VNCI 6154A          │
              │   (DoIP Gateway)      │
              └───────────┬───────────┘
                          ▼
              ┌───────────────────────┐
              │   Vehicle Gateway     │
              │   (DoIP Server)       │
              └───────────┬───────────┘
                          ▼
              ┌───────────────────────┐
              │   CAN FD / CAN Bus    │
              │   (ECU Communication) │
              └───────────────────────┘
```

---

## What the Mobile App Implements

### 1. DoIP Header Encoding/Decoding

```kotlin
data class DoIPHeader(
    val protocolVersion: Byte = 0x02,
    val inverseProtocolVersion: Byte = 0xFD,
    val payloadType: UInt,      // 0x0001, 0x0005, 0x8001, etc.
    val payloadLength: UInt     // Big-endian
)

fun encode(header: DoIPHeader): ByteArray = ByteArray(8) { ... }
fun decode(bytes: ByteArray): DoIPHeader = ...
```

### 2. Vehicle Discovery (UDP Broadcast)

```kotlin
fun discoverVehicles(timeoutMs: Int = 3000): List<VehicleInfo> {
    val socket = DatagramSocket()
    socket.broadcast = true
    
    // Send Vehicle Identification Request (0x0001)
    val request = buildDoIPMessage(payloadType = 0x0001, payload = ByteArray(0))
    socket.send(DatagramPacket(request, request.size, InetAddress.getByName("255.255.255.255"), 13400))
    
    // Collect responses (0x0002) with VIN, EID, GID
    return parseResponses(socket, timeoutMs)
}
```

### 3. TCP Connection + Routing Activation

```kotlin
class DoIPConnection(private val socket: Socket) {
    
    fun activateRouting(
        sourceAddress: Int = 0x0E00,      // Tester logical address
        targetAddress: Int = 0x1000,      // Target ECU (gateway)
        activationType: Int = 0x00,       // 0x00=Default, 0x01=OEM
        oemData: ByteArray? = null        // Required for JLR!
    ): RoutingActivationResult {
        
        // Build Routing Activation Request (0x0005)
        val payload = buildRoutingActivationPayload(
            sourceAddress, targetAddress, activationType, oemData
        )
        send(0x0005, payload)
        
        // Parse Response (0x0006)
        val response = receive()
        return parseRoutingActivationResponse(response)
    }
}
```

### 4. Diagnostic Message Exchange (UDS over DoIP)

```kotlin
fun sendUDSRequest(targetAddress: Int, udsPayload: ByteArray): ByteArray {
    // Encapsulate UDS in DoIP Diagnostic Message (0x8001)
    val doipPayload = buildDiagnosticMessagePayload(
        sourceAddress = 0x0E00,
        targetAddress = targetAddress,
        userData = udsPayload
    )
    send(0x8001, doipPayload)
    
    // Wait for Positive ACK (0x8002)
    waitForAck()
    
    // Receive Response (0x8001 with UDS response)
    return receiveUDSResponse()
}
```

### 5. Alive Check (Keep-Alive)

```kotlin
fun startAliveCheck(intervalMs: Int = 2000) {
    scope.launch {
        while (isActive) {
            send(0x0007, ByteArray(0))  // Alive Check Request
            val response = receiveWithTimeout(5000)
            if (response.payloadType != 0x0008) {
                handleConnectionLost()
            }
            delay(intervalMs)
        }
    }
}
```

---

## Why NOT D-PDU API on Mobile

| D-PDU API Approach | Direct DoIP Approach |
|-------------------|-------------------|
| Requires vendor DLLs (BVTX-VCI-PDU.dll) | Standard sockets only |
| Windows only (x86/x64) | Cross-platform (Android/iOS/Linux) |
| Bosch licensing | Open source standards |
| Vendor lock-in | Independence |
| Complex JNI/FFI on mobile | Native Kotlin/Swift code |

---

## Transport Interfaces for Mobile

| Interface | Connection to VNCI 6154A | Android API | iOS API |
|-----------|---------------------------|-------------|---------|
| **Ethernet** | USB-C → RJ45 adapter | `UsbManager` + `NetworkCallback` | `Network.framework` (NWConnection) |
| **WiFi** | VNCI in AP mode | `WifiManager` + `NsdManager` | `NEHotspotConfiguration` |
| **Cloud** | Via www.rokwy.com + ZeroTier | `OkHttp` + `URLSession` | `URLSession` |
| **BLE** | If VNCI supports GATT | `BluetoothGatt` | `CoreBluetooth` |

---

## JLR / VW Specific Configuration

```kotlin
data class VehicleDoIPConfig(
    val brand: String,              // "JLR" / "VW" / "AUDI" / etc.
    val platform: String,           // "MEB" / "PPE" / "MLB"
    val routingActivation: RoutingConfig,
    val useTLS: Boolean = false,
    val aliveCheckIntervalMs: Int = 2000
)

data class RoutingConfig(
    val activationType: Int = 0x00,
    val oemData: ByteArray? = null,  // JLR: MANDATORY! VW: null
    val requiresSecurityAccessFirst: Boolean = false  // JLR: true
)

// JLR Example:
val jlrConfig = VehicleDoIPConfig(
    brand = "JLR",
    platform = "MLB",
    routingActivation = RoutingConfig(
        activationType = 0x01,
        oemData = buildJLROEMData(vin),  // Challenge/Response
        requiresSecurityAccessFirst = true
    ),
    useTLS = true  // Some models
)

// VW MEB Example:
val vwConfig = VehicleDoIPConfig(
    brand = "VW",
    platform = "MEB",
    routingActivation = RoutingConfig(
        activationType = 0x00,
        oemData = null
    )
)
```

---

## Existing Libraries (Don't Write from Scratch)

| Language | Library | Status |
|----------|---------|--------|
| **Kotlin/Java** | `doip-java` (GitHub) | Basic implementation exists |
| **Python** | `python-doip` | Mature |
| **C++** | `libdoip` | Reference implementation |
| **Rust** | `doip-rs` | Exists |
| **Go** | `go-doip` | Exists |

**Recommendation**: Port `libdoip` (C++) or `python-doip` to Kotlin/Swift — ~2-3 weeks instead of 3 months from scratch.

---

## Testing Without Hardware

```kotlin
// DoIP Gateway Simulator for unit tests
class DoIPGatewaySimulator {
    val knownVehicles = mapOf(
        "WVWZZZAUZGW123456" to VehicleInfo(
            vin = "WVWZZZAUZGW123456",
            eid = byteArrayOf(0x00, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E),
            gid = byteArrayOf(0x00, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E),
            ip = "192.168.1.100",
            gatewayType = "VW_MEB"
        )
    )
    
    fun handleVehicleIdentificationRequest(): ByteArray { ... }
    fun handleRoutingActivation(request: ByteArray): ByteArray { ... }
    fun handleDiagnosticMessage(request: ByteArray): ByteArray { ... }
}
```

---

## Implementation Effort Estimate

| Component | Complexity | Time |
|-----------|------------|------|
| DoIP Header/Message codec | Low | 3-5 days |
| UDP Discovery + TCP Connection | Low | 3-5 days |
| Routing Activation (JLR/VW) | Medium | 1-2 weeks |
| ISO-TP Segmentation (multi-frame) | Medium | 1 week |
| UDS Services (0x10, 0x22, 0x27, 0x31, 0x34-37) | High | 3-4 weeks |
| Multi-transport abstraction | Medium | 1-2 weeks |
| Vehicle Database (VIN→ECU→DIDs) | Low | Ongoing |
| **TOTAL** | | **~8-12 weeks** |

---

## Result

A **full diagnostic client** in the phone that works with **any DoIP gateway** (VNCI 6154A, VAS, ODIS, other VCIs), independent of vendor SDKs.

---

## References

- ISO 13400:2019 - Road vehicles - Diagnostics over Internet Protocol (DoIP)
- ISO 14229 - Unified Diagnostic Services (UDS)
- ISO 15765-2 - ISO-TP (Transport Protocol)
- ISO 22900-1 - D-PDU API (for reference only, not used)
- VNCI 6154A D-PDU.xml analysis in this repository
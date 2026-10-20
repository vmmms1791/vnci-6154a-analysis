# Network Communication Analysis

## PC Software Network Stack

### VCIMngr.exe Network Libraries

| Library | Purpose | Version |
|---------|---------|---------|
| **oatpp** | C++ web framework (TCP/HTTP client/server) | Modern C++17 |
| **libevent** (event.dll/core/openssl) | Async event loop, network I/O | 2.x |
| **OpenSSL** (libcrypto/libssl) | TLS/SSL encryption | 1.1.1 |
| **WinINet/WinHTTP** | Windows HTTP client APIs | System |

### oatpp Usage (From Strings)
```
oatpp::network::tcp::client::ConnectionProvider
  - getConnection() - Blocking TCP connect
  - getConnectionAsync() - Async TCP connect
  - doConnect() - Internal connect logic
  - ConnectionInvalidator - Connection pooling

oatpp::network::tcp::Connection
  - setStreamIOMode(BLOCKING/ASYNCHRONOUS)
  - Read/Write operations

oatpp::web::protocol::http::incoming::ResponseHeadersReader
  - HTTP response parsing

oatpp::parser::json::mapping::Serializer/Deserializer
  - JSON serialization for REST APIs
```

### Network DTOs (Data Transfer Objects)
Found in strings at 0x462ce4+:
- `NetworkCreationInfoDto` - Create network config
- `NetworkMembersDto` - Network members list
- `NetworkStatusDto` - Network status
- `JoinNetworkRequestDto` - Join network request

### REST API Endpoints (Inferred)
```
POST   /controller/network              - createNetwork
DELETE /controller/network              - deleteNetwork
GET    /controller/network              - listNetworks
POST   /controller/network/{network_id}/member - createUpdateNetworkMember
GET    /controller/network/{network_id}/member - listNetworkMemberIDs
GET    /controller/network/{network_id}/member/{node_id} - getNetworkMemberByID
POST   /controller/network/{network_id} - generateNetwork
GET    /network/{network_id}            - networkStatus
POST   /joinNetwork                     - joinNetwork
POST   /leaveNetwork                    - leaveNetwork
```

## Device Network Interfaces

### Ethernet (Primary - DoIP)
- **Interface**: RJ45 100/1000 Mbps
- **Protocol**: DoIP (ISO 13400) over TCP/UDP
- **Port**: 13400 (standard DoIP)
- **Discovery**: UDP Broadcast 255.255.255.255:13400
- **IP Config**: DHCP or Static (configurable via PC software)

### USB (Secondary - D-PDU API)
- **Interface**: USB 2.0/3.0
- **Protocol**: Vendor-specific (Bosch VTX protocol)
- **Driver**: BVTX-VCI-PDU.dll loads USB driver
- **Endpoint**: Bulk IN/OUT for diagnostic data

### WiFi (Remote Diagnostic)
From strings:
- `remote_wifi_ver`, `remote_wifi_txt` - WiFi version/info
- `remote_ds_ver`, `remote_ds_txt` - Data service version/info
- `UIRemoteInfoWnd` - Remote info window
- `remote_diag.xml` - Remote diagnostic UI

Likely supports:
- **AP Mode**: Device creates hotspot for phone connection
- **Station Mode**: Connects to local WiFi for cloud access
- **ZeroTier**: VPN mesh networking (ZeroTierOne.msi in Patch/)

## Cloud/Backend Communication

### FTP Update Server
From `setting.ini`:
```ini
[FTP]
IPAddr="www.rokwy.com"
Dir="./"
```
- Firmware binary downloads
- Configuration files
- Certificate updates

### TLS/SSL Certificates
Files present:
- `ca_cert.pem` / `ca_cert_b.pem` - CA certificates (primary/backup)
- `server_key.pem` / `server_key_b.pem` - Private keys (primary/backup)

Used for:
1. **HTTPS to www.rokwy.com** - Firmware updates, config sync
2. **DoIP over TLS** - If vehicle gateway requires TLS (some OEMs)
3. **Remote Diagnostic Auth** - Mutual TLS for session authorization

### ZeroTier VPN
`ZeroTierOne.msi` in Patch folder suggests:
- Mesh VPN for remote device access
- Direct peer-to-peer through NAT
- Used for: Remote diagnostic sessions from cloud

## Network Configuration File

### /network_adapter.bin (Referenced at 0x461174)
Binary configuration for network adapter:
- IP address / Subnet / Gateway
- DNS servers
- VLAN tags
- Firewall rules
- DoIP-specific settings (source/target addresses)

## Firewall/Network Security

From resource images:
- `firewall.png`, `firewall_ok.png` - Firewall status UI
- `antivirus.png` - Antivirus status (Windows Defender integration?)

## Remote Diagnostic Flow

```
┌─────────────┐     HTTPS/TLS      ┌─────────────┐     DoIP/VPN     ┌─────────────┐
│  Mobile/    │ ◄─────────────────► │  Cloud      │ ◄─────────────► │  VNCI 6154A │
│  Tech PC    │   (www.rokwy.com)   │  Backend    │   (ZeroTier)    │  Device     │
└─────────────┘                     └─────────────┘                 └──────┬──────┘
                                                                         │
                                                                         ▼
                                                                  ┌─────────────┐
                                                                  │   Vehicle   │
                                                                  │  (DoIP/CAN) │
                                                                  └─────────────┘
```

### Authentication (VNCI_REMOTE_DIAGNOSTIC_Mutex)
- Mutex name: `VNCI_REMOTE_DIAGNOSTIC_Mutex`
- Ensures single remote diagnostic session
- Prevents concurrent access conflicts

## Mobile App Network Requirements

For Phone ↔ VNCI 6154A direct communication:

### Option 1: Direct Ethernet (USB-C/OTG Ethernet Adapter)
```
Phone --USB-C--> Ethernet Adapter --RJ45--> VNCI 6154A
```
- Phone implements: DoIP stack (UDP/TCP 13400)
- No cloud dependency
- Requires: USB Host mode, Ethernet dongle

### Option 2: WiFi Direct / Hotspot
```
Phone --WiFi--> VNCI 6154A (AP Mode)
```
- Phone connects to VNCI WiFi hotspot
- DoIP over TCP 13400
- Requires: VNCI WiFi AP firmware support

### Option 3: Bluetooth LE (If Supported)
```
Phone --BLE--> VNCI 6154A
```
- Custom GATT service for diagnostic data
- Lower bandwidth, higher latency
- Good for basic UDS, not flash programming

### Option 4: Cloud Relay (Existing Infrastructure)
```
Phone --HTTPS--> www.rokwy.com --ZeroTier/VPN--> VNCI 6154A
```
- Uses existing remote diagnostic infrastructure
- Requires: Backend API integration, user accounts
- Works over any internet connection

## Recommended Mobile Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Mobile App                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  DoIP Stack │  │  UDS/ISO-TP │  │  Vehicle DB │             │
│  │  (ISO 13400)│  │  (ISO 14229)│  │  (VIN/ECU)  │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                    │
│         ▼                ▼                ▼                    │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Transport Abstraction Layer                 │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ Ethernet │ │   WiFi   │ │   BLE    │ │  Cloud   │   │  │
│  │  │  (DoIP)  │ │  (DoIP)  │ │  (GATT)  │ │  (REST)  │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation Priority
1. **DoIP over Ethernet** - Primary, standard-compliant, high bandwidth
2. **DoIP over WiFi** - Convenience, cable-free
3. **Cloud REST API** - Remote access, fleet management
4. **BLE GATT** - Fallback, basic diagnostics only
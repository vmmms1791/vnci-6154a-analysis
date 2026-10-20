# File Structure Analysis

## Installer Package

**File**: VNCI6154ADevMngrSetup_v4.9.exe
- **Type**: Inno Setup 6.1.0 (Unicode) installer
- **Size**: 47,180,272 bytes
- **SHA256**: b57b35a11f349d1f086ef9c1f72ffc198ce31c1c5817af7d78df668e9dde5faa

## Extracted Components

### Main Application
```
app/VNCI 6154A Device Manager/
├── VCIMngr.exe                    # Main executable (3.5 MB, 3651 procedures, 1505 strings)
├── DuiLib_u.dll                   # DirectUI library (GUI)
├── event.dll                      # libevent core (154 KB, 1043 procedures)
├── event_core.dll                 # libevent core (92 KB, 701 procedures)  
├── event_openssl.dll              # libevent OpenSSL binding (11 KB, 281 procedures)
├── libcrypto-1_1.dll              # OpenSSL 1.1 crypto
├── libssl-1_1.dll                 # OpenSSL 1.1 SSL/TLS
├── setting.ini                    # Configuration (FTP server: www.rokwy.com)
├── ca_cert.pem                    # CA certificate
├── server_key.pem                 # Server private key
├── ca_cert_b.pem                  # Backup CA certificate
├── server_key_b.pem               # Backup server key
└── resource/                      # UI resources (XML layouts, images)
    ├── D-PDU.xml                  # D-PDU API configuration (KEY FINDING)
    ├── device_manager.xml         # Device manager UI
    ├── remote_diag.xml            # Remote diagnostic UI
    ├── messages.xml               # Message definitions
    └── skin.xml                   # UI skin
```

### Patch Components
```
app/Patch/
├── planet                         # Unknown binary
├── vc2022redist_x64.exe           # Visual C++ 2022 Redist x64
├── vc2022redist_x86.exe           # Visual C++ 2022 Redist x86
└── ZeroTierOne.msi                # ZeroTier VPN installer
```

## Main Executable: VCIMngr.exe

- **Format**: PE32 executable (GUI) Intel 80386
- **Architecture**: x86 (32-bit)
- **Sections**: 7 (.text, .rdata, .data, .rsrc, .reloc, Headers, tdb)
- **Image Base**: 0x400000
- **Procedures**: 3,651
- **Strings**: 1,505
- **PDB Reference**: VCIMngr.pdb (GUID: 4ae042ca-5e71-420f-812d-c50eb56e8298)

### Key Imports
- **KERNEL32.DLL**: Standard Windows APIs
- **WS2_32.DLL**: Winsock2 (WSAEnumNetworkEvents)
- **WININET.DLL**: InternetConnectW
- **WINHTTP.DLL**: WinHttpConnect
- **DUILIB_U.DLL**: DirectUI library
- **EVENT.DLL / EVENT_CORE.DLL / EVENT_OPENSSL.DLL**: libevent
- **MSVCP140.DLL / VCRUNTIME140.DLL**: Visual C++ Runtime

## Resource XML Files

### D-PDU.xml (Critical Finding)
Contains MVCI_PDU_API_ROOT configuration (v2.2.0) with multiple VCI implementations:
- **JLR-DoIP**: "JLR - JLR-DoIP, D-PDU API by Bosch" ← **DoIP Confirmed**
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

Each entry specifies:
- LIBRARY_FILE (DLL path)
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
UI layout for remote diagnostics with buttons:
- btn_cpynwid (Copy Network ID)
- btn_auth (Authorize)
- btn_disconnect
- btn_cpyregdata (Copy Registration Data)
- InfoBox (RichEdit for logging)
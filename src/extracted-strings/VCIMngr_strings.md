# Extracted Strings - VCIMngr.exe

## Device Identification
| Address | String |
|---------|--------|
| 0x4607dc | VAS6154A |
| 0x4611d8 | dev-6154a |
| 0x4612b4 | VAS6154A |
| 0x461a9c | VNCI6154ADevMngrSetup.exe |

## D-PDU API Related
| Address | String |
|---------|--------|
| 0x4617cc | pducustomer |
| 0x461958 | SOFTWARE\\D-PDU API |
| 0x461978 | D-PDU API RDF file: "%s"\n |
| 0x461994 | MVCI_PDU_API_ROOT |
| 0x4619ab | I_PDU_API |

## Network/Remote Diagnostic
| Address | String |
|---------|--------|
| 0x4601c0 | UIRemoteInfoWnd |
| 0x460c78 | remote_fw_vers |
| 0x460f3c | remote_wifi_ver |
| 0x460f5c | remote_ds_ver |
| 0x460fb4 | remote_wifi_txt |
| 0x460fd4 | remote_ds_txt |
| 0x461f30 | remote_diag.xml |
| 0x462bd4 | VNCI_REMOTE_DIAGNOSTIC_Mutex |

## Network DTOs (oatpp)
| Address | String |
|---------|--------|
| 0x461174 | /network_adapter.bin |
| 0x462ce4 | NetworkCreationInfoDto |
| 0x462cfc | network ID |
| 0x462d08 | network_id |
| 0x462d14 | NetworkMembersDto |
| 0x462d28 | members of network |
| 0x462e00 | createNetwork |
| 0x462e40 | network |
| 0x462e48 | deleteNetwork |
| 0x463ba0 | JoinNetworkRequestDto |
| 0x463bf0 | NetworkStatusDto |
| 0x463c18 | network/{network_id} |
| 0x463c30 | joinNetwork |
| 0x463c3c | networkStatus |
| 0x463c4c | listNetworks |
| 0x463c5c | leaveNetwork |
| 0x463c6c | controller/network |
| 0x463c80 | generateNetwork |
| 0x463c90 | controller/network/{network_id}/member |
| 0x463cb8 | listNetworkMemberIDs |
| 0x463cd0 | controller/network/{network_id}/member/{node_id} |
| 0x463d04 | createUpdateNetworkMember |
| 0x463d20 | getNetworkMemberByID |
| 0x463d38 | controller/network/{network_id} |

## oatpp Network Strings
| Address | String |
|---------|--------|
| 0x45af98 | [oatpp::network::tcp::client::ConnectionProvider::getConnection()]. Error. Call to getaddrinfo() failed with code |
| 0x45b010 | [oatpp::network::tcp::client::ConnectionProvider::getConnection()]. Error. Call to getaddrinfo() returned no results. |
| 0x45b088 | [oatpp::network::tcp::client::ConnectionProvider::getConnection()]: Error. Can't connect. |
| 0x45b0f8 | [oatpp::network::tcp::client::ConnectionProvider::getConnectionAsync()]. Error. Call to getaddrinfo() failed. |
| 0x45b168 | [oatpp::network::tcp::client::ConnectionProvider::getConnectionAsync()]. Error. Call to getaddrinfo() returned no results. |
| 0x45b1e8 | [oatpp::network::tcp::client::ConnectionProvider::getConnectionAsync()]: Error. Can't connect. |
| 0x45b248 | [oatpp::network::tcp::client::ConnectionProvider::doConnect()]: Error. The parameter m_clientHandle is a listening socket. |
| 0x45cb60 | [oatpp::network::tcp::Connection::setStreamIOMode()]: Error. Can't set stream I/O mode to IOMode::BLOCKING. |
| 0x45cbd0 | [oatpp::network::tcp::Connection::setStreamIOMode()]: Error. Can't set stream I/O mode to IOMode::ASYNCHRONOUS. |

## libevent Strings (event.dll / event_core.dll)
| Address | String |
|---------|--------|
| 0x10027630 / 0x100185e0 | %s: reentrant invocation. Only one event_base_loop can run on each event_base at once. |
| 0x10027884 / 0x10018834 | Can't change lock callbacks once they have been initialized. |
| 0x10027928 / 0x100188d8 | Can't change condition callbacks once they have been initialized. |
| 0x10027d14 / 0x10018cc4 | Request canceled |
| 0x10028220 / 0x100191d0 | Added a signal to event base %p with signals already added to event_base %p. Only one can have signals at a time with the %s backend. |
| 0x10028e4c | %s: cannot get connection on %I64d |
| 0x100299b0 | Unable to seed random number generator; DNS can't run. |
| 0x10029b04 | dns request canceled |
| 0x1002c863 | evdns_cancel_request |
| 0x1002c929 | evdns_getaddrinfo_cancel |
| 0x1002cfd5 | event_deferred_cb_cancel_ |
| 0x1002d557 | evhttp_cancel_request |
| 0x1002e8ad | evutil_set_evdns_getaddrinfo_cancel_fn_ |
| 0x1002f37c / 0x1001cd68 | __stdio_common_vsscanf |

## Settings
| File | Content |
|------|---------|
| setting.ini | [PREFER] LanguageIndex=0 [FTP] IPAddr="www.rokwy.com" Dir="./" |

## D-PDU.xml Key Entries
```xml
<MVCI_PDU_API>
    <SHORT_NAME>D_PDU_API_Bosch_JLR_DoIP</SHORT_NAME>
    <DESCRIPTION>JLR - JLR-DoIP, D-PDU API by Bosch</DESCRIPTION>
    <SUPPLIER_NAME>Bosch</SUPPLIER_NAME>
</MVCI_PDU_API>
```
(Plus 26 other VCI entries for VW, Ford, GM, Opel, etc.)
# Ghidra Analysis Scripts

## Script 1: Find D-PDU API Related Functions

```python
# find_dpdu_functions.py
# Ghidra Python script to locate D-PDU API integration points

from ghidra.program.model.symbol import SourceType
from ghidra.program.model.listing import CodeUnit

def find_dpdu_references():
    """Find all references to D-PDU API strings"""
    strings_to_find = [
        "SOFTWARE\\\\D-PDU API",
        "MVCI_PDU_API_ROOT",
        "I_PDU_API",
        "pducustomer",
        "D-PDU API RDF file"
    ]
    
    listing = currentProgram.getListing()
    string_manager = currentProgram.getStringManager()
    
    for s in string_manager.getStrings(True):
        str_val = str(s.getValue())
        for target in strings_to_find:
            if target.lower() in str_val.lower():
                addr = s.getAddress()
                print(f"Found string at {addr}: {str_val[:100]}")
                
                # Get xrefs
                refs = getReferencesTo(addr)
                for ref in refs:
                    from_addr = ref.getFromAddress()
                    func = getFunctionContaining(from_addr)
                    if func:
                        print(f"  Referenced from function: {func.getName()} at {func.getEntryPoint()}")
                    else:
                        print(f"  Referenced from: {from_addr}")

if __name__ == "__main__":
    find_dpdu_references()
```

## Script 2: Analyze Network/DoIP Functions

```python
# analyze_network_functions.py
# Find network-related functions using oatpp/libevent patterns

def find_network_functions():
    """Identify functions related to network communication"""
    
    # Search for functions with network-related names
    func_manager = currentProgram.getFunctionManager()
    functions = func_manager.getFunctions(True)
    
    network_keywords = [
        "connect", "Connect", "CONNECT",
        "send", "Send", "SEND",
        "recv", "Recv", "RECV", "read", "Read", "READ",
        "tcp", "TCP", "udp", "UDP",
        "socket", "Socket", "SOCKET",
        "doip", "DoIP", "DOIP",
        "network", "Network", "NETWORK",
        "http", "HTTP", "Http",
        "oatpp", "Oatpp"
    ]
    
    for func in functions:
        name = func.getName()
        for kw in network_keywords:
            if kw in name:
                print(f"Function: {name} at {func.getEntryPoint()}")
                print(f"  Signature: {func.getSignature()}")
                break

if __name__ == "__main__":
    find_network_functions()
```

## Script 3: Extract DoIP Protocol Constants

```python
# extract_doip_constants.py
# Search for DoIP protocol constants in memory

def find_doip_constants():
    """Search for DoIP payload type constants"""
    
    # DoIP Payload Types (ISO 13400)
    doip_payload_types = {
        0x0000: "Generic Negative ACK",
        0x0001: "Vehicle Identification Request",
        0x0002: "Vehicle Identification Response",
        0x0003: "Vehicle ID Request with EID",
        0x0004: "Vehicle ID Request with VIN",
        0x0005: "Routing Activation Request",
        0x0006: "Routing Activation Response",
        0x0007: "Alive Check Request",
        0x0008: "Alive Check Response",
        0x4001: "DoIP Entity Status Request",
        0x4002: "DoIP Entity Status Response",
        0x8001: "Diagnostic Message",
        0x8002: "Diagnostic Message Positive ACK",
        0x8003: "Diagnostic Message Negative ACK"
    }
    
    # Search memory for these constants
    mem = currentProgram.getMemory()
    for block in mem.getBlocks():
        if block.isReadable() and not block.isExecuteOnly():
            data = bytearray(block.getSize())
            mem.getBytes(block.getStart(), data)
            
            # Search for 2-byte constants (little endian)
            for val, desc in doip_payload_types.items():
                le_bytes = val.to_bytes(2, 'little')
                idx = 0
                while True:
                    idx = data.find(le_bytes, idx)
                    if idx == -1:
                        break
                    addr = block.getStart().add(idx)
                    print(f"Found DoIP payload type 0x{val:04X} ({desc}) at {addr}")
                    idx += 1

if __name__ == "__main__":
    find_doip_constants()
```

## Script 4: CAN FD Configuration Search

```python
# find_canfd_config.py
# Search for CAN FD related configuration

def find_canfd_strings():
    """Search for CAN FD related strings and constants"""
    
    canfd_keywords = [
        "CAN FD", "CAN_FD", "canfd", "can_fd",
        "FD", "Flexible Data",
        "bitrate", "BITRATE", "baud", "BAUD",
        "sample_point", "SAMPLE_POINT",
        "sjw", "SJW", "sync jump",
        "arbitration", "data_phase",
        "M_CAN", "m_can",
        "ISO 11898", "11898"
    ]
    
    string_manager = currentProgram.getStringManager()
    for s in string_manager.getStrings(True):
        str_val = str(s.getValue())
        for kw in canfd_keywords:
            if kw.lower() in str_val.lower():
                print(f"Found at {s.getAddress()}: {str_val}")

if __name__ == "__main__":
    find_canfd_strings()
```

## Script 5: Generate Function Call Graph

```python
# generate_callgraph.py
# Generate call graph for key functions

def generate_callgraph(entry_func_name):
    """Generate call graph starting from entry function"""
    func = getGlobalFunctions(entry_func_name)
    if not func:
        print(f"Function {entry_func_name} not found")
        return
    
    func = func[0]
    visited = set()
    
    def print_calls(f, depth=0):
        if f.getEntryPoint() in visited or depth > 5:
            return
        visited.add(f.getEntryPoint())
        indent = "  " * depth
        print(f"{indent}{f.getName()} @ {f.getEntryPoint()}")
        
        # Get called functions
        calls = getReferencesFrom(f.getEntryPoint())
        for call in calls:
            if call.getReferenceType().isCall():
                called_func = getFunctionContaining(call.getToAddress())
                if called_func:
                    print_calls(called_func, depth + 1)
    
    print_calls(func)

if __name__ == "__main__":
    # Example: analyze D-PDU reference function
    generate_callgraph("FUN_0041028e")  # Address from xref analysis
```

## Script 6: Export Decompilation

```python
# export_decompilation.py
# Export decompiled code for key functions

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def export_function_decompilation(func_addr, output_file):
    """Export decompiled C code for a function"""
    decompiler = DecompInterface()
    decompiler.openProgram(currentProgram)
    
    func = getFunctionAt(toAddr(func_addr))
    if not func:
        print(f"Function at {func_addr} not found")
        return
    
    result = decompiler.decompileFunction(func, 60, ConsoleTaskMonitor())
    if result.decompileCompleted():
        with open(output_file, 'w') as f:
            f.write(result.getDecompiledFunction().getC())
        print(f"Decompilation written to {output_file}")
    else:
        print(f"Decompilation failed: {result.getErrorMessage()}")
    
    decompiler.dispose()

if __name__ == "__main__":
    # Export key functions
    export_function_decompilation("0041028e", "dpdu_init_function.c")
    export_function_decompilation("00401000", "entry_point.c")  # Main entry
```

## Usage Instructions

1. Open VCIMngr.exe in Ghidra
2. Run Auto Analysis (Analysis → Auto Analyze)
3. Open Script Manager (Window → Script Manager)
4. Create new Python scripts from above
5. Run scripts to extract analysis data
6. Export results to `/src/ghidra-scripts/output/`

## Key Addresses to Investigate

| Address | Description |
|---------|-------------|
| 0x41028e | Function referencing "SOFTWARE\\D-PDU API" |
| 0x461958 | String: "SOFTWARE\\D-PDU API" |
| 0x461994 | String: "MVCI_PDU_API_ROOT" |
| 0x4607dc | String: "VAS6154A" |
| 0x462bd4 | String: "VNCI_REMOTE_DIAGNOSTIC_Mutex" |
| 0x461174 | String: "/network_adapter.bin" |

## Ghidra Project Settings

- **Language**: x86:LE:32:default (Windows PE)
- **Compiler**: Visual Studio 2019/2022 (MSVC)
- **Analysis**: Default + C++ Class Recovery + Exception Handling
- **PDB**: Load VCIMngr.pdb if available (GUID: 4ae042ca-5e71-420f-812d-c50eb56e8298)
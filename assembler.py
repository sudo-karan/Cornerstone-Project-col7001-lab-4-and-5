import sys
import struct


OPCODES = {
    "PUSH": 0x01, "POP": 0x02, "DUP": 0x03, "HALT": 0xFF,
    "ADD": 0x10, "SUB": 0x11, "MUL": 0x12, "DIV": 0x13, "CMP": 0x14,
    "JMP": 0x20, "JZ": 0x21, "JNZ": 0x22,
    "STORE": 0x30, "LOAD": 0x31, "CALL": 0x40, "RET": 0x41
}
def assemble(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Pass 1: Calculate label addresses
    labels = {}
    addr = 0
    for line in lines:
        parts = line.split(';')[0].split()
        if not parts: continue
        
        # Check if it's a label definition
        if parts[0].endswith(':'):
            label_name = parts[0][:-1]
            labels[label_name] = addr
            continue

        instr = parts[0].upper()
        if instr in OPCODES:
            addr += 1 # Opcode takes 1 byte
            if len(parts) > 1: 
                addr += 4 # Argument takes 4 bytes

    # Pass 2: Generate bytecode
    bytecode = bytearray()
    for line in lines:
        parts = line.split(';')[0].split() # Remove comments [cite: 128]
        if not parts: continue
        
        # Skip label definitions during generation
        if parts[0].endswith(':'):
            continue
        
        instr = parts[0].upper()
        if instr in OPCODES:
            bytecode.append(OPCODES[instr])
            if len(parts) > 1: # If instruction has an argument (like PUSH 5)
                arg = parts[1]
                if arg in labels:
                    val = labels[arg]
                else:
                    val = int(arg)
                # Pack as 32-bit little-endian integer [cite: 21]
                bytecode.extend(struct.pack("<i", val))
        
    with open(output_file, 'wb') as f:
        f.write(bytecode)

if __name__ == "__main__":
    assemble(sys.argv[1], sys.argv[2])
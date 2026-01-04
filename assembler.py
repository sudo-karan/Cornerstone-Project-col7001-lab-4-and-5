import sys
import struct

OPCODES = {
    "PUSH": 0x01, "ADD": 0x10, "HALT": 0xFF,
    "STORE": 0x30, "LOAD": 0x31, "CALL": 0x40, "RET": 0x41
}

OPCODES = {
    "PUSH": 0x01, "POP": 0x02, "DUP": 0x03, "HALT": 0xFF,
    "ADD": 0x10, "SUB": 0x11, "MUL": 0x12, "DIV": 0x13, "CMP": 0x14,
    "JMP": 0x20, "JZ": 0x21, "JNZ": 0x22,
    "STORE": 0x30, "LOAD": 0x31, "CALL": 0x40, "RET": 0x41
}
def assemble(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    bytecode = bytearray()
    for line in lines:
        parts = line.split(';')[0].split() # Remove comments [cite: 128]
        if not parts: continue
        
        instr = parts[0].upper()
        if instr in OPCODES:
            bytecode.append(OPCODES[instr])
            if len(parts) > 1: # If instruction has an argument (like PUSH 5)
                val = int(parts[1])
                # Pack as 32-bit little-endian integer [cite: 21]
                bytecode.extend(struct.pack("<i", val))
        
    with open(output_file, 'wb') as f:
        f.write(bytecode)

if __name__ == "__main__":
    assemble(sys.argv[1], sys.argv[2])
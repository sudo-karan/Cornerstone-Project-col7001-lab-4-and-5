import subprocess
import time
import os

ASM_FILE = "benchmark/loop.asm"
BIN_FILE = "benchmark/loop.bin"
ITERATIONS = 10_000_000
# Instructions per loop iteration: PUSH (1), SUB (1), DUP (1), JNZ (1) = 4 instructions
# Plus setup overhead (PUSH 10M)
INSTRUCTIONS_PER_LOOP = 4 

def run_benchmark():
    print(f"Assembling {ASM_FILE}...")
    subprocess.check_call(["python3", "assembler.py", ASM_FILE, BIN_FILE])
    
    print(f"Running benchmark ({ITERATIONS} iterations)...")
    start_time = time.time()
    
    subprocess.check_call(["./vm", BIN_FILE], stdout=subprocess.DEVNULL)
    
    end_time = time.time()
    duration = end_time - start_time
    
    total_instructions = ITERATIONS * INSTRUCTIONS_PER_LOOP
    ips = total_instructions / duration
    
    results = [
        "-" * 50,
        f"Time Taken: {duration:.4f} seconds",
        f"Total Instructions: ~{total_instructions:,}",
        f"Speed: {ips:,.0f} Instructions/sec",
        "-" * 50
    ]
    
    for line in results:
        print(line)
        
    with open("benchmark_results.txt", "w") as f:
        f.write("\n".join(results))
    
    if os.path.exists(BIN_FILE):
        os.remove(BIN_FILE)

if __name__ == "__main__":
    try:
        with open("benchmark_results.txt", "w") as f:
            f.write("Status: Starting benchmark...\n")
            
        run_benchmark()
    except Exception as e:
        import traceback
        with open("benchmark_results.txt", "a") as f:
            f.write(f"\nFATAL ERROR:\n{str(e)}\n\n")
            traceback.print_exc(file=f)

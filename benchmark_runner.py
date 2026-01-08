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
    
    # --- Run Interpreter ---
    print(f"Running Interpreter ({ITERATIONS} iterations)...")
    start_time_int = time.time()
    subprocess.check_call(["./vm", BIN_FILE], stdout=subprocess.DEVNULL)
    end_time_int = time.time()
    duration_int = end_time_int - start_time_int
    
    # --- Run JIT ---
    print(f"Running JIT ({ITERATIONS} iterations)...")
    start_time_jit = time.time()
    subprocess.check_call(["./vm", BIN_FILE, "--jit"], stdout=subprocess.DEVNULL)
    end_time_jit = time.time()
    duration_jit = end_time_jit - start_time_jit
    
    # --- Results ---
    total_instructions = ITERATIONS * INSTRUCTIONS_PER_LOOP
    ips_int = total_instructions / duration_int
    ips_jit = total_instructions / duration_jit
    speedup = ips_jit / ips_int
    
    results = [
        "-" * 60,
        f"{'Mode':<15} | {'Time (s)':<10} | {'IPS':<15} | {'Speedup':<10}",
        "-" * 60,
        f"{'Interpreter':<15} | {duration_int:<10.4f} | {ips_int:<15,.0f} | {'1.0x':<10}",
        f"{'JIT':<15} | {duration_jit:<10.4f} | {ips_jit:<15,.0f} | {f'{speedup:.1f}x':<10}",
        "-" * 60
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

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

    # --- GC Benchmark ---
    GC_ASM = "benchmark/gc_stress.asm"
    GC_BIN = "benchmark/gc_stress.bin"
    GC_ITER = 100_000
    
    print(f"\nAssembling {GC_ASM}...")
    subprocess.check_call(["python3", "assembler.py", GC_ASM, GC_BIN])
    
    print(f"Running GC Benchmark ({GC_ITER} allocations)...")
    start_gc = time.time()
    proc_gc = subprocess.run(["./vm", GC_BIN], capture_output=True, text=True)
    end_gc = time.time()
    duration_gc = end_gc - start_gc
    allocs_per_sec = GC_ITER / duration_gc
    
    # Parse GC Stats
    gc_runs = 0
    freed_objs = 0
    gc_time = 0.0
    max_heap = 0
    
    import re
    match = re.search(r"Runs: (\d+), Freed: (\d+), Total GC Time: ([\d.]+)s, Max Heap: (\d+) words", proc_gc.stdout)
    if match:
        gc_runs = int(match.group(1))
        freed_objs = int(match.group(2))
        gc_time = float(match.group(3))
        max_heap = int(match.group(4))
    
    gc_results = [
        "\n=== GC Performance ===",
        f"Time (Wall): {duration_gc:.4f} seconds",
        f"Throughput: {allocs_per_sec:,.0f} allocations/sec",
        f"GC Runs: {gc_runs}",
        f"Objects Freed: {freed_objs}",
        f"Total Time in GC: {gc_time:.6f} seconds",
        f"Max Heap Usage: {max_heap} words"
    ]
    for line in gc_results:
        print(line)
        results.append(line)
        
    with open("benchmark_results.txt", "w") as f:
        f.write("\n".join(results))
    
    if os.path.exists(GC_BIN):
         os.remove(GC_BIN)
    
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

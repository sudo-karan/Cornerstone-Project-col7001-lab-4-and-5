# Cornerstone Project: Bytecode VM & Garbage Collector

This repository contains the implementation for **Lab 4 (VM & JIT)** and **Lab 5 (Garbage Collector)**.

---

## Lab 5: Mark-Sweep Garbage Collector (Current)

The goal of Lab 5 is to extend the VM with dynamic memory management, specifically implementing a **Stop-the-World Mark-Sweep Garbage Collector**.

### 1. Heap Allocator (Task 1)

We have implemented a dynamic **Heap Allocator** to manage object memory.

- **Unified Memory Model:**
  - **Static Memory (0-1023):** Fixed-size global memory (Legacy/Lab 4).
  - **Heap Memory (1024+):** Dynamic region for objects.
- **Allocator Logic:** uses a "Bump Pointer" strategy. It maintains a `free_ptr` that moves forward as objects are allocated.
- **Object Header:** Every allocated object in the heap has a metadata header:
  - `Size`: Payload size.
  - `Next`: Link to the next allocated object (for sweeping).
  - `Mark`: Bit for GC reachability analysis.
- **New Opcode:**
  - `ALLOC (0x60)`: Pops `size` from stack, allocates memory, pushes `address` to stack.

### 2. Root Discovery (Task 2)

We have implemented **Root Discovery** to identify active objects.

- **Stack Scanning:** The GC iterates through the VM's data stack.
- **Conservative Identification:** Values on the stack that fall within the specific Heap Memory range are treated as pointers and marked.

### 3. Mark Phase (Task 3)

Once roots are identified, the **Mark Phase** recursively visits all reachable objects.

- **Transitive Reachability:** If Object A is marked, and A points to B, then B is also marked.
- **Cycle Handling:** The mark bit prevents infinite loops in cyclic graphs.

### 4. Sweep Phase (Task 4)

After marking, the **Sweep Phase** reclaims memory.

- **Linear Scan:** Iterates through the `allocated_list`.
- **Reclamation:** Objects with `Mark=0` are unlinked and "freed" (conceptually). Objects with `Mark=1` are kept and unmarked for the next cycle.

### 5. Memory Safety Features

The VM enforces strict bounds checking to ensure memory safety.

- **Stack Overflow/Underflow:** Pushing to a full stack or popping from an empty one triggers a runtime error.
- **Memory Access Bounds:** Accessing memory outside the valid 0-1023 range (for static memory) or 1024-5119 (for heap) triggers an error.
- **Heap Access:** Accessing heap memory beyond allocated bounds is also checked.

### 6. Testing the Allocator & GC

We have created a dedicated white-box C test harness to verify the internal state of the Heap (pointers, headers, linking) without relying on the full Assembler flow.

**How to Run Tests:**

```bash
# Compile and Run the C Unit Test
gcc -I. test/test_gc_impl.c jit.c -o test_gc && ./test_gc
```

**Memory Safety Tests (Assembler):**

```bash
# Compile VM
gcc -o vm vm.c jit.c

# Run Stack Overflow Test
python3 assembler.py test/test_stack_overflow.asm test/test_stack_overflow.bin
./vm test/test_stack_overflow.bin
# Output: Runtime Error: Stack Overflow

# Run Memory Out of Bounds Test
python3 assembler.py test/test_mem_oob.asm test/test_mem_oob.bin
./vm test/test_mem_oob.bin
# Output: Runtime Error: Heap Access Out of Bounds
```

**Expected Output (GC Tests):**
The test prints detailed logs of memory addresses and header states.

**1. Allocator Test:**

```text
Testing Allocator...
Goal: Verify that 'new_pair' correctly reserves space in the heap...
[Alloc] Allocating Pair at Heap Index 0...
[Alloc] Success. VM Address: 1027...
Allocator Test Passed.
```

**2. Root Discovery (Basic Reachability):**

```text
=== Test: Basic Reachability ===

  [GC] Triggering Garbage Collection...
  [GC] Finished.
  Result: 1 objects remaining.
```

**3. Advanced GC Tests (Transitive, Cycles, Deep Graph):**

```text
=== Test: Transitive Reachability ===
  Result: 2 objects remaining.

=== Test: Cyclic References ===
  Result: 2 objects remaining.

=== Test: Deep Object Graph ===
  Result: 501 objects remaining.
```

---

## Lab 4: Virtual Machine & Assembler (Completed)

The previous phase focused on building the core VM architecture.

### Features

- **Dual-Stack Architecture:** Separate Data and Return stacks.
- **JIT Compilation:** x86_64 JIT compiler (`--jit`) for performance.
- **Assembler:** Two-pass assembler (Python) with label support.
- **ISA:** 32-bit instruction set (Arithmetic, Control Flow, I/O).

### Build & Run

```bash
# Compile VM
gcc -o vm vm.c jit.c

# Run Assembly
python3 assembler.py test/test_factorial.asm test/test_factorial.bin
./vm test/test_factorial.bin
```

---

## Project Structure

| File                  | Description                                                             |
| :-------------------- | :---------------------------------------------------------------------- |
| `vm.c`                | **VM Core**: Updated with Heap (`vm->heap`) and `ALLOC` implementation. |
| `opcodes.h`           | ISA Definitions (added `ALLOC=0x60`).                                   |
| `test/test_gc_impl.c` | **Lab 5 Test Harness**: White-box testing for GC internals.             |
| `test_runner.py`      | Automated test suite (Runs both Assembly and C Unit tests).             |

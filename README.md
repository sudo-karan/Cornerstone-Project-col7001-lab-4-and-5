# Cornerstone Project: Bytecode VM & Garbage Collector

This repository contains the complete implementation for **Lab 4 (VM & JIT)** and **Lab 5 (Garbage Collector)**. it implements a robust, stack-based **Bytecode Virtual Machine (VM)** in C and a two-pass **Assembler** in Python, extended with a dynamic **Mark-Sweep Garbage Collector**.

---

## 1. Project Structure

| File/Folder           | Description                                                                                                                    |
| :-------------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| `vm.c`                | **Core VM Engine**. Written in C. Handles bytecode loading, stack operations, **JIT integration**, and **Garbage Collection**. |
| `jit.c` / `jit.h`     | **JIT Compiler**. Implementation of x86_64 machine code generation.                                                            |
| `Makefile`            | **Build Script**. Use `make` to compile the `vm` executable.                                                                   |
| `assembler.py`        | **Assembler**. Two-pass Python compiler (Source -> Binary Bytecode).                                                           |
| `opcodes.h`           | **ISA Definitions**. Header defining hex opcodes (e.g., `ALLOC=0x60`).                                                         |
| `test_runner.py`      | **Test Suite**. Automates Assembly functional tests and C-based GC unit tests.                                                 |
| `benchmark_runner.py` | **Performance Tool**. Benchmarks MIPS and GC throughput.                                                                       |
| `test/`               | **Test Cases**. Contains `.asm` feature tests and `test_gc_impl.c` (GC Unit Test).                                             |
| `benchmark/`          | **Benchmarks**. Contains `loop.asm` and `gc_stress.asm`.                                                                       |
| `Lab 4/` & `Lab 5/`   | **Documentation**. Course instructions and technical reports.                                                                  |

---

## 2. Lab 4: Virtual Machine & Assembler

### Overview

The system executes a custom 32-bit instruction set capable of complex arithmetic, control flow branching, function calls, and global memory management.

**Key Features:**

- **Dual-Stack Architecture:** Separate stacks for data (calculations) and return addresses (function calls) to prevent corruption.
- **Just-In-Time (JIT) Compilation:** Implemented x86_64 JIT compiler (using `mmap`) for significant performance speedup (up to 30x).
- **Standard Library:** Includes `PRINT` and `INPUT` instructions.
- **Robust Error Handling:** Runtime bounds checking for stack overflow/underflow, memory access, and division by zero.

### Instruction Set (ISA)

#### Data & Stack

| Opcode | Mnemonic     | Description            |
| :----- | :----------- | :--------------------- |
| `0x01` | **PUSH** val | Push integer constant. |
| `0x02` | **POP**      | Discard top element.   |
| `0x03` | **DUP**      | Duplicate top element. |

#### Arithmetic

| Opcode | Mnemonic | Description             |
| :----- | :------- | :---------------------- |
| `0x10` | **ADD**  | `a + b`                 |
| `0x11` | **SUB**  | `a - b`                 |
| `0x12` | **MUL**  | `a * b`                 |
| `0x13` | **DIV**  | `a / b`                 |
| `0x14` | **CMP**  | `1` if `a < b` else `0` |

#### Control Flow

| Opcode | Mnemonic     | Description         |
| :----- | :----------- | :------------------ |
| `0x20` | **JMP** addr | Unconditional jump. |
| `0x21` | **JZ** addr  | Jump if 0.          |
| `0x22` | **JNZ** addr | Jump if not 0.      |

#### Memory & Functions

| Opcode | Mnemonic      | Description                           |
| :----- | :------------ | :------------------------------------ |
| `0x30` | **STORE** idx | Pop value and store at `Memory[idx]`. |
| `0x31` | **LOAD** idx  | Load value from `Memory[idx]`.        |
| `0x40` | **CALL** addr | Push `PC+1` to Return Stack, jump.    |
| `0x41` | **RET**       | Pop address from Return Stack, jump.  |

#### Standard Library

| Opcode | Mnemonic  | Description              |
| :----- | :-------- | :----------------------- |
| `0x50` | **PRINT** | Pop and print to stdout. |
| `0x51` | **INPUT** | Read integer from stdin. |

---

## 3. Lab 5: Mark-Sweep Garbage Collector

The VM has been extended with dynamic memory management, implementing a **Stop-the-World Mark-Sweep Garbage Collector**.

### 1. Heap Allocator

- **Unified Memory Model:**
  - **Static Memory (0-1023):** Legacy fixed-size memory.
  - **Heap Memory (1024+):** Dynamic object region.
- **Logic:** Uses a "Bump Pointer" (`free_ptr`) strategy for fast allocation.
- **New Opcode:** `ALLOC (0x60)` - Allocates memory of given `size` and pushes the address.

### 2. Root Discovery

- **Stack Scanning:** The GC iterates through the VM's data stack.
- **Conservative Identification:** Values on the stack that fall within the specific Heap Memory range are treated as pointers and marked.

### 3. Mark Phase

- **Recursive Tracing:** Performs a Depth-First Search (DFS) from roots.
- **Cycle Handling:** Uses mark bits in the Object Header to handle cyclic references gracefully (e.g., A -> B -> A).

### 4. Sweep Phase

- **Reclamation:** Iterates through the `allocated_list` of objects.
- **Freeing:** Unmarked objects are unlinked (freed). Marked objects have their bit reset for the next cycle.

### 5. Memory Safety & Stress Handling

- **Safety:** Strict bounds checking on all Heap accesses.
- **Stress Handling:** `ALLOC` automatically triggers `vm_gc` on heap exhaustion. If space is recovered, allocation retries seamlessly.

---

## 4. Build, Test, & Benchmark

### Build the VM

```bash
make clean && make
```

### Run Tests

**Automated Suite (Assembly + GC Unit Tests):**

```bash
python3 test_runner.py
```

_Expected Output: "All tests passed!" (including C unit tests and Interpreter/JIT tests)._

**Manual GC Unit Test:**

```bash
gcc -I. test/test_gc_impl.c jit.c -o test_gc && ./test_gc
```

### Run Performance Benchmark

Runs a stress test (`benchmark/gc_stress.asm`) creating 100,000 objects.

```bash
python3 benchmark_runner.py
```

**Latest Performance Metrics (Lab 5):**

- **Throughput**: ~12.1 Million Allocations / Second
- **Execution Time**: ~0.0083 seconds
- **GC Efficiency**:
  - **GC Runs**: 4
  - **Objects Freed**: ~52,000
  - **Total Time in GC**: 0.000162s (Extremely low overhead)
  - **Max Heap Usage**: 65,535 words (Full utilization)

---
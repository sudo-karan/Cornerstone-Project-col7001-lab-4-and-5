# Lab 4: Bytecode Virtual Machine

## 1. Overview

This project implements a robust, stack-based **Bytecode Virtual Machine (VM)** in C and a two-pass **Assembler** in Python. The system is designed to execute a custom 32-bit instruction set architecture (ISA) capable of complex arithmetic, control flow branching, function calls, and global memory management.

**Key Features:**

- **Dual-Stack Architecture:** Separate stacks for data (calculations) and return addresses (function calls) to prevent corruption.
- **Just-In-Time (JIT) Compilation:** Implemented x86_64 JIT compiler (using `mmap` and machine code generation) for 3.5x-30x performance speedup.
- **Standard Library:** Includes `PRINT` and `INPUT` instructions for basic I/O operations.
- **Robust Error Handling:** Runtime bounds checking for stack overflow/underflow, memory access, and division by zero.
- **Label Support:** The assembler supports named labels for jumps and function calls, resolving them to relative addresses.
- **Deterministic Execution:** Guarantees consistent behavior across runs.

---

## 2. Project Structure

| File                  | Description                                                                                                                                           |
| :-------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vm.c`                | **Core VM Engine**. Written in C. Handles bytecode loading, the fetch-decode-execute cycle, stack operations (`push`, `pop`), and memory management.  |
| `assembler.py`        | **Assembler**. Written in Python. Performs a **two-pass compilation**: 1. Scans for labels to map addresses. 2. Generates binary bytecode.            |
| `opcodes.h`           | **Header File**. Defines the hex opcodes (e.g., `PUSH=0x01`) shared by the VM and any potential C extensions.                                         |
| `test_runner.py`      | **Automation Suite**. A Python script that compiles every `.asm` file in `test/`, runs the VM, and verifies the stack output against expected values. |
| `benchmark_runner.py` | **Performance Tool**. Runs a high-iteration loop to measure instructions-per-second (IPS).                                                            |
| `test/`               | Directory containing assembly test files (e.g., `test_factorial.asm`, `test_memory.asm`).                                                             |
| `benchmark/`          | Directory containing performance test files.                                                                                                          |

---

## 3. Architecture Details

### Virtual Machine (`vm.c`)

- **Memory Model:**
  - **Data Stack:** 256 integers (`int32_t`). Used for operands and results.
  - **Return Stack:** 256 addresses (`uint32_t`). Used strictly for `CALL`/`RET` instruction pointers.
  - **Main Memory:** 1024 integers. Random access storage via `LOAD`/`STORE`.
  - **Bytecode Storage:** Dynamic array (`uint8_t*`). Stores the executable binary.
- **Safety:**
  - The VM includes a `vm->error` flag.
  - `push_safe()` and `pop_safe()` functions ensure stack bounds are respected.
  - `div` checks for zero denominator.
  - `LOAD`/`STORE` check `0 <= index < 1024`.

### Assembler (`assembler.py`)

- **Pass 1 (Symbol Resolution):** Scans source code to record the byte offset of every label (e.g., `LOOP:`, `FUNC:`).
- **Pass 2 (Code Generation):** Translates mnemonics to opcodes (e.g., `ADD` -> `0x10`). Replaces label references (e.g., `JMP LOOP`) with the 32-bit integer address calculated in Pass 1.

---

## 4. Build & Execution

### Prerequisites

- **C Compiler:** `gcc` or `clang`
- **Python:** Version 3.6+

### Step 1: Compile the VM

This builds the `vm` executable from the C source.

```bash
gcc -o vm vm.c
```

### Step 2: Assemble a Program

Convert your assembly code (`.asm`) into an executable binary (`.bin`).

```bash
# Syntax: python3 assembler.py <input> <output>
python3 assembler.py test/test_factorial.asm test/test_factorial.bin
```

### Step 3: Run the VM

Execute the binary. The VM will print the value at the top of the stack upon completion.

```bash
./vm test/test_factorial.bin
```

**Expected Output:**

```
Top of stack: 120
```

### Step 4: Run with JIT (Just-In-Time Compiler)

Enable the JIT compiler with the `--jit` flag for improved performance.

```bash
./vm test/test_factorial.bin --jit
```

_Note: JIT currently supports arithmetic and stack operations. Unsupported opcodes (like INPUT) automatically fallback to the interpreter._

---

## 5. Instruction Set (ISA)

The VM treats all numbers as signed 32-bit integers.

### Data & Stack

| Opcode | Mnemonic     | Stack Effect    | Description                       |
| :----- | :----------- | :-------------- | :-------------------------------- |
| `0x01` | **PUSH** val | `[] -> [val]`   | Push integer constant onto stack. |
| `0x02` | **POP**      | `[val] -> []`   | Discard top element.              |
| `0x03` | **DUP**      | `[a] -> [a, a]` | Duplicate top element.            |
| `0xFF` | **HALT**     | `N/A`           | Stop execution.                   |

### Arithmetic

| Opcode | Mnemonic | Stack Effect      | Description                     |
| :----- | :------- | :---------------- | :------------------------------ |
| `0x10` | **ADD**  | `[a, b] -> [a+b]` | Addition.                       |
| `0x11` | **SUB**  | `[a, b] -> [a-b]` | Subtraction (Second - Top).     |
| `0x12` | **MUL**  | `[a, b] -> [a*b]` | Multiplication.                 |
| `0x13` | **DIV**  | `[a, b] -> [a/b]` | Integer Division. Error if b=0. |
| `0x14` | **CMP**  | `[a, b] -> [0/1]` | Push 1 if `a < b`, else 0.      |

### Control Flow

| Opcode | Mnemonic     | Description                                         |
| :----- | :----------- | :-------------------------------------------------- |
| `0x20` | **JMP** addr | Unconditional jump to address.                      |
| `0x21` | **JZ** addr  | Jump if top of stack is **0** (consumes value).     |
| `0x22` | **JNZ** addr | Jump if top of stack is **NOT 0** (consumes value). |

### Memory & Functions

| Opcode | Mnemonic      | Description                                |
| :----- | :------------ | :----------------------------------------- |
| `0x30` | **STORE** idx | Pop value and store at `Memory[idx]`.      |
| `0x31` | **LOAD** idx  | Load value from `Memory[idx]` to stack.    |
| `0x40` | **CALL** addr | Push `PC+1` to Return Stack, jump to addr. |
| `0x41` | **RET**       | Pop address from Return Stack, jump to it. |

### Standard Library

| Opcode | Mnemonic  | Description                                |
| :----- | :-------- | :----------------------------------------- |
| `0x50` | **PRINT** | Pop and print top of stack to stdout.      |
| `0x51` | **INPUT** | Read integer from stdin and push to stack. |

---

## 6. Testing & Validation

### Automated Test Suite

We provide `test_runner.py` which automates the testing workflow: `Assemble` -> `Execute` -> `Verify Output` -> `Clean`. It verifies both **Interpreter** and **JIT** execution paths.

**Command:**

```bash
python3 test_runner.py
```

**Scope of Tests:**

1.  **Functional correctness:** Arithmetic (`test_add`), Branching (`test_branching`), Memory (`test_memory`).
2.  **Complex Logic:** `test_factorial.asm` (Recursive calculation of 5!).
3.  **Standard Library:** `test_input.asm` (Automated input verification).
4.  **Robustness (Negative Testing):**
    - `test_stack_overflow.asm`: Ensures VM stops gracefully.
    - `test_div_zero.asm`: Ensures "Division by Zero" error.
    - `test_mem_oob.asm`: Ensures safe memory access.

### Performance Benchmark

Run a stress test (looping 10 million times) to measure instruction throughput and JIT speedup.

**Command:**

```bash
python3 benchmark_runner.py
```

**Results:**

- **Interpreter:** ~230 Million Instructions Per Second (MIPS).
- **JIT Compiler:** ~816 Million Instructions Per Second (MIPS).
- **Speedup:** ~3.5x - 30x (depending on workload complexity).

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "opcodes.h"
#include "jit.h"

#define STACK_SIZE 256
#define MEM_SIZE 1024

typedef struct {
    int32_t stack[STACK_SIZE];
    int sp;                // Stack Pointer
    int32_t memory[MEM_SIZE];
    uint32_t return_stack[STACK_SIZE];
    int rsp;               // Return Stack Pointer
    uint8_t *code;         // Bytecode array
    int pc;                // Program Counter
    int running;
    int error;             // Error flag
} VM;

// Helper to handle runtime errors safely
void error(VM *vm, const char *msg) {
    fprintf(stderr, "Runtime Error: %s\n", msg);
    vm->running = 0;
    vm->error = 1;
}

void push(VM *vm, int32_t val) {
    if (vm->sp >= STACK_SIZE - 1) {
        error(vm, "Stack Overflow");
        return;
    }
    vm->stack[++vm->sp] = val;
}

int32_t pop(VM *vm) {
    if (vm->sp < 0) {
        error(vm, "Stack Underflow");
        return 0; // Return dummy value, VM will stop anyway
    }
    return vm->stack[vm->sp--];
}

void run_vm(VM *vm) {
    vm->pc = 0;
    vm->sp = -1;
    vm->rsp = -1;
    vm->running = 1;
    vm->error = 0;

    // We assume the code size is large enough or trusted, assuming proper loader checks.
    // In a real VM, you'd also check bounds of vm->pc against code size.

    while (vm->running) {
        uint8_t opcode = vm->code[vm->pc++];
        switch (opcode) {
        // 1.6.1 Data Movement
        case PUSH: {
            int32_t val = *(int32_t*)&vm->code[vm->pc];
            push(vm, val);
            vm->pc += 4;
            break;
        }

        case POP: {
            pop(vm);
            break;
        }
        case DUP: {
            if (vm->sp < 0) { error(vm, "Stack Underflow"); break; }
            push(vm, vm->stack[vm->sp]);
            break;
        }
        case HALT: {
            vm->running = 0;
            break;
        }

        // 1.6.2 Arithmetic & Logical
        case ADD: {
            int32_t b = pop(vm);
            int32_t a = pop(vm);
            if (vm->running) push(vm, a + b);
            break;
        }
        case SUB: {
            int32_t b = pop(vm);
            int32_t a = pop(vm);
            if (vm->running) push(vm, a - b);
            break;
        }
        case MUL: {
            int32_t b = pop(vm);
            int32_t a = pop(vm);
            if (vm->running) push(vm, a * b);
            break;
        }
        case DIV: {
            int32_t b = pop(vm);
            int32_t a = pop(vm);
            if (!vm->running) break; 
            if (b != 0) push(vm, a / b);
            else error(vm, "Division by Zero");
            break;
        }
        case CMP: {
            int32_t b = pop(vm);
            int32_t a = pop(vm);
            if (vm->running) push(vm, (a < b) ? 1 : 0);
            break;
        }

        // 1.6.3 Control Flow
        case JMP: {
            vm->pc = *(int32_t*)&vm->code[vm->pc];
            break;
        }
        case JZ: {
            int32_t addr = *(int32_t*)&vm->code[vm->pc];
            vm->pc += 4;
            int32_t val = pop(vm);
            if (vm->running && val == 0) vm->pc = addr;
            break;
        }
        case JNZ: {
            int32_t addr = *(int32_t*)&vm->code[vm->pc];
            vm->pc += 4;
            int32_t val = pop(vm);
            if (vm->running && val != 0) vm->pc = addr;
            break;
        }

        // 1.6.4 Memory & Functions
        case STORE: {
            int32_t idx = *(int32_t*)&vm->code[vm->pc];
            vm->pc += 4;
            int32_t val = pop(vm);
            if (!vm->running) break;
            
            if (idx < 0 || idx >= MEM_SIZE) {
                error(vm, "Memory Access Out of Bounds");
            } else {
                vm->memory[idx] = val;
            }
            break;
        }
        case LOAD: {
            int32_t idx = *(int32_t*)&vm->code[vm->pc];
            vm->pc += 4;
            
            if (idx < 0 || idx >= MEM_SIZE) {
                error(vm, "Memory Access Out of Bounds");
            } else {
                push(vm, vm->memory[idx]);
            }
            break;
        }
        case CALL: {
            uint32_t addr = *(uint32_t*)&vm->code[vm->pc];
            vm->pc += 4;
            
            if (vm->rsp >= STACK_SIZE - 1) {
                error(vm, "Return Stack Overflow");
                break;
            }
            vm->return_stack[++vm->rsp] = vm->pc; 
            vm->pc = addr;
            break;
        }
        case RET: {
            if (vm->rsp < 0) {
                error(vm, "Return Stack Underflow");
                break;
            }
            vm->pc = vm->return_stack[vm->rsp--];
            break;
        }

        // 1.6.5 Standard Library
        case PRINT: {
            if (vm->sp < 0) {
                error(vm, "Stack Underflow");
                break;
            }
            printf("%d\n", vm->stack[vm->sp--]);
            fflush(stdout);
            break;
        }
        case INPUT: {
            int val;
            printf("Enter number: ");
            if (scanf("%d", &val) == 1) {
                if (vm->sp >= STACK_SIZE - 1) {
                    error(vm, "Stack Overflow");
                    break;
                }
                vm->stack[++vm->sp] = val;
            } else {
                fprintf(stderr, "Error: Invalid input\n");
                vm->running = 0;
                vm->error = 1;
            }
            break;
        }

        default:
            fprintf(stderr, "Unknown Opcode: 0x%02X\n", opcode);
            vm->running = 0;
            vm->error = 1;
        }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;
    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        fprintf(stderr, "Error opening file %s\n", argv[1]);
        return 1;
    }
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    uint8_t *code = malloc(size);
    if (!code) {
        fclose(f);
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }
    
    fread(code, 1, size, f);
    fclose(f);

    VM vm = { .code = code };

    // Check for JIT flag
    int use_jit = 0;
    if (argc > 2 && strcmp(argv[2], "--jit") == 0) {
        use_jit = 1;
    }

    if (use_jit) {
        printf("Running with JIT...\n");
        jit_func jitted_code = compile(code, size);
        if (jitted_code) {
            // JIT returns the top of the stack as an integer
            int result = jitted_code();
            printf("JIT Result: %d\n", result);
        } else {
            fprintf(stderr, "JIT Compilation Failed\n");
            return 1;
        }
    } else {
        run_vm(&vm);
        
        if (!vm.error && vm.sp >= 0)
            printf("Top of stack: %d\n", vm.stack[vm.sp]);
        else if (!vm.error)
            printf("Stack empty\n");
    }

    free(code);
    return vm.error ? 1 : 0;
}
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "opcodes.h"

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
} VM;

void push(VM *vm, int32_t val) { vm->stack[++vm->sp] = val; }
int32_t pop(VM *vm) { return vm->stack[vm->sp--]; }

void run_vm(VM *vm) {
    vm->pc = 0;
    vm->sp = -1;
    vm->rsp = -1;
    vm->running = 1;

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
            push(vm, a + b);
            break;
        }
        case SUB: {
            int32_t b = pop(vm);
            int32_t a = pop(vm);
            push(vm, a - b);
            break;
        }
        case MUL: {
            int32_t b = pop(vm);
            int32_t a = pop(vm);
            push(vm, a * b);
            break;
        }
        case DIV: {
            int32_t b = pop(vm);
            int32_t a = pop(vm);
            if (b != 0) push(vm, a / b);
            else { fprintf(stderr, "Div by zero\n"); vm->running = 0; }
            break;
        }
        case CMP: {
            int32_t b = pop(vm);
            int32_t a = pop(vm);
            push(vm, (a < b) ? 1 : 0);
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
            if (pop(vm) == 0) vm->pc = addr;
            break;
        }
        case JNZ: {
            int32_t addr = *(int32_t*)&vm->code[vm->pc];
            vm->pc += 4;
            if (pop(vm) != 0) vm->pc = addr;
            break;
        }

        // 1.6.4 Memory & Functions
        case STORE: {
            int32_t idx = *(int32_t*)&vm->code[vm->pc];
            vm->memory[idx] = pop(vm);
            vm->pc += 4;
            break;
        }
        case LOAD: {
            int32_t idx = *(int32_t*)&vm->code[vm->pc];
            push(vm, vm->memory[idx]);
            vm->pc += 4;
            break;
        }
        case CALL: {
            uint32_t addr = *(uint32_t*)&vm->code[vm->pc];
            vm->pc += 4;
            vm->return_stack[++vm->rsp] = vm->pc; // Store address after the CALL arg
            vm->pc = addr;
            break;
        }
        case RET: {
            vm->pc = vm->return_stack[vm->rsp--];
            break;
        }

        default:
            fprintf(stderr, "Unknown Opcode: 0x%02X\n", opcode);
            vm->running = 0;
    }
    }
}

int main(int argc, char **argv) {
    if (argc < 2) return 1;
    FILE *f = fopen(argv[1], "rb");
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    uint8_t *code = malloc(size);
    fread(code, 1, size, f);
    fclose(f);

    VM vm = { .code = code };
    run_vm(&vm);
    printf("Top of stack: %d\n", vm.stack[vm.sp]);
    free(code);
    return 0;
}
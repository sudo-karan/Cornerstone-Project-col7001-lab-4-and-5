#define TESTING
#include "../vm.c"
#include <assert.h>

/**
 * Type Alias: Obj
 * Represents an object handle in the VM. In our implementation, objects are
 * addressed by their index in the global address space.
 * 
 * We use intptr_t to ensure compatibility with pointer-width operations if needed,
 * though the VM uses 32-bit integer addressing.
 */
typedef intptr_t Obj; 

#define VAL_OBJ(o) ((int32_t)(o))

/*
 * Global VM Instance for Test Harness
 * 
 * This global instance allows helper functions like `new_pair` 
 * to interact with the VM state (Heap, Allocator) without explicit 
 * parameter passing, simplifying the test case syntax.
 */
VM *current_vm;

/**
 * new_pair(a, b)
 * 
 * Allocates a new Pair object in the VM Heap with two fields.
 * This helper essentially mimics the `ALLOC` opcode but is exposed directly
 * for white-box testing of the Heap structure.
 * 
 * Memory Layout for a Pair (3 Words Header + 2 Words Payload):
 * [0] Size
 * [1] Next (Free List Link)
 * [2] Marked (GC Flag)
 * [3] Field A
 * [4] Field B
 *
 * @param a First field value
 * @param b Second field value
 * @return Obj handle (VM Address) to the payload
 */
Obj new_pair(Obj a, Obj b) {
    int size = 2; // Pair object contains exactly 2 fields
    int needed = size + 3; // Overhead: 3 words for Header
    
    // Bounds Check: Ensure allocation fits in the fixed-size Heap
    if (current_vm->free_ptr + needed > HEAP_SIZE) {
        printf("  [Alloc] Error: Heap Overflow. Requested %d words, Free Index at %d\n", needed, current_vm->free_ptr);
        return 0; // Allocation failure
    }

    int32_t addr = current_vm->free_ptr;
    printf("  [Alloc] Allocating Pair at Heap Index %d (Payload Size: %d, Next Ptr: %d)\n", 
           addr, size, current_vm->allocated_list);

    // Initialize Header
    current_vm->heap[addr] = size;                     // Header[0]: Size
    current_vm->heap[addr + 1] = current_vm->allocated_list; // Header[1]: Next Object Ptr (for Sweep)
    current_vm->heap[addr + 2] = 0;                    // Header[2]: Mark Bit (Reserved for GC)
    
    // Update Allocator State
    current_vm->allocated_list = addr;                 // Prepend to allocated list
    current_vm->free_ptr += needed;                    // Advance bump pointer
    
    // Initialize Payload
    int32_t payload_addr = addr + 3;
    current_vm->heap[payload_addr] = (int32_t)a;       // Payload[0]: Field A
    current_vm->heap[payload_addr + 1] = (int32_t)b;   // Payload[1]: Field B
    
    // Calculate Virtual Address (Memory + Heap Offset)
    int32_t vm_addr = MEM_SIZE + payload_addr;
    printf("  [Alloc] Success. VM Address: %d. Fields: [%d, %d]\n", vm_addr, (int)a, (int)b);

    return (Obj)vm_addr;
}

/**
 * test_allocator()
 * 
 * Verifies the correctness of the Heap Allocator.
 * 
 * Scenarios Tested:
 * 1. Single Object Allocation: Verifies address computation and header initialization.
 * 2. Linked List Maintenance: Verifies that multiple objects are correctly linked 
 *    via the `next` pointer in their headers (crucial for the Sweep phase).
 */
void test_allocator() {
    printf("Testing Allocator...\n");
    printf("Goal: Verify that 'new_pair' correctly reserves space in the heap and links objects.\n");
    
    VM vm = {0};
    vm.free_ptr = 0;
    vm.allocated_list = -1; // -1 denotes end of list
    current_vm = &vm;
    
    printf("\n1. Allocating First Object (o1)...\n");
    Obj o1 = new_pair(0, 0);
    assert(o1 == MEM_SIZE + 0 + 3); // First object starts at heap[0] + 3 words header
    
    // Verify Header of o1
    int32_t r_addr = (int32_t)o1 - MEM_SIZE;
    printf("   -> Verified Object 1 Address: %ld\n", (long)o1);
    printf("   -> Checking Header at heap[%d]... Size should be 2.\n", r_addr - 3);
    assert(vm.heap[r_addr - 3] == 2); // Size
    assert(vm.heap[r_addr - 2] == -1); // Next should be -1 (end of list)
    
    printf("\n2. Allocating Second Object (o2) pointing to o1...\n");
    Obj o2 = new_pair(o1, 0);
    
    // Verify Linkage
    int32_t r_addr2 = (int32_t)o2 - MEM_SIZE;
    printf("   -> Verified Object 2 Address: %ld\n", (long)o2);
    printf("   -> Checking List Linkage: o2->next should point to o1's header (%d).\n", r_addr - 3);
    assert(vm.heap[r_addr2 - 2] == r_addr - 3); // o2->next points to o1
    
    printf("\nAllocator Test Passed: Objects created and linked correctly in heap.\n");
}

int main() {
    test_allocator();
    return 0;
}

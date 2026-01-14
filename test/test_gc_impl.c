#define TESTING
#include "../vm.c"
#include <assert.h>
#include <time.h>

/* --- Types and Gloabls --- */
typedef intptr_t Obj; 
#define VAL_OBJ(o) ((int32_t)(o))

VM *current_vm;

/* --- Helpers --- */

// Wrapper for vm_gc
void gc(VM *vm) {
    printf("\n  [GC] Triggering Garbage Collection...\n");
    vm_gc(vm);
    printf("  [GC] Finished.\n");
}

Obj new_pair(Obj a, Obj b) {
    int size = 2; 
    int needed = size + 3; 
    
    if (current_vm->free_ptr + needed > HEAP_SIZE) {
        printf("  [Alloc] Heap Overflow! Need %d\n", needed);
        return 0; // Allocation failure
    }

    int32_t addr = current_vm->free_ptr;
    current_vm->heap[addr] = size;                     
    current_vm->heap[addr + 1] = current_vm->allocated_list; 
    current_vm->heap[addr + 2] = 0;                    
    
    current_vm->allocated_list = addr;                 
    current_vm->free_ptr += needed;                    
    
    int32_t payload_addr = addr + 3;
    current_vm->heap[payload_addr] = (int32_t)a;       
    current_vm->heap[payload_addr + 1] = (int32_t)b;   
    
    int32_t vm_addr = MEM_SIZE + payload_addr;
    return (Obj)vm_addr;
}

// Helper: Count objects in allocated_list
int count_allocated_objects(VM *vm) {
    int count = 0;
    int32_t curr = vm->allocated_list;
    while (curr != -1) {
        count++;
        curr = vm->heap[curr + 1];
    }
    return count;
}

void reset_vm(VM *vm) {
    memset(vm, 0, sizeof(VM));
    vm->free_ptr = 0;
    vm->allocated_list = -1;
    vm->sp = -1;
    vm->rsp = -1;
    vm->running = 1;
    current_vm = vm;
}

/* --- Tests --- */

// Basic Reachability
void test_gc_basic_reachability() {
    printf("\n=== Test: Basic Reachability ===\n");
    VM vm; reset_vm(&vm);
    
    Obj a = new_pair(0, 0);
    push(&vm, VAL_OBJ(a)); // Root
    
    gc(&vm);
    
    // Outcome: Object a survives. Count should be 1.
    int count = count_allocated_objects(&vm);
    printf("  Result: %d objects remaining.\n", count);
    assert(count == 1);
}

// Unreachable Object Collection
void test_gc_unreachable_object_collection() {
    printf("\n=== Test: Unreachable Object Collection ===\n");
    VM vm; reset_vm(&vm);
    
    new_pair(0, 0); // Allocate but don't push (unreachable)
    
    gc(&vm);
    
    // Outcome: Object freed. Count should be 0.
    int count = count_allocated_objects(&vm);
    printf("  Result: %d objects remaining.\n", count);
    assert(count == 0);
}

// Transitive Reachability
void test_gc_transitive_reachability() {
    printf("\n=== Test: Transitive Reachability ===\n");
    VM vm; reset_vm(&vm);
    
    Obj a = new_pair(0, 0);
    Obj b = new_pair(a, 0); // b -> a
    
    push(&vm, VAL_OBJ(b)); // Push b
    
    gc(&vm);
    
    // Outcome: Both survive (b is root, a is reachable from b).
    // Note: This test verifies transitive reachability.
    // It is expected to fail or pass partially until recursive marking is fully implemented.
    
    int count = count_allocated_objects(&vm);
    printf("  Result: %d objects remaining.\n", count);
    assert(count == 2);
}

// Cyclic References
void test_gc_cyclic_references() {
    printf("\n=== Test: Cyclic References ===\n");
    VM vm; reset_vm(&vm);
    
    Obj a = new_pair(0, 0);
    Obj b = new_pair(a, 0); // b -> a
    
    // Manually set a->right = b (Cycle)
    // a is at address 'a'. Payload is at a. Fields at a, a+4 (if pointer arithmetic)
    // VM addresses are indices. Payload indices.
    int32_t a_idx = (int32_t)a - MEM_SIZE; 
    vm.heap[a_idx + 1] = (int32_t)b; // a[1] = b
    
    push(&vm, VAL_OBJ(a));
    
    gc(&vm);
    
    int count = count_allocated_objects(&vm);
    printf("  Result: %d objects remaining.\n", count);
    assert(count == 2);
}

// Deep Object Graph
void test_gc_deep_object_graph() {
    printf("\n=== Test: Deep Object Graph ===\n");
    VM vm; reset_vm(&vm);
    
    Obj root = new_pair(0, 0);
    Obj cur = root;
    
    for (int i = 0; i < 500; i++) { // 10000 might overflow heap in this small VM
        Obj next = new_pair(0, 0);
        int32_t cur_idx = (int32_t)cur - MEM_SIZE;
        vm.heap[cur_idx + 1] = (int32_t)next; // cur->right = next
        cur = next;
    }
    
    push(&vm, VAL_OBJ(root));
    gc(&vm);
    
    int count = count_allocated_objects(&vm);
    printf("  Result: %d objects remaining.\n", count);
    assert(count == 501); 
}

// Stress Allocation
void test_gc_stress_allocation() {
    printf("\n=== Test: Stress Allocation ===\n");
    VM vm; reset_vm(&vm);
    
    // Allocate many objects, dropping them. GC should reclaim.
    // Heap is 4096. Pair needs 5 words (20 bytes). 4096/5 ~ 800 objects.
    // We try allocating 2000.
    
    int failures = 0;
    for (int i = 0; i < 2000; i++) {
        Obj o = new_pair(0, 0);
        if (o == 0) {
            // If alloc fails, try GC
            gc(&vm);
            o = new_pair(0, 0);
            if (o == 0) failures++;
        }
        // Don't push, so it becomes garbage immediately
    }
    
    gc(&vm);
    int count = count_allocated_objects(&vm);
    printf("  Result: %d objects remaining (Should be 0).\n", count);
    assert(count == 0);
    assert(failures == 0);
}


int main() {
    test_gc_basic_reachability();
    test_gc_unreachable_object_collection();
    // test_gc_transitive_reachability(); // Task 3
    // test_gc_cyclic_references(); // Task 3
    // test_gc_deep_object_graph(); // Task 3
    // test_gc_stress_allocation(); // Task 4 (Alloc reuse logic needed for this to pass fully)
    
    printf("\nAll Active Tests Passed.\n");
    return 0;
}

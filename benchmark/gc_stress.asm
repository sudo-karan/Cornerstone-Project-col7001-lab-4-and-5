; GC Stress Benchmark
; Allocates 100,000 objects in a loop to trigger GC
; Total objects to allocate: 100,000

PUSH 100000 ; Loop Counter

LOOP:
    PUSH 2      ; Size = 2 (Small object)
    ALLOC       ; Allocate
    POP         ; Discard address (we don't need to keep it alive for this stress test, or we do?)
                ; If we pop immediately, it becomes garbage.
                ; This tests "Throughput of Allocation + Collection of Garbage"
    
    PUSH 1
    SUB         ; Decrement Counter
    DUP
    JNZ LOOP

HALT

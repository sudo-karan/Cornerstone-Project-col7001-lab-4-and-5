; Test Factorial Calculation (5!)
; Expected Result: 120

PUSH 5      
CALL FACT
HALT

FACT:
    ; Stack: [n]
    DUP         ; [n, n]
    PUSH 2      ; [n, n, 2]
    CMP         ; [n, 1 if n<2 else 0]
    JNZ RET_1   ; If n < 2, jump to base case

    ; Recursive Steps
    DUP         ; [n, n]
    PUSH 1
    SUB         ; [n, n-1]
    CALL FACT   ; [n, FACT(n-1)]
    MUL         ; [n * FACT(n-1)]
    RET

RET_1:
    ; Base Case: Return 1
    POP         ; [n] -> [] (Remove n)
    PUSH 1      ; [1]
    RET

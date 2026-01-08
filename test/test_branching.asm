; Test Branching Instructions (CMP, JZ, JMP)
; Expected Result: 1

; 1. Test CMP (Less Than)
PUSH 10
PUSH 20
CMP         ; 10 < 20 -> Pushes 1
POP         ; Clear (we verified it works if we don't crash, but let's use it for branching)

; 2. Test CMP + JZ
PUSH 20
PUSH 10
CMP         ; 20 < 10 -> Pushes 0
JZ IS_ZERO  ; Should jump because top is 0
PUSH 999    ; Should skip this
HALT

IS_ZERO:
    ; 3. Test JMP
    PUSH 5
    JMP FINISH
    PUSH 888    ; Should skip this

FINISH:
    PUSH 4
    SUB         ; 5 - 4 = 1
    HALT

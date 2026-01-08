; Test Memory Operations (LOAD/STORE)
; Expected Result: 123

PUSH 123
STORE 0     ; Store 123 at address 0

PUSH 456
STORE 1     ; Store 456 at address 1

LOAD 0      ; Load from address 0, should be 123
HALT

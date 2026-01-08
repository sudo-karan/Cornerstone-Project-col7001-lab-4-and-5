; Benchmark: 10 Million Iterations Loop
; Used to measure VM instructions per second (IPS)

PUSH 10000000   ; Counter = 10,000,000

LOOP:
    PUSH 1
    SUB         ; Counter - 1
    DUP
    JNZ LOOP    ; If Counter != 0, jump back

HALT

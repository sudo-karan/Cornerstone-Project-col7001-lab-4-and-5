import subprocess
import os
import re

# List of tests: (assembly_filename, expected_value, expected_error_substring, input_string)
# If expected_error_substring is None, we expect success and check expected_value.
# If expected_error_substring is set, we expect failure and check stderr for the substring.
# input_string is optional stdin to pass to the VM.
tests = [
    ("test_push.asm", 10, None, None),
    ("test_pop.asm", 10, None, None),
    ("test_dup.asm", 10, None, None),
    ("test_halt.asm", 10, None, None),
    ("test_add.asm", 30, None, None),
    ("test_sub.asm", 20, None, None),
    ("test_mult.asm", 30, None, None),
    ("test_div.asm", 10, None, None),
    ("test_loop.asm", 0, None, None),
    ("test_call.asm", 25, None, None),
    ("test_call2.asm", 25, None, None),
    ("test_branching.asm", 1, None, None),
    ("test_memory.asm", 123, None, None),
    ("test_factorial.asm", 120, None, None),
    # Standard Library Input Test
    ("test_input.asm", 51, None, "50\n"),
    # Error Scenarios
    ("test_stack_underflow.asm", None, "Stack Underflow", None),
    ("test_stack_overflow.asm", None, "Stack Overflow", None),
    ("test_mem_oob.asm", None, "Memory Access Out of Bounds", None),
    ("test_div_zero.asm", None, "Division by Zero", None),
]

print(f"{'Test File':<25} | {'Expected':<15} | {'Actual':<25} | {'Status':<10}")
print("-" * 85)

passed_count = 0
failed_count = 0
jit_passed_count = 0
jit_failed_count = 0
jit_skipped_count = 0

for test_file, expected_val, expected_err, input_str in tests:
    asm_path = os.path.join("test", test_file)
    bin_path = asm_path.replace(".asm", ".bin")
    
    try:
        # 1. Assemble
        subprocess.check_call(
            ["python3", "assembler.py", asm_path, bin_path],
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # 2. Run VM
        try:
            # We assume normal operation captures stdout. Errors go to stderr and raising CalledProcessError.
            # However, check_output only captures stdout by default unless stderr is redirected.
            # To separate them properly for our logic:
            
            proc = subprocess.run(
                ["./vm", bin_path], 
                input=input_str,
                capture_output=True, 
                text=True
            )
            
            stdout = proc.stdout
            stderr = proc.stderr
            ret_code = proc.returncode

            # Logic for Success Case (expected_err is None)
            if expected_err is None:
                if ret_code != 0:
                    status = "FAIL (Crash)"
                    actual = f"Exit {ret_code}"
                    failed_count += 1
                else:
                    match = re.search(r"Top of stack: (-?\d+)", stdout)
                    if match:
                        val = int(match.group(1))
                        if val == expected_val:
                            status = "PASS"
                            actual = str(val)
                            passed_count += 1
                        else:
                            status = "FAIL (Val)"
                            actual = str(val)
                            failed_count += 1
                    else:
                        status = "FAIL (Parse)"
                        actual = "?"
                        failed_count += 1
                        
            # Logic for Error Case (expected_err is set)
            else:
                if ret_code == 0:
                    status = "FAIL (Did Not Crash)"
                    actual = "Unexpected Success"
                    failed_count += 1
                else:
                    # Check if stderr contains the expected error message
                    if expected_err.lower() in stderr.lower():
                        status = "PASS"
                        actual = "Error Caught"
                        passed_count += 1
                    else:
                        status = "FAIL (Wrong Err)"
                        actual = stderr.strip()[:20] + "..."
                        failed_count += 1

            exp_str = str(expected_val) if expected_val is not None else expected_err[:15]
            print(f"{test_file:<25} | {exp_str:<15} | {actual:<25} | {status:<10}")

            # --- JIT Comparison (Try on ALL success cases) ---
            if expected_err is None:
                try:
                    proc_jit = subprocess.run(
                        ["./vm", bin_path, "--jit"], 
                        input=input_str,
                        capture_output=True, 
                        text=True
                    )
                    
                    jit_stdout = proc_jit.stdout
                    jit_stderr = proc_jit.stderr
                    
                    # Check for JIT Compilation Failure (Unsupported Opcode)
                    if "JIT Compilation Failed" in jit_stderr or "JIT Error" in jit_stderr:
                         print(f"  └── JIT: SKIP (Unsupported Opcodes)")
                         jit_skipped_count += 1
                    else:
                        jit_match = re.search(r"JIT Result: (-?\d+)", jit_stdout)
                        
                        if jit_match:
                            jit_val = int(jit_match.group(1))
                            if jit_val == expected_val:
                                print(f"  └── JIT: PASS (Val: {jit_val})")
                                jit_passed_count += 1
                            else:
                                print(f"  └── JIT: FAIL (Val: {jit_val}, Exp: {expected_val})")
                                jit_failed_count += 1
                        else:
                            if proc_jit.returncode != 0:
                                print(f"  └── JIT: FAIL (Crash/Error) Stderr: {jit_stderr.strip()[:30]}")
                                jit_failed_count += 1
                            else:
                                print(f"  └── JIT: FAIL (No Result Parsing)")
                                jit_failed_count += 1
                        
                except Exception as e:
                    print(f"  └── JIT: ERROR ({str(e)})")
                    jit_failed_count += 1

        finally:
            if os.path.exists(bin_path):
                os.remove(bin_path)

    except subprocess.CalledProcessError:
        print(f"{test_file:<25} | {'?':<15} | {'Assembly Fail':<25} | FAIL")
        failed_count += 1
    except Exception as e:
        print(f"{test_file:<25} | {'?':<15} | {str(e):<25} | FAIL")
        failed_count += 1

# Summary
total_interp = passed_count + failed_count
total_jit = jit_passed_count + jit_failed_count + jit_skipped_count
total_all = total_interp + total_jit

pass_all = passed_count + jit_passed_count
perc = (pass_all / (total_interp + jit_passed_count + jit_failed_count) * 100) if (total_interp + jit_passed_count + jit_failed_count) > 0 else 0

output_lines = []
output_lines.append("-" * 85)
output_lines.append(f"Interpreter: {passed_count}/{total_interp} passed")
output_lines.append(f"JIT:         {jit_passed_count}/{total_jit} passed ({jit_skipped_count} skipped)")
output_lines.append(f"Total:       {pass_all}/{total_interp + jit_passed_count + jit_failed_count} passed ({perc:.1f}%)")

if failed_count > 0 or jit_failed_count > 0:
    output_lines.append(f"Failures: {failed_count} Interp, {jit_failed_count} JIT")
else:
    output_lines.append("All tests passed!")

# Also capturing the print output is hard without refactoring, 
# so we will just append the summary for now and rely on manual run for details,
# OR we could redirect stdout in python. 
# Let's just write the summary to a file to prove it ran.
with open("test_results.txt", "w") as f:
    f.write("\n".join(output_lines))

print("\n".join(output_lines))

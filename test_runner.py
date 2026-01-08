import subprocess
import os
import re

# List of tests: (assembly_filename, expected_value, expected_error_substring)
# If expected_error_substring is None, we expect success and check expected_value.
# If expected_error_substring is set, we expect failure and check stderr for the substring.
tests = [
    ("test_push.asm", 10, None),
    ("test_pop.asm", 10, None),
    ("test_dup.asm", 10, None),
    ("test_halt.asm", 10, None),
    ("test_add.asm", 30, None),
    ("test_sub.asm", 20, None),
    ("test_mult.asm", 30, None),
    ("test_div.asm", 10, None),
    ("test_loop.asm", 0, None),
    ("test_call.asm", 25, None),
    ("test_call2.asm", 25, None),
    ("test_branching.asm", 1, None),
    ("test_memory.asm", 123, None),
    ("test_factorial.asm", 120, None),
    # Error Scenarios
    ("test_stack_underflow.asm", None, "Stack Underflow"),
    ("test_stack_overflow.asm", None, "Stack Overflow"),
    ("test_mem_oob.asm", None, "Memory Access Out of Bounds"),
    ("test_div_zero.asm", None, "Division by Zero"),
]

print(f"{'Test File':<25} | {'Expected':<15} | {'Actual':<25} | {'Status':<10}")
print("-" * 85)

passed_count = 0
failed_count = 0

for test_file, expected_val, expected_err in tests:
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
total = passed_count + failed_count
percentage = (passed_count / total * 100) if total > 0 else 0

print("-" * 85)
print(f"Summary: {passed_count}/{total} passed ({percentage:.1f}%)")
if failed_count > 0:
    print(f"Failed: {failed_count} tests")
else:
    print("All tests passed!")

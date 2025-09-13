#!/usr/bin/env python
"""
Demonstration of control flow features in the virtual shell.

This script showcases:
- Conditional execution with if/then/else/fi
- The test/[ command for conditions
- For loops for iteration
- While loops for repetition
- Boolean commands (true/false)
- Sleep command for timing
"""

from chuk_virtual_shell.shell_interpreter import ShellInterpreter

def main():
    shell = ShellInterpreter()
    
    print("=== Control Flow Features Demo ===\n")
    
    # Setup demo environment
    shell.execute("mkdir -p /demo/data")
    shell.execute("echo 'Hello World' > /demo/data/greeting.txt")
    shell.execute("echo '42' > /demo/data/number.txt")
    shell.execute("touch /demo/data/empty.txt")
    shell.execute("mkdir -p /demo/scripts")
    
    # 1. If/then/else statements
    print("1. IF/THEN/ELSE Statements")
    print("-" * 40)
    
    print("\nBasic if statement:")
    result = shell.execute("if true; then echo 'Condition is true'; fi")
    print(f"  Result: {result}")
    
    print("\nIf with test command:")
    result = shell.execute("if [ -e /demo/data/greeting.txt ]; then echo 'File exists'; fi")
    print(f"  Result: {result}")
    
    print("\nIf/else statement:")
    result = shell.execute("""
        if [ -e /demo/data/missing.txt ]; then
            echo 'File found'
        else
            echo 'File not found'
        fi
    """)
    print(f"  Result: {result}")
    
    print("\nIf/elif/else statement:")
    shell.execute("export NUM=42")
    result = shell.execute("""
        if [ $NUM -lt 10 ]; then
            echo 'Less than 10'
        elif [ $NUM -lt 50 ]; then
            echo 'Between 10 and 50'
        else
            echo 'Greater than or equal to 50'
        fi
    """)
    print(f"  Result: {result}")
    
    # 2. Test command demonstrations
    print("\n\n2. TEST/[ Command Examples")
    print("-" * 40)
    
    print("\nFile tests:")
    tests = [
        ("[ -e /demo/data/greeting.txt ]", "File exists"),
        ("[ -f /demo/data/greeting.txt ]", "Is a regular file"),
        ("[ -d /demo/data ]", "Is a directory"),
        ("[ -s /demo/data/greeting.txt ]", "File has content"),
        ("[ -s /demo/data/empty.txt ]", "Empty file check (should fail)"),
    ]
    
    for test_cmd, description in tests:
        shell.execute(test_cmd)
        status = "✓" if shell.return_code == 0 else "✗"
        print(f"  {description}: {status} - {test_cmd}")
    
    print("\nString tests:")
    string_tests = [
        ("[ 'hello' = 'hello' ]", "String equality"),
        ("[ 'hello' != 'world' ]", "String inequality"),
        ("[ -z '' ]", "Empty string"),
        ("[ -n 'text' ]", "Non-empty string"),
    ]
    
    for test_cmd, description in string_tests:
        shell.execute(test_cmd)
        status = "✓" if shell.return_code == 0 else "✗"
        print(f"  {description}: {status} - {test_cmd}")
    
    print("\nNumeric tests:")
    numeric_tests = [
        ("[ 5 -eq 5 ]", "Equal"),
        ("[ 5 -ne 10 ]", "Not equal"),
        ("[ 5 -lt 10 ]", "Less than"),
        ("[ 10 -gt 5 ]", "Greater than"),
        ("[ 5 -le 5 ]", "Less than or equal"),
        ("[ 5 -ge 5 ]", "Greater than or equal"),
    ]
    
    for test_cmd, description in numeric_tests:
        shell.execute(test_cmd)
        status = "✓" if shell.return_code == 0 else "✗"
        print(f"  {description}: {status} - {test_cmd}")
    
    # 3. For loops
    print("\n\n3. FOR Loops")
    print("-" * 40)
    
    print("\nBasic for loop:")
    result = shell.execute("for i in 1 2 3 4 5; do echo \"  Number: $i\"; done")
    print(result)
    
    print("\nFor loop with strings:")
    result = shell.execute("for color in red green blue; do echo \"  Color: $color\"; done")
    print(result)
    
    print("\nFor loop with glob pattern:")
    shell.execute("touch /demo/data/file1.txt /demo/data/file2.txt /demo/data/file3.txt")
    result = shell.execute("""
        for file in /demo/data/*.txt; do
            if [ -s $file ]; then
                echo "  $file has content"
            else
                echo "  $file is empty"
            fi
        done
    """)
    print(result)
    
    # 4. While loops
    print("\n\n4. WHILE Loops")
    print("-" * 40)
    
    print("\nWhile loop with counter:")
    shell.execute("export COUNT=1")
    shell.execute("touch /tmp/counter1 /tmp/counter2 /tmp/counter3")
    result = shell.execute("""
        while [ -e /tmp/counter1 ]; do
            echo "  Loop iteration"
            rm /tmp/counter1
        done
        echo "  Loop completed"
    """)
    print(result)
    
    print("\nWhile loop with condition:")
    result = shell.execute("""
        export ATTEMPTS=0
        touch /tmp/lock
        while [ -e /tmp/lock ]; do
            echo "  Checking lock..."
            rm /tmp/lock
            echo "  Lock removed"
        done
    """)
    print(result)
    
    # 5. Boolean commands
    print("\n\n5. TRUE/FALSE Commands")
    print("-" * 40)
    
    print("\nUsing true/false with logical operators:")
    examples = [
        ("true && echo '  Success'", "true with &&"),
        ("false || echo '  Fallback'", "false with ||"),
        ("true || echo '  Not shown'", "true with || (short-circuit)"),
        ("false && echo '  Not shown'", "false with && (short-circuit)"),
    ]
    
    for cmd, description in examples:
        print(f"\n{description}: {cmd}")
        result = shell.execute(cmd)
        if result:
            print(result)
    
    # 6. Sleep command
    print("\n\n6. SLEEP Command")
    print("-" * 40)
    
    print("\nDelaying execution:")
    import time
    start = time.time()
    result = shell.execute("""
        echo '  Starting...'
        sleep 0.5
        echo '  Half second later...'
        sleep 0.5
        echo '  One second total'
    """)
    elapsed = time.time() - start
    print(result)
    print(f"  Total time: {elapsed:.2f} seconds")
    
    # 7. Complex example
    print("\n\n7. Complex Example: File Processing")
    print("-" * 40)
    
    # Create some test files
    shell.execute("mkdir -p /demo/process")
    shell.execute("echo 'data1' > /demo/process/file1.dat")
    shell.execute("echo 'data2' > /demo/process/file2.dat")
    shell.execute("touch /demo/process/file3.dat")
    shell.execute("echo 'info' > /demo/process/readme.txt")
    
    print("\nProcessing files with specific extension:")
    result = shell.execute("""
        echo 'Processing .dat files:'
        for file in /demo/process/*.dat; do
            echo "  Checking $file..."
            if [ -s $file ]; then
                echo "    → Has content"
            else
                echo "    → Empty file"
            fi
            sleep 0.2
        done
        echo 'Processing complete!'
    """)
    print(result)
    
    # 8. Nested control structures
    print("\n\n8. Nested Control Structures")
    print("-" * 40)
    
    print("\nNested loops and conditions:")
    result = shell.execute("""
        for dir in data scripts process; do
            echo "Directory: /demo/$dir"
            if [ -d /demo/$dir ]; then
                for item in /demo/$dir/*; do
                    if [ -e $item ]; then
                        echo "  - Found: $item"
                    fi
                done
            else
                echo "  - Directory not found"
            fi
        done
    """)
    print(result)
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
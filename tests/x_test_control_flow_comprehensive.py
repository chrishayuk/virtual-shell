"""
Comprehensive test suite for control flow structures in the shell interpreter.
Tests for loops, while loops, if statements, case statements, functions, and more.
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class TestForLoops:
    """Test for loop functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_simple_for_loop(self):
        """Test basic for loop."""
        result = self.shell.execute("for i in 1 2 3; do echo $i; done")
        assert "1" in result
        assert "2" in result
        assert "3" in result

    def test_for_loop_with_strings(self):
        """Test for loop with string values."""
        result = self.shell.execute("for name in Alice Bob Charlie; do echo Hello $name; done")
        assert "Hello Alice" in result
        assert "Hello Bob" in result
        assert "Hello Charlie" in result

    def test_for_loop_with_glob(self):
        """Test for loop with glob expansion."""
        self.shell.execute("touch /file1.txt /file2.txt /file3.txt")
        result = self.shell.execute("for f in /*.txt; do echo Found: $f; done")
        assert "Found: /file1.txt" in result
        assert "Found: /file2.txt" in result
        assert "Found: /file3.txt" in result

    def test_for_loop_with_command_substitution(self):
        """Test for loop with command substitution."""
        self.shell.execute("mkdir /testdir")
        self.shell.execute("touch /testdir/a.txt /testdir/b.txt")
        result = self.shell.execute("for f in $(ls /testdir); do echo Processing $f; done")
        assert "Processing a.txt" in result
        assert "Processing b.txt" in result

    def test_nested_for_loops(self):
        """Test nested for loops."""
        result = self.shell.execute(
            "for i in 1 2; do for j in a b; do echo $i-$j; done; done"
        )
        assert "1-a" in result
        assert "1-b" in result
        assert "2-a" in result
        assert "2-b" in result

    def test_for_loop_with_break(self):
        """Test for loop with break statement."""
        result = self.shell.execute(
            "for i in 1 2 3 4 5; do if [ $i -eq 3 ]; then break; fi; echo $i; done"
        )
        assert "1" in result
        assert "2" in result
        assert "3" not in result
        assert "4" not in result
        assert "5" not in result

    def test_for_loop_with_continue(self):
        """Test for loop with continue statement."""
        result = self.shell.execute(
            "for i in 1 2 3 4 5; do if [ $i -eq 3 ]; then continue; fi; echo $i; done"
        )
        assert "1" in result
        assert "2" in result
        assert "3" not in result
        assert "4" in result
        assert "5" in result

    def test_for_loop_empty_list(self):
        """Test for loop with empty list."""
        result = self.shell.execute("for i in; do echo Should not appear; done")
        assert "Should not appear" not in result

    def test_for_loop_single_item(self):
        """Test for loop with single item."""
        result = self.shell.execute("for i in single; do echo $i; done")
        assert "single" in result

    def test_for_loop_with_complex_commands(self):
        """Test for loop with complex commands in body."""
        self.shell.execute("mkdir -p /data")
        result = self.shell.execute(
            "for i in 1 2 3; do echo Creating file$i; touch /data/file$i.txt; done"
        )
        assert "Creating file1" in result
        assert self.shell.fs.exists("/data/file1.txt")
        assert self.shell.fs.exists("/data/file2.txt")
        assert self.shell.fs.exists("/data/file3.txt")


class TestWhileLoops:
    """Test while loop functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_simple_while_loop(self):
        """Test basic while loop."""
        result = self.shell.execute(
            "i=0; while [ $i -lt 3 ]; do echo $i; i=$((i+1)); done"
        )
        assert "0" in result
        assert "1" in result
        assert "2" in result

    def test_while_true_with_break(self):
        """Test infinite while loop with break."""
        result = self.shell.execute(
            "i=0; while true; do echo $i; i=$((i+1)); if [ $i -eq 3 ]; then break; fi; done"
        )
        assert "0" in result
        assert "1" in result
        assert "2" in result
        assert "3" not in result

    def test_while_with_continue(self):
        """Test while loop with continue."""
        result = self.shell.execute(
            "i=0; while [ $i -lt 5 ]; do i=$((i+1)); if [ $i -eq 3 ]; then continue; fi; echo $i; done"
        )
        assert "1" in result
        assert "2" in result
        assert "3" not in result
        assert "4" in result
        assert "5" in result

    def test_while_false(self):
        """Test while loop that never executes."""
        result = self.shell.execute("while false; do echo Should not appear; done")
        assert "Should not appear" not in result

    def test_while_with_command_condition(self):
        """Test while loop with command as condition."""
        self.shell.execute("echo 3 > /counter.txt")
        result = self.shell.execute(
            "while [ $(cat /counter.txt) -gt 0 ]; do "
            "echo Count: $(cat /counter.txt); "
            "echo $(($(cat /counter.txt) - 1)) > /counter.txt; "
            "done"
        )
        assert "Count: 3" in result
        assert "Count: 2" in result
        assert "Count: 1" in result

    def test_nested_while_loops(self):
        """Test nested while loops."""
        result = self.shell.execute(
            "i=0; while [ $i -lt 2 ]; do "
            "j=0; while [ $j -lt 2 ]; do "
            "echo $i-$j; j=$((j+1)); "
            "done; i=$((i+1)); done"
        )
        assert "0-0" in result
        assert "0-1" in result
        assert "1-0" in result
        assert "1-1" in result


class TestIfStatements:
    """Test if/then/elif/else functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_simple_if(self):
        """Test basic if statement."""
        result = self.shell.execute("if true; then echo Success; fi")
        assert "Success" in result
        
        result = self.shell.execute("if false; then echo Should not appear; fi")
        assert "Should not appear" not in result

    def test_if_else(self):
        """Test if-else statement."""
        result = self.shell.execute("if true; then echo Yes; else echo No; fi")
        assert "Yes" in result
        assert "No" not in result
        
        result = self.shell.execute("if false; then echo Yes; else echo No; fi")
        assert "Yes" not in result
        assert "No" in result

    def test_if_elif_else(self):
        """Test if-elif-else statement."""
        result = self.shell.execute(
            "x=2; if [ $x -eq 1 ]; then echo One; "
            "elif [ $x -eq 2 ]; then echo Two; "
            "else echo Other; fi"
        )
        assert "One" not in result
        assert "Two" in result
        assert "Other" not in result

    def test_multiple_elif(self):
        """Test multiple elif branches."""
        result = self.shell.execute(
            "x=3; if [ $x -eq 1 ]; then echo One; "
            "elif [ $x -eq 2 ]; then echo Two; "
            "elif [ $x -eq 3 ]; then echo Three; "
            "elif [ $x -eq 4 ]; then echo Four; "
            "else echo Other; fi"
        )
        assert "Three" in result
        assert "One" not in result
        assert "Two" not in result
        assert "Four" not in result
        assert "Other" not in result

    def test_nested_if(self):
        """Test nested if statements."""
        result = self.shell.execute(
            "x=5; y=10; "
            "if [ $x -lt 10 ]; then "
            "  if [ $y -gt 5 ]; then "
            "    echo Both conditions met; "
            "  fi; "
            "fi"
        )
        assert "Both conditions met" in result

    def test_if_with_command(self):
        """Test if with command as condition."""
        self.shell.execute("touch /exists.txt")
        result = self.shell.execute("if ls /exists.txt > /dev/null 2>&1; then echo Found; fi")
        assert "Found" in result
        
        result = self.shell.execute("if ls /notexist.txt > /dev/null 2>&1; then echo Found; else echo Not found; fi")
        assert "Not found" in result

    def test_if_with_test_command(self):
        """Test if with test command conditions."""
        # File tests
        self.shell.execute("touch /file.txt")
        self.shell.execute("mkdir /dir")
        
        result = self.shell.execute("if [ -f /file.txt ]; then echo Is file; fi")
        assert "Is file" in result
        
        result = self.shell.execute("if [ -d /dir ]; then echo Is directory; fi")
        assert "Is directory" in result
        
        result = self.shell.execute("if [ -e /file.txt ]; then echo Exists; fi")
        assert "Exists" in result
        
        # String tests
        result = self.shell.execute('if [ "abc" = "abc" ]; then echo Equal; fi')
        assert "Equal" in result
        
        result = self.shell.execute('if [ "abc" != "def" ]; then echo Not equal; fi')
        assert "Not equal" in result
        
        result = self.shell.execute('if [ -z "" ]; then echo Empty; fi')
        assert "Empty" in result
        
        result = self.shell.execute('if [ -n "text" ]; then echo Not empty; fi')
        assert "Not empty" in result
        
        # Numeric tests
        result = self.shell.execute("if [ 5 -gt 3 ]; then echo Greater; fi")
        assert "Greater" in result
        
        result = self.shell.execute("if [ 2 -lt 4 ]; then echo Less; fi")
        assert "Less" in result
        
        result = self.shell.execute("if [ 3 -eq 3 ]; then echo Equal; fi")
        assert "Equal" in result
        
        result = self.shell.execute("if [ 3 -ne 4 ]; then echo Not equal; fi")
        assert "Not equal" in result
        
        result = self.shell.execute("if [ 5 -ge 5 ]; then echo Greater or equal; fi")
        assert "Greater or equal" in result
        
        result = self.shell.execute("if [ 3 -le 5 ]; then echo Less or equal; fi")
        assert "Less or equal" in result

    def test_if_with_logical_operators(self):
        """Test if with && and || operators."""
        result = self.shell.execute("if true && true; then echo Both true; fi")
        assert "Both true" in result
        
        result = self.shell.execute("if true || false; then echo At least one true; fi")
        assert "At least one true" in result
        
        result = self.shell.execute("if false && true; then echo Should not appear; else echo Failed; fi")
        assert "Failed" in result


class TestCaseStatements:
    """Test case statement functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_simple_case(self):
        """Test basic case statement."""
        result = self.shell.execute(
            'x=2; case $x in 1) echo One;; 2) echo Two;; 3) echo Three;; esac'
        )
        assert "Two" in result
        assert "One" not in result
        assert "Three" not in result

    def test_case_with_strings(self):
        """Test case with string matching."""
        result = self.shell.execute(
            'fruit=apple; case $fruit in '
            'apple) echo Red;; '
            'banana) echo Yellow;; '
            'orange) echo Orange;; '
            'esac'
        )
        assert "Red" in result

    def test_case_with_patterns(self):
        """Test case with pattern matching."""
        result = self.shell.execute(
            'file=test.txt; case $file in '
            '*.txt) echo Text file;; '
            '*.jpg|*.png) echo Image file;; '
            '*) echo Unknown;; '
            'esac'
        )
        assert "Text file" in result

    def test_case_with_default(self):
        """Test case with default branch."""
        result = self.shell.execute(
            'x=99; case $x in '
            '1) echo One;; '
            '2) echo Two;; '
            '*) echo Other;; '
            'esac'
        )
        assert "Other" in result

    def test_case_with_multiple_patterns(self):
        """Test case with multiple patterns per branch."""
        result = self.shell.execute(
            'x=b; case $x in '
            'a|b|c) echo First group;; '
            'd|e|f) echo Second group;; '
            '*) echo Other;; '
            'esac'
        )
        assert "First group" in result

    def test_case_with_complex_commands(self):
        """Test case with complex commands in branches."""
        result = self.shell.execute(
            'action=create; case $action in '
            'create) echo Creating...; touch /newfile.txt; echo Done;; '
            'delete) echo Deleting...; rm /newfile.txt 2>/dev/null; echo Done;; '
            '*) echo Unknown action;; '
            'esac'
        )
        assert "Creating..." in result
        assert "Done" in result
        assert self.shell.fs.exists("/newfile.txt")


class TestFunctions:
    """Test shell function functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_simple_function(self):
        """Test basic function definition and call."""
        self.shell.execute("greet() { echo Hello World; }")
        result = self.shell.execute("greet")
        assert "Hello World" in result

    def test_function_with_parameters(self):
        """Test function with parameters."""
        self.shell.execute("greet() { echo Hello $1; }")
        result = self.shell.execute("greet Alice")
        assert "Hello Alice" in result

    def test_function_with_multiple_parameters(self):
        """Test function with multiple parameters."""
        self.shell.execute("add() { echo $(($1 + $2)); }")
        result = self.shell.execute("add 3 5")
        assert "8" in result

    def test_function_with_local_variables(self):
        """Test function with local variables."""
        self.shell.execute("test_func() { local x=local_value; echo $x; }")
        self.shell.execute("x=global_value")
        result = self.shell.execute("test_func")
        assert "local_value" in result
        result = self.shell.execute("echo $x")
        assert "global_value" in result

    def test_function_return_value(self):
        """Test function return value."""
        self.shell.execute("check() { if [ $1 -gt 5 ]; then return 0; else return 1; fi; }")
        self.shell.execute("check 10")
        result = self.shell.execute("echo $?")
        assert "0" in result
        
        self.shell.execute("check 3")
        result = self.shell.execute("echo $?")
        assert "1" in result

    def test_function_calling_function(self):
        """Test function calling another function."""
        self.shell.execute("helper() { echo Helper: $1; }")
        self.shell.execute("main() { helper Called from main; }")
        result = self.shell.execute("main")
        assert "Helper: Called from main" in result

    def test_recursive_function(self):
        """Test recursive function."""
        self.shell.execute("""
            factorial() {
                if [ $1 -le 1 ]; then
                    echo 1
                else
                    local n=$1
                    local prev=$(factorial $(($n - 1)))
                    echo $(($n * $prev))
                fi
            }
        """)
        result = self.shell.execute("factorial 5")
        assert "120" in result


class TestUntilLoops:
    """Test until loop functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_simple_until_loop(self):
        """Test basic until loop."""
        result = self.shell.execute(
            "i=0; until [ $i -ge 3 ]; do echo $i; i=$((i+1)); done"
        )
        assert "0" in result
        assert "1" in result
        assert "2" in result
        assert "3" not in result

    def test_until_with_break(self):
        """Test until loop with break."""
        result = self.shell.execute(
            "i=0; until false; do echo $i; i=$((i+1)); if [ $i -eq 3 ]; then break; fi; done"
        )
        assert "0" in result
        assert "1" in result
        assert "2" in result
        assert "3" not in result

    def test_until_with_continue(self):
        """Test until loop with continue."""
        result = self.shell.execute(
            "i=0; until [ $i -ge 5 ]; do i=$((i+1)); if [ $i -eq 3 ]; then continue; fi; echo $i; done"
        )
        assert "1" in result
        assert "2" in result
        assert "3" not in result
        assert "4" in result
        assert "5" in result

    def test_until_true(self):
        """Test until loop that never executes."""
        result = self.shell.execute("until true; do echo Should not appear; done")
        assert "Should not appear" not in result


class TestSelectStatement:
    """Test select statement functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    @pytest.mark.skip(reason="Select statement requires interactive input")
    def test_simple_select(self):
        """Test basic select statement."""
        # Select statements are interactive and harder to test
        # This would require simulating user input
        pass


class TestControlFlowCombinations:
    """Test combinations of control flow structures."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_for_with_if(self):
        """Test for loop with if statement."""
        result = self.shell.execute(
            "for i in 1 2 3 4 5; do "
            "if [ $((i % 2)) -eq 0 ]; then "
            "echo $i is even; "
            "else "
            "echo $i is odd; "
            "fi; done"
        )
        assert "1 is odd" in result
        assert "2 is even" in result
        assert "3 is odd" in result
        assert "4 is even" in result
        assert "5 is odd" in result

    def test_while_with_case(self):
        """Test while loop with case statement."""
        result = self.shell.execute(
            "i=1; while [ $i -le 3 ]; do "
            "case $i in "
            "1) echo First;; "
            "2) echo Second;; "
            "3) echo Third;; "
            "esac; "
            "i=$((i+1)); done"
        )
        assert "First" in result
        assert "Second" in result
        assert "Third" in result

    def test_nested_control_structures(self):
        """Test deeply nested control structures."""
        result = self.shell.execute(
            "for i in 1 2; do "
            "  if [ $i -eq 1 ]; then "
            "    j=0; while [ $j -lt 2 ]; do "
            "      case $j in "
            "        0) echo First-Zero;; "
            "        1) echo First-One;; "
            "      esac; "
            "      j=$((j+1)); "
            "    done; "
            "  else "
            "    for k in a b; do "
            "      echo Second-$k; "
            "    done; "
            "  fi; "
            "done"
        )
        assert "First-Zero" in result
        assert "First-One" in result
        assert "Second-a" in result
        assert "Second-b" in result

    def test_function_with_loops(self):
        """Test function containing loops."""
        self.shell.execute("""
            process_list() {
                for item in $@; do
                    if [ "$item" = "skip" ]; then
                        continue
                    fi
                    echo Processing: $item
                done
            }
        """)
        result = self.shell.execute("process_list one skip two three")
        assert "Processing: one" in result
        assert "Processing: skip" not in result
        assert "Processing: two" in result
        assert "Processing: three" in result

    def test_control_flow_with_pipes(self):
        """Test control flow with pipes and redirections."""
        self.shell.execute("echo -e '1\\n2\\n3\\n4\\n5' > /numbers.txt")
        result = self.shell.execute(
            "for n in $(cat /numbers.txt | head -3); do "
            "if [ $n -gt 1 ]; then echo $n; fi; "
            "done | grep 2"
        )
        assert "2" in result
        assert "1" not in result
        assert "3" not in result  # grep filters it out

    def test_break_and_continue_in_nested_loops(self):
        """Test break and continue in nested loops."""
        result = self.shell.execute(
            "for i in 1 2 3; do "
            "  echo Outer: $i; "
            "  for j in a b c; do "
            "    if [ $i -eq 2 ] && [ $j = b ]; then break; fi; "
            "    echo Inner: $j; "
            "  done; "
            "done"
        )
        # When i=2 and j=b, inner loop breaks
        assert "Outer: 1" in result
        assert "Inner: a" in result
        lines = result.split('\n')
        # Count how many times "Inner: b" appears
        inner_b_count = sum(1 for line in lines if "Inner: b" in line)
        assert inner_b_count == 2  # Only for i=1 and i=3, not i=2


class TestArithmeticEvaluation:
    """Test arithmetic evaluation in control flow."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_arithmetic_in_condition(self):
        """Test arithmetic in conditions."""
        result = self.shell.execute("if [ $((5 + 3)) -eq 8 ]; then echo Correct; fi")
        assert "Correct" in result

    def test_arithmetic_expansion(self):
        """Test arithmetic expansion $(())."""
        result = self.shell.execute("echo $((10 + 5))")
        assert "15" in result
        
        result = self.shell.execute("echo $((10 - 5))")
        assert "5" in result
        
        result = self.shell.execute("echo $((10 * 5))")
        assert "50" in result
        
        result = self.shell.execute("echo $((10 / 5))")
        assert "2" in result
        
        result = self.shell.execute("echo $((10 % 3))")
        assert "1" in result

    def test_arithmetic_with_variables(self):
        """Test arithmetic with variables."""
        self.shell.execute("x=10")
        self.shell.execute("y=5")
        result = self.shell.execute("echo $(($x + $y))")
        assert "15" in result

    def test_arithmetic_in_loops(self):
        """Test arithmetic in loop conditions."""
        result = self.shell.execute(
            "sum=0; for i in 1 2 3 4 5; do sum=$((sum + i)); done; echo $sum"
        )
        assert "15" in result

    def test_increment_decrement(self):
        """Test increment and decrement operations."""
        self.shell.execute("x=5")
        self.shell.execute("x=$((x + 1))")
        result = self.shell.execute("echo $x")
        assert "6" in result
        
        self.shell.execute("x=$((x - 1))")
        result = self.shell.execute("echo $x")
        assert "5" in result


class TestEdgeCases:
    """Test edge cases and error conditions in control flow."""

    def setup_method(self):
        """Set up test environment."""
        self.shell = ShellInterpreter()

    def test_empty_loop_body(self):
        """Test loops with empty bodies."""
        # Should not crash
        result = self.shell.execute("for i in 1 2 3; do; done")
        assert result == "" or "error" not in result.lower()

    def test_malformed_if(self):
        """Test malformed if statements."""
        # Missing then
        result = self.shell.execute("if true echo test; fi")
        # Should handle gracefully
        
        # Missing fi
        result = self.shell.execute("if true; then echo test")
        # Should handle gracefully

    def test_infinite_loop_protection(self):
        """Test protection against infinite loops."""
        # This test would need timeout mechanism
        # For now, just test that break works to exit infinite loops
        result = self.shell.execute(
            "i=0; while true; do i=$((i+1)); if [ $i -gt 100 ]; then break; fi; done; echo $i"
        )
        assert "101" in result

    def test_deeply_nested_structures(self):
        """Test deeply nested control structures."""
        result = self.shell.execute(
            "for a in 1; do "
            "  for b in 2; do "
            "    for c in 3; do "
            "      for d in 4; do "
            "        for e in 5; do "
            "          echo $a$b$c$d$e; "
            "        done; "
            "      done; "
            "    done; "
            "  done; "
            "done"
        )
        assert "12345" in result

    def test_variable_scope_in_loops(self):
        """Test variable scope in loops."""
        self.shell.execute("x=outer")
        self.shell.execute("for i in 1; do x=inner; done")
        result = self.shell.execute("echo $x")
        assert "inner" in result  # Variables modified in loops affect outer scope

    def test_loop_with_empty_list(self):
        """Test loops with empty lists."""
        result = self.shell.execute("for i in $(cat /nonexistent 2>/dev/null); do echo Item: $i; done")
        assert "Item:" not in result  # Should not execute

    def test_conditional_with_command_substitution(self):
        """Test conditionals with command substitution."""
        self.shell.execute("echo 5 > /num.txt")
        result = self.shell.execute(
            "if [ $(cat /num.txt) -gt 3 ]; then echo Greater; fi"
        )
        assert "Greater" in result
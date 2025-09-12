"""
Test shell operators and variable expansion functionality
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


class TestShellOperators:
    """Test logical operators, command separators, and chaining"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = ShellInterpreter()

    def test_and_operator_success(self):
        """Test && operator when first command succeeds"""
        result = self.shell.execute("echo first && echo second")
        assert "first" in result
        assert "second" in result

    def test_and_operator_failure(self):
        """Test && operator when first command fails"""
        result = self.shell.execute("false_command && echo should_not_appear")
        assert "command not found" in result
        assert "should_not_appear" not in result

    def test_or_operator_success(self):
        """Test || operator when first command succeeds"""
        result = self.shell.execute("echo success || echo fallback")
        assert "success" in result
        assert "fallback" not in result

    def test_or_operator_failure(self):
        """Test || operator when first command fails"""
        result = self.shell.execute("false_command || echo fallback")
        assert "fallback" in result

    def test_semicolon_separator(self):
        """Test ; command separator"""
        result = self.shell.execute("echo first; echo second; echo third")
        assert "first" in result
        assert "second" in result
        assert "third" in result

    def test_mixed_operators(self):
        """Test combination of &&, ||, and ;"""
        result = self.shell.execute("echo start; echo middle && echo end")
        assert "start" in result
        assert "middle" in result
        assert "end" in result

    def test_operators_with_redirection(self):
        """Test operators with file redirection"""
        self.shell.execute("echo test > /test.txt && echo success")
        content = self.shell.fs.read_file("/test.txt")
        assert content == "test"

    def test_operators_with_pipes(self):
        """Test operators with pipes"""
        self.shell.execute("echo 'line1\nline2\nline3' > /test.txt")
        result = self.shell.execute("cat /test.txt | grep line2 && echo found")
        assert "line2" in result
        assert "found" in result


class TestVariableExpansion:
    """Test environment variable expansion"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = ShellInterpreter()

    def test_simple_variable_expansion(self):
        """Test basic $VAR expansion"""
        self.shell.execute("export TEST_VAR=hello")
        result = self.shell.execute("echo $TEST_VAR")
        assert result == "hello"

    def test_variable_in_string(self):
        """Test variable expansion in quoted string"""
        self.shell.execute("export NAME=World")
        result = self.shell.execute('echo "Hello $NAME"')
        assert result == "Hello World"

    def test_curly_brace_expansion(self):
        """Test ${VAR} expansion"""
        self.shell.execute("export VAR=test")
        result = self.shell.execute("echo ${VAR}ing")
        assert result == "testing"

    def test_undefined_variable(self):
        """Test expansion of undefined variable"""
        result = self.shell.execute("echo $UNDEFINED_VAR")
        assert result == ""

    def test_multiple_variables(self):
        """Test multiple variable expansions"""
        self.shell.execute("export VAR1=hello")
        self.shell.execute("export VAR2=world")
        result = self.shell.execute("echo $VAR1 $VAR2")
        assert result == "hello world"

    def test_variable_in_path(self):
        """Test variable expansion in file paths"""
        self.shell.execute("export DIR=/home")
        self.shell.execute("mkdir -p /home/user")
        result = self.shell.execute("cd $DIR/user && pwd")
        assert "/home/user" in result

    def test_special_variables(self):
        """Test special shell variables"""
        # $? - exit code
        self.shell.execute("true")  # Should set exit code to 0
        result = self.shell.execute("echo $?")
        assert result == "0"

        # $HOME
        result = self.shell.execute("echo $HOME")
        assert "/home/user" in result

        # $PWD
        self.shell.execute("mkdir -p /home")
        self.shell.execute("cd /home")
        result = self.shell.execute("echo $PWD")
        assert "/home" in result


class TestGlobExpansion:
    """Test wildcard/glob pattern expansion"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = ShellInterpreter()
        # Create test files
        self.shell.execute("touch /test1.txt /test2.txt /test.log /data.csv")

    def test_star_glob(self):
        """Test * wildcard expansion"""
        result = self.shell.execute("ls *.txt")
        assert "test1.txt" in result
        assert "test2.txt" in result
        assert "test.log" not in result

    def test_question_glob(self):
        """Test ? wildcard expansion"""
        result = self.shell.execute("ls test?.txt")
        assert "test1.txt" in result
        assert "test2.txt" in result

    def test_glob_with_rm(self):
        """Test glob expansion with rm command"""
        self.shell.execute("rm *.log")
        result = self.shell.execute("ls")
        assert "test.log" not in result
        assert "test1.txt" in result

    def test_glob_with_cp(self):
        """Test glob expansion with cp command"""
        self.shell.execute("mkdir /backup")
        self.shell.execute("cp *.txt /backup/")
        result = self.shell.execute("ls /backup")
        assert "test1.txt" in result
        assert "test2.txt" in result

    def test_no_match_glob(self):
        """Test glob pattern with no matches"""
        result = self.shell.execute("ls *.xyz")
        assert "No such file" in result or result == ""


class TestHomeExpansion:
    """Test tilde (~) home directory expansion"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = ShellInterpreter()

    def test_tilde_expansion(self):
        """Test ~ expands to home directory"""
        result = self.shell.execute("cd ~ && pwd")
        assert "/home/user" in result

    def test_tilde_with_path(self):
        """Test ~/path expansion"""
        self.shell.execute("mkdir -p /home/user/documents")
        result = self.shell.execute("cd ~/documents && pwd")
        assert "/home/user/documents" in result

    def test_cd_dash(self):
        """Test cd - returns to previous directory"""
        self.shell.execute("mkdir -p /home")
        self.shell.execute("mkdir -p /tmp")
        self.shell.execute("cd /home")
        self.shell.execute("cd /tmp")
        result = self.shell.execute("cd - && pwd")
        assert "/home" in result


class TestCommandSubstitution:
    """Test command substitution with $() and backticks"""

    def setup_method(self):
        """Set up test environment"""
        self.shell = ShellInterpreter()

    def test_dollar_paren_substitution(self):
        """Test $(command) substitution"""
        self.shell.execute("echo hello > /test.txt")
        result = self.shell.execute("echo Content: $(cat /test.txt)")
        assert result == "Content: hello"

    def test_backtick_substitution(self):
        """Test `command` substitution"""
        self.shell.execute("echo world > /test.txt")
        result = self.shell.execute("echo Content: `cat /test.txt`")
        assert result == "Content: world"

    def test_nested_substitution(self):
        """Test nested command substitution"""
        self.shell.execute("echo /home > /path.txt")
        result = self.shell.execute("cd $(cat /path.txt) && pwd")
        assert "/home" in result

    def test_substitution_in_variable(self):
        """Test command substitution in variable assignment"""
        self.shell.execute("echo test > /data.txt")
        self.shell.execute("export VAR=$(cat /data.txt)")
        result = self.shell.execute("echo $VAR")
        assert result == "test"
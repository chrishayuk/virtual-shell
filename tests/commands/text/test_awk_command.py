"""
tests/chuk_virtual_shell/commands/text/test_awk_command.py
"""
import pytest
from chuk_virtual_shell.commands.text.awk import AwkCommand
from tests.dummy_shell import DummyShell

@pytest.fixture
def awk_command():
    # Setup a dummy file system with sample files
    files = {
        "data.txt": "Alice 30 Engineer\nBob 25 Designer\nCarol 35 Manager",
        "numbers.txt": "10 20\n30 40\n50 60",
        "csv.txt": "name,age,job\nAlice,30,Engineer\nBob,25,Designer",
        "grades.txt": "John 85\nJane 92\nBob 78\nAlice 95",
    }
    dummy_shell = DummyShell(files)
    command = AwkCommand(shell_context=dummy_shell)
    return command

def test_awk_missing_program(awk_command):
    output = awk_command.execute([])
    assert output == "awk: missing program"

def test_awk_print_all(awk_command):
    output = awk_command.execute(["{print}", "data.txt"])
    lines = output.splitlines()
    assert len(lines) == 3
    assert "Alice 30 Engineer" in lines[0]

def test_awk_print_first_field(awk_command):
    output = awk_command.execute(["{print $1}", "data.txt"])
    lines = output.splitlines()
    assert lines == ["Alice", "Bob", "Carol"]

def test_awk_print_multiple_fields(awk_command):
    output = awk_command.execute(["{print $1,$3}", "data.txt"])
    lines = output.splitlines()
    assert "Alice Engineer" in lines[0]
    assert "Bob Designer" in lines[1]

def test_awk_field_separator(awk_command):
    output = awk_command.execute(["-F", ",", "{print $2}", "csv.txt"])
    lines = output.splitlines()
    assert "age" in lines[0]
    assert "30" in lines[1]
    assert "25" in lines[2]

def test_awk_pattern_match(awk_command):
    output = awk_command.execute(["/Alice/", "data.txt"])
    assert "Alice 30 Engineer" in output
    assert "Bob" not in output

def test_awk_field_comparison(awk_command):
    output = awk_command.execute(['$2>30 {print $1}', "data.txt"])
    assert "Carol" in output
    assert "Alice" not in output
    assert "Bob" not in output

def test_awk_line_number(awk_command):
    output = awk_command.execute(['NR==1 {print}', "data.txt"])
    assert "Alice 30 Engineer" in output
    assert "Bob" not in output

def test_awk_print_line_numbers(awk_command):
    output = awk_command.execute(['{print NR}', "numbers.txt"])
    lines = output.splitlines()
    assert lines == ["1", "2", "3"]

def test_awk_print_field_count(awk_command):
    output = awk_command.execute(['{print NF}', "data.txt"])
    lines = output.splitlines()
    assert all(line == "3" for line in lines)

def test_awk_sum_column(awk_command):
    output = awk_command.execute(['{sum+=$1} END{print sum}', "numbers.txt"])
    assert "90" in output  # 10+30+50

def test_awk_begin_block(awk_command):
    output = awk_command.execute(['BEGIN{print "Header"} {print $1}', "data.txt"])
    lines = output.splitlines()
    assert lines[0] == "Header"
    assert lines[1] == "Alice"

def test_awk_end_block(awk_command):
    output = awk_command.execute(['{print $1} END{print "Footer"}', "data.txt"])
    lines = output.splitlines()
    assert lines[-1] == "Footer"

def test_awk_variable_assignment(awk_command):
    output = awk_command.execute(["-v", "name=Test", 'BEGIN{print name}', "data.txt"])
    assert "Test" in output

def test_awk_stdin_processing(awk_command):
    # Simulate stdin
    awk_command.shell._stdin_buffer = "Field1 Field2\nField3 Field4"
    output = awk_command.execute(['{print $2}'])
    lines = output.splitlines()
    assert lines == ["Field2", "Field4"]

def test_awk_average_calculation(awk_command):
    output = awk_command.execute(['{sum+=$2} END{print sum/NR}', "grades.txt"])
    # Average of 85, 92, 78, 95 = 87.5
    assert "87" in output  # Allowing for float representation

def test_awk_no_input_files(awk_command):
    output = awk_command.execute(['{print}'])
    assert "no input files" in output
"""
tests/chuk_virtual_shell/commands/text/test_sort_uniq_wc_commands.py
"""

import pytest
from chuk_virtual_shell.commands.text.sort import SortCommand
from chuk_virtual_shell.commands.text.uniq import UniqCommand
from chuk_virtual_shell.commands.text.wc import WcCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def commands():
    files = {
        "unsorted.txt": "banana\napple\ncherry\napple\ndate",
        "numbers.txt": "10\n5\n20\n3\n15",
        "fields.txt": "John 25\nAlice 30\nBob 20\nCarol 35",
        "duplicates.txt": "line1\nline1\nline2\nline2\nline2\nline3",
        "mixed_case.txt": "Apple\napple\nBanana\nbanana",
        "sample.txt": "Hello world\nThis is a test\nWith multiple lines",
    }
    dummy_shell = DummyShell(files)

    sort_cmd = SortCommand(shell_context=dummy_shell)
    uniq_cmd = UniqCommand(shell_context=dummy_shell)
    wc_cmd = WcCommand(shell_context=dummy_shell)

    return sort_cmd, uniq_cmd, wc_cmd, dummy_shell


# SORT COMMAND TESTS


def test_sort_basic(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["unsorted.txt"])
    lines = output.splitlines()
    assert lines == ["apple", "apple", "banana", "cherry", "date"]


def test_sort_reverse(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["-r", "unsorted.txt"])
    lines = output.splitlines()
    assert lines == ["date", "cherry", "banana", "apple", "apple"]


def test_sort_numeric(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["-n", "numbers.txt"])
    lines = output.splitlines()
    assert lines == ["3", "5", "10", "15", "20"]


def test_sort_unique(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["-u", "unsorted.txt"])
    lines = output.splitlines()
    assert lines == ["apple", "banana", "cherry", "date"]


def test_sort_by_field(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["-k", "2", "-n", "fields.txt"])
    lines = output.splitlines()
    assert lines[0] == "Bob 20"
    assert lines[1] == "John 25"
    assert lines[2] == "Alice 30"
    assert lines[3] == "Carol 35"


def test_sort_ignore_case(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["-f", "mixed_case.txt"])
    lines = output.splitlines()
    # Should group apples together, bananas together
    assert lines[0].lower() == "apple"
    assert lines[1].lower() == "apple"
    assert lines[2].lower() == "banana"
    assert lines[3].lower() == "banana"


def test_sort_combined_options(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["-rn", "numbers.txt"])
    lines = output.splitlines()
    assert lines == ["20", "15", "10", "5", "3"]


def test_sort_stdin(commands):
    sort_cmd, _, _, dummy_shell = commands
    dummy_shell._stdin_buffer = "zebra\nalpha\nbeta"
    output = sort_cmd.execute([])
    lines = output.splitlines()
    assert lines == ["alpha", "beta", "zebra"]


def test_sort_ignore_blanks(commands):
    sort_cmd, _, _, dummy_shell = commands
    dummy_shell.fs.write_file("blanks.txt", "  zebra\nalpha\n  beta")
    output = sort_cmd.execute(["-b", "blanks.txt"])
    lines = output.splitlines()
    assert lines == ["alpha", "  beta", "  zebra"]


def test_sort_invalid_field_number(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["-k", "abc", "fields.txt"])
    assert "invalid field number" in output


def test_sort_field_option_no_arg(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["-k"])
    assert "option requires an argument" in output


def test_sort_separator_option(commands):
    sort_cmd, _, _, dummy_shell = commands
    dummy_shell.fs.write_file("csv.txt", "John,25\nAlice,30\nBob,20")
    output = sort_cmd.execute(["-t", ",", "-k", "2", "-n", "csv.txt"])
    lines = output.splitlines()
    assert lines[0] == "Bob,20"
    assert lines[1] == "John,25"
    assert lines[2] == "Alice,30"


def test_sort_separator_option_no_arg(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["-t"])
    assert "option requires an argument" in output


def test_sort_combined_options_all(commands):
    sort_cmd, _, _, dummy_shell = commands
    dummy_shell.fs.write_file("mixed.txt", "Apple\napple\nBanana\nbanana")
    output = sort_cmd.execute(["-fub", "mixed.txt"])
    lines = output.splitlines()
    # The unique option in sort works on exact matches after sorting, not case-insensitive matches
    # So we should still have 4 lines, but they're sorted with case-insensitive comparison
    assert len(lines) == 4


def test_sort_empty_stdin(commands):
    sort_cmd, _, _, dummy_shell = commands
    # No stdin buffer
    if hasattr(dummy_shell, "_stdin_buffer"):
        delattr(dummy_shell, "_stdin_buffer")
    output = sort_cmd.execute([])
    assert output == ""


def test_sort_nonexistent_file(commands):
    sort_cmd, _, _, _ = commands
    output = sort_cmd.execute(["nonexistent.txt"])
    assert "No such file or directory" in output


def test_sort_empty_lines(commands):
    sort_cmd, _, _, dummy_shell = commands
    dummy_shell.fs.write_file("empty.txt", "")
    output = sort_cmd.execute(["empty.txt"])
    assert output == ""


def test_sort_field_separator_whitespace(commands):
    sort_cmd, _, _, dummy_shell = commands
    dummy_shell.fs.write_file("whitespace.txt", "John\t25\nAlice\t\t30\nBob   20")
    output = sort_cmd.execute(["-k", "2", "-n", "whitespace.txt"])
    lines = output.splitlines()
    # Should handle various whitespace
    assert "20" in lines[0]  # Bob should be first


def test_sort_field_out_of_range(commands):
    sort_cmd, _, _, dummy_shell = commands
    dummy_shell.fs.write_file("short.txt", "a\nb c\nd e f")
    output = sort_cmd.execute(["-k", "3", "short.txt"])
    lines = output.splitlines()
    # Lines without field 3 should sort as empty string
    assert lines[0] == "a"  # No field 3, sorts first
    assert lines[1] == "b c"  # No field 3, sorts second
    assert lines[2] == "d e f"  # Has field 3 "f", sorts last


def test_sort_numeric_invalid_values(commands):
    sort_cmd, _, _, dummy_shell = commands
    dummy_shell.fs.write_file("invalid_nums.txt", "abc\n123\nxyz456\n-789")
    output = sort_cmd.execute(["-n", "invalid_nums.txt"])
    lines = output.splitlines()
    # Check that -789 sorts first (negative) and that sorting worked
    assert lines[0] == "-789"
    # Just verify we have the expected number of lines and it doesn't crash
    assert len(lines) == 4


# UNIQ COMMAND TESTS


def test_uniq_basic(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["duplicates.txt"])
    lines = output.splitlines()
    assert lines == ["line1", "line2", "line3"]


def test_uniq_count(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["-c", "duplicates.txt"])
    lines = output.splitlines()
    assert "2 line1" in lines[0]
    assert "3 line2" in lines[1]
    assert "1 line3" in lines[2]


def test_uniq_duplicates_only(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["-d", "duplicates.txt"])
    lines = output.splitlines()
    assert lines == ["line1", "line2"]


def test_uniq_unique_only(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["-u", "duplicates.txt"])
    lines = output.splitlines()
    assert lines == ["line3"]


def test_uniq_ignore_case(commands):
    _, uniq_cmd, _, dummy_shell = commands
    dummy_shell.fs.write_file("case_test.txt", "Hello\nhello\nWorld\nworld\nworld")
    output = uniq_cmd.execute(["-i", "case_test.txt"])
    lines = output.splitlines()
    assert len(lines) == 2  # Hello and World (case-insensitive)


def test_uniq_skip_fields_invalid(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["-f", "abc", "duplicates.txt"])
    assert "invalid number of fields to skip" in output


def test_uniq_skip_fields_no_arg(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["-f"])
    assert "option requires an argument" in output


def test_uniq_skip_chars_option(commands):
    _, uniq_cmd, _, dummy_shell = commands
    dummy_shell.fs.write_file("chars_test.txt", "  hello\n  hello\n  world")
    output = uniq_cmd.execute(["-s", "2", "chars_test.txt"])
    lines = output.splitlines()
    assert len(lines) == 2  # Should skip first 2 chars and see "hello" as duplicate


def test_uniq_skip_chars_invalid(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["-s", "xyz", "duplicates.txt"])
    assert "invalid number of characters to skip" in output


def test_uniq_skip_chars_no_arg(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["-s"])
    assert "option requires an argument" in output


def test_uniq_width_option(commands):
    _, uniq_cmd, _, dummy_shell = commands
    dummy_shell.fs.write_file("width_test.txt", "hello123\nhello456\nworld789")
    output = uniq_cmd.execute(["-w", "5", "width_test.txt"])
    lines = output.splitlines()
    assert len(lines) == 2  # Should compare only first 5 chars: "hello" vs "world"


def test_uniq_width_invalid(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["-w", "bad", "duplicates.txt"])
    assert "invalid number of characters to compare" in output


def test_uniq_width_no_arg(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["-w"])
    assert "option requires an argument" in output


def test_uniq_combined_options(commands):
    _, uniq_cmd, _, dummy_shell = commands
    dummy_shell.fs.write_file("combined_test.txt", "line1\nline1\nline2")
    output = uniq_cmd.execute(["-cd", "combined_test.txt"])
    lines = output.splitlines()
    # Should count duplicates only
    assert "2" in lines[0] and "line1" in lines[0]


def test_uniq_empty_stdin(commands):
    _, uniq_cmd, _, dummy_shell = commands
    # No stdin buffer
    if hasattr(dummy_shell, "_stdin_buffer"):
        delattr(dummy_shell, "_stdin_buffer")
    output = uniq_cmd.execute([])
    assert output == ""


def test_uniq_nonexistent_file(commands):
    _, uniq_cmd, _, _ = commands
    output = uniq_cmd.execute(["nonexistent.txt"])
    assert "No such file or directory" in output


def test_uniq_empty_content(commands):
    _, uniq_cmd, _, dummy_shell = commands
    dummy_shell.fs.write_file("empty.txt", "")
    output = uniq_cmd.execute(["empty.txt"])
    assert output == ""


def test_uniq_skip_fields_beyond_available(commands):
    _, uniq_cmd, _, dummy_shell = commands
    dummy_shell.fs.write_file("short_fields.txt", "a\na\nb c")
    output = uniq_cmd.execute(["-f", "5", "short_fields.txt"])
    lines = output.splitlines()
    # All lines become empty after skipping 5 fields, so they're all duplicates
    assert len(lines) == 1  # All collapse to one line


def test_uniq_skip_chars_beyond_length(commands):
    _, uniq_cmd, _, dummy_shell = commands
    dummy_shell.fs.write_file("short_chars.txt", "hi\nhi\nhello")
    output = uniq_cmd.execute(["-s", "10", "short_chars.txt"])
    lines = output.splitlines()
    # All lines become empty after skipping 10 chars, so should collapse to one line
    assert len(lines) == 1


def test_uniq_width_limit(commands):
    _, uniq_cmd, _, dummy_shell = commands
    dummy_shell.fs.write_file("width_limit.txt", "hello123\nhello456")
    output = uniq_cmd.execute(["-w", "5", "width_limit.txt"])
    lines = output.splitlines()
    # Both start with "hello", so should be treated as duplicates
    assert len(lines) == 1


def test_uniq_output_to_file(commands):
    _, uniq_cmd, _, dummy_shell = commands
    output = uniq_cmd.execute(["duplicates.txt", "output.txt"])
    # Should write to file and return empty string
    assert output == ""
    # Check that file was created
    file_content = dummy_shell.fs.read_file("output.txt")
    assert "line1" in file_content and "line2" in file_content


def test_uniq_skip_fields(commands):
    _, uniq_cmd, _, dummy_shell = commands
    dummy_shell.fs.write_file("fields.txt", "a 1\nb 1\nc 2")
    output = uniq_cmd.execute(["-f", "1", "fields.txt"])
    lines = output.splitlines()
    assert len(lines) == 2  # Skip first field, so "1" and "2" are unique


def test_uniq_stdin(commands):
    _, uniq_cmd, _, dummy_shell = commands
    dummy_shell._stdin_buffer = "a\na\nb\nb\nc"
    output = uniq_cmd.execute([])
    lines = output.splitlines()
    assert lines == ["a", "b", "c"]


def test_uniq_output_file(commands):
    _, uniq_cmd, _, dummy_shell = commands
    uniq_cmd.execute(["duplicates.txt", "output.txt"])
    content = dummy_shell.fs.read_file("output.txt")
    lines = content.splitlines()
    assert lines == ["line1", "line2", "line3"]


# WC COMMAND TESTS


def test_wc_default(commands):
    _, _, wc_cmd, _ = commands
    output = wc_cmd.execute(["sample.txt"])
    # Default shows lines, words, bytes
    parts = output.split()
    assert parts[0] == "3"  # lines
    assert parts[1] == "9"  # words (Hello world / This is a test / With multiple lines)
    # bytes will vary based on encoding


def test_wc_lines_only(commands):
    _, _, wc_cmd, _ = commands
    output = wc_cmd.execute(["-l", "sample.txt"])
    assert "3" in output


def test_wc_words_only(commands):
    _, _, wc_cmd, _ = commands
    output = wc_cmd.execute(["-w", "sample.txt"])
    assert "9" in output


def test_wc_bytes(commands):
    _, _, wc_cmd, dummy_shell = commands
    dummy_shell.fs.write_file("test.txt", "Hello")
    output = wc_cmd.execute(["-c", "test.txt"])
    assert "5" in output


def test_wc_chars(commands):
    _, _, wc_cmd, dummy_shell = commands
    dummy_shell.fs.write_file("test.txt", "Hello")
    output = wc_cmd.execute(["-m", "test.txt"])
    assert "5" in output


def test_wc_max_line_length(commands):
    _, _, wc_cmd, dummy_shell = commands
    dummy_shell.fs.write_file("lines.txt", "short\na very long line here\nmedium")
    output = wc_cmd.execute(["-L", "lines.txt"])
    assert "21" in output  # length of "a very long line here"


def test_wc_multiple_files(commands):
    _, _, wc_cmd, _ = commands
    output = wc_cmd.execute(["sample.txt", "unsorted.txt"])
    lines = output.splitlines()
    assert len(lines) == 3  # Two files plus total
    assert "total" in lines[-1]


def test_wc_combined_options(commands):
    _, _, wc_cmd, _ = commands
    output = wc_cmd.execute(["-lw", "sample.txt"])
    parts = output.split()
    assert parts[0] == "3"  # lines
    assert parts[1] == "9"  # words


def test_wc_stdin(commands):
    _, _, wc_cmd, dummy_shell = commands
    dummy_shell._stdin_buffer = "Line 1\nLine 2\nLine 3"
    output = wc_cmd.execute(["-l"])
    assert "3" in output


def test_wc_empty_file(commands):
    _, _, wc_cmd, dummy_shell = commands
    dummy_shell.fs.write_file("empty.txt", "")
    output = wc_cmd.execute(["empty.txt"])
    parts = output.split()
    assert parts[0] == "0"  # lines
    assert parts[1] == "0"  # words
    assert parts[2] == "0"  # bytes

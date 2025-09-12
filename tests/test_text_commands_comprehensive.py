"""
tests/test_text_commands_comprehensive.py - Comprehensive tests for all text processing commands
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


@pytest.fixture
def shell():
    """Create a shell instance for testing"""
    shell = ShellInterpreter()
    shell.execute("mkdir -p /tmp")
    return shell


# ============= AWK TESTS =============


def test_awk_field_extraction(shell):
    """Test AWK field extraction"""
    shell.fs.write_file("/tmp/data.txt", "one two three\nfour five six")

    # Extract first field
    result = shell.execute("awk '{print $1}' /tmp/data.txt")
    assert result == "one\nfour"

    # Extract multiple fields
    result = shell.execute("awk '{print $2, $3}' /tmp/data.txt")
    assert "two  three" in result or "two three" in result


def test_awk_field_separator(shell):
    """Test AWK with custom field separator"""
    shell.fs.write_file("/tmp/csv.txt", "a,b,c\nd,e,f")

    # Using -F flag
    result = shell.execute("awk -F, '{print $2}' /tmp/csv.txt")
    assert result == "b\ne"

    # Using -F with attached separator
    result = shell.execute("awk -F\",\" '{print $1}' /tmp/csv.txt")
    assert result == "a\nd"


def test_awk_nr_variable(shell):
    """Test AWK NR (line number) variable"""
    shell.fs.write_file("/tmp/lines.txt", "line1\nline2\nline3")

    result = shell.execute("awk '{print NR \": \" $0}' /tmp/lines.txt")
    assert "1" in result.split("\n")[0]
    assert "2" in result.split("\n")[1]
    assert "3" in result.split("\n")[2]


def test_awk_calculations(shell):
    """Test AWK arithmetic operations"""
    shell.fs.write_file("/tmp/numbers.txt", "10\n20\n30")

    # Sum calculation
    result = shell.execute("awk '{sum+=$1} END {print sum}' /tmp/numbers.txt")
    assert result.strip() in ["60", "60.0"]

    # Average calculation
    result = shell.execute(
        "awk '{sum+=$1; count++} END {print sum/count}' /tmp/numbers.txt"
    )
    assert "20" in result


def test_awk_pattern_matching(shell):
    """Test AWK pattern matching"""
    shell.fs.write_file("/tmp/mixed.txt", "apple 10\nbanana 20\napricot 30")

    # Match lines starting with 'a'
    result = shell.execute("awk '/^a/ {print $2}' /tmp/mixed.txt")
    assert "10" in result
    assert "30" in result
    assert "20" not in result


def test_awk_begin_end(shell):
    """Test AWK BEGIN and END blocks"""
    shell.fs.write_file("/tmp/data.txt", "1\n2\n3")

    result = shell.execute(
        'awk \'BEGIN {print "Start"} {sum+=$1} END {print "Total:", sum}\' /tmp/data.txt'
    )
    assert "Start" in result
    assert "Total:" in result
    assert "6" in result


def test_awk_empty_file(shell):
    """Test AWK with empty file"""
    shell.fs.write_file("/tmp/empty.txt", "")

    result = shell.execute("awk '{print $1}' /tmp/empty.txt")
    assert result == ""

    # BEGIN/END still execute
    result = shell.execute(
        'awk \'BEGIN {print "start"} END {print "end"}\' /tmp/empty.txt'
    )
    assert "start" in result
    assert "end" in result


# ============= GREP TESTS =============


def test_grep_basic_search(shell):
    """Test basic grep search"""
    shell.fs.write_file("/tmp/text.txt", "hello world\ngoodbye world\nhello again")

    result = shell.execute('grep "hello" /tmp/text.txt')
    assert "hello world" in result
    assert "hello again" in result
    assert "goodbye" not in result


def test_grep_case_insensitive(shell):
    """Test grep -i case insensitive search"""
    shell.fs.write_file("/tmp/case.txt", "HELLO\nhello\nHeLLo")

    result = shell.execute('grep -i "hello" /tmp/case.txt')
    lines = result.strip().split("\n")
    assert len(lines) == 3


def test_grep_invert_match(shell):
    """Test grep -v invert match"""
    shell.fs.write_file("/tmp/data.txt", "include\nexclude\ninclude")

    result = shell.execute('grep -v "exclude" /tmp/data.txt')
    assert "include" in result
    assert "exclude" not in result


def test_grep_line_numbers(shell):
    """Test grep -n show line numbers"""
    shell.fs.write_file("/tmp/lines.txt", "no\nyes\nno\nyes")

    result = shell.execute('grep -n "yes" /tmp/lines.txt')
    assert "2:yes" in result
    assert "4:yes" in result


def test_grep_count_matches(shell):
    """Test grep -c count matches"""
    shell.fs.write_file("/tmp/count.txt", "a\nb\na\nc\na")

    result = shell.execute('grep -c "a" /tmp/count.txt')
    assert result.strip() == "3"


def test_grep_whole_word(shell):
    """Test grep -w whole word match"""
    shell.fs.write_file("/tmp/words.txt", "testing\ntest\ntested")

    result = shell.execute('grep -w "test" /tmp/words.txt')
    assert result.strip() == "test"


def test_grep_regex_patterns(shell):
    """Test grep with regex patterns"""
    shell.fs.write_file("/tmp/regex.txt", "123\nabc\n456\nxyz")

    # Match digits
    result = shell.execute('grep "[0-9]" /tmp/regex.txt')
    assert "123" in result
    assert "456" in result
    assert "abc" not in result


def test_grep_empty_pattern(shell):
    """Test grep with empty pattern"""
    shell.fs.write_file("/tmp/test.txt", "line1\nline2")

    result = shell.execute('grep "" /tmp/test.txt')
    # Empty pattern should match all lines
    assert "line1" in result
    assert "line2" in result


# ============= SED TESTS =============


def test_sed_substitute(shell):
    """Test sed substitute command"""
    shell.fs.write_file("/tmp/text.txt", "old text old")

    # Replace first occurrence
    result = shell.execute('sed "s/old/new/" /tmp/text.txt')
    assert result == "new text old"

    # Replace all occurrences
    result = shell.execute('sed "s/old/new/g" /tmp/text.txt')
    assert result == "new text new"


def test_sed_delete_lines(shell):
    """Test sed delete lines"""
    shell.fs.write_file("/tmp/lines.txt", "1\n2\n3\n4\n5")

    # Delete first line
    result = shell.execute('sed "1d" /tmp/lines.txt')
    assert "1" not in result
    assert "2" in result

    # Delete range
    result = shell.execute('sed "2,4d" /tmp/lines.txt')
    assert result == "1\n5"


def test_sed_print_lines(shell):
    """Test sed -n with print"""
    shell.fs.write_file("/tmp/data.txt", "a\nb\nc\nd")

    # Print specific line
    result = shell.execute('sed -n "2p" /tmp/data.txt')
    assert result == "b"

    # Print range
    result = shell.execute('sed -n "2,3p" /tmp/data.txt')
    assert result == "b\nc"


def test_sed_multiple_commands(shell):
    """Test sed with multiple commands"""
    shell.fs.write_file("/tmp/test.txt", "foo bar baz")

    result = shell.execute('sed -e "s/foo/FOO/" -e "s/baz/BAZ/" /tmp/test.txt')
    assert result == "FOO bar BAZ"


def test_sed_with_delimiter(shell):
    """Test sed with different delimiters"""
    shell.fs.write_file("/tmp/paths.txt", "/usr/bin/test")

    # Using different delimiter to avoid escaping slashes
    result = shell.execute('sed "s|/usr|/opt|g" /tmp/paths.txt')
    assert result == "/opt/bin/test"


# ============= HEAD TESTS =============


def test_head_default(shell):
    """Test head default behavior (10 lines)"""
    content = "\n".join([str(i) for i in range(20)])
    shell.fs.write_file("/tmp/numbers.txt", content)

    result = shell.execute("head /tmp/numbers.txt")
    lines = result.strip().split("\n")
    assert len(lines) == 10
    assert lines[0] == "0"
    assert lines[9] == "9"


def test_head_n_option(shell):
    """Test head -n option"""
    shell.fs.write_file("/tmp/test.txt", "1\n2\n3\n4\n5")

    result = shell.execute("head -n 3 /tmp/test.txt")
    assert result == "1\n2\n3"

    # Negative n (all but last 2 lines)
    result = shell.execute("head -n -2 /tmp/test.txt")
    assert result == "1\n2\n3"


def test_head_empty_file(shell):
    """Test head with empty file"""
    shell.fs.write_file("/tmp/empty.txt", "")

    result = shell.execute("head /tmp/empty.txt")
    assert result == ""


def test_head_fewer_lines(shell):
    """Test head when file has fewer lines than requested"""
    shell.fs.write_file("/tmp/short.txt", "1\n2\n3")

    result = shell.execute("head -n 10 /tmp/short.txt")
    assert result == "1\n2\n3"


# ============= TAIL TESTS =============


def test_tail_default(shell):
    """Test tail default behavior (10 lines)"""
    content = "\n".join([str(i) for i in range(20)])
    shell.fs.write_file("/tmp/numbers.txt", content)

    result = shell.execute("tail /tmp/numbers.txt")
    lines = result.strip().split("\n")
    assert len(lines) == 10
    assert lines[0] == "10"
    assert lines[9] == "19"


def test_tail_n_option(shell):
    """Test tail -n option"""
    shell.fs.write_file("/tmp/test.txt", "1\n2\n3\n4\n5")

    result = shell.execute("tail -n 3 /tmp/test.txt")
    assert result == "3\n4\n5"

    # With + prefix (from line N to end)
    result = shell.execute("tail -n +3 /tmp/test.txt")
    assert result == "3\n4\n5"


def test_tail_empty_file(shell):
    """Test tail with empty file"""
    shell.fs.write_file("/tmp/empty.txt", "")

    result = shell.execute("tail /tmp/empty.txt")
    assert result == ""


# ============= SORT TESTS =============


def test_sort_alphabetical(shell):
    """Test sort alphabetical"""
    shell.fs.write_file("/tmp/words.txt", "zebra\napple\nbanana")

    result = shell.execute("sort /tmp/words.txt")
    assert result == "apple\nbanana\nzebra"


def test_sort_numeric(shell):
    """Test sort -n numeric"""
    shell.fs.write_file("/tmp/numbers.txt", "100\n20\n3")

    # Without -n, sorts alphabetically
    result = shell.execute("sort /tmp/numbers.txt")
    assert result == "100\n20\n3"

    # With -n, sorts numerically
    result = shell.execute("sort -n /tmp/numbers.txt")
    assert result == "3\n20\n100"


def test_sort_reverse(shell):
    """Test sort -r reverse"""
    shell.fs.write_file("/tmp/data.txt", "a\nb\nc")

    result = shell.execute("sort -r /tmp/data.txt")
    assert result == "c\nb\na"


def test_sort_unique(shell):
    """Test sort -u unique"""
    shell.fs.write_file("/tmp/dups.txt", "b\na\nb\nc\na")

    result = shell.execute("sort -u /tmp/dups.txt")
    assert result == "a\nb\nc"


def test_sort_empty_lines(shell):
    """Test sort with empty lines"""
    shell.fs.write_file("/tmp/empty_lines.txt", "b\n\na\n\nc")

    result = shell.execute("sort /tmp/empty_lines.txt")
    # Empty lines should sort first
    lines = result.split("\n")
    assert lines[0] == ""
    assert lines[1] == ""


# ============= UNIQ TESTS =============


def test_uniq_remove_duplicates(shell):
    """Test uniq removing consecutive duplicates"""
    shell.fs.write_file("/tmp/dups.txt", "a\na\nb\nb\nb\nc")

    result = shell.execute("uniq /tmp/dups.txt")
    assert result == "a\nb\nc"


def test_uniq_count(shell):
    """Test uniq -c count occurrences"""
    shell.fs.write_file("/tmp/data.txt", "a\na\na\nb\nb\nc")

    result = shell.execute("uniq -c /tmp/data.txt")
    assert "3 a" in result or "      3 a" in result
    assert "2 b" in result or "      2 b" in result
    assert "1 c" in result or "      1 c" in result


def test_uniq_duplicate_only(shell):
    """Test uniq -d show only duplicates"""
    shell.fs.write_file("/tmp/mixed.txt", "unique\ndup\ndup\nalso_unique")

    result = shell.execute("uniq -d /tmp/mixed.txt")
    assert result == "dup"


def test_uniq_unique_only(shell):
    """Test uniq -u show only unique lines"""
    shell.fs.write_file("/tmp/mixed.txt", "unique\ndup\ndup\nalso_unique")

    result = shell.execute("uniq -u /tmp/mixed.txt")
    assert "unique" in result
    assert "also_unique" in result
    assert "dup" not in result


def test_uniq_non_consecutive(shell):
    """Test uniq with non-consecutive duplicates"""
    shell.fs.write_file("/tmp/data.txt", "a\nb\na")

    # uniq only removes consecutive duplicates
    result = shell.execute("uniq /tmp/data.txt")
    assert result == "a\nb\na"

    # Need to sort first to remove all duplicates
    result = shell.execute("sort /tmp/data.txt | uniq")
    assert result == "a\nb"


# ============= WC TESTS =============


def test_wc_all_counts(shell):
    """Test wc showing all counts"""
    shell.fs.write_file("/tmp/test.txt", "hello world\ntest line\n")

    result = shell.execute("wc /tmp/test.txt")
    # Should show lines, words, bytes
    parts = result.split()
    assert "2" in parts  # 2 lines
    assert "4" in parts  # 4 words
    assert "22" in parts  # 22 bytes


def test_wc_lines_only(shell):
    """Test wc -l lines only"""
    shell.fs.write_file("/tmp/lines.txt", "1\n2\n3\n4\n5")

    result = shell.execute("wc -l /tmp/lines.txt")
    assert "5" in result


def test_wc_words_only(shell):
    """Test wc -w words only"""
    shell.fs.write_file("/tmp/words.txt", "one two three\nfour five")

    result = shell.execute("wc -w /tmp/words.txt")
    assert "5" in result


def test_wc_bytes_only(shell):
    """Test wc -c bytes only"""
    shell.fs.write_file("/tmp/bytes.txt", "12345")

    result = shell.execute("wc -c /tmp/bytes.txt")
    assert "5" in result


def test_wc_empty_file(shell):
    """Test wc with empty file"""
    shell.fs.write_file("/tmp/empty.txt", "")

    result = shell.execute("wc /tmp/empty.txt")
    assert "0" in result  # Should show 0 for all counts


def test_wc_stdin(shell):
    """Test wc with stdin"""
    shell.fs.write_file("/tmp/input.txt", "line 1\nline 2\nline 3")

    result = shell.execute("wc < /tmp/input.txt")
    assert "3" in result  # 3 lines
    assert "6" in result  # 6 words


# ============= DIFF TESTS =============


def test_diff_identical_files(shell):
    """Test diff with identical files"""
    shell.fs.write_file("/tmp/file1.txt", "same content")
    shell.fs.write_file("/tmp/file2.txt", "same content")

    result = shell.execute("diff /tmp/file1.txt /tmp/file2.txt")
    assert result == ""


def test_diff_different_files(shell):
    """Test diff with different files"""
    shell.fs.write_file("/tmp/old.txt", "line 1\nline 2\nline 3")
    shell.fs.write_file("/tmp/new.txt", "line 1\nmodified 2\nline 3")

    result = shell.execute("diff /tmp/old.txt /tmp/new.txt")
    assert "line 2" in result
    assert "modified 2" in result


def test_diff_unified_format(shell):
    """Test diff -u unified format"""
    shell.fs.write_file("/tmp/a.txt", "old")
    shell.fs.write_file("/tmp/b.txt", "new")

    result = shell.execute("diff -u /tmp/a.txt /tmp/b.txt")
    assert "---" in result
    assert "+++" in result
    assert "-old" in result
    assert "+new" in result


def test_diff_ignore_whitespace(shell):
    """Test diff -w ignore whitespace"""
    shell.fs.write_file("/tmp/spaces.txt", "a  b  c")
    shell.fs.write_file("/tmp/single.txt", "a b c")

    result = shell.execute("diff -w /tmp/spaces.txt /tmp/single.txt")
    assert result == ""


# ============= PATCH TESTS =============


def test_patch_apply_simple(shell):
    """Test applying a simple patch"""
    shell.fs.write_file("/tmp/original.txt", "line 1\nold line\nline 3")

    patch = """--- original.txt
+++ modified.txt
@@ -1,3 +1,3 @@
 line 1
-old line
+new line
 line 3"""
    shell.fs.write_file("/tmp/fix.patch", patch)

    result = shell.execute("patch /tmp/original.txt < /tmp/fix.patch")
    assert "patching file" in result

    content = shell.fs.read_file("/tmp/original.txt")
    assert "new line" in content
    assert "old line" not in content


def test_patch_reverse(shell):
    """Test patch -R reverse"""
    shell.fs.write_file("/tmp/file.txt", "new version")

    patch = """--- a.txt
+++ b.txt
@@ -1 +1 @@
-old version
+new version"""
    shell.fs.write_file("/tmp/changes.patch", patch)

    shell.execute("patch -R /tmp/file.txt < /tmp/changes.patch")

    content = shell.fs.read_file("/tmp/file.txt")
    assert content == "old version"


# ============= EDGE CASES =============


def test_nonexistent_file_handling(shell):
    """Test commands with non-existent files"""
    # Each command should handle gracefully
    assert (
        "No such file" in shell.execute('grep "test" /tmp/nonexistent.txt')
        or shell.execute('grep "test" /tmp/nonexistent.txt') == ""
    )

    assert (
        "No such file" in shell.execute('sed "s/a/b/" /tmp/nonexistent.txt')
        or shell.execute('sed "s/a/b/" /tmp/nonexistent.txt') == ""
    )

    assert (
        "No such file" in shell.execute('awk "{print}" /tmp/nonexistent.txt')
        or shell.execute('awk "{print}" /tmp/nonexistent.txt') == ""
    )


def test_very_long_lines(shell):
    """Test commands with very long lines"""
    long_line = "a" * 10000
    shell.fs.write_file("/tmp/long.txt", long_line)

    # Commands should handle long lines
    result = shell.execute("wc -c /tmp/long.txt")
    assert "10000" in result

    result = shell.execute("head -n 1 /tmp/long.txt")
    assert len(result) == 10000


def test_binary_content_handling(shell):
    """Test commands with binary-like content"""
    # Create file with special characters
    content = "line1\x00\x01\x02\nline2"
    shell.fs.write_file("/tmp/binary.txt", content)

    # Commands should handle binary content gracefully
    result = shell.execute("wc -l /tmp/binary.txt")
    assert "2" in result  # Should still count lines


def test_unicode_content(shell):
    """Test commands with Unicode content"""
    shell.fs.write_file("/tmp/unicode.txt", "Hello 世界\nПривет мир\n🌍🌎🌏")

    # Commands should handle Unicode
    result = shell.execute('grep "世界" /tmp/unicode.txt')
    assert "Hello 世界" in result

    result = shell.execute("wc -l /tmp/unicode.txt")
    assert "3" in result

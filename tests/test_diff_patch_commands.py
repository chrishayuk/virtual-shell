"""
tests/test_diff_patch_commands.py - Tests for diff and patch commands
"""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter


@pytest.fixture
def shell():
    """Create a shell instance for testing"""
    shell = ShellInterpreter()
    shell.execute("mkdir -p /tmp")
    return shell


def test_diff_basic(shell):
    """Test basic diff functionality"""
    # Create two files
    shell.fs.write_file("/tmp/file1.txt", "Line 1\nLine 2\nLine 3")
    shell.fs.write_file("/tmp/file2.txt", "Line 1\nLine 2 modified\nLine 3")

    # Get diff
    result = shell.execute("diff /tmp/file1.txt /tmp/file2.txt")
    assert "Line 2" in result
    assert "Line 2 modified" in result


def test_diff_unified_format(shell):
    """Test diff -u unified format"""
    # Create two files
    shell.fs.write_file("/tmp/old.txt", "foo\nbar\nbaz")
    shell.fs.write_file("/tmp/new.txt", "foo\nBAR\nbaz")

    # Get unified diff
    result = shell.execute("diff -u /tmp/old.txt /tmp/new.txt")
    assert "---" in result
    assert "+++" in result
    assert "-bar" in result
    assert "+BAR" in result


def test_diff_context_format(shell):
    """Test diff -c context format"""
    # Create two files
    shell.fs.write_file("/tmp/a.txt", "1\n2\n3\n4\n5")
    shell.fs.write_file("/tmp/b.txt", "1\n2\nX\n4\n5")

    # Get context diff
    result = shell.execute("diff -c /tmp/a.txt /tmp/b.txt")
    assert "***" in result
    assert "---" in result


def test_diff_brief_mode(shell):
    """Test diff -q brief mode"""
    # Create identical files
    shell.fs.write_file("/tmp/same1.txt", "content")
    shell.fs.write_file("/tmp/same2.txt", "content")

    # Should report no difference
    result = shell.execute("diff -q /tmp/same1.txt /tmp/same2.txt")
    assert result == ""

    # Create different files
    shell.fs.write_file("/tmp/diff1.txt", "content1")
    shell.fs.write_file("/tmp/diff2.txt", "content2")

    # Should report difference
    result = shell.execute("diff -q /tmp/diff1.txt /tmp/diff2.txt")
    assert "differ" in result


def test_diff_ignore_case(shell):
    """Test diff -i ignore case"""
    # Create files with case differences
    shell.fs.write_file("/tmp/lower.txt", "hello world")
    shell.fs.write_file("/tmp/upper.txt", "HELLO WORLD")

    # With -i, should show no differences
    result = shell.execute("diff -i /tmp/lower.txt /tmp/upper.txt")
    assert result == ""


def test_diff_ignore_whitespace(shell):
    """Test diff -w ignore all whitespace"""
    # Create files with whitespace differences
    shell.fs.write_file("/tmp/spaces.txt", "hello   world")
    shell.fs.write_file("/tmp/tabs.txt", "hello\tworld")

    # With -w, should show no differences
    result = shell.execute("diff -w /tmp/spaces.txt /tmp/tabs.txt")
    assert result == ""


def test_diff_side_by_side(shell):
    """Test diff --side-by-side format"""
    # Create two files
    shell.fs.write_file("/tmp/left.txt", "A\nB\nC")
    shell.fs.write_file("/tmp/right.txt", "A\nX\nC")

    # Get side-by-side diff
    result = shell.execute("diff --side-by-side /tmp/left.txt /tmp/right.txt")
    assert "|" in result or "<" in result or ">" in result


def test_patch_apply_unified(shell):
    """Test applying a unified diff patch"""
    # Create original file
    shell.fs.write_file("/tmp/original.txt", "Line 1\nLine 2\nLine 3")

    # Create patch
    patch_content = """--- /tmp/original.txt
+++ /tmp/modified.txt
@@ -1,3 +1,3 @@
 Line 1
-Line 2
+Line 2 modified
 Line 3"""
    shell.fs.write_file("/tmp/changes.patch", patch_content)

    # Apply patch
    result = shell.execute("patch /tmp/original.txt < /tmp/changes.patch")
    assert "patching file" in result

    # Verify file was patched
    content = shell.fs.read_file("/tmp/original.txt")
    assert "Line 2 modified" in content


def test_patch_reverse(shell):
    """Test patch -R reverse patch"""
    # Create file
    shell.fs.write_file("/tmp/file.txt", "NEW")

    # Create patch that changes OLD to NEW
    patch_content = """--- a.txt
+++ b.txt
@@ -1 +1 @@
-OLD
+NEW"""
    shell.fs.write_file("/tmp/forward.patch", patch_content)

    # Apply reverse patch (should change NEW to OLD)
    shell.execute("patch -R /tmp/file.txt < /tmp/forward.patch")

    content = shell.fs.read_file("/tmp/file.txt")
    assert content == "OLD"


def test_patch_dry_run(shell):
    """Test patch --dry-run"""
    # Create file
    shell.fs.write_file("/tmp/test.txt", "original")

    # Create patch
    patch_content = """--- test.txt
+++ test.txt
@@ -1 +1 @@
-original
+modified"""
    shell.fs.write_file("/tmp/test.patch", patch_content)

    # Dry run shouldn't modify file
    result = shell.execute("patch --dry-run /tmp/test.txt < /tmp/test.patch")
    assert "would be patched" in result or "patching file" in result

    # File should be unchanged
    content = shell.fs.read_file("/tmp/test.txt")
    assert content == "original"


def test_patch_with_backup(shell):
    """Test patch -b backup creation"""
    # Create file
    shell.fs.write_file("/tmp/data.txt", "old content")

    # Create patch
    patch_content = """--- data.txt
+++ data.txt
@@ -1 +1 @@
-old content
+new content"""
    shell.fs.write_file("/tmp/update.patch", patch_content)

    # Apply patch with backup
    shell.execute("patch -b /tmp/data.txt < /tmp/update.patch")

    # Check new content
    assert shell.fs.read_file("/tmp/data.txt") == "new content"

    # Check backup exists
    assert shell.fs.read_file("/tmp/data.txt.orig") == "old content"


def test_patch_input_file_option(shell):
    """Test patch -i input file option"""
    # Create file
    shell.fs.write_file("/tmp/target.txt", "foo")

    # Create patch file
    patch_content = """--- target.txt
+++ target.txt
@@ -1 +1 @@
-foo
+bar"""
    shell.fs.write_file("/tmp/changes.patch", patch_content)

    # Apply patch with -i
    shell.execute("patch -i /tmp/changes.patch /tmp/target.txt")

    content = shell.fs.read_file("/tmp/target.txt")
    assert content == "bar"


def test_diff_and_patch_workflow(shell):
    """Test complete diff and patch workflow"""
    # Create original and modified versions
    shell.fs.write_file("/tmp/v1.txt", "Feature A: disabled\nFeature B: enabled")
    shell.fs.write_file("/tmp/v2.txt", "Feature A: enabled\nFeature B: enabled")

    # Create patch
    shell.execute("diff -u /tmp/v1.txt /tmp/v2.txt > /tmp/features.patch")

    # Apply patch to a copy of v1
    shell.execute("cp /tmp/v1.txt /tmp/v1_copy.txt")
    shell.execute("patch /tmp/v1_copy.txt < /tmp/features.patch")

    # v1_copy should now match v2
    v1_copy = shell.fs.read_file("/tmp/v1_copy.txt")
    v2 = shell.fs.read_file("/tmp/v2.txt")
    assert v1_copy == v2


def test_patch_normal_diff_format(shell):
    """Test patch with normal diff format"""
    # Create file
    shell.fs.write_file("/tmp/normal.txt", "line1\nline2\nline3")

    # Create normal format patch
    patch_content = """2c2
< line2
---
> line2 changed"""
    shell.fs.write_file("/tmp/normal.patch", patch_content)

    # Apply patch
    shell.execute("patch /tmp/normal.txt < /tmp/normal.patch")

    content = shell.fs.read_file("/tmp/normal.txt")
    assert "line2 changed" in content

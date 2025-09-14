"""
tests/commands/text/test_patch_command.py - Tests for patch command
"""

import pytest
from tests.dummy_shell import DummyShell
from chuk_virtual_shell.commands.text.patch import PatchCommand


@pytest.fixture
def patch_setup():
    """Set up patch command with test files"""
    shell = DummyShell({})
    cmd = PatchCommand(shell)

    # Create original file
    shell.create_file("original.txt", "Line 1\nLine 2\nLine 3\nLine 4")

    # Create a unified diff patch
    unified_patch = """--- original.txt
+++ modified.txt
@@ -1,4 +1,5 @@
 Line 1
-Line 2
+Line 2 modified
 Line 3
 Line 4
+Line 5"""
    shell.create_file("unified.patch", unified_patch)

    # Create a normal diff patch
    normal_patch = """2c2
< Line 2
---
> Line 2 modified
4a5
> Line 5"""
    shell.create_file("normal.patch", normal_patch)

    return shell, cmd


def test_patch_no_input():
    """Test patch with no input"""
    shell = DummyShell({})
    cmd = PatchCommand(shell)

    result = cmd.execute([])
    assert "no patch input" in result


def test_patch_file_not_found(patch_setup):
    """Test patch with non-existent patch file"""
    shell, cmd = patch_setup

    result = cmd.execute(["-i", "nonexistent.patch"])
    assert "No such file or directory" in result


def test_patch_unified_format(patch_setup):
    """Test applying a unified diff patch"""
    shell, cmd = patch_setup

    # Apply patch using -i option
    result = cmd.execute(["-i", "unified.patch", "original.txt"])
    assert "patching file original.txt" in result

    # Check the result
    content = shell.fs.read_file("original.txt")
    assert "Line 2 modified" in content
    assert "Line 5" in content
    assert "Line 2\n" not in content


def test_patch_normal_format(patch_setup):
    """Test applying a normal diff patch"""
    shell, cmd = patch_setup

    # Set up stdin buffer for patch
    shell._stdin_buffer = shell.fs.read_file("normal.patch")

    result = cmd.execute(["original.txt"])
    assert "patching file original.txt" in result

    # Check the result
    content = shell.fs.read_file("original.txt")
    assert "Line 2 modified" in content
    assert "Line 5" in content


def test_patch_reverse(patch_setup):
    """Test reversing a patch"""
    shell, cmd = patch_setup

    # First apply the patch
    shell._stdin_buffer = shell.fs.read_file("unified.patch")
    cmd.execute(["original.txt"])

    # Now reverse it
    shell._stdin_buffer = shell.fs.read_file("unified.patch")
    result = cmd.execute(["-R", "original.txt"])
    assert "patching file original.txt" in result

    # Should be back to original
    content = shell.fs.read_file("original.txt")
    assert content == "Line 1\nLine 2\nLine 3\nLine 4"


def test_patch_backup(patch_setup):
    """Test patch with backup option"""
    shell, cmd = patch_setup

    original_content = shell.fs.read_file("original.txt")

    # Apply patch with backup
    shell._stdin_buffer = shell.fs.read_file("unified.patch")
    result = cmd.execute(["-b", "original.txt"])
    assert "patching file original.txt" in result

    # Check backup was created
    backup_content = shell.fs.read_file("original.txt.orig")
    assert backup_content == original_content

    # Check file was patched
    new_content = shell.fs.read_file("original.txt")
    assert "Line 2 modified" in new_content


def test_patch_output_file(patch_setup):
    """Test patch with output file option"""
    shell, cmd = patch_setup

    # Apply patch to different output file
    shell._stdin_buffer = shell.fs.read_file("unified.patch")
    result = cmd.execute(["-o", "output.txt", "original.txt"])
    assert "patching file original.txt to output.txt" in result

    # Original should be unchanged
    original = shell.fs.read_file("original.txt")
    assert "Line 2\n" in original
    assert "Line 5" not in original

    # Output should have changes
    output = shell.fs.read_file("output.txt")
    assert "Line 2 modified" in output
    assert "Line 5" in output


def test_patch_dry_run(patch_setup):
    """Test patch with dry-run option"""
    shell, cmd = patch_setup

    original_content = shell.fs.read_file("original.txt")

    # Do a dry run
    shell._stdin_buffer = shell.fs.read_file("unified.patch")
    result = cmd.execute(["--dry-run", "original.txt"])
    assert "checking file" in result
    assert "Hunk #1 succeeded" in result

    # File should be unchanged
    new_content = shell.fs.read_file("original.txt")
    assert new_content == original_content


def test_patch_strip_level(patch_setup):
    """Test patch with strip level option"""
    shell, cmd = patch_setup

    # Create a patch with path components
    path_patch = """--- a/src/original.txt
+++ b/src/original.txt
@@ -1,4 +1,4 @@
 Line 1
-Line 2
+Line 2 modified
 Line 3
 Line 4"""

    shell._stdin_buffer = path_patch

    # Apply with strip level 2 (removes a/src/ or b/src/)
    result = cmd.execute(["-p", "2", "original.txt"])
    assert "patching file original.txt" in result

    content = shell.fs.read_file("original.txt")
    assert "Line 2 modified" in content


def test_patch_new_file():
    """Test patch creating a new file"""
    shell = DummyShell({})
    cmd = PatchCommand(shell)

    # Patch that creates a new file
    new_file_patch = """--- /dev/null
+++ newfile.txt
@@ -0,0 +1,3 @@
+New Line 1
+New Line 2
+New Line 3"""

    shell._stdin_buffer = new_file_patch
    result = cmd.execute([])
    assert "patching file newfile.txt" in result

    # Check new file was created
    content = shell.fs.read_file("newfile.txt")
    assert content == "New Line 1\nNew Line 2\nNew Line 3"


def test_patch_multiple_hunks():
    """Test patch with multiple hunks"""
    shell = DummyShell({})
    cmd = PatchCommand(shell)

    shell.create_file("multi.txt", "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6")

    multi_patch = """--- multi.txt
+++ multi.txt
@@ -1,3 +1,3 @@
 Line 1
-Line 2
+Line 2 modified
 Line 3
@@ -4,3 +4,4 @@
 Line 4
 Line 5
-Line 6
+Line 6 modified
+Line 7"""

    shell._stdin_buffer = multi_patch
    result = cmd.execute(["multi.txt"])
    assert "patching file multi.txt" in result

    content = shell.fs.read_file("multi.txt")
    assert "Line 2 modified" in content
    assert "Line 6 modified" in content
    assert "Line 7" in content

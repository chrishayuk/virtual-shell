"""Tests for the tree command."""

import pytest
from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.commands.navigation.tree import TreeCommand


@pytest.fixture
def shell():
    """Create a shell instance for testing."""
    return ShellInterpreter()


class TestTreeCommand:
    """Test cases for the tree command."""

    def test_tree_empty_directory(self, shell):
        """Test tree on empty directory."""
        tree_cmd = TreeCommand(shell)
        shell.fs.mkdir("/empty")

        result = tree_cmd.execute(["/empty"])
        assert "/empty" in result
        assert "0 directories, 0 files" in result

    def test_tree_simple_structure(self, shell):
        """Test tree with simple directory structure."""
        tree_cmd = TreeCommand(shell)

        # Create structure
        shell.fs.mkdir("/test")
        shell.fs.touch("/test/file1.txt")
        shell.fs.touch("/test/file2.txt")
        shell.fs.mkdir("/test/subdir")
        shell.fs.touch("/test/subdir/file3.txt")

        result = tree_cmd.execute(["/test"])
        assert "├── file1.txt" in result
        assert "├── file2.txt" in result
        assert "└── subdir" in result  # subdir is last, so uses └──
        assert "    └── file3.txt" in result  # Indentation continues with spaces
        assert "1 directories, 3 files" in result

    def test_tree_current_directory(self, shell):
        """Test tree with no arguments (current directory)."""
        tree_cmd = TreeCommand(shell)

        # Create files in current directory
        shell.fs.touch("file1.txt")
        shell.fs.mkdir("dir1")

        result = tree_cmd.execute([])
        assert "file1.txt" in result
        assert "dir1" in result

    def test_tree_directories_only(self, shell):
        """Test tree with -d flag (directories only)."""
        tree_cmd = TreeCommand(shell)

        shell.fs.mkdir("/test")
        shell.fs.mkdir("/test/dir1")
        shell.fs.mkdir("/test/dir2")
        shell.fs.touch("/test/file.txt")
        shell.fs.mkdir("/test/dir1/subdir")

        result = tree_cmd.execute(["-d", "/test"])
        assert "dir1" in result
        assert "dir2" in result
        assert "subdir" in result
        assert "file.txt" not in result
        assert "3 directories" in result
        assert "files" not in result  # Should not mention files when -d is used

    def test_tree_max_depth(self, shell):
        """Test tree with -L flag (max depth)."""
        tree_cmd = TreeCommand(shell)

        # Create deep structure
        shell.fs.mkdir("/test")
        shell.fs.mkdir("/test/level1")
        shell.fs.mkdir("/test/level1/level2")
        shell.fs.mkdir("/test/level1/level2/level3")
        shell.fs.touch("/test/level1/level2/level3/deep.txt")

        # Limit to 2 levels
        result = tree_cmd.execute(["-L", "2", "/test"])
        assert "level1" in result
        assert "level2" in result
        assert "level3" not in result
        assert "deep.txt" not in result

    def test_tree_show_hidden(self, shell):
        """Test tree with -a flag (show hidden files)."""
        tree_cmd = TreeCommand(shell)

        shell.fs.mkdir("/test")
        shell.fs.touch("/test/.hidden")
        shell.fs.touch("/test/visible.txt")
        shell.fs.mkdir("/test/.hiddendir")

        # Without -a
        result = tree_cmd.execute(["/test"])
        assert ".hidden" not in result
        assert "visible.txt" in result
        assert ".hiddendir" not in result

        # With -a
        result = tree_cmd.execute(["-a", "/test"])
        assert ".hidden" in result
        assert "visible.txt" in result
        assert ".hiddendir" in result

    def test_tree_full_path(self, shell):
        """Test tree with -f flag (full path)."""
        tree_cmd = TreeCommand(shell)

        shell.fs.mkdir("/test")
        shell.fs.mkdir("/test/subdir")
        shell.fs.touch("/test/subdir/file.txt")

        result = tree_cmd.execute(["-f", "/test"])
        assert "/test/subdir" in result
        assert "/test/subdir/file.txt" in result

    def test_tree_ignore_pattern(self, shell):
        """Test tree with -I flag (ignore pattern)."""
        tree_cmd = TreeCommand(shell)

        shell.fs.mkdir("/test")
        shell.fs.touch("/test/file.txt")
        shell.fs.touch("/test/file.pyc")
        shell.fs.touch("/test/data.json")
        shell.fs.touch("/test/cache.pyc")

        result = tree_cmd.execute(["-I", "*.pyc", "/test"])
        assert "file.txt" in result
        assert "data.json" in result
        assert "file.pyc" not in result
        assert "cache.pyc" not in result

    def test_tree_dirs_first(self, shell):
        """Test tree with --dirsfirst flag."""
        tree_cmd = TreeCommand(shell)

        shell.fs.mkdir("/test")
        shell.fs.touch("/test/aaa.txt")
        shell.fs.mkdir("/test/zzz_dir")
        shell.fs.touch("/test/bbb.txt")

        result = tree_cmd.execute(["--dirsfirst", "/test"])
        lines = result.split("\n")

        # Find positions of items
        dir_pos = next(i for i, line in enumerate(lines) if "zzz_dir" in line)
        aaa_pos = next(i for i, line in enumerate(lines) if "aaa.txt" in line)

        # Directory should come before file even though 'z' > 'a'
        assert dir_pos < aaa_pos

    def test_tree_multiple_directories(self, shell):
        """Test tree with multiple directory arguments."""
        tree_cmd = TreeCommand(shell)

        shell.fs.mkdir("/dir1")
        shell.fs.touch("/dir1/file1.txt")
        shell.fs.mkdir("/dir2")
        shell.fs.touch("/dir2/file2.txt")

        result = tree_cmd.execute(["/dir1", "/dir2"])
        assert "/dir1" in result
        assert "file1.txt" in result
        assert "/dir2" in result
        assert "file2.txt" in result

    def test_tree_nonexistent_directory(self, shell):
        """Test tree with non-existent directory."""
        tree_cmd = TreeCommand(shell)

        result = tree_cmd.execute(["/nonexistent"])
        assert "No such file or directory" in result

    def test_tree_file_instead_of_directory(self, shell):
        """Test tree on a file instead of directory."""
        tree_cmd = TreeCommand(shell)
        shell.fs.touch("/test.txt")

        result = tree_cmd.execute(["/test.txt"])
        assert "Not a directory" in result

    def test_tree_invalid_level(self, shell):
        """Test tree with invalid -L argument."""
        tree_cmd = TreeCommand(shell)

        result = tree_cmd.execute(["-L", "abc", "/"])
        assert "must be numeric" in result

    def test_tree_missing_level_argument(self, shell):
        """Test tree with -L but no level specified."""
        tree_cmd = TreeCommand(shell)

        result = tree_cmd.execute(["-L"])
        assert "requires an argument" in result

    def test_tree_invalid_option(self, shell):
        """Test tree with invalid option."""
        tree_cmd = TreeCommand(shell)

        result = tree_cmd.execute(["-x", "/"])
        assert "invalid option" in result

    def test_tree_last_item_branch(self, shell):
        """Test that last item uses └── instead of ├──."""
        tree_cmd = TreeCommand(shell)

        shell.fs.mkdir("/test")
        shell.fs.touch("/test/first.txt")
        shell.fs.touch("/test/last.txt")

        result = tree_cmd.execute(["/test"])
        lines = result.split("\n")

        # First item should use ├──
        first_line = next(line for line in lines if "first.txt" in line)
        assert "├──" in first_line

        # Last item should use └──
        last_line = next(line for line in lines if "last.txt" in line)
        assert "└──" in last_line

    def test_tree_complex_structure(self, shell):
        """Test tree with complex nested structure."""
        tree_cmd = TreeCommand(shell)

        # Create complex structure
        shell.fs.mkdir("/project")
        shell.fs.mkdir("/project/src")
        shell.fs.mkdir("/project/src/models")
        shell.fs.mkdir("/project/src/views")
        shell.fs.mkdir("/project/tests")
        shell.fs.mkdir("/project/docs")
        shell.fs.touch("/project/README.md")
        shell.fs.touch("/project/src/main.py")
        shell.fs.touch("/project/src/models/user.py")
        shell.fs.touch("/project/src/views/home.py")
        shell.fs.touch("/project/tests/test_main.py")

        result = tree_cmd.execute(["/project"])

        # Verify structure
        assert "├── README.md" in result
        assert "├── docs" in result
        assert "├── src" in result
        assert "│   ├── main.py" in result
        assert "│   ├── models" in result
        assert "│   │   └── user.py" in result
        assert "│   └── views" in result
        assert "│       └── home.py" in result
        assert "└── tests" in result
        assert "    └── test_main.py" in result
        assert "5 directories, 5 files" in result

import pytest
from chuk_virtual_shell.commands.filesystem.find import FindCommand
from tests.dummy_shell import DummyShell


@pytest.fixture
def dummy_fs_structure():
    """
    Create a dummy filesystem structure with files and directories at various depths:

    /
    ├── home/
    │   └── user/
    │       ├── doc.txt
    │       ├── notes.md
    │       └── projects/
    │           ├── project1/
    │           │   ├── README.md
    │           │   └── main.py
    │           └── project2/
    │               ├── README.md
    │               └── config.json
    ├── tmp/
    │   ├── cache.tmp
    │   └── .hidden_file
    └── var/
        └── log/
            └── system.log
    """
    return {
        "/": {"home": {}, "tmp": {}, "var": {}},
        "/home": {"user": {}},
        "/home/user": {
            "doc.txt": "Document content",
            "notes.md": "Notes content",
            "projects": {},
        },
        "/home/user/projects": {"project1": {}, "project2": {}},
        "/home/user/projects/project1": {
            "README.md": "Project 1 readme",
            "main.py": "print('Hello')",
        },
        "/home/user/projects/project2": {
            "README.md": "Project 2 readme",
            "config.json": '{"key": "value"}',
        },
        "/tmp": {"cache.tmp": "temp data", ".hidden_file": "hidden content"},
        "/var": {"log": {}},
        "/var/log": {"system.log": "log entries"},
        # Individual file entries
        "/home/user/doc.txt": "Document content",
        "/home/user/notes.md": "Notes content",
        "/home/user/projects/project1/README.md": "Project 1 readme",
        "/home/user/projects/project1/main.py": "print('Hello')",
        "/home/user/projects/project2/README.md": "Project 2 readme",
        "/home/user/projects/project2/config.json": '{"key": "value"}',
        "/tmp/cache.tmp": "temp data",
        "/tmp/.hidden_file": "hidden content",
        "/var/log/system.log": "log entries",
    }


@pytest.fixture
def find_command(dummy_fs_structure):
    """Create a FindCommand with a dummy shell using the dummy filesystem."""
    dummy_shell = DummyShell(dummy_fs_structure)
    dummy_shell.fs.current_directory = "/home/user"
    dummy_shell.environ = {"PWD": "/home/user"}

    # Ensure find/search methods are available for tests
    if not hasattr(dummy_shell.fs, "find"):
        # Add a simple implementation of find that returns all paths
        def find_impl(path, recursive=True):
            results = []
            # Get all keys from dummy_fs_structure that start with the path
            for key in dummy_fs_structure.keys():
                if key.startswith(path):
                    if key != path:  # Don't include the path itself
                        if (
                            recursive or "/" not in key[len(path) + 1 :]
                        ):  # Check depth if not recursive
                            results.append(key)
            return results

        dummy_shell.fs.find = find_impl

    return FindCommand(shell_context=dummy_shell)


def test_find_no_options(find_command):
    """
    Test find with no options - should list all files and directories under current directory.
    """
    output = find_command.execute([])

    # Output should include all paths under /home/user
    assert "/home/user/doc.txt" in output
    assert "/home/user/notes.md" in output
    assert "/home/user/projects" in output
    assert "/home/user/projects/project1" in output
    assert "/home/user/projects/project1/README.md" in output

    # Should not include files outside /home/user
    assert "/tmp/cache.tmp" not in output


def test_find_with_path(find_command):
    """
    Test find with a specific path - should list all files and directories under that path.
    """
    output = find_command.execute(["/tmp"])

    # Output should include all paths under /tmp
    assert "/tmp/cache.tmp" in output
    assert "/tmp/.hidden_file" in output

    # Should not include files outside /tmp
    assert "/home/user/doc.txt" not in output


def test_find_name_pattern(find_command):
    """
    Test find with -name option to filter by name pattern.
    """
    output = find_command.execute(["-name", "*.md"])

    # Output should include only .md files
    assert "notes.md" in output
    assert "README.md" in output

    # Should not include non-.md files
    assert "doc.txt" not in output
    assert "main.py" not in output


def test_find_type_filter(find_command):
    """
    Test find with -type option to filter by file type (d=directory, f=file).
    """
    # Test finding only directories
    output_dirs = find_command.execute(["-type", "d"])
    lines = output_dirs.splitlines()

    # Should include directories
    assert any("projects" in line for line in lines)
    assert any("project1" in line for line in lines)
    assert any("project2" in line for line in lines)

    # Should not include files
    assert not any("doc.txt" in line for line in lines)
    assert not any("README.md" in line for line in lines)

    # Test finding only files
    output_files = find_command.execute(["-type", "f"])
    lines = output_files.splitlines()

    # Should include files
    assert any("doc.txt" in line for line in lines)
    assert any("notes.md" in line for line in lines)
    assert any("README.md" in line for line in lines)

    # Should not include directories
    assert not any(line.endswith("projects") for line in lines)
    assert not any(line.endswith("project1") for line in lines)


def test_find_maxdepth(find_command):
    """
    Test find with -maxdepth option to limit recursion depth.
    """
    # With maxdepth=1, should only show immediate children
    output = find_command.execute(["-maxdepth", "1"])
    lines = output.splitlines()

    # Should include immediate children
    assert any("doc.txt" in line for line in lines)
    assert any("notes.md" in line for line in lines)
    assert any("projects" in line for line in lines)

    # Should not include deeper nested files
    assert not any("project1" in line for line in lines)
    assert not any("README.md" in line for line in lines)


def test_find_multiple_paths(find_command):
    """
    Test find with multiple starting paths.
    """
    output = find_command.execute(["/tmp", "/var"])

    # Output should include files from both /tmp and /var
    assert "/tmp/cache.tmp" in output
    assert "/var/log/system.log" in output

    # Should not include files from other directories
    assert "/home/user/doc.txt" not in output


def test_find_combination(find_command):
    """
    Test find with a combination of options.
    """
    output = find_command.execute(["/home", "-name", "README.md", "-type", "f"])

    # Output should include only README.md files (basenames)
    assert "README.md" in output

    # Should not include other files or directories
    assert "main.py" not in output
    assert "projects" not in output
    assert "doc.txt" not in output


def test_find_non_existent(find_command):
    """
    Test find with a non-existent path.
    """
    output = find_command.execute(["/nonexistent"])

    # Fix: check for lowercase expected text.
    assert (
        "no such file or directory" in output.lower()
        or "cannot access" in output.lower()
    )

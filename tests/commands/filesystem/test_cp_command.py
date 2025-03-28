# # tests/chuk_virtual_shell/commands/filesystem/test_cp_command.py
# import pytest
# from chuk_virtual_shell.commands.filesystem.copy_command import CpCommand
# from chuk_virtual_shell.shell_interpreter import ShellInterpreter
# import os

# @pytest.fixture
# def cp_command():
#     # Create a real shell interpreter using the "memory" provider.
#     shell = ShellInterpreter(fs_provider="memory")
#     # Ensure we're at the root directory.
#     shell.fs.current_directory = "/"
#     # Pre-populate the filesystem:
#     # Create file /file1 with content, and directory /dir.
#     shell.fs.write_file("/file1", "Hello World")
#     shell.fs.mkdir("/dir")
#     # Create the CpCommand using the shell context.
#     command = CpCommand(shell_context=shell)
#     return command

# def test_cp_single_file(cp_command):
#     # Test copying a single file from /file1 to /file2.
#     output = cp_command.execute(["file1", "file2"])
#     assert output == ""
#     # Verify that /file2 now exists and its content matches /file1.
#     content = cp_command.shell.fs.read_file("file2")
#     assert content == "Hello World"

# def test_cp_multiple_files(cp_command):
#     # Create an extra file /file3.
#     cp_command.shell.fs.write_file("/file3", "Another file")
#     # Copy file1 and file3 into directory /dir.
#     output = cp_command.execute(["file1", "file3", "dir"])
#     # Expect no error output.
#     assert output == ""
#     # Verify that the files were copied into /dir with their original names.
#     file1_dest = os.path.join("dir", "file1")
#     file3_dest = os.path.join("dir", "file3")
#     assert cp_command.shell.fs.read_file(file1_dest) == "Hello World"
#     assert cp_command.shell.fs.read_file(file3_dest) == "Another file"

# def test_cp_non_existent(cp_command):
#     # Attempt to copy a non-existent file.
#     output = cp_command.execute(["nonexistent", "dest"])
#     expected = "cp: nonexistent: No such file"
#     assert output == expected

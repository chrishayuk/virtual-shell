# debug/check_shell_initializes.py
from chuk_virtual_shell.shell_interpreter import ShellInterpreter

shell = ShellInterpreter()
print("Shell initialized")
print(shell.prompt())
result = shell.execute("ls /")
print(result)
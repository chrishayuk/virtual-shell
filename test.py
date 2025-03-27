# test.py
from shell_interpreter import ShellInterpreter

shell = ShellInterpreter()
print("Shell initialized")
print(shell.prompt())
result = shell.execute("ls /")
print(result)
# tests/sandbox/test_environment_loader.py
# imports
from chuk_virtual_shell.sandbox.loader.environment_loader import load_environment


def test_load_environment_with_values():
    config = {
        "environment": {
            "HOME": "/env_test",
            "PATH": "/usr/bin",
            "USER": "env_user",
            "CUSTOM": "custom_value",
        }
    }
    env = load_environment(config)
    assert env["HOME"] == "/env_test"
    assert env["CUSTOM"] == "custom_value"
    # Check that default value for SHELL is provided.
    assert env["SHELL"] == "/bin/pyodide-shell"


def test_load_environment_defaults():
    # With no environment section, expect defaults.
    config = {"name": "empty"}
    env = load_environment(config)
    # Check a few defaults.
    assert env["HOME"] == "/sandbox"
    assert env["SHELL"] == "/bin/pyodide-shell"

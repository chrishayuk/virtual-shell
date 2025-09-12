#!/usr/bin/env python3
"""
Simple test runner for virtual shell examples.

This script provides a quick way to test that the virtual shell
is working correctly by running key example scripts.
"""

import sys
import time
from pathlib import Path

# Add project root to path
# Script is now in examples/commands, so go up two levels to get project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.script_runner import ScriptRunner


def run_example(shell, runner, script_name, description):
    """Run a single example script.

    Args:
        shell: Shell interpreter instance
        runner: Script runner instance
        script_name: Name of the script file
        description: Description of what the script tests

    Returns:
        True if successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Script: {script_name}")
    print("-" * 60)

    try:
        # Find the script
        script_paths = [
            f"examples/{script_name}",
            f"examples/commands/{script_name}",
            f"examples/commands/filesystem/{script_name}",
            f"examples/commands/navigation/{script_name}",
            f"examples/commands/text/{script_name}",
            f"examples/commands/system/{script_name}",
            f"examples/commands/environment/{script_name}",
        ]

        script_path = None
        for path in script_paths:
            full_path = project_root / path
            if full_path.exists():
                script_path = path
                break

        if not script_path:
            print(f"❌ Script not found: {script_name}")
            return False

        # Load script content
        with open(project_root / script_path, "r") as f:
            content = f.read()

        # Copy to virtual filesystem
        virtual_path = f"/tmp/{script_name}"
        shell.fs.write_file(virtual_path, content)

        # Run the script
        start_time = time.time()

        if script_name.endswith(".sh"):
            output = runner.run_script(virtual_path)
        elif script_name.endswith(".py"):
            output = shell.execute(f"python {virtual_path}")
        else:
            print(f"❌ Unknown script type: {script_name}")
            return False

        execution_time = time.time() - start_time

        # Check success
        if output:
            # Show first 300 characters of output
            preview = output[:300] + "..." if len(output) > 300 else output
            print(f"✅ SUCCESS ({execution_time:.2f}s)")
            print(f"Output preview: {preview}")
            return True
        else:
            print(f"✅ SUCCESS ({execution_time:.2f}s) - No output")
            return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 70)
    print("VIRTUAL SHELL EXAMPLE TESTS")
    print("=" * 70)
    print("\nThis will run key example scripts to verify the virtual shell")
    print("is working correctly.\n")

    # Initialize shell
    print("Initializing virtual shell...")
    try:
        config_path = project_root / "config" / "default.yaml"
        if config_path.exists():
            shell = ShellInterpreter(sandbox_yaml=str(config_path))
        else:
            shell = ShellInterpreter()
        runner = ScriptRunner(shell)
        print("✅ Virtual shell initialized\n")
    except Exception as e:
        print(f"❌ Failed to initialize shell: {e}")
        return 1

    # Define test scripts
    test_scripts = [
        # Basic examples
        ("hello_world.sh", "Basic shell script execution"),
        ("hello_world.py", "Python script execution"),
        ("file_operations.sh", "File system operations"),
        ("text_processing.sh", "Text processing commands"),
        # Command category demos
        ("working_commands_demo.sh", "Comprehensive working commands"),
        ("navigation_simple_demo.sh", "Navigation commands (cd, pwd, ls)"),
        ("environment_demo.sh", "Environment variables (env, export)"),
        ("system_demo.sh", "System commands (whoami, uptime, etc)"),
    ]

    # Run tests
    results = []
    for script_name, description in test_scripts:
        success = run_example(shell, runner, script_name, description)
        results.append((script_name, description, success))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for _, _, success in results if success)
    failed = total - passed

    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed} ({passed*100/total:.0f}%)")
    print(f"Failed: {failed} ({failed*100/total:.0f}%)")

    print("\nDetailed Results:")
    for script_name, description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {description}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Virtual shell is working correctly")
        return 0
    else:
        print(f"\n⚠️ {failed} test(s) failed")
        print("Please review the failures above")
        return 1


if __name__ == "__main__":
    sys.exit(main())

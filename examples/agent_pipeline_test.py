#!/usr/bin/env python3
"""
Test agent pipelines and advanced features.
"""

from chuk_virtual_shell.shell_interpreter import ShellInterpreter
import time


def test_agent_pipelines():
    """Test agent pipeline functionality"""

    # Create shell instance
    shell = ShellInterpreter()

    print("=== Agent Pipeline Test ===\n")

    # Setup directories and agents
    shell.execute("mkdir -p /agents")
    shell.execute("mkdir -p /data")

    # Create multiple specialized agents
    analyzer_agent = """#!agent
name: analyzer
model: gpt-3.5-turbo
system_prompt: Analyze input and extract key information
tools: [wc, grep, sort]
input: stdin
output: stdout
temperature: 0.3
"""

    formatter_agent = """#!agent
name: formatter
model: gpt-3.5-turbo
system_prompt: Format analysis results into clean output
input: stdin
output: stdout
temperature: 0.5
"""

    shell.fs.write_file("/agents/analyzer.agent", analyzer_agent)
    shell.fs.write_file("/agents/formatter.agent", formatter_agent)
    print("✓ Created analyzer and formatter agents\n")

    # Create test data
    test_data = """Project Status Report
====================
Tasks Completed: 15
Tasks In Progress: 8
Tasks Pending: 12
Bugs Fixed: 23
New Features: 5
Code Reviews: 18"""

    shell.fs.write_file("/data/report.txt", test_data)
    print("✓ Created test data file\n")

    # Test 1: Single agent processing
    print("=== Test 1: Single Agent ===")
    print("Command: cat /data/report.txt | head -3")
    result = shell.execute("cat /data/report.txt | head -3")
    print(f"Result:\n{result}\n")

    # Test 2: Agent with file input
    print("=== Test 2: Agent with File Input ===")
    print(
        "Command: agent /agents/analyzer.agent -i /data/report.txt -o /data/analysis.txt"
    )
    result = shell.execute(
        "agent /agents/analyzer.agent -i /data/report.txt -o /data/analysis.txt"
    )
    print(f"Result: {result}")

    if shell.fs.exists("/data/analysis.txt"):
        analysis = shell.fs.read_file("/data/analysis.txt")
        print(f"Analysis output: {analysis[:200]}...\n")

    # Test 3: Multiple background agents
    print("=== Test 3: Multiple Background Agents ===")

    # Create different input files
    for i in range(3):
        shell.fs.write_file(
            f"/data/input{i}.txt", f"Test data {i}\nProcessing item {i}"
        )

    # Launch multiple agents in background
    for i in range(3):
        cmd = f"agent /agents/analyzer.agent -b -i /data/input{i}.txt -o /data/output{i}.txt"
        result = shell.execute(cmd)
        print(f"Launched: {result}")

    print("\nCurrent agent processes:")
    result = shell.execute("agent -l")
    print(result)

    # Test 4: Process lifecycle
    print("\n=== Test 4: Process Lifecycle ===")

    # Get list of processes
    processes = shell.agent_manager.list_processes()
    active_processes = [p for p in processes if p.is_active()]

    if active_processes:
        test_pid = active_processes[0].pid
        print(f"Testing with agent {test_pid}")

        # Check status
        print(f"\n1. Status of {test_pid}:")
        result = shell.execute(f"agent -s {test_pid}")
        print(result[:200] + "..." if len(result) > 200 else result)

        # Wait a bit for completion
        time.sleep(0.5)

        # Check status again
        print("\n2. Status after wait:")
        result = shell.execute(f"agent -s {test_pid}")
        if "No such agent" in result:
            print("Agent completed and was cleaned up")
        else:
            print(result[:200] + "..." if len(result) > 200 else result)

    # Test 5: Agent composition patterns
    print("\n=== Test 5: Composition Patterns ===")

    # Pattern 1: Sequential processing
    print("Pattern 1: Sequential processing")
    shell.fs.write_file("/data/numbers.txt", "5\n2\n8\n1\n9\n3")
    result = shell.execute("cat /data/numbers.txt | sort | head -3")
    print(f"Sorted numbers (top 3): {result}")

    # Pattern 2: Parallel with aggregation (simulated)
    print("\nPattern 2: Parallel processing simulation")
    print("Creating 3 data files...")
    for i in range(3):
        shell.fs.write_file(f"/data/dataset{i}.txt", f"Dataset {i}\nValue: {i * 10}")

    print("Processing each file with agent...")
    for i in range(3):
        shell.execute(
            f"agent /agents/analyzer.agent -i /data/dataset{i}.txt -o /data/result{i}.txt"
        )

    # Aggregate results
    print("Aggregating results...")
    all_results = []
    for i in range(3):
        if shell.fs.exists(f"/data/result{i}.txt"):
            content = shell.fs.read_file(f"/data/result{i}.txt")
            all_results.append(f"Result {i}: {content[:50]}...")

    if all_results:
        print("Aggregated outputs:")
        for r in all_results:
            print(f"  - {r}")

    # Test 6: Error handling
    print("\n=== Test 6: Error Handling ===")

    print("1. Non-existent agent file:")
    result = shell.execute("agent /agents/nonexistent.agent")
    print(f"   Result: {result}")

    print("\n2. Invalid agent definition:")
    shell.fs.write_file("/agents/invalid.agent", "not a valid agent file")
    result = shell.execute("agent /agents/invalid.agent")
    print(f"   Result: {result}")

    print("\n3. Kill non-existent process:")
    result = shell.execute("agent -k nonexistent_pid")
    print(f"   Result: {result}")

    # Final status
    print("\n=== Final Status ===")
    result = shell.execute("agent -l")
    print(f"Running agents: {result}")

    # Cleanup completed processes
    shell.agent_manager.cleanup_completed()
    result = shell.execute("agent -l")
    print(f"After cleanup: {result}")

    print("\n=== Pipeline Test Complete ===")
    print("Demonstrated:")
    print("  ✓ Single agent execution")
    print("  ✓ File-based I/O")
    print("  ✓ Multiple background agents")
    print("  ✓ Process lifecycle management")
    print("  ✓ Composition patterns")
    print("  ✓ Error handling")


def main():
    """Main entry point"""
    print("Starting Agent Pipeline Test...\n")
    test_agent_pipelines()


if __name__ == "__main__":
    main()

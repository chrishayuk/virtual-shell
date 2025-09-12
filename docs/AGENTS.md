# AI Agents as Shell Processes

The virtual shell now supports AI agents as first-class processes that can be executed, piped, and managed like any other shell command.

## Overview

AI agents are defined as special script files with the `.agent` extension and can:
- Run as foreground or background processes
- Accept input via stdin, files, or pipes
- Output to stdout, files, or pipes
- Be chained together in pipelines
- Maintain session or persistent memory
- Access shell commands as tools

## Agent Definition Format

Agent files use a YAML-based format with a special shebang:

```yaml
#!agent
name: my_agent
model: gpt-3.5-turbo
system_prompt: |
  You are a helpful assistant that...
  
tools:
  - ls
  - cat
  - grep
  
input: stdin
output: stdout
context_size: 4096
memory: session
temperature: 0.7
max_tokens: 1000
timeout: 30

environment:
  MY_VAR: value
```

### Fields

- **name**: Agent identifier
- **model**: LLM model to use (e.g., gpt-3.5-turbo, gpt-4, claude-3.5-sonnet)
- **system_prompt**: Instructions defining the agent's role and behavior
- **tools**: List of shell commands the agent can execute
- **input**: Input mode (stdin, file, socket, pipe)
- **output**: Output mode (stdout, file, socket, pipe)
- **context_size**: Maximum context window size
- **memory**: Memory persistence (none, session, persistent)
- **temperature**: LLM temperature (0.0-1.0)
- **max_tokens**: Maximum tokens in response
- **timeout**: Execution timeout in seconds
- **environment**: Environment variables for the agent

## Using Agents

### Basic Execution

```bash
# Run an agent
agent assistant.agent

# With input file
agent analyzer.agent -i data.txt

# With output file
agent coder.agent -o output.py

# With timeout
agent processor.agent -t 60
```

### Piping and Redirection

```bash
# Pipe input to agent
echo "Hello" | agent chat.agent

# Pipe from command
ls -la | agent analyzer.agent

# Chain agents in pipeline
cat data.csv | agent analyzer.agent | agent reporter.agent

# Redirect output
agent helper.agent < input.txt > output.txt
```

### Background Execution

```bash
# Run in background
agent monitor.agent -b

# Background with I/O
agent processor.agent -b -i input.txt -o result.txt
```

### Process Management

```bash
# List running agents
agent -l

# Show agent status
agent -s agent_1

# Kill an agent
agent -k agent_1
```

## Example Agents

### Assistant Agent
```yaml
#!agent
name: assistant
model: gpt-3.5-turbo
system_prompt: |
  You are a helpful AI assistant in a shell environment.
  Help users with file operations and answer questions.
tools:
  - ls
  - cat
  - mkdir
  - touch
input: stdin
output: stdout
memory: session
```

### Code Analyzer
```yaml
#!agent
name: code_analyzer
model: gpt-4
system_prompt: |
  Analyze code for quality, bugs, and improvements.
  Provide specific, actionable feedback.
tools:
  - cat
  - grep
  - python
input: stdin
output: stdout
temperature: 0.3
```

### System Monitor
```yaml
#!agent
name: monitor
model: gpt-3.5-turbo
system_prompt: |
  Monitor system resources and detect anomalies.
  Alert on issues and provide recommendations.
tools:
  - ls
  - df
  - du
  - ps
  - tail
input: stdin
output: stdout
memory: persistent
timeout: 300
```

## Agent Pipelines

Agents can be combined in powerful pipelines:

```bash
# Analyze and report
cat logs.txt | agent log_analyzer.agent | agent report_writer.agent > report.md

# Multi-stage processing
find . -name "*.py" | agent code_scanner.agent | agent security_checker.agent

# Parallel processing with aggregation
(agent analyzer1.agent < data1.txt &
 agent analyzer2.agent < data2.txt &
 wait) | agent aggregator.agent
```

## Memory Modes

### None
No memory between invocations. Each run is independent.

### Session
Memory persists during the shell session but is cleared when the shell exits.

### Persistent
Memory is saved to disk and persists across sessions. Stored in `/var/agent_memory/`.

## Tool Access

Agents can execute shell commands listed in their `tools` configuration:

```python
# Agent can use these tools internally
tools:
  - ls      # List files
  - cat     # Read files
  - grep    # Search text
  - echo    # Output text
  - python  # Run Python code
```

The agent receives tool results and can chain them together to accomplish complex tasks.

## Integration with chuk-llm

The agent system integrates with [chuk-llm](https://github.com/chrishayuk/chuk-llm) for LLM interactions:

- Supports multiple providers (OpenAI, Anthropic, Google, etc.)
- Automatic model discovery
- Streaming responses
- Function calling
- Configurable via environment variables

Set up your API keys:
```bash
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
```

## Implementation Details

### Architecture

1. **AgentDefinition**: Parses and validates agent configuration files
2. **AgentProcess**: Manages individual agent process lifecycle
3. **AgentProcessManager**: Orchestrates multiple agent processes
4. **AgentCommand**: Shell command interface for agent operations
5. **LLMInterface**: Handles LLM interactions via chuk-llm

### Process States

- **PENDING**: Process created but not started
- **RUNNING**: Actively executing
- **SUSPENDED**: Temporarily paused
- **COMPLETED**: Finished successfully
- **FAILED**: Terminated with error
- **TERMINATED**: Forcefully stopped

### File Structure

```
chuk_virtual_shell/
├── agents/
│   ├── __init__.py
│   ├── agent_definition.py    # Agent configuration parser
│   ├── agent_process.py       # Process management
│   └── llm_interface.py       # LLM integration
├── commands/
│   └── system/
│       └── agent.py           # Agent shell command
└── examples/
    └── agents/
        ├── assistant.agent
        ├── analyzer.agent
        ├── coder.agent
        └── monitor.agent
```

## Future Enhancements

- **Agent Communication**: Direct agent-to-agent messaging
- **Resource Limits**: CPU/memory quotas per agent
- **Agent Marketplace**: Share and discover agent definitions
- **Visual Pipeline Builder**: GUI for creating agent workflows
- **Distributed Execution**: Run agents across multiple machines
- **Event Triggers**: Launch agents on file changes or schedules
- **Custom Tools**: Plugin system for extending agent capabilities

## Conclusion

AI agents as shell processes bring the power of LLMs directly into the command line workflow. They can be composed, piped, and managed just like traditional Unix tools, enabling powerful AI-augmented automation and analysis pipelines.
# AI Agent Examples

This directory contains demonstrations of AI agents running as shell processes.

## Quick Start

### 1. Basic Agent Demo
```bash
# Run the clean demo (best for first-time users)
uv run python demo.py
```

This shows:
- ✅ AI agents responding to queries
- ✅ File I/O operations
- ✅ Background processes
- ✅ Process management

### 2. Multi-Agent Collaboration
```bash
# Run the software team simulation
uv run python examples/software_team_demo.py
```

Watch 6 specialized agents work together:
- Product Owner
- Tech Lead
- Backend Developer
- Frontend Developer
- QA Engineer
- DevOps Engineer

### 3. Agent Pipelines
```bash
# Run the collaboration demo
uv run python run_multi_agent.py
```

See agents:
- Communicate through pipes and files
- Execute in parallel
- Process data in pipelines
- Coordinate on complex tasks

## Prerequisites

### For Mock Mode (No API Key Required)
Just run the demos - they'll use simulated responses.

### For Real LLM Mode
1. Set up your API key in `.env`:
```bash
OPENAI_API_KEY=your_key_here
```

2. Install chuk-llm:
```bash
pip install chuk-llm
```

## Agent Definition Format

Agents are defined as YAML files with `#!agent` shebang:

```yaml
#!agent
name: my_agent
model: gpt-3.5-turbo
system_prompt: |
  You are a helpful assistant...
tools: [ls, cat, echo]
input: stdin
output: stdout
temperature: 0.7
```

## Example Commands

```bash
# Run a single agent
agent assistant.agent

# Pipe input to agent
echo "Hello" | agent chat.agent

# Chain agents
cat data.txt | agent analyzer.agent | agent reporter.agent

# Background execution
agent monitor.agent -b

# List running agents
agent -l

# Kill an agent
agent -k agent_1
```

## Demo Files

- `agent_clean_demo.py` - Basic demo with clean output
- `agent_real_llm_demo.py` - Demo with real LLM integration
- `multi_agent_collaboration.py` - Team collaboration scenario
- `software_team_demo.py` - Software development team simulation
- `agent_pipeline_test.py` - Pipeline and parallel execution tests

## Key Features Demonstrated

1. **Process Management**: Agents run with PIDs and can be managed like processes
2. **I/O Redirection**: Full support for pipes, input/output redirection
3. **Parallel Execution**: Multiple agents running simultaneously
4. **Communication**: Agents communicate via files and pipes
5. **Tool Access**: Agents can execute shell commands
6. **Memory**: Session and persistent memory options

## Troubleshooting

### Async Warnings
Some async cleanup warnings may appear at exit - these are harmless and don't affect functionality.

### API Rate Limits
If using real LLMs, be aware of rate limits. The demos include timeouts to prevent hanging.

### Background Processes
Background agents continue running after the demo. Use `agent -l` to list and `agent -k <pid>` to kill them.

## Learn More

- [Full Agent Documentation](../docs/AGENTS.md)
- [Agent Architecture](../chuk_virtual_shell/agents/README.md)
- [Creating Custom Agents](../docs/CUSTOM_AGENTS.md)
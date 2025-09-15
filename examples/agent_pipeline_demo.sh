#!/bin/bash
# Agent Pipeline Demo - Showcasing AI agents as shell processes

echo "=== AI Agent Pipeline Demo ==="
echo ""

# Create workspace
mkdir -p /workspace/code
mkdir -p /agents

# Create test data
cat > /workspace/data.csv << EOF
name,age,city
Alice,30,New York
Bob,25,Los Angeles
Charlie,35,Chicago
David,28,Boston
Eve,32,Seattle
EOF

cat > /workspace/code/example.py << 'EOF'
def process_data(filename):
    """Process CSV data and generate statistics"""
    import csv
    
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    total_age = sum(int(row['age']) for row in data)
    avg_age = total_age / len(data)
    
    cities = {row['city'] for row in data}
    
    return {
        'count': len(data),
        'average_age': avg_age,
        'unique_cities': len(cities)
    }

if __name__ == "__main__":
    result = process_data("/workspace/data.csv")
    print(f"Statistics: {result}")
EOF

# Create agents
cat > /agents/data_analyzer.agent << 'EOF'
#!agent
name: data_analyzer
model: gpt-3.5-turbo
system_prompt: |
  You are a data analysis agent. Analyze CSV data and provide insights.
  Focus on patterns, statistics, and actionable recommendations.
tools:
  - cat
  - wc
  - sort
  - uniq
  - head
input: stdin
output: stdout
temperature: 0.3
EOF

cat > /agents/code_reviewer.agent << 'EOF'
#!agent
name: code_reviewer
model: gpt-3.5-turbo
system_prompt: |
  You are a code review agent. Review Python code for:
  - Code quality and style
  - Potential bugs
  - Performance improvements
  - Best practices
  Be constructive and specific in your feedback.
tools:
  - cat
  - grep
  - python
input: stdin
output: stdout
temperature: 0.4
EOF

cat > /agents/report_generator.agent << 'EOF'
#!agent
name: report_generator
model: gpt-3.5-turbo
system_prompt: |
  You are a report generation agent. Create concise, well-formatted reports
  from analysis results. Use markdown formatting for clarity.
input: stdin
output: stdout
temperature: 0.5
EOF

echo "=== Demo 1: Simple Data Analysis ==="
echo "Command: cat /workspace/data.csv | agent /agents/data_analyzer.agent"
echo "---"
cat /workspace/data.csv | agent /agents/data_analyzer.agent
echo ""

echo "=== Demo 2: Code Review ==="
echo "Command: cat /workspace/code/example.py | agent /agents/code_reviewer.agent"
echo "---"
cat /workspace/code/example.py | agent /agents/code_reviewer.agent
echo ""

echo "=== Demo 3: Agent Pipeline ==="
echo "Command: cat /workspace/data.csv | agent /agents/data_analyzer.agent | agent /agents/report_generator.agent"
echo "---"
cat /workspace/data.csv | agent /agents/data_analyzer.agent | agent /agents/report_generator.agent
echo ""

echo "=== Demo 4: Background Processing ==="
echo "Starting background agent..."
agent /agents/data_analyzer.agent -b -i /workspace/data.csv -o /workspace/analysis.txt
echo ""

echo "=== Demo 5: List Running Agents ==="
agent -l
echo ""

echo "=== Demo 6: Parallel Processing with Agents ==="
echo "Processing multiple files in parallel..."

# Create more test files
echo "Sample log entry 1" > /workspace/log1.txt
echo "Error: Connection failed" > /workspace/log2.txt
echo "Warning: Low memory" > /workspace/log3.txt

# Process in parallel (simulated with background jobs)
agent /agents/data_analyzer.agent -b -i /workspace/log1.txt -o /workspace/result1.txt
agent /agents/data_analyzer.agent -b -i /workspace/log2.txt -o /workspace/result2.txt
agent /agents/data_analyzer.agent -b -i /workspace/log3.txt -o /workspace/result3.txt

echo "Agents processing in background..."
agent -l
echo ""

echo "=== Demo Complete ==="
echo "AI agents have been integrated as first-class shell processes!"
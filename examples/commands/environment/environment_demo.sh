#!/bin/bash

# Environment Commands Comprehensive Demo
# This script demonstrates all environment commands within the virtual shell

echo "=== ENVIRONMENT COMMANDS DEMO ==="
echo

# 1. ENV COMMAND - Display Environment Variables
echo "=== 1. ENV COMMAND ==="

echo "Display all environment variables:"
env

echo "Environment variables should show defaults like USER, HOME, PWD, etc."
echo

# 2. EXPORT COMMAND - Set Environment Variables
echo "=== 2. EXPORT COMMAND ==="

echo "Setting new environment variables:"
export TEST_VAR="Hello World"
export DEMO_PATH="/demo/path"
export DEMO_NUMBER=42
export DEMO_BOOL=true

echo "Variables set: TEST_VAR, DEMO_PATH, DEMO_NUMBER, DEMO_BOOL"
echo

echo "Verify new variables are set:"
env | grep -E "(TEST_VAR|DEMO_PATH|DEMO_NUMBER|DEMO_BOOL)"
echo

# 3. USING ENVIRONMENT VARIABLES
echo "=== 3. USING ENVIRONMENT VARIABLES ==="

echo "Display specific environment variables:"
echo "TEST_VAR is: $TEST_VAR"
echo "DEMO_PATH is: $DEMO_PATH" 
echo "DEMO_NUMBER is: $DEMO_NUMBER"
echo "DEMO_BOOL is: $DEMO_BOOL"
echo

echo "Using environment variables in commands:"
echo "Creating directory based on DEMO_PATH:"
mkdir -p "/tmp/${DEMO_PATH}"
echo "Directory created at: /tmp/${DEMO_PATH}"

echo "Creating file with environment variable content:"
echo "This is the content of TEST_VAR: $TEST_VAR" > /tmp/env_test.txt
echo "File created with environment variable content:"
cat /tmp/env_test.txt
echo

# 4. MODIFYING EXISTING VARIABLES
echo "=== 4. MODIFYING EXISTING VARIABLES ==="

echo "Current PATH variable:"
echo "PATH=$PATH"
echo

echo "Adding to PATH:"
export PATH="$PATH:/custom/bin"
echo "New PATH: $PATH"
echo

echo "Modifying PS1 (if it exists):"
export PS1="DEMO> "
echo "PS1 set to: $PS1"
echo

# 5. UNSETTING VARIABLES (using export with empty value)
echo "=== 5. MANAGING VARIABLES ==="

echo "Setting a temporary variable:"
export TEMP_VAR="temporary value"
echo "TEMP_VAR set to: $TEMP_VAR"

echo "Current environment shows TEMP_VAR:"
env | grep TEMP_VAR || echo "TEMP_VAR not found in env output"
echo

# 6. ENVIRONMENT VARIABLE TYPES DEMO
echo "=== 6. VARIABLE TYPES DEMO ==="

echo "Setting different types of values:"
export STRING_VAR="This is a string with spaces"
export NUMBER_VAR=123
export FLOAT_VAR=3.14159
export BOOLEAN_VAR=false
export PATH_VAR="/usr/local/bin:/usr/bin:/bin"
export COMMA_VAR="value1,value2,value3"

echo "Display all demo variables:"
env | grep -E "(STRING_VAR|NUMBER_VAR|FLOAT_VAR|BOOLEAN_VAR|PATH_VAR|COMMA_VAR)"
echo

# 7. USING VARIABLES IN FILE OPERATIONS
echo "=== 7. VARIABLES IN FILE OPERATIONS ==="

echo "Creating files using environment variables:"
echo "Content for number file" > "/tmp/file_${NUMBER_VAR}.txt"
echo "Content for boolean file" > "/tmp/config_${BOOLEAN_VAR}.txt"

echo "Files created:"
ls /tmp/file_*.txt /tmp/config_*.txt
echo

echo "Reading file content using variables:"
cat "/tmp/file_${NUMBER_VAR}.txt"
cat "/tmp/config_${BOOLEAN_VAR}.txt"
echo

# 8. CONDITIONAL OPERATIONS BASED ON ENVIRONMENT
echo "=== 8. CONDITIONAL ENVIRONMENT USAGE ==="

echo "Setting a configuration variable:"
export DEBUG_MODE=enabled
export LOG_LEVEL=info
export APP_ENV=development

echo "Using variables for conditional file creation:"
if [ "$DEBUG_MODE" = "enabled" ]; then
    echo "Debug mode is enabled" > /tmp/debug.log
    echo "Created debug.log because DEBUG_MODE=$DEBUG_MODE"
else
    echo "Debug mode is disabled"
fi

echo "Creating configuration based on LOG_LEVEL:"
echo "log_level=$LOG_LEVEL" > /tmp/app.conf
echo "debug_mode=$DEBUG_MODE" >> /tmp/app.conf
echo "environment=$APP_ENV" >> /tmp/app.conf

echo "Generated configuration file:"
cat /tmp/app.conf
echo

# 9. ENVIRONMENT VARIABLE SUBSTITUTION IN TEXT
echo "=== 9. VARIABLE SUBSTITUTION ==="

echo "Creating template file:"
echo "Welcome to the application!" > /tmp/template.txt
echo "Environment: \$APP_ENV" >> /tmp/template.txt
echo "Debug Mode: \$DEBUG_MODE" >> /tmp/template.txt
echo "Log Level: \$LOG_LEVEL" >> /tmp/template.txt

echo "Template file content:"
cat /tmp/template.txt
echo

echo "Process template with variable substitution (manual):"
sed "s/\$APP_ENV/$APP_ENV/g; s/\$DEBUG_MODE/$DEBUG_MODE/g; s/\$LOG_LEVEL/$LOG_LEVEL/g" /tmp/template.txt > /tmp/processed.txt

echo "Processed template:"
cat /tmp/processed.txt
echo

# 10. WORKING WITH SYSTEM ENVIRONMENT VARIABLES
echo "=== 10. SYSTEM ENVIRONMENT VARIABLES ==="

echo "Display common system variables:"
echo "USER: $USER"
echo "HOME: $HOME" 
echo "PWD: $PWD"
echo "PATH: $PATH"
echo

echo "Modify system-like variables:"
export USER="demo_user"
export HOME="/home/demo_user"

echo "Updated system variables:"
echo "USER: $USER"
echo "HOME: $HOME"
echo

# 11. ENVIRONMENT VARIABLES IN PYTHON INTEGRATION
echo "=== 11. PYTHON ENVIRONMENT INTEGRATION ==="

echo "Creating Python script that uses environment variables:"
echo "#!/usr/bin/env python3" > /tmp/env_python.py
echo "import os" >> /tmp/env_python.py
echo "print('Python Environment Variable Demo')" >> /tmp/env_python.py
echo "print(f'TEST_VAR: {os.environ.get(\"TEST_VAR\", \"Not set\")}')" >> /tmp/env_python.py
echo "print(f'DEBUG_MODE: {os.environ.get(\"DEBUG_MODE\", \"Not set\")}')" >> /tmp/env_python.py
echo "print(f'APP_ENV: {os.environ.get(\"APP_ENV\", \"Not set\")}')" >> /tmp/env_python.py
echo "print(f'PATH: {os.environ.get(\"PATH\", \"Not set\")}')" >> /tmp/env_python.py

echo "Running Python script with environment variables:"
python /tmp/env_python.py
echo

# 12. COMPLEX ENVIRONMENT SETUP
echo "=== 12. COMPLEX ENVIRONMENT SETUP ==="

echo "Setting up a complex application environment:"
export APP_NAME="VirtualShellApp"
export APP_VERSION="1.0.0"
export DATABASE_URL="sqlite:///app.db"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="super-secret-key-123"
export ALLOWED_HOSTS="localhost,127.0.0.1"
export DEBUG=true

echo "Application environment variables:"
env | grep -E "(APP_|DATABASE_|REDIS_|SECRET_|ALLOWED_|DEBUG)"
echo

echo "Creating application config file from environment:"
echo "# Application Configuration" > /tmp/app_config.ini
echo "[app]" >> /tmp/app_config.ini
echo "name = $APP_NAME" >> /tmp/app_config.ini
echo "version = $APP_VERSION" >> /tmp/app_config.ini
echo "debug = $DEBUG" >> /tmp/app_config.ini
echo "" >> /tmp/app_config.ini
echo "[database]" >> /tmp/app_config.ini
echo "url = $DATABASE_URL" >> /tmp/app_config.ini
echo "" >> /tmp/app_config.ini
echo "[security]" >> /tmp/app_config.ini
echo "secret_key = $SECRET_KEY" >> /tmp/app_config.ini
echo "allowed_hosts = $ALLOWED_HOSTS" >> /tmp/app_config.ini

echo "Generated application configuration:"
cat /tmp/app_config.ini
echo

# 13. FINAL ENVIRONMENT STATE
echo "=== 13. FINAL ENVIRONMENT STATE ==="

echo "Complete environment summary:"
echo "Total environment variables:"
env | wc -l

echo "Demo variables created in this session:"
env | grep -E "(TEST_|DEMO_|STRING_|NUMBER_|FLOAT_|BOOLEAN_|PATH_VAR|COMMA_|DEBUG_|LOG_|APP_|DATABASE_|REDIS_|SECRET_|ALLOWED_)"

echo "Files created using environment variables:"
ls -la /tmp/*.txt /tmp/*.log /tmp/*.config /tmp/*.ini /tmp/*.py | head -10

echo "=== ENVIRONMENT DEMO COMPLETE ==="
echo "Environment commands (env, export) demonstrated successfully!"
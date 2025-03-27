#!/bin/bash
# build_and_run.sh - Build and run the PyodideShell in a Docker container

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display progress
progress() {
  echo -e "${BLUE}[INFO]${NC} $1"
}

# Function to display success
success() {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Function to display errors
error() {
  echo -e "${RED}[ERROR]${NC} $1"
  exit 1
}

# Function to display warnings
warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
  error "Docker is not installed. Please install Docker first."
fi

# Build the Docker image
progress "Building PyodideShell Docker image..."
docker build -t pyodide-vshell .

if [ $? -ne 0 ]; then
  error "Failed to build Docker image."
fi

success "Docker image built successfully."

# Run the container
progress "Starting PyodideShell in Docker container..."
echo ""
docker run -it --rm \
  --name pyodide-vshell-instance \
  -v "$(pwd)/data:/app/data" \
  pyodide-vshell

# Cleanup after exit
if [ $? -eq 0 ]; then
  success "PyodideShell exited successfully."
else
  warning "PyodideShell exited with an error. Exit code: $?"
fi
// node_pyodide_shell.js
const { loadPyodide } = require("pyodide");
const readline = require('readline');
const readlineSync = require('readline-sync');
const fs = require('fs');
const path = require('path');

// Create a readline interface for interactive input/output
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Function to recursively load Python modules from directory
function loadPythonModules(pyodide, dir) {
  // Check if directory exists at the specified path
  if (!fs.existsSync(dir)) {
    // Try looking in the parent directory if running from pyodide-container
    const parentDir = path.join('..', dir);
    if (fs.existsSync(parentDir)) {
      console.log(`Directory ${dir} not found, using ${parentDir} instead`);
      dir = parentDir;
    } else {
      throw new Error(`Could not find Python modules directory at ${dir} or ${parentDir}`);
    }
  }

  // Create the base directory in Pyodide
  try {
    pyodide.runPython(`
import os
os.makedirs('./virtual_shell', exist_ok=True)
    `);
  } catch (e) {
    console.error(`Error creating base directory:`, e);
    throw e;
  }

  // Function to recursively process directories
  function processDirectory(currentDir, pyodidePath) {
    console.log(`Processing directory: ${currentDir} -> ${pyodidePath}`);
    
    // Create the directory in Pyodide
    pyodide.runPython(`
import os
os.makedirs('${pyodidePath}', exist_ok=True)
    `);
    
    const files = fs.readdirSync(currentDir);
    
    files.forEach(file => {
      const fullPath = path.join(currentDir, file);
      const pyodideFilePath = path.join(pyodidePath, file).replace(/\\/g, '/');
      
      if (fs.statSync(fullPath).isDirectory()) {
        // Process subdirectory
        processDirectory(fullPath, pyodideFilePath);
      } else if (file.endsWith('.py')) {
        try {
          // Read the Python file
          const content = fs.readFileSync(fullPath, 'utf8');
          
          // Use a safer method to get content into Python
          const base64Content = Buffer.from(content).toString('base64');
          
          pyodide.runPython(`
import os
import base64

# Ensure the directory exists
os.makedirs(os.path.dirname('${pyodideFilePath}'), exist_ok=True)

# Write the file content
with open('${pyodideFilePath}', 'w') as f:
    content = base64.b64decode('${base64Content}').decode('utf-8')
    f.write(content)
          `);
          
          console.log(`Loaded file: ${pyodideFilePath}`);
        } catch (e) {
          console.error(`Error loading ${fullPath}:`, e);
        }
      }
    });
  }
  
  // Start processing from the virtual_shell directory
  const baseDir = path.basename(dir);
  processDirectory(dir, `./${baseDir}`);
}

async function runPyodideShell() {
  console.log("Loading Pyodide... this may take a moment");
  
  // Load Pyodide
  const pyodide = await loadPyodide();
  console.log("Pyodide loaded successfully");
  
  // Set up Python path and environment
  await pyodide.runPythonAsync(`
    import sys
    import os
    
    # Make sure the current directory is in the path
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    
    # Also add virtual_shell specifically
    if './virtual_shell' not in sys.path:
        sys.path.insert(0, './virtual_shell')
    
    print("Initial sys.path:", sys.path)
    
    # Create any necessary directories
    os.makedirs('./virtual_shell', exist_ok=True)
    
    # Set up environment variables that might be needed
    os.environ['PYTHONPATH'] = './virtual_shell:' + os.environ.get('PYTHONPATH', '')
    os.environ['HOME'] = '/home/pyodide'
    os.environ['USER'] = 'pyodide'
  `);
  
  // Debug the filesystem structure first
  const vsPath = fs.existsSync('./virtual_shell') ? './virtual_shell' : 
                 fs.existsSync('../virtual_shell') ? '../virtual_shell' : null;
  
  if (!vsPath) {
    console.error("Could not find virtual_shell directory in either current or parent directory");
    process.exit(1);
  }
  
  console.log(`Found virtual_shell at ${vsPath}`);
  console.log(`Directory contents:`, fs.readdirSync(vsPath));
  
  // Check if it has any Python files
  const hasPyFiles = fs.readdirSync(vsPath, { recursive: true })
                       .some(file => file.endsWith('.py'));
  
  if (!hasPyFiles) {
    console.error("No Python files found in the virtual_shell directory");
    process.exit(1);
  }
  
  // Load Python files into Pyodide's virtual filesystem
  try {
    loadPythonModules(pyodide, vsPath);
    console.log("Python modules loaded");
    
    // Debug what was loaded
    pyodide.runPython(`
import os
import sys

print("Current working directory:", os.getcwd())
print("Files in virtual_shell:")
if os.path.exists('./virtual_shell'):
    for root, dirs, files in os.walk('./virtual_shell'):
        for file in files:
            print(os.path.join(root, file))
else:
    print("virtual_shell directory not found in Pyodide filesystem")

print("sys.path:", sys.path)
    `);
  } catch (e) {
    console.error("Error loading Python modules:", e);
    process.exit(1);
  }
  
  // Register a synchronous node input function for Pyodide
  pyodide.registerJsModule("nodepy", {
    input(prompt) {
      // This is a blocking synchronous call, which works for simple shells
      process.stdout.write(prompt);
      return readlineSync.question('');
    },
    print(text) {
      console.log(text);
    }
  });
  
  // Add the bridge to Python
  await pyodide.runPythonAsync(`
    # Set up a custom input function that uses Node.js
    import builtins
    import nodepy
    
    # Override the built-in input function
    def custom_input(prompt=""):
      return nodepy.input(prompt)
    
    # Replace the built-in input function
    builtins.input = custom_input
    
    # Also set up a print function that ensures output is flushed
    original_print = builtins.print
    def custom_print(*args, **kwargs):
      result = original_print(*args, **kwargs)
      import sys
      sys.stdout.flush()
      return result
      
    builtins.print = custom_print
  `);
  
  // Content for pyodide_main.py
  const pyodideMainContent = `"""
pyodide_main.py - Pyodide-compatible main entry point for PyodideShell
"""
import sys
import os
import json
from virtual_shell.shell_interpreter import ShellInterpreter
import nodepy  # Import the JS-registered module

def pyodide_main():
    """Run an interactive shell in the Pyodide environment"""
    print("Starting PyodideShell in Pyodide environment...")
    
    # Create shell interpreter with memory provider
    shell = ShellInterpreter()
    
    # Print provider info
    print(f"Using filesystem provider: {shell.fs.get_provider_name()}")
    
    # Synchronous shell loop for Pyodide
    while shell.running:
        # Print prompt
        prompt = shell.prompt()
        
        # Use the synchronous nodepy.input
        try:
            cmd_line = nodepy.input(prompt)
            
            # Handle empty command
            if not cmd_line:
                continue
            
            # Execute command and show result
            result = shell.execute(cmd_line)
            if result:
                print(result)
                
        except Exception as e:
            print(f"Error: {e}")
    
    print("Goodbye from PyodideShell!")

if __name__ == "__main__":
    pyodide_main()
`;

  // Create a pyodide-specific main.py file
  try {
    await pyodide.runPythonAsync(`
# Create a pyodide-compatible main.py file
with open('pyodide_main.py', 'w') as f:
    f.write("""${pyodideMainContent}""")
    
print("Created pyodide_main.py")

# Use it directly
try:
    print("Running pyodide_main.py...")
    from pyodide_main import pyodide_main
    pyodide_main()
except Exception as e:
    print(f"Error executing pyodide_main.py: {e}")
    import traceback
    traceback.print_exc()
    `);
  } catch (e) {
    console.error("Error running custom main script:", e);
    console.error(e.stack);
  } finally {
    rl.close();
  }
}

runPyodideShell();
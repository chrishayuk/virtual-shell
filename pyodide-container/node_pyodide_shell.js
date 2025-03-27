// node_pyodide_shell.js
const { loadPyodide } = require("pyodide");
const fs = require('fs');
const path = require('path');

// Function to recursively load Python modules into Pyodide
function loadPythonModules(pyodide, dir) {
  if (!fs.existsSync(dir)) {
    const parentDir = path.join('..', dir);
    if (fs.existsSync(parentDir)) {
      dir = parentDir;
    } else {
      throw new Error(`Could not find Python modules directory at ${dir} or ${parentDir}`);
    }
  }

  // Ensure "virtual_shell" directory exists in the Pyodide filesystem
  pyodide.runPython(`
import os
os.makedirs('./virtual_shell', exist_ok=True)
  `);

  // Recursively process a directory, copying .py files to the Pyodide FS
  function processDirectory(currentDir, pyodidePath) {
    pyodide.runPython(`
import os
os.makedirs('${pyodidePath}', exist_ok=True)
    `);

    const files = fs.readdirSync(currentDir);
    for (const file of files) {
      const fullPath = path.join(currentDir, file);
      const pyodideFilePath = path.join(pyodidePath, file).replace(/\\/g, '/');

      // Recurse into subdirectories
      if (fs.statSync(fullPath).isDirectory()) {
        processDirectory(fullPath, pyodideFilePath);
      }
      // Copy .py files
      else if (file.endsWith('.py')) {
        const content = fs.readFileSync(fullPath, 'utf8');
        const base64Content = Buffer.from(content).toString('base64');
        pyodide.runPython(`
import os, base64
os.makedirs(os.path.dirname('${pyodideFilePath}'), exist_ok=True)
with open('${pyodideFilePath}', 'w') as f:
    f.write(base64.b64decode('${base64Content}').decode('utf-8'))
        `);
      }
    }
  }

  const baseDir = path.basename(dir);
  processDirectory(dir, `./${baseDir}`);
}

async function runPyodideShell() {
  // Minimal console message
  console.log("Initializing Pyodide shell...");

  // Load Pyodide
  const pyodide = await loadPyodide();

  // Configure Python environment
  await pyodide.runPythonAsync(`
import sys, os

if '.' not in sys.path:
    sys.path.insert(0, '.')
if './virtual_shell' not in sys.path:
    sys.path.insert(0, './virtual_shell')

os.makedirs('./virtual_shell', exist_ok=True)

os.environ['PYTHONPATH'] = './virtual_shell:' + os.environ.get('PYTHONPATH','')
os.environ['HOME'] = '/home/pyodide'
os.environ['USER'] = 'pyodide'
`);

  // Locate and verify local virtual_shell directory
  const vsPath = fs.existsSync('./virtual_shell')
    ? './virtual_shell'
    : (fs.existsSync('../virtual_shell') ? '../virtual_shell' : null);

  if (!vsPath) {
    console.error("Error: could not find 'virtual_shell' in current or parent directory.");
    process.exit(1);
  }

  // Check if there are Python files
  const hasPyFiles = fs
    .readdirSync(vsPath, { recursive: true })
    .some(file => file.endsWith('.py'));
  if (!hasPyFiles) {
    console.error("Error: no Python files found in 'virtual_shell'.");
    process.exit(1);
  }

  // Load Python modules into Pyodide
  loadPythonModules(pyodide, vsPath);

  // Set up raw-mode input without printing a prompt from Node
  pyodide.registerJsModule("nodepy", {
    async input(_prompt) {
      return new Promise((resolve) => {
        let input = "";
        process.stdin.setRawMode(true);
        process.stdin.resume();
        process.stdin.setEncoding('utf8');
  
        function onData(char) {
          switch(char) {
            case "\r":
            case "\n":
              process.stdout.write("\n");
              process.stdin.setRawMode(false);
              process.stdin.pause();
              process.stdin.removeListener("data", onData);
              resolve(input);
              break;
            
            case "\u0003": // Ctrl+C
              process.stdout.write("^C\n");
              input = "";
              process.stdin.setRawMode(false);
              process.stdin.pause();
              process.stdin.removeListener("data", onData);
              resolve(input);
              break;
            
            case "\u007f": // Backspace
            case "\b":
              if (input.length > 0) {
                // Move cursor back, write space, move cursor back again
                process.stdout.write("\b \b");
                input = input.slice(0, -1);
              }
              break;
            
            default:
              // Printable characters
              if (char >= " " && char <= "~") {
                process.stdout.write(char);
                input += char;
              }
          }
        }
  
        process.stdin.on("data", onData);
      });
    },
    print(text) {
      console.log(text);
    }
  });
  
  // Override Python's built-in input/print with custom versions
  await pyodide.runPythonAsync(`
import builtins, sys, nodepy

def custom_input(prompt=""):
    return nodepy.input(prompt)
builtins.input = custom_input

orig_print = builtins.print
def custom_print(*args, **kwargs):
    r = orig_print(*args, **kwargs)
    sys.stdout.flush()
    return r
builtins.print = custom_print
`);

  // Minimal Python shell content (no debug prints)
  const pyodideMainContent = `"""
pyodide_main.py - Pyodide-compatible main entry point for PyodideShell
"""
import sys
import os
from virtual_shell.shell_interpreter import ShellInterpreter

def pyodide_main():
    # Minimal start message
    shell = ShellInterpreter()
    while shell.running:
        prompt = shell.prompt()
        try:
            cmd_line = input(prompt)
            if not cmd_line:
                continue
            result = shell.execute(cmd_line)
            if result:
                print(result)
        except Exception as e:
            print(f"Error: {e}")

    # Minimal exit message
    print("Goodbye from PyodideShell!")

if __name__ == "__main__":
    pyodide_main()
`;

  // Create pyodide_main.py inside Pyodide
  const escapedContent = JSON.stringify(pyodideMainContent);
  try {
    await pyodide.runPythonAsync(`
with open('pyodide_main.py', 'w') as f:
    f.write(${escapedContent})

try:
    from pyodide_main import pyodide_main
    pyodide_main()
except Exception as e:
    print(f"Error executing pyodide_main.py: {e}")
    import traceback
    traceback.print_exc()
`);
  } catch (err) {
    console.error("Failed to run Pyodide main script:", err);
  } finally {
    // Keep the Node process alive indefinitely
    await new Promise(() => {});
  }
}

// Start the shell
runPyodideShell();
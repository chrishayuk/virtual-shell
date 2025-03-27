// node_pyodide_shell.js
const { loadPyodide } = require("pyodide");
const fs = require('fs');
const path = require('path');

// Function to recursively load Python modules from directory
function loadPythonModules(pyodide, dir) {
  if (!fs.existsSync(dir)) {
    const parentDir = path.join('..', dir);
    if (fs.existsSync(parentDir)) {
      console.log(`Directory ${dir} not found, using ${parentDir} instead`);
      dir = parentDir;
    } else {
      throw new Error(`Could not find Python modules directory at ${dir} or ${parentDir}`);
    }
  }

  // Create the base directory in Pyodide
  pyodide.runPython(`
import os
os.makedirs('./virtual_shell', exist_ok=True)
  `);

  function processDirectory(currentDir, pyodidePath) {
    console.log(`Processing directory: ${currentDir} -> ${pyodidePath}`);

    pyodide.runPython(`
import os
os.makedirs('${pyodidePath}', exist_ok=True)
    `);

    const files = fs.readdirSync(currentDir);
    files.forEach(file => {
      const fullPath = path.join(currentDir, file);
      const pyodideFilePath = path.join(pyodidePath, file).replace(/\\/g, '/');

      if (fs.statSync(fullPath).isDirectory()) {
        // Recursively handle subdirectories
        processDirectory(fullPath, pyodideFilePath);
      } else if (file.endsWith('.py')) {
        const content = fs.readFileSync(fullPath, 'utf8');
        const base64Content = Buffer.from(content).toString('base64');

        pyodide.runPython(`
import os
import base64
os.makedirs(os.path.dirname('${pyodideFilePath}'), exist_ok=True)
with open('${pyodideFilePath}', 'w') as f:
    content = base64.b64decode('${base64Content}').decode('utf-8')
    f.write(content)
        `);

        console.log(`Loaded file: ${pyodideFilePath}`);
      }
    });
  }

  const baseDir = path.basename(dir);
  processDirectory(dir, `./${baseDir}`);
}

async function runPyodideShell() {
  console.log("Loading Pyodide... this may take a moment");
  const pyodide = await loadPyodide();
  console.log("Pyodide loaded successfully");

  // Set up Python path and environment
  await pyodide.runPythonAsync(`
    import sys
    import os
    if '.' not in sys.path:
        sys.path.insert(0, '.')
    if './virtual_shell' not in sys.path:
        sys.path.insert(0, './virtual_shell')
    print("Initial sys.path:", sys.path)
    os.makedirs('./virtual_shell', exist_ok=True)
    os.environ['PYTHONPATH'] = './virtual_shell:' + os.environ.get('PYTHONPATH', '')
    os.environ['HOME'] = '/home/pyodide'
    os.environ['USER'] = 'pyodide'
  `);

  // Locate the local "virtual_shell" directory to load
  const vsPath = fs.existsSync('./virtual_shell') 
               ? './virtual_shell' 
               : (fs.existsSync('../virtual_shell') ? '../virtual_shell' : null);

  if (!vsPath) {
    console.error("Could not find virtual_shell directory in either current or parent directory");
    process.exit(1);
  }

  console.log(`Found virtual_shell at ${vsPath}`);
  console.log(`Directory contents:`, fs.readdirSync(vsPath));

  // Check if we have .py files
  const hasPyFiles = fs.readdirSync(vsPath, { recursive: true })
                      .some(file => file.endsWith('.py'));
  if (!hasPyFiles) {
    console.error("No Python files found in the virtual_shell directory");
    process.exit(1);
  }

  // Copy local Python files into Pyodide FS
  try {
    loadPythonModules(pyodide, vsPath);
    console.log("Python modules loaded");
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

  // Register raw-mode input, but do NOT print the prompt here
  pyodide.registerJsModule("nodepy", {
    // Raw-mode input with live echo
    async input(_prompt) {
      // Let Python do the prompt printing; we skip it here.
      return new Promise((resolve) => {
        let input = "";
        process.stdin.setRawMode(true);
        process.stdin.resume();
        process.stdin.setEncoding('utf8');
        
        function onData(char) {
          if (char === "\r" || char === "\n") {
            process.stdout.write("\n");
            process.stdin.setRawMode(false);
            process.stdin.pause();
            process.stdin.removeListener("data", onData);
            resolve(input);
          } else if (char === "\u0003") {
            // Ctrl+C
            process.stdout.write("^C\n");
            // Decide how to handle. Let's just return empty string
            input = "";
            process.stdin.setRawMode(false);
            process.stdin.pause();
            process.stdin.removeListener("data", onData);
            resolve(input);
          } else {
            // Echo typed character
            process.stdout.write(char);
            input += char;
          }
        }
        
        process.stdin.on("data", onData);
      });
    },

    // Python's print ends up calling this
    print(text) {
      console.log(text);
    }
  });

  // Override Python's built-in input and print
  await pyodide.runPythonAsync(`
    import builtins
    import nodepy

    def custom_input(prompt=""):
      return nodepy.input(prompt)

    builtins.input = custom_input

    original_print = builtins.print
    def custom_print(*args, **kwargs):
      result = original_print(*args, **kwargs)
      import sys
      sys.stdout.flush()
      return result

    builtins.print = custom_print
  `);

  // Create and write pyodide_main.py
  const pyodideMainContent = `"""
pyodide_main.py - Pyodide-compatible main entry point for PyodideShell
"""
import sys
import os
from virtual_shell.shell_interpreter import ShellInterpreter

def pyodide_main():
    print("Starting PyodideShell in Pyodide environment...")
    shell = ShellInterpreter()
    print(f"Using filesystem provider: {shell.fs.get_provider_name()}")
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
    print("Goodbye from PyodideShell!")

if __name__ == "__main__":
    pyodide_main()
`;
  const escapedContent = JSON.stringify(pyodideMainContent);

  try {
    await pyodide.runPythonAsync(`
with open('pyodide_main.py', 'w') as f:
    f.write(${escapedContent})

print("Created pyodide_main.py")
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
    // Keep Node.js alive forever (until Ctrl+C) so it doesn’t exit
    await new Promise(() => {});
  }
}

runPyodideShell();

const { loadPyodide } = require("pyodide");
const fs = require("fs");
const path = require("path");

// Function to recursively load Python modules into Pyodide
function loadPythonModules(pyodide, dir) {
  if (!fs.existsSync(dir)) {
    const parentDir = path.join("..", dir);
    if (fs.existsSync(parentDir)) {
      dir = parentDir;
    } else {
      throw new Error(`Could not find Python modules directory at ${dir} or ${parentDir}`);
    }
  }

  // Ensure the target directory exists in the Pyodide filesystem
  pyodide.runPython(`
import os
os.makedirs('${"./" + path.basename(dir)}', exist_ok=True)
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
      const pyodideFilePath = path.join(pyodidePath, file).replace(/\\/g, "/");

      // Recurse into subdirectories
      if (fs.statSync(fullPath).isDirectory()) {
        processDirectory(fullPath, pyodideFilePath);
      }
      // Copy .py files
      else if (file.endsWith(".py")) {
        const content = fs.readFileSync(fullPath, "utf8");
        const base64Content = Buffer.from(content).toString("base64");
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

// New: Function to load a folder (non‑Python files) into Pyodide's FS.
function loadFolder(pyodide, folderPath, destPath) {
  if (!fs.existsSync(folderPath)) {
    throw new Error(`Folder ${folderPath} does not exist`);
  }

  // Create destination directory in Pyodide's FS.
  pyodide.runPython(`
import os
os.makedirs('${destPath}', exist_ok=True)
  `);

  const files = fs.readdirSync(folderPath);
  for (const file of files) {
    const fullPath = path.join(folderPath, file);
    const destFilePath = path.join(destPath, file).replace(/\\/g, "/");

    if (fs.statSync(fullPath).isDirectory()) {
      loadFolder(pyodide, fullPath, destFilePath);
    } else {
      // Read file content as UTF-8 text.
      const content = fs.readFileSync(fullPath, "utf8");
      const escapedContent = JSON.stringify(content); // properly escape newlines etc.
      pyodide.runPython(`
import os
os.makedirs(os.path.dirname('${destFilePath}'), exist_ok=True)
with open('${destFilePath}', 'w') as f:
    f.write(${escapedContent})
      `);
    }
  }
}

async function runPyodideShell() {
  console.log("Initializing Pyodide shell...");

  // Load Pyodide.
  const pyodide = await loadPyodide();

  // Load PyYAML package.
  console.log("Loading pyyaml");
  await pyodide.loadPackage("pyyaml");
  console.log("Loaded pyyaml");

  // Load micropip.
  console.log("Loading micropip");
  await pyodide.loadPackage("micropip");
  console.log("Loaded micropip");

  console.log("Installing typing-extensions==4.12.2 from PyPI (with constraints)");
  await pyodide.runPythonAsync(`
  import micropip
  await micropip.install("typing-extensions==4.12.2")
  `);
  console.log("Installed typing-extensions");
  

  // Install the external package 'chuk_virtual_fs' from PyPI.
  console.log("Installing chuk_virtual_fs from PyPI");
  await pyodide.runPythonAsync(`
import micropip
await micropip.install("chuk_virtual_fs")
  `);
  console.log("Installed chuk_virtual_fs");

  // Install anyio via micropip.
  console.log("Installing anyio from PyPI");
  await pyodide.runPythonAsync(`
import micropip
await micropip.install("anyio")
  `);
  console.log("Installed anyio");

  // Install ssl via micropip.
  console.log("Installing ssl from PyPI");
  await pyodide.runPythonAsync(`
import micropip
await micropip.install("ssl")
  `);
  console.log("Installed ssl");

// Install chuk_mcp via micropip with keep_going=True.
console.log("Installing chuk_mcp from PyPI (ignoring missing wheels)");
await pyodide.runPythonAsync(`
import micropip
await micropip.install("chuk_mcp", keep_going=True)
`);
console.log("Installed chuk_mcp (with keep_going=True)");


  // Configure Python environment: add chuk_virtual_shell to sys.path and set environment variables.
  await pyodide.runPythonAsync(`
import sys, os
if './chuk_virtual_shell' not in sys.path:
    sys.path.insert(0, './chuk_virtual_shell')
os.environ['PYTHONPATH'] = './chuk_virtual_shell:' + os.environ.get('PYTHONPATH','')
os.environ['HOME'] = '/home/pyodide'
os.environ['USER'] = 'pyodide'
os.environ['PYODIDE_SANDBOX'] = 'ai_sandbox'
  `);

  // Locate and verify local chuk_virtual_shell directory.
  const vsShellPath = fs.existsSync("./chuk_virtual_shell")
    ? "./chuk_virtual_shell"
    : (fs.existsSync("../chuk_virtual_shell") ? "../chuk_virtual_shell" : null);
  if (!vsShellPath) {
    console.error("Error: could not find 'chuk_virtual_shell' in current or parent directory.");
    process.exit(1);
  }

  // Load chuk_virtual_shell into Pyodide's filesystem.
  loadPythonModules(pyodide, vsShellPath);

  // NEW: Load configuration folder into Pyodide's filesystem.
  // Assume your config folder (with ai_sandbox.yaml) is located at pyodide-container/config.
  const configFolderPath = path.join(__dirname, "config"); // Adjust if needed.
  console.log(`Loading configuration files from ${configFolderPath} into /home/pyodide/config...`);
  loadFolder(pyodide, configFolderPath, "/home/pyodide/config");

  // Set up raw-mode input without printing a prompt from Node.
  pyodide.registerJsModule("nodepy", {
    async input(_prompt) {
      return new Promise((resolve) => {
        let input = "";
        process.stdin.setRawMode(true);
        process.stdin.resume();
        process.stdin.setEncoding("utf8");

        function onData(char) {
          switch (char) {
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
                process.stdout.write("\b \b");
                input = input.slice(0, -1);
              }
              break;
            default:
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

  // Override Python's built-in input/print with custom versions.
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

  // Minimal Python shell content.
  const pyodideMainContent = `"""
pyodide_main.py - Pyodide-compatible main entry point for PyodideShell
"""
import sys
import os
from chuk_virtual_shell.shell_interpreter import ShellInterpreter

def pyodide_main():
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

    print("Goodbye from PyodideShell!")

if __name__ == "__main__":
    pyodide_main()
  `;

  // Create pyodide_main.py inside Pyodide.
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
    // Keep the Node process alive indefinitely.
    await new Promise(() => {});
  }
}

// Start the shell.
runPyodideShell();

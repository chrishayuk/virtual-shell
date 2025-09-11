#!/usr/bin/env python3
"""
Run all example scripts in the virtual shell.

This script discovers and executes all .sh and .py example scripts
within the virtual shell environment, providing a comprehensive test
of all shell functionality.
"""

import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict

# Add the project root to the path
# Script is now in examples/commands, so go up two levels to get project root
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from chuk_virtual_shell.shell_interpreter import ShellInterpreter
from chuk_virtual_shell.script_runner import ScriptRunner


class ExampleRunner:
    """Runner for virtual shell example scripts."""
    
    def __init__(self, sandbox_config: str = None):
        """Initialize the example runner.
        
        Args:
            sandbox_config: Path to sandbox YAML configuration file
        """
        self.sandbox_config = sandbox_config or "config/default.yaml"
        self.shell = None
        self.runner = None
        self.results = []
        
    def setup_shell(self):
        """Initialize the virtual shell and script runner."""
        print(f"Initializing virtual shell with config: {self.sandbox_config}")
        
        # Check if config exists
        config_path = Path(self.sandbox_config)
        if not config_path.exists():
            # Try relative to project root
            config_path = project_root / self.sandbox_config
            if config_path.exists():
                self.sandbox_config = str(config_path)
            else:
                print(f"Warning: Config file not found: {self.sandbox_config}")
                print("Using default memory provider")
                self.shell = ShellInterpreter()
        else:
            self.shell = ShellInterpreter(sandbox_yaml=str(config_path))
        
        self.runner = ScriptRunner(self.shell)
        print("Virtual shell initialized successfully\n")
        
    def find_example_scripts(self) -> List[Tuple[str, str]]:
        """Find all example scripts in the examples directory.
        
        Returns:
            List of tuples (script_path, script_type)
        """
        examples_dir = project_root / "examples"
        scripts = []
        
        # Find all .sh and .py files in examples directory
        for pattern in ["**/*.sh", "**/*.py"]:
            for script_path in examples_dir.glob(pattern):
                # Skip __pycache__ and other non-example files
                if "__pycache__" in str(script_path):
                    continue
                
                # Skip test runner scripts themselves
                script_name = script_path.name
                if script_name in ["run_all_examples.py", "test_examples.py"]:
                    continue
                    
                script_type = script_path.suffix[1:]  # Remove the dot
                relative_path = script_path.relative_to(project_root)
                scripts.append((str(relative_path), script_type))
        
        # Sort scripts for consistent execution order
        scripts.sort()
        
        return scripts
    
    def load_script_content(self, script_path: str) -> str:
        """Load script content from file.
        
        Args:
            script_path: Path to the script file
            
        Returns:
            Script content as string
        """
        full_path = project_root / script_path
        if not full_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
            
        with open(full_path, 'r') as f:
            return f.read()
    
    def run_script(self, script_path: str, script_type: str) -> Dict:
        """Run a single script in the virtual shell.
        
        Args:
            script_path: Path to the script
            script_type: Type of script (sh or py)
            
        Returns:
            Dictionary with execution results
        """
        result = {
            'script': script_path,
            'type': script_type,
            'status': 'pending',
            'output': '',
            'error': None,
            'execution_time': 0
        }
        
        try:
            # Load script content
            content = self.load_script_content(script_path)
            
            # Copy script to virtual filesystem
            virtual_path = f"/tmp/{Path(script_path).name}"
            self.shell.fs.write_file(virtual_path, content)
            
            # Execute script based on type
            start_time = time.time()
            
            if script_type == 'sh':
                # Execute shell script
                output = self.runner.run_script(virtual_path)
            elif script_type == 'py':
                # Execute Python script
                output = self.shell.execute(f"python {virtual_path}")
            else:
                raise ValueError(f"Unknown script type: {script_type}")
            
            execution_time = time.time() - start_time
            
            result['output'] = output or "Script executed successfully (no output)"
            result['status'] = 'success'
            result['execution_time'] = execution_time
            
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            result['output'] = f"Error executing script: {e}"
        
        return result
    
    def run_all_examples(self, filter_pattern: str = None):
        """Run all example scripts.
        
        Args:
            filter_pattern: Optional pattern to filter scripts (e.g., "filesystem")
        """
        print("=" * 70)
        print("VIRTUAL SHELL EXAMPLE RUNNER")
        print("=" * 70)
        print()
        
        # Setup shell
        self.setup_shell()
        
        # Find all scripts
        scripts = self.find_example_scripts()
        
        if filter_pattern:
            scripts = [(path, type_) for path, type_ in scripts 
                      if filter_pattern in path]
            print(f"Filtering scripts with pattern: {filter_pattern}")
        
        print(f"Found {len(scripts)} example scripts to run:")
        for script_path, script_type in scripts:
            print(f"  - {script_path} ({script_type})")
        print()
        
        # Run each script
        total_scripts = len(scripts)
        for idx, (script_path, script_type) in enumerate(scripts, 1):
            print(f"[{idx}/{total_scripts}] Running: {script_path}")
            print("-" * 50)
            
            result = self.run_script(script_path, script_type)
            self.results.append(result)
            
            # Print output (truncated if too long)
            output = result['output']
            if len(output) > 500:
                output = output[:500] + "\n... (output truncated) ..."
            
            if result['status'] == 'success':
                print(f"✅ SUCCESS ({result['execution_time']:.2f}s)")
                if output:
                    print("Output preview:")
                    print(output)
            else:
                print(f"❌ FAILED: {result['error']}")
            
            print()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print execution summary."""
        print("=" * 70)
        print("EXECUTION SUMMARY")
        print("=" * 70)
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['status'] == 'success')
        failed = sum(1 for r in self.results if r['status'] == 'failed')
        total_time = sum(r['execution_time'] for r in self.results)
        
        print(f"Total scripts executed: {total}")
        print(f"Successful: {successful} ({successful*100/total:.1f}%)")
        print(f"Failed: {failed} ({failed*100/total:.1f}%)")
        print(f"Total execution time: {total_time:.2f}s")
        print()
        
        if failed > 0:
            print("Failed scripts:")
            for result in self.results:
                if result['status'] == 'failed':
                    print(f"  ❌ {result['script']}: {result['error']}")
            print()
        
        # Group results by category
        categories = {}
        for result in self.results:
            parts = result['script'].split('/')
            if len(parts) > 2:
                category = parts[2]  # examples/commands/CATEGORY/...
                if category not in categories:
                    categories[category] = {'success': 0, 'failed': 0}
                
                if result['status'] == 'success':
                    categories[category]['success'] += 1
                else:
                    categories[category]['failed'] += 1
        
        if categories:
            print("Results by category:")
            for category, counts in sorted(categories.items()):
                total_cat = counts['success'] + counts['failed']
                print(f"  {category}: {counts['success']}/{total_cat} successful")
        
        print()
        
        # Overall status
        if failed == 0:
            print("🎉 ALL EXAMPLES PASSED!")
            print("✅ Virtual shell is fully functional")
        elif successful > failed:
            print("⚠️  MOST EXAMPLES PASSED")
            print(f"✅ {successful}/{total} scripts executed successfully")
        else:
            print("❌ MULTIPLE FAILURES DETECTED")
            print("Please review the failed scripts above")
    
    def run_specific_category(self, category: str):
        """Run examples from a specific category.
        
        Args:
            category: Category name (filesystem, navigation, text, system, environment)
        """
        print(f"Running examples for category: {category}")
        self.run_all_examples(filter_pattern=f"commands/{category}")
    
    def run_single_script(self, script_path: str):
        """Run a single specific script.
        
        Args:
            script_path: Path to the script relative to project root
        """
        print(f"Running single script: {script_path}")
        print("=" * 70)
        
        self.setup_shell()
        
        # Determine script type
        script_type = Path(script_path).suffix[1:]
        
        result = self.run_script(script_path, script_type)
        
        print(f"Script: {result['script']}")
        print(f"Status: {result['status']}")
        print(f"Execution time: {result['execution_time']:.2f}s")
        
        if result['status'] == 'success':
            print("✅ Script executed successfully")
            print("\nOutput:")
            print(result['output'])
        else:
            print(f"❌ Script failed: {result['error']}")


def main():
    """Main entry point for the example runner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run virtual shell example scripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all examples
  python run_all_examples.py
  
  # Run examples from a specific category
  python run_all_examples.py --category filesystem
  python run_all_examples.py --category navigation
  
  # Run a single specific script
  python run_all_examples.py --script examples/hello_world.sh
  
  # Use a specific sandbox configuration
  python run_all_examples.py --sandbox config/readonly.yaml
  
  # Filter scripts by pattern
  python run_all_examples.py --filter "text_processing"
        """
    )
    
    parser.add_argument(
        '--category', 
        choices=['filesystem', 'navigation', 'text', 'system', 'environment'],
        help='Run examples from a specific category'
    )
    
    parser.add_argument(
        '--script',
        help='Run a single specific script'
    )
    
    parser.add_argument(
        '--sandbox',
        default='config/default.yaml',
        help='Sandbox configuration file to use'
    )
    
    parser.add_argument(
        '--filter',
        help='Filter scripts by pattern in path'
    )
    
    args = parser.parse_args()
    
    # Create runner
    runner = ExampleRunner(sandbox_config=args.sandbox)
    
    try:
        if args.script:
            # Run single script
            runner.run_single_script(args.script)
        elif args.category:
            # Run category
            runner.run_specific_category(args.category)
        else:
            # Run all (with optional filter)
            runner.run_all_examples(filter_pattern=args.filter)
            
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user")
        runner.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
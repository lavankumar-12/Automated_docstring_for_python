"""Logic for checking staged files during the git pre-commit hook."""
import subprocess
import sys
import os

def get_staged_files():
    """Returns a list of staged .py files."""
    try:
        output = subprocess.check_output(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"], text=True)
        return [f for f in output.splitlines() if f.endswith(".py")]
    except subprocess.CalledProcessError:
        return []

def main():
    """Main execution point for the pre-commit check."""
    staged_files = get_staged_files()
    if not staged_files:
        print("No staged Python files to check.")
        return

    print(f"Checking {len(staged_files)} staged files for docstrings...")
    
    failed = False
    for file in staged_files:
        print(f"\n>> Checking {file}")
        # Run main.py with --check-only flag
        result = subprocess.run([sys.executable, "main.py", file, "--check-only"])
        if result.returncode != 0:
            failed = True

    if failed:
        print("\n\033[91mCOMMIT BLOCKED: Docstring requirements not met.\033[0m")
        print("Please fix the issues above before committing.")
        sys.exit(1)
    else:
        print("\n\033[92mDocstring checks passed!\033[0m")

if __name__ == "__main__":
    main()

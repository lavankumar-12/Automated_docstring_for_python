"""Installation script for setting up git hooks."""
import os
import sys
import stat

def install():
    """Installs the pre-commit hook into the .git folder."""
    hook_path = os.path.join(".git", "hooks", "pre-commit")
    
    if not os.path.exists(".git"):
        print("Error: .git directory not found. Are you in the root of the repository?")
        sys.exit(1)

    hook_content = f"""#!/bin/sh
# Pre-commit hook for docstring validation
python scripts/pre_commit_check.py
"""

    with open(hook_path, "w") as f:
        f.write(hook_content)

    # Make the hook executable
    st = os.stat(hook_path)
    os.chmod(hook_path, st.st_mode | stat.S_IEXEC)

    print(f"Pre-commit hook installed successfully at {hook_path}")

if __name__ == "__main__":
    install()

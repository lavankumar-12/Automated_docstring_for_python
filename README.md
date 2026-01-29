# Automated Python Docstring Generator & Coverage Reporter

## Milestone 3: Workflow & CI Integration

This project has been extended to include professional automation and configuration features.

### New Features

1.  **Centralized Configuration (`pyproject.toml`)**:
    *   Configure minimum coverage threshold.
    *   Set default docstring style (Google, NumPy, reST).
    *   Enable/Disable validation rules globally.

2.  **Git Pre-Commit Hook**:
    *   Automatically validates staged files before every commit.
    *   Blocks commits if documentation coverage is below the threshold or style rules are violated.
    *   Install it by running: `python scripts/setup_hooks.py`

3.  **GitHub Actions CI Workflow**:
    *   Validates all project files on every push and pull request.
    *   Ensures that only well-documented code is merged into the main branch.

### Prerequisites

*   Python 3.11+ (uses `tomllib`)
*   Install dependencies: `pip install -r requirements.txt`

### Usage

#### 1. Setup Pre-commit Hook
```bash
python scripts/setup_hooks.py
```

#### 2. Manual Validation
```bash
python main.py <file_path> --check-only
```

#### 3. Configuration
Edit `pyproject.toml`:
```toml
[tool.docstring_generator]
min_coverage = 80.0
default_style = "google"
validation_enabled = true
```

### Files
- `main.py`: Core logic, CLI, and validation.
- `app.py`: Streamlit UI.
- `scripts/setup_hooks.py`: Hook installer.
- `scripts/pre_commit_check.py`: Hook logic.
- `.github/workflows/docstring_ci.yml`: CI configuration.

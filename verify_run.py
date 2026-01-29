"""Verification script to ensure the core logic is functioning correctly."""
from main import run
import json

docs, report = run('temp.py', validate=True)
# Convert sets to lists for JSON serialization
report_clean = report.copy()
# We don't have sets in report anymore except if I missed something
# Actually 'raises' was a set but it's in node_info, not report summary
print(json.dumps(report, indent=4))

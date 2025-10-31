#!/usr/bin/env python3
"""
Check which scenarios were not found
"""
import json

# Load files
scenarios = json.load(open('scenarios.json'))
issues = json.load(open('stat_issues_comprehensive.json'))

# Check all issue categories
all_scenario_ids = set()
for category, issue_list in issues.items():
    for issue in issue_list:
        all_scenario_ids.add(issue['scenario_id'])

# Check which ones exist
missing = []
found = []
for sid in all_scenario_ids:
    if sid in scenarios:
        found.append(sid)
    else:
        missing.append(sid)

print(f"Found: {len(found)} scenarios")
print(f"Missing: {len(missing)} scenarios")
print(f"\nMissing scenario IDs:")
for sid in sorted(missing):
    print(f"  - {sid}")

# Check if they might be in delayed_effects or other structures
print(f"\n\nLooking for missing scenarios in other structures...")
for sid in missing:
    for key, scenario in scenarios.items():
        # Check if it might be referenced elsewhere
        scenario_str = json.dumps(scenario)
        if sid in scenario_str:
            print(f"  Found '{sid}' referenced in '{key}'")

#!/usr/bin/env python3
"""
Fix stat issues in scenarios.json based on comprehensive analysis
"""
import json
import sys

def load_json_file(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(filepath, data):
    """Save JSON file with proper formatting"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_scenario(scenarios, scenario_id):
    """Find scenario by ID in the scenarios dict"""
    # Scenarios are top-level keys
    return scenarios.get(scenario_id, None)

def apply_budget_fixes(scenarios, issues):
    """Apply budget error fixes"""
    fixes_applied = 0
    for issue in issues:
        scenario = find_scenario(scenarios, issue['scenario_id'])
        if scenario and 'choices' in scenario:
            choice_idx = issue['choice_index']
            if choice_idx < len(scenario['choices']):
                choice = scenario['choices'][choice_idx]
                if 'result' in choice and 'stats' in choice['result']:
                    stats = choice['result']['stats']
                    # Remove or update budget
                    if issue['recommended'] and 'budget' in issue['recommended']:
                        # Update to recommended value
                        stats['budget'] = issue['recommended']['budget']
                        fixes_applied += 1
                    elif 'budget' in stats:
                        # Remove budget entirely
                        del stats['budget']
                        fixes_applied += 1
    return fixes_applied

def apply_stress_fixes(scenarios, issues):
    """Apply stress error fixes"""
    fixes_applied = 0
    for issue in issues:
        scenario = find_scenario(scenarios, issue['scenario_id'])
        if scenario and 'choices' in scenario:
            choice_idx = issue['choice_index']
            if choice_idx < len(scenario['choices']):
                choice = scenario['choices'][choice_idx]
                if 'result' not in choice:
                    choice['result'] = {}
                if 'stats' not in choice['result']:
                    choice['result']['stats'] = {}

                # Apply recommended stress value
                if 'stress' in issue['recommended']:
                    choice['result']['stats']['stress'] = issue['recommended']['stress']
                    fixes_applied += 1
    return fixes_applied

def apply_principled_local_fixes(scenarios, issues):
    """Apply principled/local_friendly conflict fixes"""
    fixes_applied = 0
    for issue in issues:
        scenario = find_scenario(scenarios, issue['scenario_id'])
        if scenario and 'choices' in scenario:
            choice_idx = issue['choice_index']
            if choice_idx < len(scenario['choices']):
                choice = scenario['choices'][choice_idx]
                if 'result' in choice and 'deputy_morale' in choice['result']:
                    deputy = choice['result']['deputy_morale']
                    # Update principled and/or local_friendly
                    if 'principled' in issue['recommended']:
                        deputy['principled'] = issue['recommended']['principled']
                    if 'local_friendly' in issue['recommended']:
                        deputy['local_friendly'] = issue['recommended']['local_friendly']
                    fixes_applied += 1
    return fixes_applied

def apply_project_success_fixes(scenarios, issues):
    """Apply project success overvaluation fixes"""
    fixes_applied = 0
    for issue in issues:
        scenario = find_scenario(scenarios, issue['scenario_id'])
        if scenario and 'choices' in scenario:
            choice_idx = issue['choice_index']
            if choice_idx < len(scenario['choices']):
                choice = scenario['choices'][choice_idx]
                if 'result' in choice and 'stats' in choice['result']:
                    if 'project_success' in issue['recommended']:
                        choice['result']['stats']['project_success'] = issue['recommended']['project_success']
                        fixes_applied += 1
    return fixes_applied

def apply_wellbeing_fixes(scenarios, issues):
    """Apply missing wellbeing fixes"""
    fixes_applied = 0
    for issue in issues:
        scenario = find_scenario(scenarios, issue['scenario_id'])
        if scenario and 'choices' in scenario:
            choice_idx = issue['choice_index']
            if choice_idx < len(scenario['choices']):
                choice = scenario['choices'][choice_idx]
                if 'result' not in choice:
                    choice['result'] = {}
                if 'stats' not in choice['result']:
                    choice['result']['stats'] = {}

                # Add wellbeing stat
                if 'wellbeing' in issue['recommended']:
                    choice['result']['stats']['wellbeing'] = issue['recommended']['wellbeing']
                    fixes_applied += 1
    return fixes_applied

def apply_reputation_fixes(scenarios, issues):
    """Apply reputation internal-only fixes"""
    fixes_applied = 0
    for issue in issues:
        scenario = find_scenario(scenarios, issue['scenario_id'])
        if scenario and 'choices' in scenario:
            choice_idx = issue['choice_index']
            if choice_idx < len(scenario['choices']):
                choice = scenario['choices'][choice_idx]
                if 'result' in choice and 'stats' in choice['result']:
                    stats = choice['result']['stats']
                    if 'reputation' in stats:
                        # Remove reputation for internal actions
                        del stats['reputation']
                        fixes_applied += 1
    return fixes_applied

def apply_budget_adjustment_fixes(scenarios, issues):
    """Apply budget adjustment paradox fixes"""
    fixes_applied = 0
    for issue in issues:
        scenario = find_scenario(scenarios, issue['scenario_id'])
        if scenario and 'choices' in scenario:
            choice_idx = issue['choice_index']
            if choice_idx < len(scenario['choices']):
                choice = scenario['choices'][choice_idx]
                if 'result' in choice and 'stats' in choice['result']:
                    if 'budget' in issue['recommended']:
                        choice['result']['stats']['budget'] = issue['recommended']['budget']
                        fixes_applied += 1
    return fixes_applied

def main():
    # Load files
    print("Loading scenarios.json...")
    scenarios = load_json_file('scenarios.json')

    print("Loading stat_issues_comprehensive.json...")
    issues = load_json_file('stat_issues_comprehensive.json')

    # Apply fixes by category
    print("\n=== Applying Fixes ===\n")

    print("1. Fixing budget errors...")
    budget_fixes = apply_budget_fixes(scenarios, issues['budget_errors'])
    print(f"   ✓ Applied {budget_fixes} budget fixes")

    print("2. Fixing stress direction errors...")
    stress_fixes = apply_stress_fixes(scenarios, issues['stress_errors'])
    print(f"   ✓ Applied {stress_fixes} stress fixes")

    print("3. Fixing principled/local_friendly conflicts...")
    principled_fixes = apply_principled_local_fixes(scenarios, issues['principled_local_conflicts'])
    print(f"   ✓ Applied {principled_fixes} principled/local fixes")

    print("4. Fixing project success overvaluation...")
    project_fixes = apply_project_success_fixes(scenarios, issues['project_success_overvalued'])
    print(f"   ✓ Applied {project_fixes} project success fixes")

    print("5. Adding missing wellbeing stats...")
    wellbeing_fixes = apply_wellbeing_fixes(scenarios, issues['missing_wellbeing'])
    print(f"   ✓ Applied {wellbeing_fixes} wellbeing fixes")

    print("6. Fixing reputation for internal actions...")
    reputation_fixes = apply_reputation_fixes(scenarios, issues['reputation_internal_only'])
    print(f"   ✓ Applied {reputation_fixes} reputation fixes")

    print("7. Fixing budget adjustment paradoxes...")
    budget_adj_fixes = apply_budget_adjustment_fixes(scenarios, issues['budget_adjustment_paradox'])
    print(f"   ✓ Applied {budget_adj_fixes} budget adjustment fixes")

    total_fixes = (budget_fixes + stress_fixes + principled_fixes +
                   project_fixes + wellbeing_fixes + reputation_fixes + budget_adj_fixes)

    print(f"\n=== Total: {total_fixes} fixes applied ===\n")

    # Save updated scenarios
    print("Saving updated scenarios.json...")
    save_json_file('scenarios.json', scenarios)
    print("✓ Done!")

    return 0

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Script to process GitHub issues and update the leaderboard.
"""

import json
import os
import re
from datetime import datetime

def parse_issue_body(body):
    """Parse the issue body to extract submission data."""
    data = {}
    
    # Patterns to match the issue template format
    patterns = {
        'student_name': r'### Student Name\s*\n\s*(.+?)(?=\n###|\n\n###|$)',
        'model_length': r'### Model Length\s*\n\s*(.+?)(?=\n###|\n\n###|$)',
        'accuracy': r'### Accuracy\s*\n\s*(.+?)(?=\n###|\n\n###|$)',
        'tensorboard_link': r'### TensorBoard Link\s*\n\s*(.+?)(?=\n###|\n\n###|$)',
        'improvement_description': r'### Improvement Description\s*\n\s*(.+?)(?=\n###|\n\n###|$)',
        'gpu_hours': r'### GPU Hours\s*\n\s*(.+?)(?=\n###|\n\n###|$)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, body, re.DOTALL | re.MULTILINE)
        if match:
            value = match.group(1).strip()
            # Skip if value is empty or "N/A" or "_No response_"
            if value and value.lower() not in ['n/a', '_no response_', 'no response']:
                data[key] = value
    
    return data

def load_leaderboard(filepath='docs/leaderboard.json'):
    """Load existing leaderboard data."""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {'submissions': []}

def save_leaderboard(data, filepath='docs/leaderboard.json'):
    """Save leaderboard data."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def update_leaderboard(issue_number, issue_title, issue_author, issue_body, issue_url):
    """Update the leaderboard with new submission."""
    leaderboard = load_leaderboard()
    
    # Parse the issue body
    submission_data = parse_issue_body(issue_body)
    
    # Check if submission already exists
    existing_index = None
    for i, sub in enumerate(leaderboard['submissions']):
        if sub['issue_number'] == issue_number:
            existing_index = i
            break
    
    # Create submission entry
    submission = {
        'issue_number': issue_number,
        'student_name': submission_data.get('student_name', issue_author),
        'model_length': submission_data.get('model_length', 'N/A'),
        'accuracy': submission_data.get('accuracy', 'N/A'),
        'tensorboard_link': submission_data.get('tensorboard_link', ''),
        'improvement_description': submission_data.get('improvement_description', ''),
        'gpu_hours': submission_data.get('gpu_hours', 'N/A'),
        'issue_url': issue_url,
        'submitted_at': datetime.utcnow().isoformat(),
        'verified': False
    }
    
    # Update or add submission
    if existing_index is not None:
        # Preserve verification status if it was already verified
        submission['verified'] = leaderboard['submissions'][existing_index].get('verified', False)
        leaderboard['submissions'][existing_index] = submission
    else:
        leaderboard['submissions'].append(submission)
    
    # Sort by accuracy (descending), handling non-numeric values
    def get_accuracy_value(sub):
        acc = sub.get('accuracy', 'N/A')
        if acc == 'N/A':
            return -1
        # Remove % sign and convert to float
        acc_str = str(acc).strip().replace('%', '')
        try:
            val = float(acc_str)
            # If value is greater than 1, assume it's a percentage
            if val > 1:
                val = val / 100
            return val
        except ValueError:
            return -1
    
    leaderboard['submissions'].sort(key=get_accuracy_value, reverse=True)
    
    # Save updated leaderboard
    save_leaderboard(leaderboard)
    
    print(f"Updated leaderboard with issue #{issue_number}")
    return True

def mark_verified(issue_number):
    """Mark a submission as verified."""
    leaderboard = load_leaderboard()
    
    for sub in leaderboard['submissions']:
        if sub['issue_number'] == issue_number:
            sub['verified'] = True
            save_leaderboard(leaderboard)
            print(f"Marked issue #{issue_number} as verified")
            return True
    
    print(f"Issue #{issue_number} not found in leaderboard")
    return False

def remove_submission(issue_number):
    """Remove a submission from the leaderboard."""
    leaderboard = load_leaderboard()
    
    initial_count = len(leaderboard['submissions'])
    leaderboard['submissions'] = [
        sub for sub in leaderboard['submissions'] 
        if sub['issue_number'] != issue_number
    ]
    
    if len(leaderboard['submissions']) < initial_count:
        save_leaderboard(leaderboard)
        print(f"Removed submission for issue #{issue_number}")
        return True
    
    print(f"Issue #{issue_number} not found in leaderboard")
    return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python process_issue.py <action> [args...]")
        print("Actions:")
        print("  update <issue_number> <issue_title> <issue_author> <issue_url> <issue_body>")
        print("  verify <issue_number>")
        print("  remove <issue_number>")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'update':
        if len(sys.argv) < 7:
            print("Error: update action requires issue_number, issue_title, issue_author, issue_url, and issue_body")
            sys.exit(1)
        
        issue_number = int(sys.argv[2])
        issue_title = sys.argv[3]
        issue_author = sys.argv[4]
        issue_url = sys.argv[5]
        issue_body = sys.argv[6]
        
        update_leaderboard(issue_number, issue_title, issue_author, issue_body, issue_url)
    
    elif action == 'verify':
        if len(sys.argv) < 3:
            print("Error: verify action requires issue_number")
            sys.exit(1)
        
        issue_number = int(sys.argv[2])
        mark_verified(issue_number)
    
    elif action == 'remove':
        if len(sys.argv) < 3:
            print("Error: remove action requires issue_number")
            sys.exit(1)
        
        issue_number = int(sys.argv[2])
        remove_submission(issue_number)
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Script to fix deprecated actions/upload-artifact@v3 to v4 in all workflow files
"""
import os
import glob

def fix_workflows():
    """Fix deprecated artifact actions in all workflow files"""
    workflow_files = glob.glob('.github/workflows/*.yml')
    
    for file_path in workflow_files:
        print(f"Processing {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace deprecated artifact actions
        original_content = content
        content = content.replace('actions/upload-artifact@v3', 'actions/upload-artifact@v4')
        content = content.replace('actions/cache@v3', 'actions/cache@v4')
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Updated {file_path}")
        else:
            print(f"  No changes needed for {file_path}")

if __name__ == "__main__":
    fix_workflows()
    print("Done!")
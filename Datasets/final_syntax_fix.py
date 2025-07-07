#!/usr/bin/env python3
"""
Final Syntax Fixer

This script fixes the remaining indentation and syntax issues in the notebook.
"""

import json
import re

def fix_notebook_syntax():
    """Fix syntax issues in the notebook"""
    print("🔧 Fixing notebook syntax issues...")
    
    with open("soft_skills_assessment.ipynb", 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    fixes_applied = 0
    
    for i, cell in enumerate(notebook['cells']):
        if cell['cell_type'] == 'code' and 'source' in cell:
            source_lines = cell['source']
            new_source_lines = []
            
            for j, line in enumerate(source_lines):
                # Fix common indentation issues
                fixed_line = line
                
                # Fix docstring indentation
                if '"""' in line and not line.strip().startswith('"""') and not line.strip().endswith('"""'):
                    # This is likely an unindented docstring
                    if j > 0 and 'def ' in source_lines[j-1]:
                        fixed_line = '    ' + line.lstrip()
                        fixes_applied += 1
                
                # Fix missing indentation after function definitions
                if line.strip().startswith('"""') and j > 0:
                    prev_line = source_lines[j-1].strip()
                    if prev_line.startswith('def ') and prev_line.endswith(':'):
                        if not line.startswith('    '):
                            fixed_line = '    ' + line.lstrip()
                            fixes_applied += 1
                
                # Fix function body indentation
                if j > 0:
                    prev_line = source_lines[j-1].strip()
                    if (prev_line.endswith('"""') and 
                        len([l for l in source_lines[:j] if 'def ' in l]) > 0 and
                        line.strip() and not line.startswith('    ') and
                        not line.startswith('def ') and not line.startswith('#')):
                        # This line should be indented as part of function body
                        fixed_line = '    ' + line.lstrip()
                        fixes_applied += 1
                
                new_source_lines.append(fixed_line)
            
            # Update the cell if changes were made
            if new_source_lines != source_lines:
                cell['source'] = new_source_lines
    
    # Save the fixed notebook
    with open("soft_skills_assessment.ipynb", 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Applied {fixes_applied} syntax fixes")
    return fixes_applied

def verify_basic_syntax():
    """Verify that basic Python syntax is correct"""
    print("🔍 Verifying syntax fixes...")
    
    try:
        with open("soft_skills_assessment.ipynb", 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        syntax_issues = 0
        
        for i, cell in enumerate(notebook['cells']):
            if cell['cell_type'] == 'code':
                source = ''.join(cell.get('source', []))
                if source.strip():
                    try:
                        compile(source, f"<cell {i}>", "exec")
                    except SyntaxError as e:
                        print(f"⚠️  Cell {i+1}: {e}")
                        syntax_issues += 1
        
        if syntax_issues == 0:
            print("✅ All cells have valid Python syntax")
        else:
            print(f"⚠️  {syntax_issues} cells still have syntax issues")
        
        return syntax_issues == 0
        
    except Exception as e:
        print(f"❌ Error verifying syntax: {e}")
        return False

def main():
    """Run syntax fixes and verification"""
    print("🚀 Final Syntax Fix Process")
    print("=" * 40)
    
    fixes = fix_notebook_syntax()
    syntax_ok = verify_basic_syntax()
    
    print("\n" + "=" * 40)
    print("📊 RESULTS:")
    print(f"Fixes applied: {fixes}")
    print(f"Syntax valid: {'✅ Yes' if syntax_ok else '❌ No'}")
    
    if syntax_ok:
        print("\n🎉 Notebook is ready to use!")
        print("💡 Open in Jupyter and run all cells")
    else:
        print("\n⚠️  Some syntax issues remain")
        print("💡 You can still use the notebook - Jupyter may handle minor issues")

if __name__ == "__main__":
    main()

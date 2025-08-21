#!/usr/bin/env python3
"""
Final PEP 8 cleanup script - improved version.
Handles remaining violations with better logic.
"""

import os
import re


def fix_long_comments(content, max_length=79):
    """Break long comments into multiple lines."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if line.strip().startswith('#') and len(line) > max_length:
            # Get indentation and comment content
            indent = len(line) - len(line.lstrip())
            base_indent = ' ' * indent
            comment_text = line.strip()[1:].strip()
            
            # Break comment into multiple lines
            words = comment_text.split()
            current_line = base_indent + '#'
            
            for word in words:
                if len(current_line + ' ' + word) <= max_length:
                    if current_line.endswith('#'):
                        current_line += ' ' + word
                    else:
                        current_line += ' ' + word
                else:
                    fixed_lines.append(current_line)
                    current_line = base_indent + '# ' + word
            
            if current_line.strip() != base_indent.strip() + '#':
                fixed_lines.append(current_line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_long_strings(content, max_length=79):
    """Break long string lines."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) > max_length and ('"' in line or "'" in line):
            # Get indentation
            indent = len(line) - len(line.lstrip())
            base_indent = ' ' * indent
            
            # Try to break at string concatenation points
            if ' + ' in line and ('"' in line or "'" in line):
                parts = line.split(' + ')
                if len(parts) > 1:
                    fixed_lines.append(parts[0] + ' +')
                    for part in parts[1:]:
                        fixed_lines.append(base_indent + '    ' + part)
                    continue
            
            # Try to break long f-strings or regular strings
            if 'f"' in line or "f'" in line or '"' in line or "'" in line:
                # Simple approach: if line is too long, try to break it
                if len(line) > max_length:
                    # Find a good break point (comma, space, etc.)
                    break_points = [', ', ' and ', ' or ', ' if ', ' else ']
                    broken = False
                    
                    for bp in break_points:
                        if bp in line:
                            pos = line.rfind(bp, 0, max_length - 2)
                            if pos > indent + 10:  # Don't break too early
                                first_part = line[:pos + len(bp)]
                                second_part = line[pos + len(bp):]
                                fixed_lines.append(first_part)
                                fixed_lines.append(base_indent + '    ' + second_part)
                                broken = True
                                break
                    
                    if not broken:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_w503_violations(content):
    """Fix W503 by moving binary operators to end of previous line."""
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        
        # Check if line starts with binary operator
        binary_ops = ['and ', 'or ', '== ', '!= ', '>= ', '<= ', '> ', '< ', 
                     '+ ', '- ', '* ', '/ ', '% ']
        
        starts_with_op = any(stripped.startswith(op) for op in binary_ops)
        
        if starts_with_op and fixed_lines:
            # Find which operator it starts with
            operator = None
            for op in binary_ops:
                if stripped.startswith(op):
                    operator = op.strip()
                    rest = stripped[len(op):].strip()
                    break
            
            if operator and fixed_lines[-1].strip():
                # Move operator to end of previous line
                prev_line = fixed_lines[-1].rstrip()
                fixed_lines[-1] = prev_line + ' ' + operator
                
                # Add the rest as a new line with proper indentation
                indent = len(line) - len(line.lstrip())
                base_indent = ' ' * indent
                if rest:
                    fixed_lines.append(base_indent + rest)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return '\n'.join(fixed_lines)


def fix_e502_e128_issues(content):
    """Fix E502 redundant backslash and E128 indentation issues."""
    # Remove redundant backslashes before closing brackets
    content = re.sub(r'\\\s*\n(\s*)([)\]}])', r'\n\1\2', content)
    
    # Fix continuation line indentation
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        if i > 0 and line.strip():
            prev_line = lines[i-1]
            
            # If previous line ends with certain chars, this might be continuation
            if (prev_line.rstrip().endswith(('(', '[', '{', ',', '\\')) and
                not line.lstrip().startswith(('#', '"""', "'''", 'def ', 'class '))):
                
                # Check if current line needs better indentation
                prev_indent = len(prev_line) - len(prev_line.lstrip())
                current_indent = len(line) - len(line.lstrip())
                
                # If it's a continuation but not properly indented
                if current_indent <= prev_indent and line.strip():
                    base_indent = ' ' * prev_indent
                    content_part = line.lstrip()
                    fixed_lines.append(f'{base_indent}    {content_part}')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_file(file_path):
    """Apply all fixes to a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes in sequence
        content = fix_e502_e128_issues(content)
        content = fix_w503_violations(content)
        content = fix_long_comments(content)
        content = fix_long_strings(content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix all files."""
    # Files that need fixing based on flake8 output
    files_to_fix = [
        "src/entities/entity.py",
        "src/entities/player.py", 
        "src/entities/zombie.py",
        "src/managers/chest_manager.py",
        "src/managers/input_manager.py",
        "src/managers/map_manager.py",
        "src/managers/reset_coordinator.py",
        "src/managers/spawn_manager.py",
        "src/managers/testing_manager.py",
        "src/managers/ui_manager.py",
        "src/sprites/car.py",
        "src/sprites/chest.py",
        "src/testing/centralized_tests.py",
        "src/testing/integration.py",
        "src/testing/test_runner.py",
        "src/testing/tracking_components.py",
        "src/views/fading_view.py",
        "src/views/game_view.py",
        "src/views/transition_view.py"
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_file(file_path):
                fixed_count += 1
    
    print(f"\nProcessed {fixed_count} files")
    
    # Run black to clean up formatting
    print("Running black formatter...")
    os.system("python -m black --line-length=79 .")


if __name__ == '__main__':
    main()

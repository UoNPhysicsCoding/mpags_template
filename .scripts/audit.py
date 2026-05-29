import sys, subprocess, datetime, json, os

def get_code_lines(file_path):
    ext = os.path.splitext(file_path)[1]
    
    try:
        if ext == '.ipynb':
            with open(file_path, 'r', encoding='utf-8') as f:
                nb = json.load(f)
                # Count lines only in 'code' cells
                total_lines = 0
                for cell in nb.get('cells', []):
                    if cell.get('cell_type') == 'code':
                        # Sum the number of lines in each code cell
                        total_lines += len(cell.get('source', []))
                return total_lines
        
        elif ext in ['.py', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        
        else:
            return 0
    except Exception:
        return 0

# Main execution logic
file_path = sys.argv[1]
timestamp = datetime.datetime.now().strftime('%H:%M:%S')
line_count = get_code_lines(file_path)

subprocess.run(['git', 'add', file_path], capture_output=True)
result = subprocess.run(['git', 'commit', '-m', f'Time: {timestamp} | LOC: {line_count}'], capture_output=True)

if result.returncode == 0:
    subprocess.run(['git', 'push'], capture_output=True)
import sys, subprocess, datetime, json, os

def get_meaningful_lines(file_path):
    ext = os.path.splitext(file_path)[1]
    try:
        lines = []
        if ext == '.ipynb':
            with open(file_path, 'r', encoding='utf-8') as f:
                nb = json.load(f)
                for cell in nb.get('cells', []):
                    if cell.get('cell_type') == 'code':
                        lines.extend(cell.get('source', []))
        elif ext in ['.py', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        
        # This is the fix: Only count lines that aren't just empty or whitespace
        meaningful_lines = [l for l in lines if l.strip()]
        return len(meaningful_lines)
    except Exception:
        return 0

file_path = sys.argv[1]
timestamp = datetime.datetime.now().strftime('%H:%M:%S')
line_count = get_meaningful_lines(file_path)

subprocess.run(['git', 'add', file_path], capture_output=True)
subprocess.run(['git', 'commit', '-m', f'Time: {timestamp} | Num_newlines: {line_count}'], capture_output=True)
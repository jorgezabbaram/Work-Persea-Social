import os

base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Scan all service folders and convert any .py file that starts with UTF-16 LE BOM
for root, dirs, files in os.walk(base):
    # skip virtual envs, __pycache__, .git
    if any(x in root for x in ('site-packages', '__pycache__', '.venv', '.git')):
        continue
    for f in files:
        if f.endswith('.py'):
            full = os.path.join(root, f)
            try:
                b = open(full, 'rb').read()
                if len(b) >= 2 and b[0] == 0xFF and b[1] == 0xFE:
                    print('Convirtiendo', full)
                    s = b.decode('utf-16')
                    open(full, 'w', encoding='utf-8').write(s)
                # else: keep file as-is
            except Exception as e:
                print('ERROR', full, e)

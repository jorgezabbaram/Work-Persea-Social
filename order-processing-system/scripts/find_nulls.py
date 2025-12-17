import os

base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
found = []
for root, dirs, files in os.walk(base):
    # skip virtual envs and caches
    if any(x in root for x in ('site-packages', '__pycache__', '.venv', '.git')):
        continue
    for f in files:
        if f.endswith('.py'):
            p = os.path.join(root, f)
            try:
                with open(p, 'rb') as fh:
                    b = fh.read()
                if b.find(b'\x00') != -1:
                    found.append(p)
            except Exception as e:
                print('ERR', p, e)
if found:
    print('\n'.join(found))
else:
    print('NO_NULLS')

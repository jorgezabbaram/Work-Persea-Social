#!/usr/bin/env python3
import os
import sys
import subprocess

def has_nul(path):
    try:
        with open(path, 'rb') as f:
            return b'\x00' in f.read()
    except Exception:
        return False

def scan_app():
    bad = []
    for root, _, files in os.walk('/app'):
        for f in files:
            if f.endswith('.py') or f.endswith('.ini'):
                p = os.path.join(root, f)
                if has_nul(p):
                    bad.append(p)
    return bad

def run(cmd):
    print('-> running:', cmd)
    rc = subprocess.call(cmd, shell=True)
    if rc != 0:
        print(f'Command failed (rc={rc}): {cmd}')
        sys.exit(rc)

if __name__ == '__main__':
    bad = scan_app()
    if bad:
        print('ERROR: archivos con bytes NUL detectados:')
        for p in bad:
            print(' -', p)
        sys.exit(2)

    if os.getenv('SKIP_MIGRATIONS', '0') != '1':
        run('alembic upgrade head')

    os.execvp('uvicorn', ['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'])

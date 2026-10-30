import os
import re
import subprocess
import sys

command = ['git', '-c', f'safe.directory={os.getcwd()}']
reference = sys.argv[1] if len(sys.argv) > 1 else 'origin/main'
base = subprocess.check_output(command + ['merge-base', 'HEAD', reference]).strip().decode('ascii')
patch = subprocess.check_output(command + ['diff', '--no-color', '--no-ext-diff', '--no-textconv', '--unified=0', base, '--'])
path = ''
number = 0
in_hunk = False
errors = 0
checked = 0
for line in patch.split(b'\n'):
    if line.startswith(b'diff --git '):
        in_hunk = False
    elif not in_hunk and line.startswith(b'+++ '):
        path = line[4:].decode('ascii', 'backslashreplace')
        if path.startswith('b/'):
            path = path[2:]
    elif match := re.match(rb'@@ -\d+(?:,\d+)? \+(\d+)', line):
        number = int(match[1])
        in_hunk = True
    elif in_hunk and line.startswith(b'+'):
        checked += 1
        if not line[1:].isascii():
            print(f'{path}:{number}: non-ASCII added text', file=sys.stderr)
            errors += 1
        number += 1
    elif in_hunk and line.startswith(b' '):
        number += 1
print(f'ASCII additions: {checked} lines checked, {errors} errors')
sys.exit(1 if errors else 0)

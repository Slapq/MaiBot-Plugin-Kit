import subprocess, os

repo = r's:\VSCODE\CodeX\MaiBot-Plugin-Kit'

def run(cmd):
    r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print('$', ' '.join(str(c) for c in cmd))
    if r.stdout.strip(): print('OUT:', r.stdout[:300])
    if r.stderr.strip(): print('ERR:', r.stderr[:300])

# 在 .gitignore 加入 __*.py 规则
gi = os.path.join(repo, '.gitignore')
with open(gi, encoding='utf-8') as f:
    content = f.read()
if '__*.py' not in content:
    with open(gi, 'a', encoding='utf-8') as f:
        f.write('\n# 临时辅助脚本\n__*.py\n')

run(['git', 'rm', '--cached', '--ignore-unmatch', '__git_push.py'])
run(['git', 'add', '.gitignore'])
run(['git', 'commit', '-m', 'chore: gitignore __*.py temp scripts'])
run(['git', 'push', 'origin', 'HEAD:refs/heads/main'])
print('Done.')

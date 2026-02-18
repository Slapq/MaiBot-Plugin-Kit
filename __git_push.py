import subprocess

repo = r's:\VSCODE\CodeX\MaiBot-Plugin-Kit'

def run(cmd):
    r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print('$', ' '.join(str(c) for c in cmd))
    if r.stdout.strip(): print('OUT:', r.stdout[:400])
    if r.stderr.strip(): print('ERR:', r.stderr[:400])
    return r.returncode

run(['git', 'add', '-A'])
run(['git', 'commit', '-m', 'feat(js): idiomatic JS API - arrow fn, mai.reply(), ctx.send/match/param/config, new docs'])
run(['git', 'push', 'origin', 'HEAD:refs/heads/main'])
print('Done.')

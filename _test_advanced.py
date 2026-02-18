"""测试 mai_advanced 模块和 advanced 模板"""
import sys, os, ast, shutil, subprocess
sys.path.insert(0, '.')

PASS = "[OK]"
FAIL = "[FAIL]"

def test(name, fn):
    try:
        fn()
        print(f"  {PASS} {name}")
    except Exception as e:
        print(f"  {FAIL} {name}")
        print(f"      {e}")

# 1. 导入测试
def t_import():
    from mai_advanced import AdvancedReplyBuilder, ReplyComponent, PromptModifier

def t_reply_component():
    from mai_advanced import ReplyComponent
    c1 = ReplyComponent.text("你好", typing=True)
    assert c1.type == "text"
    assert c1.extra["typing"] is True
    c2 = ReplyComponent.emoji("b64")
    assert c2.type == "emoji"
    c3 = ReplyComponent.image("imgb64")
    assert c3.type == "image"
    c4 = ReplyComponent.from_tuple(("text", "hello"))
    assert c4.content == "hello"

def t_create_advanced():
    result = subprocess.run(
        [sys.executable, '-m', 'mai_plugin_cli', 'create', '_test_adv_plugin',
         '--template', 'advanced', '--author', 'test', '--yes'],
        capture_output=True, text=True, encoding='utf-8'
    )
    assert '_test_adv_plugin' in result.stdout or 'success' in result.stdout.lower() or os.path.isdir('_test_adv_plugin')

def t_plugin_py_syntax():
    with open('_test_adv_plugin/plugin.py', encoding='utf-8') as f:
        code = f.read()
    ast.parse(code)  # 会在语法错误时抛出 SyntaxError

def t_manifest_valid():
    import json
    with open('_test_adv_plugin/_manifest.json', encoding='utf-8') as f:
        m = json.load(f)
    assert m.get('manifest_version') == 1
    assert 'advanced' in m.get('keywords', [])

print("=" * 50)
print("  mai_advanced 模块测试")
print("=" * 50)

test("导入 mai_advanced", t_import)
test("ReplyComponent 工厂方法", t_reply_component)
test("创建 advanced 模板", t_create_advanced)
test("plugin.py 语法合法", t_plugin_py_syntax)
test("manifest.json 合法", t_manifest_valid)

# 清理
if os.path.isdir('_test_adv_plugin'):
    shutil.rmtree('_test_adv_plugin')
    print("\n  [清理] _test_adv_plugin 已删除")

print("=" * 50)

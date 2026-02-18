"""快速验证 advanced 模板 - 不使用 subprocess"""
import sys, os, ast, json, shutil
sys.path.insert(0, '.')
os.chdir(os.path.dirname(os.path.abspath(__file__)))

ok = True

# 1. mai_advanced 导入
try:
    from mai_advanced import AdvancedReplyBuilder, ReplyComponent, PromptModifier
    from mai_advanced.reply_builder import ReplyComponent as RC
    c = RC.text("hello", typing=True)
    assert c.type == "text" and c.extra["typing"] is True
    c2 = RC.from_tuple(("emoji", "b64data"))
    assert c2.type == "emoji"
    print("[OK] mai_advanced 导入 + ReplyComponent 工厂方法")
except Exception as e:
    print(f"[FAIL] mai_advanced: {e}")
    ok = False

# 2. main.py choices 包含 advanced
try:
    content = open('mai_plugin_cli/commands/main.py', encoding='utf-8').read()
    assert '"advanced"' in content, "main.py choices 不含 advanced"
    print("[OK] main.py choices 已含 advanced")
except Exception as e:
    print(f"[FAIL] main.py: {e}")
    ok = False

# 3. 模拟模板替换 + 语法检查
try:
    template_py = open('mai_plugin_cli/templates/advanced/plugin.py', encoding='utf-8').read()
    replacements = {
        "{{PLUGIN_NAME}}": "test_adv",
        "{{PLUGIN_DISPLAY_NAME}}": "Test Adv",
        "{{PLUGIN_DESCRIPTION}}": "desc",
        "{{PLUGIN_VERSION}}": "1.0.0",
        "{{PLUGIN_AUTHOR}}": "tester",
        "{{PLUGIN_YEAR}}": "2025",
        "{{PLUGIN_CLASS_NAME}}": "TestAdvPlugin",
        "{{ACTION_CLASS_NAME}}": "TestAdvAction",
        "{{COMMAND_CLASS_NAME}}": "TestAdvCommand",
        "{{TOOL_CLASS_NAME}}": "TestAdvTool",
    }
    for k, v in replacements.items():
        template_py = template_py.replace(k, v)
    ast.parse(template_py)
    print("[OK] advanced plugin.py 替换后语法合法")
except SyntaxError as e:
    print(f"[FAIL] plugin.py 语法错误: {e}")
    ok = False

# 4. manifest.json 合法
try:
    with open('mai_plugin_cli/templates/advanced/_manifest.json', encoding='utf-8') as f:
        m = json.load(f)
    assert m.get('manifest_version') == 1
    assert 'advanced' in m.get('keywords', [])
    assert m['host_application']['min_version'] == '0.8.0'
    print("[OK] advanced _manifest.json 合法")
except Exception as e:
    print(f"[FAIL] manifest: {e}")
    ok = False

# 5. create.py TEMPLATE_INFO 含 advanced
try:
    from mai_plugin_cli.commands.create import TEMPLATE_INFO, validate_plugin_name, _build_class_prefix
    assert 'advanced' in TEMPLATE_INFO
    assert validate_plugin_name("test_adv")
    assert _build_class_prefix("test_adv") == "TestAdv"
    print("[OK] create.py TEMPLATE_INFO 含 advanced, 工具函数正常")
except Exception as e:
    print(f"[FAIL] create.py: {e}")
    ok = False

# 6. 文档文件存在
doc_files = [
    'docs/advanced/guide.md',
    'docs/advanced/reply-builder.md',
    'docs/advanced/prompt-modifier.md',
    'docs/advanced/reply-component.md',
]
for f in doc_files:
    if os.path.exists(f):
        print(f"[OK] {f}")
    else:
        print(f"[FAIL] 缺少文档: {f}")
        ok = False

print()
print("=" * 40)
if ok:
    print("  全部验证通过!")
else:
    print("  存在失败项，请检查")
print("=" * 40)

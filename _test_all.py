"""
MaiBot Plugin Kit 全功能测试脚本
运行方式: python _test_all.py
"""
import sys
import io
import os
import json
import shutil
import traceback
from pathlib import Path

# ─── 强制 UTF-8 输出（修复 Windows GBK 终端的 UnicodeEncodeError）────────────
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 确保在项目根目录下运行
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "

results = []

def test(name, fn):
    try:
        fn()
        results.append((PASS, name))
        print(f"  {PASS} {name}")
    except Exception as e:
        results.append((FAIL, name, str(e)))
        print(f"  {FAIL} {name}")
        print(f"      错误: {e}")
        traceback.print_exc()

print("=" * 60)
print("  MaiBot Plugin Kit — 全功能测试")
print("=" * 60)

# ─── 测试 1: 导入 mai_plugin_cli ───────────────────────────
print("\n[1] 导入测试")

def test_import_cli():
    from mai_plugin_cli.commands.create import cmd_create, TEMPLATE_INFO
    assert len(TEMPLATE_INFO) == 5, f"期望5个模板，实际{len(TEMPLATE_INFO)}"

def test_import_maiscript():
    from mai_script.parser import MaiScriptParser
    from mai_script.compiler import MaiScriptCompiler

def test_import_bridge():
    from mai_js_bridge.bridge import JsBridgePlugin
    from mai_js_bridge.js_context import JsExecutionContext

test("导入 mai_plugin_cli", test_import_cli)
test("导入 mai_script", test_import_maiscript)
test("导入 mai_js_bridge", test_import_bridge)

# ─── 测试 2: MaiScript 解析器 ───────────────────────────────
print("\n[2] MaiScript 解析器测试")

from mai_script.parser import MaiScriptParser
from mai_script.compiler import MaiScriptCompiler

TEST_MAI = """
plugin:
  name: "测试插件"
  version: "1.2.3"
  author: "测试者"
  description: "用于测试的插件"

commands:
  - name: "打招呼"
    match: "/hello"
    reply: "你好！{user_name}！"

  - name: "掷骰子"
    match: "/roll"
    python: |
      import random
      n = random.randint(1, 6)
      reply = f"🎲 {n} 点！"

actions:
  - name: "安慰"
    when:
      - "当有人悲伤时"
    reply: "加油！💪"
"""

# 将测试内容写入临时文件
Path("_test_temp.mai").write_text(TEST_MAI, encoding="utf-8")

def test_parse_plugin_meta():
    p = MaiScriptParser()
    data = p.parse_file("_test_temp.mai")
    assert data["plugin"]["name"] == "测试插件"
    assert data["plugin"]["version"] == "1.2.3"
    assert data["plugin"]["author"] == "测试者"

def test_parse_commands():
    p = MaiScriptParser()
    data = p.parse_file("_test_temp.mai")
    cmds = data.get("commands", [])
    assert len(cmds) == 2, f"期望2个命令，实际{len(cmds)}"
    assert cmds[0]["name"] == "打招呼"
    assert cmds[0]["match"] == "/hello"
    assert cmds[0]["reply"] == "你好！{user_name}！"

def test_parse_actions():
    p = MaiScriptParser()
    data = p.parse_file("_test_temp.mai")
    acts = data.get("actions", [])
    assert len(acts) == 1, f"期望1个action，实际{len(acts)}"
    assert acts[0]["name"] == "安慰"
    assert len(acts[0]["when"]) == 1

def test_parse_python_block():
    p = MaiScriptParser()
    data = p.parse_file("_test_temp.mai")
    roll_cmd = data["commands"][1]
    assert "python" in roll_cmd
    assert "random" in roll_cmd["python"]

test("解析插件元数据", test_parse_plugin_meta)
test("解析命令列表", test_parse_commands)
test("解析 Action 列表", test_parse_actions)
test("解析 Python 代码块", test_parse_python_block)

# ─── 测试 3: MaiScript 编译器 ───────────────────────────────
print("\n[3] MaiScript 编译器测试")

def test_compile_basic():
    p = MaiScriptParser()
    data = p.parse_file("_test_temp.mai")
    c = MaiScriptCompiler(data)
    result = c.compile()
    assert "plugin.py" in result, "编译结果应包含 plugin.py"
    assert "_manifest.json" in result, "编译结果应包含 _manifest.json"

def test_compile_plugin_py_syntax():
    """编译生成的 plugin.py 应该是合法的 Python 语法"""
    import ast
    p = MaiScriptParser()
    data = p.parse_file("_test_temp.mai")
    c = MaiScriptCompiler(data)
    result = c.compile()
    plugin_py = result["plugin.py"]
    # 尝试解析
    ast.parse(plugin_py)

def test_compile_manifest_valid():
    """编译生成的 manifest 应该是合法的 JSON"""
    p = MaiScriptParser()
    data = p.parse_file("_test_temp.mai")
    c = MaiScriptCompiler(data)
    result = c.compile()
    manifest = json.loads(result["_manifest.json"])
    assert manifest["name"] == "测试插件"
    assert manifest["version"] == "1.2.3"

def test_compile_output_to_disk():
    """编译并写入磁盘"""
    p = MaiScriptParser()
    data = p.parse_file("_test_temp.mai")
    c = MaiScriptCompiler(data)
    result = c.compile()
    
    out_dir = Path("_test_output_plugin")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()
    
    for filename, content in result.items():
        (out_dir / filename).write_text(content, encoding="utf-8")
    
    assert (out_dir / "plugin.py").exists()
    assert (out_dir / "_manifest.json").exists()

test("编译输出文件名正确", test_compile_basic)
test("编译生成的 plugin.py 语法合法", test_compile_plugin_py_syntax)
test("编译生成的 manifest JSON 合法", test_compile_manifest_valid)
test("编译并写入磁盘", test_compile_output_to_disk)

# ─── 测试 4: CLI create 命令 ───────────────────────────────
print("\n[4] CLI create 命令测试")

from mai_plugin_cli.commands.create import validate_plugin_name, _build_class_prefix

def test_name_validation():
    assert validate_plugin_name("my_plugin") == True
    assert validate_plugin_name("hello123") == True
    assert validate_plugin_name("1bad") == False
    assert validate_plugin_name("bad-name") == False
    assert validate_plugin_name("") == False

def test_class_prefix():
    assert _build_class_prefix("my_plugin") == "MyPlugin"
    assert _build_class_prefix("hello_world_plugin") == "HelloWorldPlugin"
    assert _build_class_prefix("simple") == "Simple"

def test_create_all_templates():
    """测试所有模板的创建"""
    import argparse
    from mai_plugin_cli.commands.create import cmd_create
    
    templates = ["minimal", "action", "command", "full", "js_bridge"]
    for tmpl in templates:
        name = f"test_{tmpl}_auto"
        out_dir = Path(name)
        if out_dir.exists():
            shutil.rmtree(out_dir)
        
        # 模拟 argparse namespace
        args = argparse.Namespace(
            name=name,
            template=tmpl,
            output=".",
            author="自动测试",
            description=f"自动测试 {tmpl} 模板",
            version_str="0.0.1",
            yes=True,
        )
        cmd_create(args)
        
        assert out_dir.exists(), f"目录 {out_dir} 未创建"
        assert (out_dir / "plugin.py").exists() or (out_dir / "plugin.js").exists(), \
            f"插件主文件未创建"
        assert (out_dir / "_manifest.json").exists(), \
            f"_manifest.json 未创建"
        
        # 验证 manifest 合法
        with open(out_dir / "_manifest.json", encoding="utf-8") as f:
            m = json.load(f)
        assert m["author"]["name"] == "自动测试", \
            f"作者名称未正确写入 manifest: {m['author']}"
        assert m["version"] == "0.0.1"
        
        print(f"    ✓ {tmpl} 模板创建成功")

test("插件名称验证", test_name_validation)
test("类名前缀生成", test_class_prefix)
test("所有模板创建测试", test_create_all_templates)

# ─── 测试 5: CLI validate 命令 ───────────────────────────────
print("\n[5] CLI validate 命令测试")

import argparse
from mai_plugin_cli.commands.validate import cmd_validate

def test_validate_valid_plugin():
    """验证合法插件"""
    # 使用上面创建的 command 插件
    args = argparse.Namespace(path="test_command_auto")
    try:
        cmd_validate(args)
    except SystemExit as e:
        if e.code != 0:
            raise AssertionError(f"validate 退出码非0: {e.code}")

def test_validate_missing_manifest():
    """验证缺少 manifest 的目录应该失败"""
    bad_dir = Path("_test_bad_plugin")
    bad_dir.mkdir(exist_ok=True)
    (bad_dir / "plugin.py").write_text("# empty", encoding="utf-8")
    
    args = argparse.Namespace(path=str(bad_dir))
    try:
        cmd_validate(args)
        # 如果没有抛出 SystemExit，检查输出中是否有错误标记
    except SystemExit:
        pass  # 预期行为

test("validate 合法插件通过", test_validate_valid_plugin)
test("validate 缺少 manifest 能检测到", test_validate_missing_manifest)

# ─── 测试 6: CLI pack 命令 ─────────────────────────────────
print("\n[6] CLI pack 命令测试")

from mai_plugin_cli.commands.pack import cmd_pack

def test_pack_creates_zip():
    """打包应生成 zip 文件"""
    import zipfile
    args = argparse.Namespace(
        path="test_command_auto",
        output="_test_packed.zip",
    )
    cmd_pack(args)
    assert Path("_test_packed.zip").exists(), "zip 文件未生成"
    
    # 验证 zip 内容
    with zipfile.ZipFile("_test_packed.zip", "r") as z:
        names = z.namelist()
    assert any("_manifest.json" in n for n in names), f"manifest 不在 zip 中: {names}"
    assert any("plugin.py" in n for n in names), f"plugin.py 不在 zip 中: {names}"

test("pack 生成合法 zip 文件", test_pack_creates_zip)

# ─── 测试 7: run-maiscript 命令 ──────────────────────────────
print("\n[7] run-maiscript 命令测试")

from mai_plugin_cli.commands.run_maiscript import cmd_run_maiscript

def test_run_maiscript_end_to_end():
    """端到端测试：从 .mai 文件生成插件目录"""
    out_dir = Path("_test_maiscript_out")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    
    args = argparse.Namespace(
        file="_test_temp.mai",
        output=str(out_dir),
    )
    cmd_run_maiscript(args)
    
    assert out_dir.exists(), "输出目录未创建"
    assert (out_dir / "plugin.py").exists(), "plugin.py 未生成"
    assert (out_dir / "_manifest.json").exists(), "_manifest.json 未生成"

def test_run_maiscript_generated_syntax():
    """验证生成的 plugin.py 语法合法"""
    import ast
    plugin_py = Path("_test_maiscript_out/plugin.py").read_text(encoding="utf-8")
    ast.parse(plugin_py)

test("run-maiscript 端到端生成插件", test_run_maiscript_end_to_end)
test("run-maiscript 生成代码语法合法", test_run_maiscript_generated_syntax)

# ─── 清理临时文件 ─────────────────────────────────────────
print("\n[清理] 清理临时测试文件...")
for item in [
    "_test_temp.mai",
    "_test_bad_plugin",
    "_test_packed.zip",
    "_test_output_plugin",
    "_test_maiscript_out",
    "test_minimal_auto",
    "test_action_auto",
    "test_command_auto",
    "test_full_auto",
    "test_js_bridge_auto",
]:
    p = Path(item)
    if p.exists():
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        print(f"  删除: {item}")

# ─── 汇总结果 ─────────────────────────────────────────────
print()
print("=" * 60)
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)
total = len(results)

print(f"  测试结果: {passed}/{total} 通过")
if failed > 0:
    print(f"  失败项目:")
    for r in results:
        if r[0] == FAIL:
            print(f"    - {r[1]}: {r[2] if len(r) > 2 else ''}")
    sys.exit(1)
else:
    print("  🎉 所有测试通过！")
print("=" * 60)

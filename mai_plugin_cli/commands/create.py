"""
mai create 命令实现
交互式创建麦麦插件，支持 --yes 非交互模式
"""
import os
import json
import shutil
import re
import sys
from pathlib import Path
from datetime import datetime

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

TEMPLATE_INFO = {
    "minimal": {
        "title": "🔹 Minimal（最简模板）",
        "desc": "最小化插件骨架，只有必要的结构，适合从零手写",
        "skill": "Python 基础",
    },
    "action": {
        "title": "🎭 Action（行为插件）",
        "desc": "让麦麦拥有新的自主行为，如发图/语音/搜索等，由 LLM 决定何时调用",
        "skill": "Python + 异步基础",
    },
    "command": {
        "title": "💻 Command（命令插件）",
        "desc": "响应固定命令（如 /ping /weather），精确触发，无 LLM 参与",
        "skill": "Python 基础",
    },
    "full": {
        "title": "🌟 Full（完整功能插件）",
        "desc": "包含 Action + Command + Tool + EventHandler 的完整示例，展示所有功能",
        "skill": "Python 进阶",
    },
    "js_bridge": {
        "title": "⚡ JS Bridge（JS 轻量插件）",
        "desc": "使用 JavaScript 编写简单插件逻辑，通过桥接器与麦麦交互",
        "skill": "JavaScript 基础",
    },
    "advanced": {
        "title": "🚀 Advanced（高级功能插件）",
        "desc": "演示回复组件注入、自定义提示词、底层 LLM 调用等高级功能，需要 mai_advanced 扩展层",
        "skill": "Python 进阶 + 异步",
    },
}


def validate_plugin_name(name: str) -> bool:
    """验证插件名称格式（英文+数字+下划线）"""
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", name))


def _is_interactive() -> bool:
    """检测当前是否在交互式终端运行"""
    return sys.stdin.isatty()


def _prompt(prompt_text: str, default: str, yes_mode: bool) -> str:
    """
    提示用户输入，支持默认值。
    在 yes_mode 或非交互式模式下直接返回默认值。
    """
    if yes_mode or not _is_interactive():
        return default
    try:
        value = input(f"{prompt_text} [{default}]: ").strip()
        return value if value else default
    except (KeyboardInterrupt, EOFError):
        print("\n\n已取消。")
        sys.exit(0)


def _confirm(prompt_text: str, default: bool, yes_mode: bool) -> bool:
    """
    询问用户 yes/no。
    在 yes_mode 模式下直接返回 default。
    """
    if yes_mode or not _is_interactive():
        return default
    hint = "Y/n" if default else "y/N"
    try:
        ans = input(f"{prompt_text} ({hint}): ").strip().lower()
        if not ans:
            return default
        return ans in ("y", "yes", "是")
    except (KeyboardInterrupt, EOFError):
        print("\n\n已取消。")
        sys.exit(0)


def select_template_interactive() -> str:
    """交互式选择模板"""
    print("\n📦 请选择插件模板：\n")
    keys = list(TEMPLATE_INFO.keys())
    for i, key in enumerate(keys, 1):
        info = TEMPLATE_INFO[key]
        print(f"  [{i}] {info['title']}")
        print(f"       {info['desc']}")
        print(f"       技术要求：{info['skill']}\n")

    while True:
        try:
            choice = input(f"请输入序号 (1-{len(keys)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
            else:
                print(f"❌ 请输入 1 到 {len(keys)} 之间的数字")
        except ValueError:
            print("❌ 请输入有效的数字")
        except (KeyboardInterrupt, EOFError):
            print("\n\n已取消。")
            sys.exit(0)


def _build_class_prefix(name: str) -> str:
    """将 my_plugin -> MyPlugin"""
    return "".join(word.capitalize() for word in name.split("_"))


def cmd_create(args):
    """创建新插件"""
    name = args.name
    yes_mode = getattr(args, "yes", False)

    # 验证插件名
    if not validate_plugin_name(name):
        print(f"❌ 插件名称 '{name}' 格式不正确！")
        print("   必须以字母开头，只能包含字母、数字和下划线")
        print("   示例：my_plugin, helloWorld, weather2025")
        sys.exit(1)

    # 选择模板
    template = args.template
    if template is None:
        if yes_mode or not _is_interactive():
            template = "minimal"
            print(f"ℹ️  非交互模式，使用默认模板：minimal")
        else:
            template = select_template_interactive()

    info = TEMPLATE_INFO[template]
    print(f"\n✅ 已选择模板：{info['title']}")

    # 获取插件信息
    if not yes_mode:
        print("\n📝 请填写插件信息（按回车使用默认值）：\n")

    default_desc = f"一个使用 {template} 模板创建的麦麦插件"
    author = args.author or _prompt("  作者名称", "未知作者", yes_mode)
    description = args.description or _prompt("  插件描述", default_desc, yes_mode)
    version = getattr(args, "version_str", None) or _prompt("  版本号", "1.0.0", yes_mode)

    # 确定输出路径
    output_dir = Path(args.output) / name
    if output_dir.exists():
        overwrite = _confirm(f"\n⚠️  目录 '{output_dir}' 已存在，是否覆盖？", False, yes_mode)
        if not overwrite:
            print("已取消。")
            sys.exit(0)
        shutil.rmtree(output_dir)

    # 验证模板目录
    template_dir = TEMPLATES_DIR / template
    if not template_dir.exists():
        print(f"❌ 模板目录不存在：{template_dir}")
        sys.exit(1)

    # 复制模板
    shutil.copytree(template_dir, output_dir)
    print(f"\n📁 正在创建插件目录：{output_dir}")

    # 计算替换值
    class_prefix = _build_class_prefix(name)
    replacements = {
        "{{PLUGIN_NAME}}": name,
        "{{PLUGIN_DISPLAY_NAME}}": name.replace("_", " ").title(),
        "{{PLUGIN_DESCRIPTION}}": description,
        "{{PLUGIN_VERSION}}": version,
        "{{PLUGIN_AUTHOR}}": author,
        "{{PLUGIN_YEAR}}": str(datetime.now().year),
        "{{PLUGIN_CLASS_NAME}}": class_prefix + "Plugin",
        "{{ACTION_CLASS_NAME}}": class_prefix + "Action",
        "{{COMMAND_CLASS_NAME}}": class_prefix + "Command",
        "{{TOOL_CLASS_NAME}}": class_prefix + "Tool",
        "{{HANDLER_CLASS_NAME}}": class_prefix + "EventHandler",
        "{{START_HANDLER_CLASS_NAME}}": class_prefix + "StartHandler",
    }

    # 递归替换所有文本文件中的模板变量
    for filepath in output_dir.rglob("*"):
        if filepath.is_file():
            try:
                content = filepath.read_text(encoding="utf-8")
                for k, v in replacements.items():
                    content = content.replace(k, v)
                filepath.write_text(content, encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                pass  # 跳过二进制文件

    # 更新 manifest.json
    manifest_path = output_dir / "_manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            manifest["name"] = name.replace("_", " ").title()
            manifest["version"] = version
            manifest["description"] = description
            if "author" not in manifest or not isinstance(manifest["author"], dict):
                manifest["author"] = {}
            manifest["author"]["name"] = author
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️  更新 manifest.json 时出现警告：{e}")

    # 成功提示
    print(f"\n🎉 插件 '{name}' 创建成功！\n")
    print("📂 目录结构：")
    for p in sorted(output_dir.rglob("*")):
        rel = p.relative_to(output_dir.parent)
        indent = "  " * (len(rel.parts) - 1)
        icon = "📁" if p.is_dir() else "📄"
        print(f"  {indent}{icon} {p.name}")

    print(f"\n🚀 下一步：")
    main_file = "plugin.js" if template == "js_bridge" else "plugin.py"
    print(f"  1. 进入目录：cd {output_dir}")
    print(f"  2. 编辑主文件：{main_file}")
    print(f"  3. 验证插件：python -m mai_plugin_cli validate {output_dir}")
    print(f"  4. 复制到 MaiBot/plugins/ 目录，重启 MaiBot")
    print(f"\n📚 文档：https://maibot-plugin-kit.pages.dev/guide/\n")

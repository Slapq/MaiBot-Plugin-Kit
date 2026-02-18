"""
mai list-templates 命令实现
"""


TEMPLATE_DETAILS = {
    "minimal": {
        "title": "🔹 Minimal（最简模板）",
        "desc": "最小化插件骨架，只有必要的结构文件",
        "files": ["_manifest.json", "plugin.py", "README.md"],
        "skill": "Python 基础",
        "use_case": "从零开始手写插件，或学习插件结构",
    },
    "action": {
        "title": "🎭 Action（行为插件）",
        "desc": "扩展麦麦的自主行为能力，由 LLM 智能决定何时触发",
        "files": ["_manifest.json", "plugin.py", "config.schema.py", "README.md"],
        "skill": "Python + 异步基础",
        "use_case": "发表情、搜索信息、播放音乐、天气查询等智能行为",
    },
    "command": {
        "title": "💻 Command（命令插件）",
        "desc": "精确响应用户的固定命令，立即执行无需 LLM",
        "files": ["_manifest.json", "plugin.py", "README.md"],
        "skill": "Python 基础",
        "use_case": "/ping /help /status 等管理命令",
    },
    "full": {
        "title": "🌟 Full（完整功能插件）",
        "desc": "包含 Action + Command + Tool + EventHandler 的完整功能示例",
        "files": ["_manifest.json", "plugin.py", "config.schema.py", "README.md", "utils.py"],
        "skill": "Python 进阶",
        "use_case": "需要多种功能的复杂插件，如签到系统、游戏等",
    },
    "js_bridge": {
        "title": "⚡ JS Bridge（JS 轻量插件）",
        "desc": "使用 JavaScript 编写插件逻辑，通过内置桥接器与麦麦交互",
        "files": ["_manifest.json", "plugin.py", "plugin.js", "README.md"],
        "skill": "JavaScript 基础",
        "use_case": "前端开发者、不熟悉 Python 的用户快速开发简单插件",
    },
}


def cmd_list_templates(args):
    print("\n📦 MaiBot 插件可用模板\n")
    print("=" * 60)

    for key, info in TEMPLATE_DETAILS.items():
        print(f"\n  {info['title']}")
        print(f"  模板标识：{key}")
        print(f"  描述：{info['desc']}")
        print(f"  技术要求：{info['skill']}")
        print(f"  适用场景：{info['use_case']}")
        print(f"  包含文件：{', '.join(info['files'])}")
        print(f"  创建命令：mai create my_plugin -t {key}")
        print()

    print("=" * 60)
    print("\n💡 使用示例：")
    print("  mai create weather_plugin -t action      # 天气查询 Action 插件")
    print("  mai create admin_commands -t command     # 管理命令插件")
    print("  mai create my_game -t full               # 完整游戏插件")
    print("  mai create quick_tool -t js_bridge       # JS 快速工具插件")
    print()

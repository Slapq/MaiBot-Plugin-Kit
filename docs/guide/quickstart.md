# 🚀 快速开始指南

本指南将帮助你在 **5 分钟内**创建并运行你的第一个 MaiBot 插件。

## 前置条件

- Python 3.9+
- 已安装并运行中的 MaiBot（v0.7.0+）
- 基本的命令行操作能力

## 安装脚手架

将 `MaiBot-Plugin-Kit` 克隆或下载到本地：

```bash
git clone https://github.com/your-repo/MaiBot-Plugin-Kit.git
cd MaiBot-Plugin-Kit
```

> 💡 也可以直接将 `mai_plugin_cli`、`mai_js_bridge`、`mai_script` 目录复制到你的工作目录中使用。

## 创建第一个插件

### 方式一：交互式创建（推荐）

```bash
python -m mai_plugin_cli create my_first_plugin
```

然后按提示选择模板和填写信息：

```
📦 请选择插件模板：

  [1] 🔹 Minimal（最简模板）
       最小化插件骨架，只有必要的结构，适合从零手写
       技术要求：Python 基础

  [2] 🎭 Action（行为插件）
       让麦麦拥有新的自主行为
       技术要求：Python + 异步基础

  [3] 💻 Command（命令插件）
       响应固定命令（如 /ping /weather）
       技术要求：Python 基础

  [4] 🌟 Full（完整功能插件）
       包含所有组件类型的完整示例
       技术要求：Python 进阶

  [5] ⚡ JS Bridge（JS 轻量插件）
       使用 JavaScript 编写插件逻辑
       技术要求：JavaScript 基础

请输入序号 (1-5): 3
```

### 方式二：直接指定模板

```bash
# Command 插件（响应 /ping 等命令）
python -m mai_plugin_cli create ping_plugin -t command

# Action 插件（麦麦自主行为）
python -m mai_plugin_cli create weather_action -t action --author "你的名字"

# JS 插件（JavaScript 编写）
python -m mai_plugin_cli create js_plugin -t js_bridge
```

## 目录结构说明

创建后的目录结构（以 `command` 模板为例）：

```
my_first_plugin/
├── _manifest.json    ← 插件元数据（必须）
├── plugin.py         ← 插件主文件（在此编写逻辑）
└── README.md         ← 插件说明文档
```

## 编写插件逻辑

打开 `plugin.py`，找到 `execute()` 方法，修改你的逻辑：

```python
async def execute(self) -> Tuple[bool, Optional[str], bool]:
    # 获取用户输入的参数（如果有的话）
    param = self.matched.group(1) if self.matched else None
    
    if param == "hello":
        await self.send_text("👋 你好！")
    else:
        await self.send_text(f"✅ 收到了命令！参数：{param or '无'}")
    
    return True, "执行成功", True
```

## 安装插件到 MaiBot

将插件目录复制到 MaiBot 的 `plugins/` 目录：

```bash
# Windows
xcopy /E /I my_first_plugin "C:\MaiBot\plugins\my_first_plugin"

# Linux/Mac
cp -r my_first_plugin /path/to/MaiBot/plugins/
```

然后**重启 MaiBot**，插件就会自动加载。

## 验证插件

```bash
python -m mai_plugin_cli validate ./my_first_plugin
```

输出示例：
```
🔍 正在验证插件：/path/to/my_first_plugin

📂 检查文件结构...
  ✅ _manifest.json
  ✅ plugin.py

📋 检查 manifest.json...
  ✅ manifest_version = 1
  ✅ name = My First Plugin
  ✅ version = 1.0.0
  ...

==================================================
✅ 验证通过！共 2 个警告
```

## 下一步

- 📖 了解 [插件架构](/guide/architecture)
- 📤 查看 [发送 API 文档](/api/send_api)
- 🤖 学习如何使用 [LLM API](/api/llm_api)
- ✨ 尝试 [MaiScript 零代码开发](/maiscript/intro)

# 🚀 快速开始

本指南将带你用 **MaiBot Plugin Kit** 的工具从零开始开发一个麦麦插件。

## 什么是 MaiBot Plugin Kit？

MaiBot Plugin Kit 是一个**插件开发工具包**，提供：

| 工具 | 作用 |
|------|------|
| `mai_plugin_cli`（`mai` 命令） | 脚手架工具：创建/验证/打包插件 |
| `mai_script` | MaiScript 编译器：写 YAML 自动生成插件 |
| `mai_js_bridge` | JS 桥接层：用 JavaScript 写插件逻辑 |
| `mai_advanced` | 高级 API：自定义 prompt、回复注入、重写 |

## 前置条件

- Python 3.10+
- 已克隆 [MaiBot](https://github.com/Mai-with-u/MaiBot)（插件最终要放在 MaiBot 里运行）
- 本工具包位于 `MaiBot/../MaiBot-Plugin-Kit/` 或已安装

## 安装脚手架工具

```bash
# 方式 A：直接从源码使用（推荐开发时）
cd MaiBot-Plugin-Kit
pip install -e .

# 安装成功后可以直接用 mai 命令
mai --help
```

安装完成后你会看到：

```
  __  __       _   ____        _       _
 |  \/  |     (_) |  _ \      | |     | |
 | \  / | __ _ _  | |_) | ___ | |_   | |
 ...
  麦麦插件脚手架工具 v1.0.0  —  让插件开发变得简单！
```

---

## 方式一：用 CLI 脚手架快速创建（推荐）

### 1. 创建插件项目

```bash
# 交互式创建（会提示选择模板）
mai create my_plugin

# 指定模板直接创建
mai create my_plugin -t command      # 命令插件
mai create my_plugin -t action       # 行为插件
mai create my_plugin -t full         # 包含全部组件的完整插件
mai create my_plugin -t js_bridge    # JS 插件
mai create my_plugin -t advanced     # 高级功能插件

# 带参数（非交互模式）
mai create weather_plugin -t command \
    --author "你的名字" \
    --description "天气查询插件" \
    --version-str "1.0.0" \
    -y
```

可选模板列表（`mai list-templates`）：

| 模板 | 说明 | 推荐人群 |
|------|------|----------|
| `minimal` | 最简骨架，只有必要结构 | 有经验、从零手写 |
| `action` | 麦麦自主触发的行为 | Python 基础 |
| `command` | 用户输入命令触发 | Python 基础 |
| `full` | Action + Command + Tool + EventHandler | Python 进阶 |
| `js_bridge` | 用 JavaScript 写逻辑 | 前端开发者 |
| `advanced` | 自定义 prompt、回复注入 | Python 进阶 |

### 2. 查看生成的文件

```bash
my_plugin/
├── _manifest.json   ← 插件描述文件（名称/版本/作者）
├── plugin.py        ← 插件主文件（已填写你的信息）
├── config.toml      ← 配置文件（自动生成，首次运行后出现）
└── README.md        ← 说明文档
```

### 3. 编辑 plugin.py

生成的 `plugin.py` 已经包含正确的类名和基本结构，**所有 `{{PLUGIN_NAME}}` 等占位符都已被替换**：

```python
# 生成后的实际内容（以 weather_plugin 为例）
class WeatherPluginCommand(BaseCommand):
    command_name = "weather_plugin"
    command_description = "天气查询插件"
    command_pattern = r"^/weather_plugin$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        reply_message = self.get_config("command.reply", "收到命令！")
        await self.send_text(reply_message)
        return True, "命令执行成功", True
```

修改 `command_pattern` 和 `execute()` 方法实现你的功能。

### 4. 验证插件

```bash
mai validate ./my_plugin
```

输出示例：
```
✅ _manifest.json 格式正确
✅ plugin.py 语法正确
✅ 插件结构验证通过
```

### 5. 打包插件

```bash
mai pack ./my_plugin
# 生成 my_plugin-1.0.0.zip，可分享给他人
```

### 6. 部署到 MaiBot

将插件目录复制到 MaiBot 的 `plugins/` 文件夹：

```
MaiBot/
├── bot.py
└── plugins/
    └── my_plugin/      ← 把这个文件夹放进去
        ├── _manifest.json
        └── plugin.py
```

然后重启 MaiBot：
```bash
python bot.py
```

---

## 方式二：MaiScript（零代码，适合小白）

用 YAML 写插件，一键编译为 Python。详见 [MaiScript 文档](/maiscript/intro)。

```yaml
# my_plugin.mai
plugin:
  name: "打招呼插件"
  author: "你的名字"
  description: "回应 /hello 命令"

commands:
  - name: "打招呼"
    match: "/hello"
    reply: "你好呀！😊"
```

```bash
mai run-maiscript my_plugin.mai
# ✅ 编译成功！插件目录：my_plugin/
```

---

## 方式三：JS 插件

用 JavaScript 写插件逻辑，详见 [JS 插件文档](/js/quickstart)。

```bash
mai create my_plugin -t js_bridge
# 编辑 plugin.js
```

---

## 编写真实插件示例

### 天气查询命令插件

```bash
mai create weather_plugin -t command -y
```

修改 `weather_plugin/plugin.py`：

```python
import aiohttp
from typing import List, Optional, Tuple, Type

from src.plugin_system import (
    BasePlugin, register_plugin, BaseCommand, ComponentInfo, ConfigField,
)
from src.common.logger import get_logger

logger = get_logger("weather_plugin")


class WeatherPluginCommand(BaseCommand):
    command_name = "weather"
    command_description = "查询天气"
    command_pattern = r"^/weather\s+(?P<city>\S+)$"   # /weather 北京

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        city = self.matched_groups.get("city", "")
        if not city:
            await self.send_text("用法：/weather 城市名")
            return False, "缺少城市", True

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://wttr.in/{city}?format=3&lang=zh",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    result = await resp.text()
            await self.send_text(f"🌤️ {result}")
        except Exception as e:
            await self.send_text(f"❌ 查询失败：{e}")

        return True, f"查询 {city} 天气", True


@register_plugin
class WeatherPluginPlugin(BasePlugin):
    plugin_name: str = "weather_plugin"
    enable_plugin: bool = True
    dependencies: List[str] = []
    python_dependencies: List[str] = ["aiohttp"]   # 声明依赖
    config_file_name: str = "config.toml"
    config_schema: dict = {}

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [(WeatherPluginCommand.get_command_info(), WeatherPluginCommand)]
```

验证并部署：
```bash
mai validate ./weather_plugin
cp -r weather_plugin/ ../MaiBot/plugins/
```

---

## 下一步

- 🏗️ [插件架构详解（Action / Command / Tool / EventHandler）](/guide/architecture)
- ✨ [MaiScript 零代码插件](/maiscript/intro)
- ⚡ [JS 插件开发](/js/quickstart)
- 🚀 [高级功能（自定义 Prompt / 回复注入）](/advanced/guide)
- 📤 [发送 API](/api/send_api)

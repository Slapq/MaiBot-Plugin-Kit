# 🚀 快速开始

本指南将带你用真实可运行的代码创建第一个 MaiBot 插件。

## 前置条件

- **Python 3.10+**（MaiBot 要求）
- 已克隆并运行 [MaiBot](https://github.com/Mai-with-u/MaiBot)
- 了解基本 Python 语法

## 插件放置位置

将你的插件目录放入 MaiBot 根目录的 `plugins/` 文件夹：

```
MaiBot/
├── bot.py
├── plugins/
│   ├── __init__.py
│   └── my_first_plugin/    ← 你的插件在这里
│       ├── _manifest.json
│       └── plugin.py
```

## 最简插件（5 分钟上手）

### 第一步：创建 `_manifest.json`

```json
{
  "manifest_version": 1,
  "name": "我的第一个插件",
  "version": "1.0.0",
  "description": "Hello World 插件",
  "author": {
    "name": "你的名字"
  }
}
```

### 第二步：创建 `plugin.py`

```python
from typing import List, Tuple, Type

from src.plugin_system import (
    BasePlugin,
    register_plugin,
    ComponentInfo,
    ConfigField,
)

@register_plugin
class MyFirstPlugin(BasePlugin):
    """我的第一个 MaiBot 插件"""

    plugin_name: str = "my_first_plugin"
    enable_plugin: bool = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name: str = "config.toml"
    config_schema: dict = {}

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return []
```

### 第三步：启动 MaiBot

```bash
python bot.py
```

日志中看到插件加载成功即完成 🎉

---

## 添加 Command（响应命令）

用户输入 `/hello` 时，麦麦立即回复：

```python
import datetime
from typing import List, Optional, Tuple, Type

from src.plugin_system import (
    BasePlugin, register_plugin,
    BaseCommand, ComponentInfo, ConfigField,
)
from src.common.logger import get_logger

logger = get_logger("my_plugin")


class HelloCommand(BaseCommand):
    """响应 /hello 命令"""

    command_name = "hello"
    command_description = "打招呼命令"
    command_pattern = r"^/hello$"          # 精确匹配

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        await self.send_text("你好！😊")
        # 返回 (成功, 日志, 是否拦截后续处理)
        return True, "打招呼成功", True


class TimeCommand(BaseCommand):
    """响应 /time 命令"""

    command_name = "time"
    command_description = "查询当前时间"
    command_pattern = r"^/time$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        fmt = self.get_config("time.format", "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now().strftime(fmt)
        await self.send_text(f"⏰ 当前时间：{now}")
        return True, f"时间: {now}", True


@register_plugin
class MyPlugin(BasePlugin):

    plugin_name: str = "my_plugin"
    enable_plugin: bool = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name: str = "config.toml"

    config_schema: dict = {
        "time": {
            "format": ConfigField(type=str, default="%Y-%m-%d %H:%M:%S", description="时间格式"),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            (HelloCommand.get_command_info(), HelloCommand),
            (TimeCommand.get_command_info(), TimeCommand),
        ]
```

---

## 添加 Action（麦麦主动触发）

Action 由麦麦的决策系统自主判断是否使用，无需用户输入命令：

```python
from src.plugin_system import (
    BasePlugin, register_plugin,
    BaseAction, ComponentInfo, ConfigField,
    ActionActivationType,
)

class GreetAction(BaseAction):
    """问候 Action"""

    action_name = "my_greet"
    action_description = "向用户发送友好问候"

    # 激活方式：ALWAYS(始终) / RANDOM(随机) / KEYWORD(关键词) / NEVER(禁用)
    activation_type = ActionActivationType.KEYWORD
    activation_keywords = ["你好", "hello", "hi"]
    keyword_case_sensitive = False

    # 帮助 LLM 判断何时选用此 Action
    action_require = [
        "当有人主动打招呼时使用",
        "不要连续使用",
    ]
    associated_types = ["text"]
    action_parameters = {
        "greeting": "要发送的问候语",
    }

    async def execute(self) -> Tuple[bool, str]:
        greeting = self.action_data.get("greeting", "你好！")
        await self.send_text(greeting)
        return True, "问候成功"
```

---

## 带参数的命令

使用命名捕获组 `(?P<参数名>正则)` 提取参数：

```python
class WeatherCommand(BaseCommand):
    command_name = "weather"
    command_description = "查询天气"
    # 匹配：/weather 北京
    command_pattern = r"^/weather\s+(?P<city>\S+)$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        city = self.matched_groups.get("city", "")
        await self.send_text(f"查询 {city} 的天气中...")
        return True, f"查询城市: {city}", True
```

---

## 配置文件

在插件类中定义 `config_schema`，MaiBot 会自动生成 `config.toml`：

```python
from src.plugin_system import ConfigField

config_schema = {
    "plugin": {
        "enabled": ConfigField(type=bool, default=True, description="是否启用"),
    },
    "greeting": {
        "message": ConfigField(type=str, default="你好！", description="问候语"),
        "use_emoji": ConfigField(type=bool, default=True, description="是否使用表情"),
    },
}
```

在组件中通过 `self.get_config("section.key", 默认值)` 读取：

```python
message = self.get_config("greeting.message", "你好！")
```

> ⚠️ **不要手动创建 config.toml！** 让 MaiBot 自动生成。

---

## 消息类型

`associated_types` 和 `send_type()` 支持的消息类型（依赖 Adapter 支持）：

| 类型 | 说明 | 内容格式 |
|------|------|---------|
| `text` | 文本 | 字符串 |
| `emoji` | 表情包 | base64（无头） |
| `image` | 图片 | base64（无头） |
| `reply` | 回复 | 消息 ID |
| `voice` | 语音 | wav base64 |
| `voiceurl` | 语音 URL | URL 字符串 |
| `music` | 网易云音乐 | 音乐 ID |
| `videourl` | 视频 URL | URL 字符串 |
| `file` | 文件 | 文件路径 |

---

## 下一步

- 🏗️ [插件架构详解](/guide/architecture)
- 📤 [发送 API](/api/send_api)
- 🤖 [LLM API](/api/llm_api)
- ✨ [MaiScript 零代码开发](/maiscript/intro)

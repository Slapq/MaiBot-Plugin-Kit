# 🏗️ 插件架构详解

## 插件目录结构

```
MaiBot/
├── bot.py
├── plugins/
│   └── my_plugin/
│       ├── _manifest.json   ← 插件元数据（必须）
│       ├── plugin.py        ← 插件主代码（必须）
│       ├── config.toml      ← 自动生成的配置文件（不要手动创建）
│       └── README.md        ← 可选
```

---

## 四种组件类型

| 组件 | 基类 | 触发方式 | 返回值 |
|------|------|---------|--------|
| **Action** | `BaseAction` | 麦麦决策系统自主选择 | `Tuple[bool, str]` |
| **Command** | `BaseCommand` | 用户消息匹配正则 | `Tuple[bool, Optional[str], bool]` |
| **Tool** | `BaseTool` | LLM 生成回复时主动调用 | `Dict[str, Any]` |
| **EventHandler** | `BaseEventHandler` | 系统事件（消息/启动/停止） | `Tuple[bool, bool, Optional[str], None, None]` |

---

## Action 激活机制（两层决策）

```
第一层：激活控制（Action 是否进入候选池）
    ALWAYS   → 始终进入
    RANDOM   → 按 random_activation_probability 概率进入
    KEYWORD  → 消息包含 activation_keywords 时进入
    NEVER    → 永不进入

第二层：使用决策（麦麦是否选择使用）
    LLM 根据 action_require 和聊天上下文决定
```

---

## EventType 可用事件

```python
from src.plugin_system import EventType

EventType.ON_MESSAGE   # 每条消息触发
EventType.ON_START     # MaiBot 启动时触发（连接数据库、初始化资源）
EventType.ON_STOP      # MaiBot 停止时触发（清理资源、断开连接）
```

### EventHandler 返回值说明

```python
async def execute(self, message) -> Tuple[bool, bool, Optional[str], None, None]:
    #                                     成功   继续传递  日志描述   保留  保留
    return True, True, "处理成功", None, None
```

- **第1个 bool**：是否执行成功
- **第2个 bool**：是否继续将事件传递给后续 Handler（`False` 表示拦截）
- **第3个 Optional[str]**：日志描述，可为 `None`

---

## 完整插件骨架

```python
from typing import Any, Dict, List, Optional, Tuple, Type

from src.plugin_system import (
    BasePlugin, register_plugin,
    BaseAction, BaseCommand, BaseTool, BaseEventHandler,
    ComponentInfo, ActionActivationType, ConfigField,
    EventType, MaiMessages, ToolParamType, ReplyContentType,
    emoji_api,
)
from src.plugin_system.base.config_types import section_meta
from src.common.logger import get_logger

logger = get_logger("my_plugin")


# ─────── Action ───────────────────────────────
class MyAction(BaseAction):
    action_name = "my_action"
    action_description = "动作描述"
    activation_type = ActionActivationType.RANDOM
    random_activation_probability = 0.2
    action_require = ["合适时机", "不要频繁"]
    associated_types = ["text"]
    action_parameters = {"content": "发送的内容"}

    async def execute(self) -> Tuple[bool, str]:
        await self.send_text(self.action_data.get("content", ""))
        return True, "执行成功"


# ─────── Command ──────────────────────────────
class MyCommand(BaseCommand):
    command_name = "mycmd"
    command_description = "命令描述"
    command_pattern = r"^/mycmd(?:\s+(?P<arg>.+))?$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        arg = self.matched_groups.get("arg", "")
        await self.send_text(f"收到：{arg}")
        return True, "命令成功", True


# ─────── Tool ─────────────────────────────────
class MyTool(BaseTool):
    name = "my_tool"
    description = "工具描述（供 LLM 理解）"
    available_for_llm = True
    parameters = [
        ("query", ToolParamType.STRING, "查询内容", True, None),
    ]

    async def execute(self, function_args: Dict[str, Any]) -> Dict[str, Any]:
        query = function_args.get("query", "")
        return {"name": self.name, "content": f"查询结果：{query}"}


# ─────── EventHandler ─────────────────────────
class MyStartHandler(BaseEventHandler):
    event_type = EventType.ON_START
    handler_name = "my_start_handler"
    handler_description = "启动时初始化"

    async def execute(self, message: Optional[Any]) -> Tuple[bool, bool, Optional[str], None, None]:
        logger.info("[my_plugin] 插件已启动")
        return True, True, None, None, None


class MyMessageHandler(BaseEventHandler):
    event_type = EventType.ON_MESSAGE
    handler_name = "my_message_handler"
    handler_description = "处理每条消息"

    async def execute(self, message: Optional[MaiMessages]) -> Tuple[bool, bool, Optional[str], None, None]:
        if not message:
            return True, True, None, None, None
        # 处理消息...
        return True, True, None, None, None


# ─────── 插件注册 ──────────────────────────────
@register_plugin
class MyPlugin(BasePlugin):
    plugin_name: str = "my_plugin"
    enable_plugin: bool = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name: str = "config.toml"

    # config_section_descriptions 可以使用 section_meta 添加顺序/折叠
    config_section_descriptions = {
        "plugin": "插件基本配置",
        "feature": "功能配置",
    }
    # 或使用 section_meta 高级模式：
    # from src.plugin_system.base.config_types import section_meta
    # config_section_descriptions = {
    #     "plugin": section_meta("插件基本配置", order=1),
    #     "feature": section_meta("功能配置", collapsed=True, order=2),
    # }

    config_schema: dict = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用"),
            "config_version": ConfigField(type=str, default="1.0.0", description="版本"),
        },
        "feature": {
            "message": ConfigField(type=str, default="你好", description="默认消息"),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            (MyAction.get_action_info(), MyAction),
            (MyCommand.get_command_info(), MyCommand),
            (MyTool.get_tool_info(), MyTool),
            (MyStartHandler.get_handler_info(), MyStartHandler),
            (MyMessageHandler.get_handler_info(), MyMessageHandler),
        ]
```

---

## ConfigField 完整参数

```python
ConfigField(
    type=str,                    # 数据类型（必须）
    default="默认值",            # 默认值（必须）
    description="说明文字",      # 说明，写入 toml 注释（必须）

    # WebUI 显示相关（可选）
    label="显示标签",            # WebUI 中显示的字段名
    hint="提示文字",             # WebUI 输入框下方的提示
    placeholder="输入示例",      # 输入框占位符
    disabled=False,              # True 表示只读（展示用）
    order=1,                     # 在 section 内的排列顺序
    input_type="textarea",       # 输入类型："text"/"textarea"/"password"
    rows=5,                      # textarea 行数
    choices=["选项A","选项B"],   # 下拉选项（type=str 时有效）
    min=0,                       # 数值最小值
    max=100,                     # 数值最大值
    step=1.0,                    # 数值步长
)
```

---

## section_meta 用法

```python
from src.plugin_system.base.config_types import section_meta

config_section_descriptions = {
    "plugin": section_meta("插件基本配置", order=1),
    "advanced": section_meta("高级设置", collapsed=True, order=10),
}
```

- `collapsed=True`：WebUI 中默认折叠该 section
- `order`：section 在 WebUI 中的排列顺序（数字越小越靠前）

---

## _manifest.json 完整格式

```json
{
  "manifest_version": 1,
  "name": "插件显示名称",
  "version": "1.0.0",
  "description": "插件功能描述",
  "author": {
    "name": "你的名字",
    "url": "https://github.com/yourname"
  },
  "license": "MIT",
  "homepage_url": "https://github.com/yourname/my-plugin",
  "repository_url": "https://github.com/yourname/my-plugin",
  "keywords": ["keyword1", "keyword2"],
  "categories": ["tools", "fun"],
  "host_application": {
    "min_version": "0.7.0",
    "max_version": "9.9.9"
  },
  "plugin_info": {
    "is_built_in": false,
    "plugin_type": "general",
    "components": [
      {"type": "action", "name": "my_action", "description": "动作描述"},
      {"type": "command", "name": "mycmd", "description": "命令描述"}
    ]
  }
}
```

**必须字段**：`manifest_version`、`name`、`version`、`description`、`author.name`  
**可选字段**：其余均可省略，但建议填写 `license` 和 `keywords`

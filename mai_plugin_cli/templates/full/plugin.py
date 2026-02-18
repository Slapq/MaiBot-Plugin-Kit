"""
{{PLUGIN_DISPLAY_NAME}} - 完整功能插件

{{PLUGIN_DESCRIPTION}}

作者：{{PLUGIN_AUTHOR}}
版本：{{PLUGIN_VERSION}}

包含所有组件类型：Action / Command / Tool / EventHandler
删除不需要的部分即可。
"""

from typing import Any, Dict, List, Optional, Tuple, Type

from src.plugin_system import (
    BasePlugin,
    register_plugin,
    BaseAction,
    BaseCommand,
    BaseTool,
    BaseEventHandler,
    ComponentInfo,
    ActionActivationType,
    ConfigField,
    EventType,
    MaiMessages,
    ToolParamType,
)
from src.common.logger import get_logger

logger = get_logger("{{PLUGIN_NAME}}")


# ═══════════════════════════════════════════════
#  Action 组件：由麦麦自主决策是否触发
# ═══════════════════════════════════════════════

class {{ACTION_CLASS_NAME}}(BaseAction):
    """主动行为组件"""

    action_name = "{{PLUGIN_NAME}}_action"
    action_description = "{{PLUGIN_DESCRIPTION}}"
    activation_type = ActionActivationType.RANDOM
    random_activation_probability = 0.2

    action_require = [
        "当场景适合时使用",
        "不要连续频繁触发",
    ]
    associated_types = ["text"]
    action_parameters = {
        "content": "要发送的内容描述",
        "reason": "触发原因",
    }
    parallel_action = False

    async def execute(self) -> Tuple[bool, str]:
        content = self.action_data.get("content", "")
        message = self.get_config("action.message", "你好！")

        logger.info(f"[{{PLUGIN_NAME}}] Action 触发，user={self.user_nickname}")
        await self.send_text(message)

        await self.store_action_info(
            action_build_into_prompt=True,
            action_prompt_display=f"执行了 {{PLUGIN_NAME}} 行为",
            action_done=True,
        )
        return True, "Action 执行成功"


# ═══════════════════════════════════════════════
#  Command 组件：用户输入命令时触发
# ═══════════════════════════════════════════════

class {{COMMAND_CLASS_NAME}}(BaseCommand):
    """命令响应组件"""

    command_name = "{{PLUGIN_NAME}}"
    command_description = "{{PLUGIN_DESCRIPTION}}"
    # 使用命名捕获组提取参数：(?P<param_name>regex)
    command_pattern = r"^/{{PLUGIN_NAME}}(?:\s+(?P<param>.+))?$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        param = self.matched_groups.get("param", "")
        reply = self.get_config("command.reply", "收到！")

        logger.info(f"[{{PLUGIN_NAME}}] Command 触发，param={param}")
        await self.send_text(f"{reply}（参数：{param}）" if param else reply)

        return True, "Command 执行成功", True


# ═══════════════════════════════════════════════
#  Tool 组件：供 LLM 在生成回复时调用
# ═══════════════════════════════════════════════

class {{TOOL_CLASS_NAME}}(BaseTool):
    """工具组件 - LLM 可调用"""

    name = "{{PLUGIN_NAME}}_tool"
    description = "工具功能描述，帮助 LLM 理解何时调用"
    parameters = [
        # (参数名, 类型, 描述, 是否必须, 默认值)
        ("input", ToolParamType.STRING, "输入内容", True, None),
    ]
    available_for_llm = True

    async def execute(self, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """Tool 执行逻辑，返回 {"name": self.name, "content": 结果字符串}"""
        input_val = function_args.get("input", "")
        result = f"处理结果：{input_val}"
        return {"name": self.name, "content": result}


# ═══════════════════════════════════════════════
#  EventHandler 组件：监听系统事件
# ═══════════════════════════════════════════════

class {{HANDLER_CLASS_NAME}}Start(BaseEventHandler):
    """
    启动事件处理器 - MaiBot 启动时执行一次

    event_type 可选：
    - EventType.ON_START    : 启动时触发（初始化资源）
    - EventType.ON_STOP     : 停止时触发（清理资源）
    - EventType.ON_MESSAGE  : 每条消息触发
    """

    event_type = EventType.ON_START
    handler_name = "{{PLUGIN_NAME}}_start"
    handler_description = "启动初始化处理器"

    async def execute(self, message: Optional[Any]) -> Tuple[bool, bool, Optional[str], None, None]:
        """ON_START 时 message 为 None"""
        logger.info(f"[{{PLUGIN_NAME}}] 插件已启动，执行初始化...")
        return True, True, None, None, None


class {{HANDLER_CLASS_NAME}}(BaseEventHandler):
    """消息事件处理器 - 每条消息触发"""

    event_type = EventType.ON_MESSAGE
    handler_name = "{{PLUGIN_NAME}}_handler"
    handler_description = "消息事件处理器"

    async def execute(self, message: Optional[MaiMessages]) -> Tuple[bool, bool, Optional[str], None, None]:
        """
        返回 (是否成功, 是否继续传递, 日志, None, None)
        第二个值为 False 时拦截该消息，不再传给其他 Handler。
        """
        if not message:
            return True, True, None, None, None

        # logger.debug(f"[{{PLUGIN_NAME}}] 收到消息: {message.plain_text}")

        return True, True, None, None, None


# ═══════════════════════════════════════════════
#  插件注册
# ═══════════════════════════════════════════════

@register_plugin
class {{PLUGIN_CLASS_NAME}}(BasePlugin):
    """{{PLUGIN_DESCRIPTION}}"""

    plugin_name: str = "{{PLUGIN_NAME}}"
    enable_plugin: bool = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name: str = "config.toml"

    config_section_descriptions = {
        "plugin": "插件基本配置",
        "action": "Action 行为配置",
        "command": "Command 命令配置",
    }

    config_schema: dict = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件"),
            "config_version": ConfigField(type=str, default="{{PLUGIN_VERSION}}", description="配置版本"),
        },
        "action": {
            "message": ConfigField(type=str, default="你好！", description="Action 发送的消息"),
        },
        "command": {
            "reply": ConfigField(type=str, default="收到！", description="命令回复前缀"),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            ({{ACTION_CLASS_NAME}}.get_action_info(), {{ACTION_CLASS_NAME}}),
            ({{COMMAND_CLASS_NAME}}.get_command_info(), {{COMMAND_CLASS_NAME}}),
            ({{TOOL_CLASS_NAME}}.get_tool_info(), {{TOOL_CLASS_NAME}}),
            ({{HANDLER_CLASS_NAME}}Start.get_handler_info(), {{HANDLER_CLASS_NAME}}Start),
            ({{HANDLER_CLASS_NAME}}.get_handler_info(), {{HANDLER_CLASS_NAME}}),
        ]

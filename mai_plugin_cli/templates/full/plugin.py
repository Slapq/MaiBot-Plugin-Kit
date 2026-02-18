"""
完整插件模板 - {{plugin_name}}
作者：{{author}}

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
    ReplyContentType,
    emoji_api,
)
from src.common.logger import get_logger

logger = get_logger("{{plugin_name}}")


# ═══════════════════════════════════════════════
#  Action 组件：由麦麦自主决策是否触发
# ═══════════════════════════════════════════════

class {{ClassName}}Action(BaseAction):
    """主动行为组件"""

    action_name = "{{plugin_name}}_action"
    action_description = "{{description}}"
    activation_type = ActionActivationType.RANDOM
    random_activation_probability = 0.2

    action_require = [
        "当场景适合时使用",
        "不要连续频繁触发",
    ]
    associated_types = ["text"]
    action_parameters = {
        "content": "要发送的内容描述",
    }
    parallel_action = False

    async def execute(self) -> Tuple[bool, str]:
        """
        Action 执行逻辑

        属性：self.action_data / self.group_id / self.user_id /
              self.user_nickname / self.platform / self.chat_id /
              self.chat_stream / self.is_group / self.thinking_id /
              self.action_message
        """
        content = self.action_data.get("content", "")
        message = self.get_config("action.message", "你好！")

        logger.info(f"[{{plugin_name}}] Action 触发，user={self.user_nickname}")
        await self.send_text(message)

        await self.store_action_info(
            action_build_into_prompt=True,
            action_prompt_display=f"执行了 {{plugin_name}} 行为",
            action_done=True,
        )
        return True, "Action 执行成功"


# ═══════════════════════════════════════════════
#  Command 组件：用户输入命令时触发
# ═══════════════════════════════════════════════

class {{ClassName}}Command(BaseCommand):
    """命令响应组件"""

    command_name = "{{plugin_name}}"
    command_description = "{{description}}"
    # 使用命名捕获组提取参数：(?P<param_name>regex)
    command_pattern = r"^/{{plugin_name}}(?:\s+(?P<param>.+))?$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        """
        Command 执行逻辑

        属性：self.matched_groups / self.message.raw_message /
              self.message.chat_stream / self.message.stream_id /
              self.message.plain_text / self.message.message_segment
        """
        param = self.matched_groups.get("param", "")
        reply = self.get_config("command.reply", "收到！")

        logger.info(f"[{{plugin_name}}] Command 触发，param={param}")
        await self.send_text(f"{reply}（参数：{param}）" if param else reply)

        # 返回 (成功, 日志描述, 是否拦截后续处理)
        return True, "Command 执行成功", True


# ═══════════════════════════════════════════════
#  Tool 组件：供 LLM 在生成回复时调用
# ═══════════════════════════════════════════════

class {{ClassName}}Tool(BaseTool):
    """工具组件 - LLM 可调用"""

    name = "{{plugin_name}}_tool"
    description = "工具功能描述，帮助 LLM 理解何时调用"
    parameters = [
        # (参数名, 类型, 描述, 是否必须, 默认值)
        ("input", ToolParamType.STRING, "输入内容", True, None),
    ]
    available_for_llm = True

    async def execute(self, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tool 执行逻辑
        返回 {"name": self.name, "content": 结果字符串}
        """
        input_val = function_args.get("input", "")
        result = f"处理结果：{input_val}"
        return {"name": self.name, "content": result}


# ═══════════════════════════════════════════════
#  EventHandler 组件：监听系统事件
# ═══════════════════════════════════════════════

class {{ClassName}}EventHandler(BaseEventHandler):
    """
    事件处理组件

    event_type 可选：
    - EventType.ON_MESSAGE  : 每条消息触发
    """

    event_type = EventType.ON_MESSAGE
    handler_name = "{{plugin_name}}_handler"
    handler_description = "消息事件处理器"

    async def execute(self, message: Optional[MaiMessages]) -> Tuple[bool, bool, Optional[str], None, None]:
        """
        EventHandler 执行逻辑

        返回 Tuple[bool, bool, str|None, None, None]
            → (是否成功, 是否继续传递事件, 日志描述, None, None)
        """
        if not message:
            return True, True, None, None, None

        # 在这里处理每条消息
        # logger.debug(f"[{{plugin_name}}] 收到消息: {message.plain_text}")

        # 返回 True, True 表示成功且继续传递给其他 handler
        return True, True, None, None, None


# ═══════════════════════════════════════════════
#  插件注册
# ═══════════════════════════════════════════════

@register_plugin
class {{ClassName}}Plugin(BasePlugin):
    """{{description}}"""

    plugin_name: str = "{{plugin_name}}"
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
            "config_version": ConfigField(type=str, default="1.0.0", description="配置版本"),
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
            # 注册 Action
            ({{ClassName}}Action.get_action_info(), {{ClassName}}Action),
            # 注册 Command
            ({{ClassName}}Command.get_command_info(), {{ClassName}}Command),
            # 注册 Tool（如不需要可删除）
            ({{ClassName}}Tool.get_tool_info(), {{ClassName}}Tool),
            # 注册 EventHandler（如不需要可删除）
            ({{ClassName}}EventHandler.get_handler_info(), {{ClassName}}EventHandler),
        ]

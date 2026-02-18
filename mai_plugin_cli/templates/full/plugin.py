"""
{{PLUGIN_DISPLAY_NAME}} - Full 完整功能麦麦插件模板

这是一个包含所有组件类型的完整示例插件，展示了：
  - Action：麦麦自主触发的行为（由 LLM 决策）
  - Command：响应用户固定命令（正则匹配）
  - Tool：为 LLM 提供额外信息的工具（LLM 可调用）
  - EventHandler：监听系统事件（如消息到达等）

接口来源：MaiBot 官方源码 src/plugin_system
作者：{{PLUGIN_AUTHOR}}
版本：{{PLUGIN_VERSION}}
"""

import datetime
from typing import Any, Dict, List, Optional, Tuple, Type

from src.plugin_system import (
    ActionActivationType,
    BaseAction,
    BaseCommand,
    BaseEventHandler,
    BasePlugin,
    BaseTool,
    ComponentInfo,
    ConfigField,
    EventType,
    MaiMessages,
    ReplyContentType,
    ToolParamType,
    register_plugin,
)
from src.common.logger import get_logger

logger = get_logger("{{PLUGIN_NAME}}")


# =============================================================================
# 1. Action 组件 —— 麦麦自主触发的行为
# =============================================================================


class {{ACTION_CLASS_NAME}}(BaseAction):
    """
    Action 组件：麦麦根据对话上下文自主决定是否使用。

    工作流程：
      1. LLM 根据 action_require / action_description 判断是否使用此 Action
      2. LLM 从对话中提取 action_parameters 中定义的参数
      3. 调用 execute()，在其中实现任意功能
    """

    # ===== 必填：Action 基本信息 =====
    action_name = "{{PLUGIN_NAME}}_action"
    action_description = "{{PLUGIN_DESCRIPTION}}（Action 组件）"
    activation_type = ActionActivationType.ALWAYS   # ALWAYS / KEYWORD / RANDOM

    # ===== 必填：LLM 提示配置 =====
    action_parameters = {
        "reason":  "执行动作的原因",
        "content": "要发送的内容（可选）",
    }
    action_require = [
        "当需要 {{PLUGIN_DISPLAY_NAME}} 相关操作时",
        "当用户请求 {{PLUGIN_NAME}} 功能时",
    ]
    associated_types = ["text"]

    async def execute(self) -> Tuple[bool, str]:
        """
        可用属性：
            self.action_data          - LLM 提取的参数字典
            self.message              - 触发消息对象（MaiMessages）
            self.message.chat_stream  - 聊天流（用于 generator_api）
            self.message.raw_message  - 用户原始消息文本
            self.stream_id            - 当前聊天流 ID

        可用方法：
            await self.send_text(text)                  - 发送文本
            await self.send_text(text, storage_message=False) - 发送但不入库
            self.get_config("section.key", default)     - 读取配置
        """
        reason  = self.action_data.get("reason", "")
        content = self.action_data.get("content", "")
        prefix  = self.get_config("action.prefix", "【{{PLUGIN_DISPLAY_NAME}}】")

        try:
            msg = f"{prefix} {content or '执行成功'}"
            await self.send_text(msg)
            return True, f"Action 执行成功，原因：{reason}"
        except Exception as e:
            logger.error(f"[{{PLUGIN_CLASS_NAME}}] Action 执行失败：{e}")
            return False, str(e)


# =============================================================================
# 2. Command 组件 —— 响应用户固定命令
# =============================================================================


class {{COMMAND_CLASS_NAME}}(BaseCommand):
    """
    Command 组件：精确匹配用户命令并响应，不经过 LLM。

    command_pattern 使用正则表达式，支持捕获组提取参数。
    """

    command_name        = "{{PLUGIN_NAME}}_command"
    command_description = "{{PLUGIN_DESCRIPTION}}（Command 组件）"
    command_pattern     = r"^/{{PLUGIN_NAME}}(?:\s+(\w+))?(?:\s+(.+))?$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        """
        可用属性：
            self.message.raw_message  - 用户原始消息文本
            self.message.chat_stream  - 聊天流
            self.matched              - re.Match 对象（pattern 匹配结果）

        返回：
            (success, log_message, intercept)
              success   - 是否成功
              log_message - 日志描述（可为 None）
              intercept - 是否拦截（阻止后续处理）
        """
        import re
        # 从原始消息中提取参数（也可直接用 self.matched）
        m = re.match(self.command_pattern, self.message.raw_message)
        sub_cmd = m.group(1) if m else None
        param   = m.group(2) if m else None

        try:
            if sub_cmd == "help" or sub_cmd is None:
                help_text = (
                    f"📖 {{PLUGIN_DISPLAY_NAME}} 帮助\n"
                    f"版本：{{PLUGIN_VERSION}}\n\n"
                    f"命令列表：\n"
                    f"  /{{PLUGIN_NAME}} help   - 显示此帮助\n"
                    f"  /{{PLUGIN_NAME}} info   - 插件信息\n"
                    f"  /{{PLUGIN_NAME}} time   - 当前时间\n"
                )
                await self.send_text(help_text)

            elif sub_cmd == "info":
                await self.send_text(
                    f"🔌 插件信息\n"
                    f"名称：{{PLUGIN_DISPLAY_NAME}}\n"
                    f"版本：{{PLUGIN_VERSION}}\n"
                    f"作者：{{PLUGIN_AUTHOR}}\n"
                    f"描述：{{PLUGIN_DESCRIPTION}}"
                )

            elif sub_cmd == "time":
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                await self.send_text(f"🕒 当前时间：{now}")

            else:
                await self.send_text(
                    f"❓ 未知子命令：{sub_cmd}，"
                    f"输入 /{{PLUGIN_NAME}} help 查看帮助"
                )

            return True, f"Command 执行成功：{sub_cmd}", True

        except Exception as e:
            logger.error(f"[{{PLUGIN_CLASS_NAME}}] Command 执行失败：{e}")
            return False, str(e), True


# =============================================================================
# 3. Tool 组件 —— 为 LLM 提供额外信息（LLM 可直接调用）
# =============================================================================


class {{TOOL_CLASS_NAME}}(BaseTool):
    """
    Tool 组件：LLM 可以主动调用的工具，返回结构化信息供 LLM 参考。

    Tool 不直接发送消息；它返回数据，由 LLM 决定如何使用。
    适合：查询数据库、获取天气、搜索信息、数值计算等。

    官方 API 说明：
      name            - 工具名称（snake_case）
      description     - 工具功能描述
      parameters      - 参数列表，每项为 (name, ToolParamType, description, required, default)
      available_for_llm - 是否向 LLM 公开此工具
      execute(function_args: dict) -> dict  - 返回 {"name": self.name, "content": 结果字符串}
    """

    name            = "{{PLUGIN_NAME}}_tool"
    description     = "获取 {{PLUGIN_DISPLAY_NAME}} 相关信息，为 LLM 提供参考数据"
    available_for_llm = True

    # 参数格式：(参数名, ToolParamType, 描述, 是否必填, 默认值)
    parameters = [
        ("query", ToolParamType.STRING, "查询关键词", True,  None),
        ("limit", ToolParamType.INT,    "返回结果数量上限", False, 5),
    ]

    async def execute(self, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行 Tool 并返回结果字典（由 LLM 读取）。
        返回格式固定：{"name": self.name, "content": 结果字符串}
        """
        query = function_args.get("query", "")
        limit = function_args.get("limit", 5)

        try:
            # 在此实现数据查询逻辑
            now    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result = f"查询 '{query}' 的结果（最多 {limit} 条）：当前时间为 {now}"
            return {"name": self.name, "content": result}

        except Exception as e:
            logger.error(f"[{{PLUGIN_CLASS_NAME}}] Tool 执行失败：{e}")
            return {"name": self.name, "content": f"工具执行失败：{str(e)}"}


# =============================================================================
# 4. EventHandler 组件 —— 监听系统事件
# =============================================================================


class {{PLUGIN_CLASS_NAME}}EventHandler(BaseEventHandler):
    """
    EventHandler 组件：监听 MaiBot 事件并作出响应。

    官方 API 说明：
      event_type          - 监听的事件类型（EventType 枚举，单个）
      handler_name        - 处理器名称（唯一标识）
      handler_description - 处理器描述
      execute(message: MaiMessages | None)
          -> Tuple[bool, bool, str | None, None, None]
            (success, continue_process, log_msg, None, None)

    可用 EventType：
      EventType.ON_MESSAGE       - 收到消息时
      EventType.ON_GROUP_JOIN    - 新成员加入群聊
      EventType.ON_GROUP_LEAVE   - 成员离开群聊
    """

    event_type          = EventType.ON_MESSAGE
    handler_name        = "{{PLUGIN_NAME}}_event_handler"
    handler_description = "监听并处理 {{PLUGIN_DISPLAY_NAME}} 相关事件"

    async def execute(
        self, message: "MaiMessages | None"
    ) -> Tuple[bool, bool, Optional[str], None, None]:
        """
        处理收到的事件。
          返回值第 2 项为 True 表示继续后续处理，False 表示拦截。

        可用属性（当 event_type=ON_MESSAGE 时）：
            message.raw_message  - 消息文本
            message.stream_id    - 聊天流 ID
            message.chat_stream  - 聊天流对象
        """
        if message and message.raw_message:
            logger.debug(
                f"[{{PLUGIN_CLASS_NAME}}] 收到消息：{message.raw_message[:50]}"
            )
        return True, True, "事件已处理", None, None


# =============================================================================
# 插件主类
# =============================================================================


@register_plugin
class {{PLUGIN_CLASS_NAME}}(BasePlugin):
    """{{PLUGIN_DISPLAY_NAME}} 完整功能插件主类"""

    plugin_name           = "{{PLUGIN_NAME}}"
    enable_plugin: bool   = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name      = "config.toml"

    # 配置节描述（可选，供自动生成的 config.toml 使用注释）
    config_section_descriptions = {
        "plugin": "插件基本信息",
        "action": "Action 组件配置",
    }

    config_schema: dict = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True,  description="是否启用插件"),
            "debug":   ConfigField(type=bool, default=False, description="是否开启调试模式"),
        },
        "action": {
            "prefix": ConfigField(
                type=str,
                default="【{{PLUGIN_DISPLAY_NAME}}】",
                description="Action 消息前缀",
            ),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """注册所有组件"""
        return [
            # Action 组件（LLM 自主触发）
            ({{ACTION_CLASS_NAME}}.get_action_info(),  {{ACTION_CLASS_NAME}}),
            # Command 组件（用户命令触发）
            ({{COMMAND_CLASS_NAME}}.get_command_info(), {{COMMAND_CLASS_NAME}}),
            # Tool 组件（LLM 可调用）
            ({{TOOL_CLASS_NAME}}.get_tool_info(),      {{TOOL_CLASS_NAME}}),
            # EventHandler 组件（取消注释来启用）
            # ({{PLUGIN_CLASS_NAME}}EventHandler.get_handler_info(), {{PLUGIN_CLASS_NAME}}EventHandler),
        ]

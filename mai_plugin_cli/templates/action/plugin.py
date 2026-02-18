"""
Action 插件模板 - {{plugin_name}}
作者：{{author}}

Action 由麦麦的决策系统自主选择是否使用，不需要用户明确输入命令。
适合：主动问候、情绪反应、主动分享内容、添加表情包等场景。
"""

from typing import List, Tuple, Type

from src.plugin_system import (
    BasePlugin,
    register_plugin,
    BaseAction,
    ComponentInfo,
    ActionActivationType,
    ConfigField,
)
from src.common.logger import get_logger

logger = get_logger("{{plugin_name}}")


class {{ClassName}}Action(BaseAction):
    """
    Action 组件 - 在合适的时机由麦麦自主触发

    activation_type 控制此 Action 何时进入决策候选池：
    - ActionActivationType.ALWAYS   : 始终在候选池中（核心功能用）
    - ActionActivationType.RANDOM   : 按概率进入候选池（需设置 random_activation_probability）
    - ActionActivationType.KEYWORD  : 检测到关键词时进入（需设置 activation_keywords）
    - ActionActivationType.NEVER    : 永不激活（调试/禁用用）
    """

    # ── 基本信息（必须填写）──────────────────────────────
    action_name = "{{plugin_name}}_action"
    action_description = "{{description}}"

    # ── 激活配置 ─────────────────────────────────────────
    activation_type = ActionActivationType.RANDOM
    random_activation_probability = 0.3      # RANDOM 模式：30% 概率进入候选池

    # activation_type = ActionActivationType.KEYWORD
    # activation_keywords = ["关键词1", "关键词2"]
    # keyword_case_sensitive = False

    # ── 使用场景描述（帮助 LLM 决定何时选用此 Action）────
    action_require = [
        "在合适的场景使用",   # ← 根据你的插件功能修改这里
        "不要频繁使用",
    ]

    # ── 此 Action 会发送哪些类型的消息 ────────────────────
    # 可选: "text" "emoji" "image" "reply" "voice" "command"
    #       "voiceurl" "music" "videourl" "file"
    associated_types = ["text"]

    # ── LLM 调用此 Action 时会传入的参数 ──────────────────
    # LLM 会根据描述生成参数值，存入 self.action_data
    action_parameters = {
        "content": "要发送的内容",
    }

    # ── 是否允许与其他 Action 并行执行 ────────────────────
    parallel_action = False

    async def execute(self) -> Tuple[bool, str]:
        """
        Action 核心执行逻辑

        可用属性：
            self.action_data      : LLM 传入的参数字典
            self.group_id         : 群号
            self.user_id          : 触发者 QQ 号
            self.user_nickname    : 触发者昵称
            self.platform         : 平台（如 "qq"）
            self.chat_id          : 聊天流 ID
            self.chat_stream      : ChatStream 对象
            self.is_group         : 是否群聊
            self.thinking_id      : 本次思考 ID
            self.action_message   : 完整的消息数据字典

        可用方法：
            await self.send_text(content, reply_to="", typing=False)
            await self.send_emoji(emoji_base64)
            await self.send_image(image_base64)
            await self.send_custom(message_type, content)
            await self.send_command(command_name, args={})
            await self.store_action_info(action_build_into_prompt=True, action_prompt_display="...", action_done=True)
            self.get_config("section.key", default_value)

        返回：
            Tuple[bool, str]  →  (是否成功, 日志描述)
        """
        # 从 LLM 传入的参数中获取值
        content = self.action_data.get("content", "")

        # 从配置文件读取
        message_template = self.get_config("action.message", "{{description}}")

        logger.info(f"[{{plugin_name}}] Action 执行，user={self.user_nickname}")

        # 发送文本消息
        await self.send_text(message_template)

        # 将此次行为写入提示词上下文（可选）
        await self.store_action_info(
            action_build_into_prompt=True,
            action_prompt_display=f"执行了 {{plugin_name}} 动作",
            action_done=True,
        )

        return True, "执行成功"


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
    }

    config_schema: dict = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件"),
            "config_version": ConfigField(type=str, default="1.0.0", description="配置版本"),
        },
        "action": {
            "message": ConfigField(type=str, default="{{description}}", description="Action 发送的消息模板"),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            ({{ClassName}}Action.get_action_info(), {{ClassName}}Action),
        ]

"""
{{PLUGIN_DISPLAY_NAME}} - Action 插件

{{PLUGIN_DESCRIPTION}}

作者：{{PLUGIN_AUTHOR}}
版本：{{PLUGIN_VERSION}}

Action 由麦麦的决策系统自主选择是否使用，无需用户输入命令。
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

logger = get_logger("{{PLUGIN_NAME}}")


class {{ACTION_CLASS_NAME}}(BaseAction):
    """
    Action 组件 - 在合适的时机由麦麦自主触发

    activation_type 控制此 Action 何时进入决策候选池：
    - ActionActivationType.ALWAYS   : 始终在候选池中（核心功能用）
    - ActionActivationType.RANDOM   : 按概率进入候选池（需设置 random_activation_probability）
    - ActionActivationType.KEYWORD  : 检测到关键词时进入（需设置 activation_keywords）
    - ActionActivationType.NEVER    : 永不激活（调试/禁用用）
    """

    action_name = "{{PLUGIN_NAME}}_action"
    action_description = "{{PLUGIN_DESCRIPTION}}"

    activation_type = ActionActivationType.RANDOM
    random_activation_probability = 0.3      # 30% 概率进入候选池

    # activation_type = ActionActivationType.KEYWORD
    # activation_keywords = ["关键词1", "关键词2"]
    # keyword_case_sensitive = False

    # 帮助 LLM 决定何时选用此 Action
    action_require = [
        "在合适的场景使用",
        "不要频繁使用",
    ]

    # 此 Action 会发送哪些类型的消息
    # 可选: "text" "emoji" "image" "reply" "voice" "command" "voiceurl" "music" "videourl" "file"
    associated_types = ["text"]

    # LLM 调用此 Action 时会传入的参数（LLM 根据描述自动生成参数值）
    action_parameters = {
        "content": "要发送的内容",
        "reason": "触发原因",
    }

    parallel_action = False

    async def execute(self) -> Tuple[bool, str]:
        """
        Action 核心执行逻辑

        常用属性：
            self.action_data      : LLM 传入的参数字典
            self.user_nickname    : 触发者昵称
            self.group_id         : 群号
            self.user_id          : 用户 QQ 号
            self.chat_stream      : ChatStream 对象
            self.is_group         : 是否群聊
            self.stream_id        : 聊天流 ID

        常用方法：
            await self.send_text(content)
            await self.send_emoji(emoji_base64)
            await self.send_image(image_base64)
            await self.store_action_info(action_build_into_prompt=True, action_prompt_display="...", action_done=True)
            self.get_config("section.key", default_value)
        """
        content = self.action_data.get("content", "")
        message_template = self.get_config("action.message", "{{PLUGIN_DESCRIPTION}}")

        logger.info(f"[{{PLUGIN_NAME}}] Action 执行，user={self.user_nickname}")

        await self.send_text(message_template)

        await self.store_action_info(
            action_build_into_prompt=True,
            action_prompt_display=f"执行了 {{PLUGIN_NAME}} 动作",
            action_done=True,
        )

        return True, "执行成功"


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
    }

    config_schema: dict = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件"),
            "config_version": ConfigField(type=str, default="{{PLUGIN_VERSION}}", description="配置版本"),
        },
        "action": {
            "message": ConfigField(type=str, default="{{PLUGIN_DESCRIPTION}}", description="Action 发送的消息模板"),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            ({{ACTION_CLASS_NAME}}.get_action_info(), {{ACTION_CLASS_NAME}}),
        ]

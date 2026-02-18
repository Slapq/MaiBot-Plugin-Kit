"""
{{PLUGIN_DISPLAY_NAME}} - Command 插件

{{PLUGIN_DESCRIPTION}}

作者：{{PLUGIN_AUTHOR}}
版本：{{PLUGIN_VERSION}}

Command 在用户输入匹配正则表达式时立即触发，是确定性的被动响应。
适合：/help /ping /天气 城市 等明确命令。
"""

from typing import List, Optional, Tuple, Type

from src.plugin_system import (
    BasePlugin,
    register_plugin,
    BaseCommand,
    ComponentInfo,
    ConfigField,
)
from src.common.logger import get_logger

logger = get_logger("{{PLUGIN_NAME}}")


class {{COMMAND_CLASS_NAME}}(BaseCommand):
    """
    Command 组件 - 响应用户输入的特定命令

    command_pattern 使用 Python 正则表达式。
    若需提取参数，使用命名捕获组：(?P<参数名>匹配规则)
    匹配结果存入 self.matched_groups 字典。

    示例（带参数）：
        command_pattern = r"^/{{PLUGIN_NAME}}\\s+(?P<param>\\S+)$"
        # 用户输入 /{{PLUGIN_NAME}} hello → self.matched_groups["param"] == "hello"
    """

    command_name = "{{PLUGIN_NAME}}"
    command_description = "{{PLUGIN_DESCRIPTION}}"

    # 精确匹配命令（不带参数）
    command_pattern = r"^/{{PLUGIN_NAME}}$"

    # 带参数版本（取消注释以使用）：
    # command_pattern = r"^/{{PLUGIN_NAME}}(?:\s+(?P<param>.+))?$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        """
        Command 核心执行逻辑

        常用属性：
            self.matched_groups         : 正则命名捕获组字典
            self.message.raw_message    : 用户原始消息文本
            self.message.chat_stream    : ChatStream 对象
            self.message.stream_id      : 当前聊天流 ID
            self.message.plain_text     : 消息纯文本

        常用方法：
            await self.send_text(content)
            await self.send_emoji(emoji_base64)
            await self.send_image(image_base64)
            self.get_config("section.key", default_value)

        返回：
            Tuple[bool, Optional[str], bool]
                → (是否成功, 日志描述, 是否拦截后续处理)
            第三个值建议设为 True，避免命令被麦麦当普通消息处理
        """
        # 如使用带参数的 pattern，这样获取：
        # param = self.matched_groups.get("param", "")

        reply_message = self.get_config("command.reply", "收到命令！")

        logger.info(f"[{{PLUGIN_NAME}}] Command 触发，stream={self.message.stream_id}")

        await self.send_text(reply_message)

        return True, "命令执行成功", True


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
        "command": "命令响应配置",
    }

    config_schema: dict = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件"),
            "config_version": ConfigField(type=str, default="{{PLUGIN_VERSION}}", description="配置版本"),
        },
        "command": {
            "reply": ConfigField(type=str, default="收到命令！", description="命令回复内容"),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            ({{COMMAND_CLASS_NAME}}.get_command_info(), {{COMMAND_CLASS_NAME}}),
        ]

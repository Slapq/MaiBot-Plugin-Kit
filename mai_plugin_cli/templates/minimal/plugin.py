"""
{{PLUGIN_DISPLAY_NAME}} - 最简骨架插件

{{PLUGIN_DESCRIPTION}}

作者：{{PLUGIN_AUTHOR}}
版本：{{PLUGIN_VERSION}}
"""

from typing import List, Tuple, Type

from src.plugin_system import (
    BasePlugin,
    register_plugin,
    ComponentInfo,
    ConfigField,
)
from src.common.logger import get_logger

logger = get_logger("{{PLUGIN_NAME}}")


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
    }

    config_schema: dict = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件"),
            "config_version": ConfigField(type=str, default="{{PLUGIN_VERSION}}", description="配置版本"),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """返回插件组件列表（在这里注册你的 Action / Command / Tool）"""
        return []

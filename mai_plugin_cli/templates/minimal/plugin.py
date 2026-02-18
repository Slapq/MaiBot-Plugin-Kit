"""
最简插件模板 - {{plugin_name}}
作者：{{author}}

这是一个骨架插件，仅包含最基本的结构。
复制此模板，在 get_plugin_components() 中注册你的组件。
"""

from typing import List, Tuple, Type

from src.plugin_system import (
    BasePlugin,
    register_plugin,
    ComponentInfo,
    ConfigField,
)
from src.common.logger import get_logger

logger = get_logger("{{plugin_name}}")


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
    }

    config_schema: dict = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用插件"),
            "config_version": ConfigField(type=str, default="1.0.0", description="配置版本"),
        },
    }

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """返回插件组件列表"""
        return []

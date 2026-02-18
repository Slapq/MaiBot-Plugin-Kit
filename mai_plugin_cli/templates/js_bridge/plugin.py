"""
{{PLUGIN_DISPLAY_NAME}} - JS Bridge 麦麦插件

这是一个 JavaScript 桥接插件。核心逻辑写在 plugin.js 中，
Python 层负责加载并桥接 JS 与 MaiBot API。

作者：{{PLUGIN_AUTHOR}}
版本：{{PLUGIN_VERSION}}

【注意】本模板依赖 mai_js_bridge 模块，需要将其放在：
  MaiBot/plugins/ 的父目录中，或者安装到 Python 环境。
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple, Type

from src.plugin_system import BasePlugin, register_plugin, ComponentInfo

# 将 mai_js_bridge 加入路径（如果尚未安装）
_kit_path = Path(__file__).parent.parent.parent.parent
if str(_kit_path) not in sys.path:
    sys.path.insert(0, str(_kit_path))

try:
    from mai_js_bridge import JsBridgeLoader
    _HAS_JS_BRIDGE = True
except ImportError:
    _HAS_JS_BRIDGE = False


@register_plugin
class {{PLUGIN_CLASS_NAME}}(BasePlugin):
    """{{PLUGIN_DISPLAY_NAME}} JS 桥接插件主类"""

    plugin_name = "{{PLUGIN_NAME}}"
    enable_plugin = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name = "config.toml"
    config_schema: dict = {}

    # JS 插件文件路径（相对于当前目录）
    _js_file = Path(__file__).parent / "plugin.js"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bridge: "JsBridgeLoader | None" = None

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """加载 JS 文件中定义的组件"""
        if not _HAS_JS_BRIDGE:
            import logging
            logging.warning(
                f"[{{PLUGIN_CLASS_NAME}}] mai_js_bridge 未安装，JS 插件无法加载。"
                f"请确保 MaiBot-Plugin-Kit 目录存在并可访问。"
            )
            return []

        if not self._js_file.exists():
            import logging
            logging.warning(f"[{{PLUGIN_CLASS_NAME}}] plugin.js 不存在：{self._js_file}")
            return []

        # 创建 JS 桥接器并加载 JS 插件
        self._bridge = JsBridgeLoader(str(self._js_file), plugin_name=self.plugin_name)
        components = self._bridge.get_components()
        return components

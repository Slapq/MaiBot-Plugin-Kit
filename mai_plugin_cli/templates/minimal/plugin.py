"""
{{PLUGIN_DISPLAY_NAME}} - 最简麦麦插件模板

这是一个最简化的插件模板，包含了插件运行所需的最少代码。
你可以在此基础上添加 Action、Command、Tool 等组件。

作者：{{PLUGIN_AUTHOR}}
版本：{{PLUGIN_VERSION}}
"""

from typing import List, Tuple, Type
from src.plugin_system import BasePlugin, register_plugin, ComponentInfo


@register_plugin
class {{PLUGIN_CLASS_NAME}}(BasePlugin):
    """{{PLUGIN_DISPLAY_NAME}} 插件主类"""

    # ===== 插件基本信息（必填）=====
    plugin_name = "{{PLUGIN_NAME}}"       # 插件唯一标识符（英文）
    enable_plugin = True                   # 是否启用插件
    dependencies: List[str] = []           # 依赖的其他插件名称列表
    python_dependencies: List[str] = []    # 依赖的 Python 包列表（如 ["requests", "pillow"]）
    config_file_name = "config.toml"       # 配置文件名
    config_schema: dict = {}               # 配置文件结构定义（空 = 无配置文件）

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """
        返回插件包含的组件列表。
        
        组件类型说明：
          - Action：麦麦自主决定是否使用的行为（由 LLM 触发）
          - Command：用户输入特定命令时触发（正则匹配）
          - Tool：为 LLM 提供额外信息的工具
          - EventHandler：监听系统事件（如新成员加入等）
        
        示例（添加 Action）：
            from .my_action import MyAction
            return [(MyAction.get_action_info(), MyAction)]
        """
        return []  # 目前没有组件，返回空列表

"""
Test Cmd Plugin - Command 类型麦麦插件

Command 响应用户输入的固定命令（通过正则表达式匹配）。
无需 LLM 参与，精确触发，适合管理类/功能类命令。

使用场景：
  - /ping、/help、/status 等管理命令
  - /weather 上海 等带参数的查询命令
  - 需要精确控制触发条件的场景

作者：测试者
版本：2.0.0
"""

import re
import datetime
from typing import List, Tuple, Type, Optional

from src.plugin_system import (
    BasePlugin,
    register_plugin,
    BaseCommand,
    ComponentInfo,
    ConfigField,
)


# =============================================================================
# Command 组件定义
# =============================================================================


class TestCmdPluginCommand(BaseCommand):
    """
    Test Cmd Plugin 的核心 Command 组件。
    
    Command 的工作流程：
    1. 消息匹配：使用 command_pattern 正则表达式匹配用户消息
    2. 参数提取：通过正则捕获组提取参数
    3. 执行：调用 execute() 方法
    """

    # ===== 必填：Command 基本信息 =====
    command_name = "test_cmd_plugin_command"
    command_description = "测试命令插件"

    # 匹配用户消息的正则表达式
    # 示例：
    #   r"^/ping$"                    - 精确匹配 "/ping"
    #   r"^/weather\s+(.+)$"          - 匹配 "/weather 城市名"，捕获城市名
    #   r"^/(help|h|\?)$"             - 匹配多种形式的帮助命令
    #   r"^/calc\s+(\d+)\s*([+\-*/])\s*(\d+)$"  - 匹配 "/calc 1 + 2"
    command_pattern = r"^/test_cmd_plugin(?:\s+(.+))?$"

    # ===== 可选配置 =====
    # 是否在私聊中也有效（默认 True）
    # intercept_in_private = True
    
    # 是否在群聊中有效（默认 True）
    # intercept_in_group = True

    # =============================================================================
    # 核心执行逻辑
    # =============================================================================

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        """
        Command 的核心执行方法。
        
        可用属性：
            self.matched           - 正则匹配结果对象（re.Match）
            self.params            - 捕获组列表（匹配到的参数）
            self.raw_message       - 用户原始消息文本
            self.chat_stream       - 当前聊天流对象
            self.stream_id         - 当前聊天流 ID
            self.sender_name       - 发送者昵称
            self.sender_id         - 发送者 ID
        
        可用方法：
            self.send_text(text)                - 发送文本
            self.send_image(base64_str)          - 发送图片
            self.get_config(key, default)        - 读取配置值
        
        返回值：
            (True, "日志信息", True)   - 成功，第三个参数表示是否阦截后续处理
            (False, "错误信息", True)  - 失败
        """
        # ===== 提取正则捕获的参数 =====
        # 如果正则有捕获组，可以通过 self.matched.group(1) 等方式获取
        param = None
        if self.matched:
            param = self.matched.group(1)  # 捕获第一个参数（如果有）

        # ===== 在此编写你的核心逻辑 =====
        try:
            if param:
                # 有参数时的处理
                response = f"收到参数：{param}"
            else:
                # 无参数时的处理（或显示帮助）
                response = (
                    f"✅ Test Cmd Plugin 正在运行！\n"
                    f"📌 用法：/test_cmd_plugin [参数]\n"
                    f"🕒 当前时间：{datetime.datetime.now().strftime('%H:%M:%S')}"
                )

            await self.send_text(response)
            return True, f"test_cmd_plugin 命令执行成功", True

        except Exception as e:
            self.logger.error(f"[TestCmdPluginPlugin] 执行失败：{e}")
            await self.send_text(f"❌ 执行失败：{str(e)}")
            return False, f"执行失败：{str(e)}", True


# =============================================================================
# 插件主类
# =============================================================================


@register_plugin
class TestCmdPluginPlugin(BasePlugin):
    """Test Cmd Plugin 插件主类"""

    plugin_name = "test_cmd_plugin"
    enable_plugin = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name = "config.toml"
    config_schema: dict = {}

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """注册插件包含的组件"""
        return [
            (TestCmdPluginCommand.get_command_info(), TestCmdPluginCommand),
        ]

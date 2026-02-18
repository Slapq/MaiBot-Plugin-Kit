"""
测试打招呼插件 - 由 MaiScript 自动生成

一个测试MaiScript功能的插件

作者：测试者
版本：1.0.0

⚠️ 此文件由 mai_script 编译器自动生成，请勿直接修改。
   如需修改，请编辑源 .mai 文件后重新编译。
"""

from typing import List, Tuple, Type, Optional
from src.plugin_system import (
    BasePlugin,
    register_plugin,
    BaseAction,
    BaseCommand,
    ComponentInfo,
    ActionActivationType,
)

# ---- Command: 打招呼 ----
class 测试打招呼插件Cmd打招呼(BaseCommand):
    """响应命令：打招呼（/hello）"""
    command_name = "打招呼"
    command_description = "响应 /hello 命令"
    command_pattern = r"^/hello$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        user_name = getattr(self, "sender_name", "朋友")
        await self.send_text(f"你好！{user_name}！😊")
        return True, "打招呼 执行成功", True

# ---- Command: 掷骰子 ----
class 测试打招呼插件Cmd掷骰子(BaseCommand):
    """响应命令：掷骰子（/roll）"""
    command_name = "掷骰子"
    command_description = "响应 /roll 命令"
    command_pattern = r"^/roll$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        try:
            import random
            n = random.randint(1, 6)
            reply = f"🎲 你掷出了 {n} 点！"
            if "reply" in dir():
                await self.send_text(str(reply))
        except Exception as e:
            self.logger.error(f"[测试打招呼插件Cmd掷骰子] 执行失败：{e}")
            await self.send_text(f"❌ 执行失败：{str(e)}")
        return True, "掷骰子 执行成功", True

# ---- Command: 查时间 ----
class 测试打招呼插件Cmd查时间(BaseCommand):
    """响应命令：查时间（/time）"""
    command_name = "查时间"
    command_description = "响应 /time 命令"
    command_pattern = r"^/time$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        try:
            import datetime
            now = datetime.datetime.now()
            reply = f"现在是 {now.strftime('%H:%M:%S')}"
            if "reply" in dir():
                await self.send_text(str(reply))
        except Exception as e:
            self.logger.error(f"[测试打招呼插件Cmd查时间] 执行失败：{e}")
            await self.send_text(f"❌ 执行失败：{str(e)}")
        return True, "查时间 执行成功", True

# ---- Action: 安慰用户 ----
class 测试打招呼插件Act安慰用户(BaseAction):
    """Action：安慰用户"""
    action_name = "安慰用户"
    action_description = "当 当有人表达悲伤或失落时 时执行"
    activation_type = ActionActivationType.ALWAYS
    action_parameters = {'reason': '执行原因'}
    action_require = ['当有人表达悲伤或失落时', '当有人说自己很难过时']
    associated_types = ['text']

    async def execute(self) -> Tuple[bool, str]:
        reason = self.action_data.get("reason", "")
        await self.send_text(f"没关系的！加油！💪")
        return True, "安慰用户 执行成功"

# ---- 主插件类 ----
@register_plugin
class 测试打招呼插件Plugin(BasePlugin):
    """由 MaiScript 生成：测试打招呼插件"""

    plugin_name = "测试打招呼插件"
    enable_plugin = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name = "config.toml"
    config_schema: dict = {}

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """返回所有组件"""
        return [
            (测试打招呼插件Cmd打招呼.get_command_info(), 测试打招呼插件Cmd打招呼),
            (测试打招呼插件Cmd掷骰子.get_command_info(), 测试打招呼插件Cmd掷骰子),
            (测试打招呼插件Cmd查时间.get_command_info(), 测试打招呼插件Cmd查时间),
            (测试打招呼插件Act安慰用户.get_action_info(), 测试打招呼插件Act安慰用户),
        ]
"""
Test Action Plugin - Action 类型麦麦插件

Action 是麦麦的自主行为。当 LLM 判断需要这个行为时，会自动调用它。
例如：天气查询、发表情、搜索信息、播放音乐等。

使用场景：
  - 随机化的互动行为
  - 情绪和表情表达
  - 根据上下文自动触发
  - 增强麦麦的智能行为

作者：未知作者
版本：1.0.0
"""

from typing import List, Tuple, Type, Optional
from src.plugin_system import (
    BasePlugin,
    register_plugin,
    BaseAction,
    ComponentInfo,
    ActionActivationType,
    ChatMode,
    ConfigField,
)


# =============================================================================
# Action 组件定义
# =============================================================================


class TestActionPluginAction(BaseAction):
    """
    Test Action Plugin 的核心 Action 组件。
    
    Action 的工作流程：
    1. LLM 决策：根据 action_require 和 action_description 判断是否使用
    2. 参数提取：LLM 从对话中提取 action_parameters 中定义的参数
    3. 执行：调用 execute() 方法，可在此做任何事情
    """

    # ===== 必填：Action 基本信息 =====
    action_name = "test_action_plugin_action"
    action_description = "一个使用 action 模板创建的麦麦插件"

    # 激活类型：
    #   ALWAYS    - 始终可用（推荐）
    #   RANDOM    - 随机激活（适合随机事件）
    #   KEYBOARD  - 需要特定触发词
    activation_type = ActionActivationType.ALWAYS

    # 聊天模式限制（可选）：
    #   GROUP_CHAT  - 仅群聊
    #   PRIVATE_CHAT - 仅私聊
    #   UNIVERSAL   - 两者都支持（默认）
    # 取消注释来限制模式：
    # mode = ChatMode.GROUP_CHAT

    # ===== 必填：LLM 提示配置 =====
    # LLM 执行时会传入的参数（LLM 从对话中提取这些参数的值）
    action_parameters = {
        "reason": "执行此动作的原因（简短描述）",
        # 可以添加更多参数，例如：
        # "target_user": "目标用户的名字（如果有）",
        # "message_content": "要发送的消息内容",
    }

    # LLM 判断使用此 Action 的条件描述（越具体越准确）
    action_require = [
        "当需要执行 Test Action Plugin 相关操作时",
        "当用户请求与 test_action_plugin 相关的功能时",
        # 可以添加更多条件，例如：
        # "当用户说'帮我查查天气'时",
        # "当需要发送一个表情包时",
    ]

    # 关联的消息类型（告诉 LLM 这个 Action 会产生什么类型的回复）
    # 可选值：["text", "image", "emoji", "voice", "video"]
    associated_types = ["text"]

    # ===== 可选：随机激活概率（activation_type = RANDOM 时有效）=====
    # default_enable_ratio = 0.3  # 30% 的概率激活

    # =============================================================================
    # 核心执行逻辑
    # =============================================================================

    async def execute(self) -> Tuple[bool, str]:
        """
        Action 的核心执行方法。
        
        可用属性：
            self.action_data     - LLM 提取的参数字典（如 action_parameters 中定义的）
            self.chat_stream     - 当前聊天流对象
            self.stream_id       - 当前聊天流 ID（用于发送消息）
            self.message_id      - 触发消息的 ID
        
        可用方法：
            self.send_text(text)                 - 发送文本消息
            self.send_image(base64_str)           - 发送图片（base64 格式）
            self.send_emoji(base64_str)           - 发送表情包（base64 格式）
            self.send_custom(type, data)          - 发送自定义类型消息
            self.get_config(key, default)         - 读取配置值
            self.get_recent_messages(n)           - 获取最近 n 条消息
            self.generate_reply(extra_info)       - 使用麦麦的风格化生成器生成回复
        
        返回值：
            (True, "成功描述")   - 执行成功
            (False, "失败原因")  - 执行失败
        """
        # ===== 获取 LLM 传入的参数 =====
        reason = self.action_data.get("reason", "")

        # ===== 读取配置（如果有的话）=====
        # greeting_msg = self.get_config("messages.greeting", "你好！")

        # ===== 在此编写你的核心逻辑 =====
        try:
            # 示例：发送文本消息
            reply_text = f"Test Action Plugin 执行成功！原因：{reason}"
            await self.send_text(reply_text)

            # 示例：发送图片
            # import base64
            # with open("image.png", "rb") as f:
            #     img_base64 = base64.b64encode(f.read()).decode()
            # await self.send_image(img_base64)

            # 示例：使用麦麦风格生成器
            # success, llm_data = await self.generate_reply(
            #     extra_info=f"用户需要：{reason}"
            # )
            # if success and llm_data and llm_data.reply_set:
            #     from src.plugin_system import send_api
            #     await send_api.custom_reply_set_to_stream(
            #         llm_data.reply_set, self.stream_id
            #     )

            return True, f"Test Action Plugin 执行成功"

        except Exception as e:
            self.logger.error(f"[TestActionPluginPlugin] 执行失败：{e}")
            return False, f"执行失败：{str(e)}"


# =============================================================================
# 插件主类
# =============================================================================


@register_plugin
class TestActionPluginPlugin(BasePlugin):
    """Test Action Plugin 插件主类"""

    plugin_name = "test_action_plugin"
    enable_plugin = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name = "config.toml"

    # ===== 配置文件定义（可选）=====
    # 取消注释并修改来添加配置项
    # config_schema: dict = {
    #     "plugin": {
    #         "enabled": ConfigField(type=bool, default=True, description="是否启用插件"),
    #     },
    #     "messages": {
    #         "greeting": ConfigField(
    #             type=str,
    #             default="你好！",
    #             description="问候语"
    #         ),
    #     },
    # }
    config_schema: dict = {}

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        """注册插件包含的组件"""
        return [
            (TestActionPluginAction.get_action_info(), TestActionPluginAction),
        ]

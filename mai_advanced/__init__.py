"""
mai_advanced - MaiBot 高级 API 扩展层

提供比基础模板更强大的功能：
- 自定义提示词回复（完全控制 LLM 输入）
- 回复组件注入（在正常回复前/后追加内容）
- 回复重写（替换/改写已生成的回复）
- 工具增强生成（调用内置工具 + LLM）
- 提示词检查（return_prompt=True 获取实际使用的提示词）

使用示例：
    from mai_advanced import AdvancedReplyBuilder, PromptModifier

    # 在 Action.execute() 中：
    builder = AdvancedReplyBuilder(self)
    await builder.generate_with_custom_prompt("你是一个专业厨师...")
"""

from .reply_builder import AdvancedReplyBuilder, ReplyComponent
from .prompt_modifier import PromptModifier

__all__ = [
    "AdvancedReplyBuilder",
    "ReplyComponent",
    "PromptModifier",
]

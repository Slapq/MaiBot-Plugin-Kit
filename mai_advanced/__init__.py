"""
mai_advanced - MaiBot 高级 API 扩展层

提供比基础模板更强大的功能：
- 自定义提示词回复（完全控制 LLM 输入）
- 回复组件注入（在正常回复前/后追加内容）
- 回复重写（替换/改写已生成的回复）
- 工具增强生成（调用内置工具 + LLM）
- 提示词检查（return_prompt=True 获取实际使用的提示词）

使用示例：
    from mai_advanced import AdvancedReplyBuilder, ReplyComponent, PromptModifier

    # 在 Action.execute() 或 Command.execute() 中：
    builder = AdvancedReplyBuilder(self)

    # 用完全自定义的提示词生成并发送回复（不走麦麦人格层）
    await builder.generate_custom_reply(
        prompt="你是一个专业厨师，请给出一道简单的家常菜食谱",
        send_result=True,
    )

    # 在正常回复前后注入额外内容
    await builder.generate_reply(
        extra_info="注意用俏皮的语气",
        prepend=[ReplyComponent.text("🤔 思考中…")],
    )

    # 直接调用底层 LLM（不发送，仅获取文本）
    modifier = PromptModifier(self)
    ok, text = await modifier.call_model(prompt="今天天气怎么样？")
"""

from .reply_builder import AdvancedReplyBuilder, ReplyComponent
from .prompt_modifier import PromptModifier

__all__ = [
    "AdvancedReplyBuilder",
    "ReplyComponent",
    "PromptModifier",
]

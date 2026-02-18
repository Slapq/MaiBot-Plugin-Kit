"""
{{PLUGIN_DISPLAY_NAME}} - 高级功能演示插件

演示如何使用 mai_advanced 扩展层实现：
1. 自定义提示词回复（完全控制 LLM 输入）
2. 回复组件注入（在正常回复前/后追加内容）
3. 回复重写（用麦麦语气说出你的内容）
4. 直接调用底层 LLM（不经过人格/上下文）
5. 获取实际提示词（调试）

作者：{{PLUGIN_AUTHOR}}
版本：{{PLUGIN_VERSION}}
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

# ──────────────────────────────────────────────────────────────────────────────
# 示例 1：使用自定义提示词的 Command
# ──────────────────────────────────────────────────────────────────────────────

class {{COMMAND_CLASS_NAME}}(BaseCommand):
    """
    /{{PLUGIN_NAME}} ask <问题> — 使用完全自定义提示词让 LLM 回答。

    与普通 generate_reply 的区别：
    - 不使用麦麦的人格、不附带聊天上下文
    - 你完全控制提示词的每一个字
    - 适合专业问答、代码生成、结构化输出
    """
    command_name = "{{PLUGIN_NAME}}_ask"
    command_description = "使用自定义提示词直接调用 LLM"
    command_pattern = r"^/{{PLUGIN_NAME}}\s+ask\s+(?P<question>.+)$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        # 使用命名捕获组（文档确认 matched_groups = re.match.groupdict()）
        question = self.matched_groups.get("question", "")
        if not question:
            await self.send_text("❌ 用法：/{{PLUGIN_NAME}} ask 你的问题")
            return False, "缺少问题", True

        # ── 方式 A：使用 AdvancedReplyBuilder（推荐，更简洁）──
        from mai_advanced import AdvancedReplyBuilder

        builder = AdvancedReplyBuilder(self)

        # 构造完全自定义的提示词
        custom_prompt = f"""你是一个博学多才、简洁友好的助手。
用户问：{question}
请给出简洁清晰的回答（不超过 200 字）。"""

        ok, result_text = await builder.generate_custom_reply(
            prompt=custom_prompt,
            send_result=True,   # 自动发送结果
        )

        if not ok:
            await self.send_text("❌ 生成回复失败，请稍后重试")
            return False, "生成失败", True

        return True, "自定义提示词回复成功", True


class {{COMMAND_CLASS_NAME}}Rewrite(BaseCommand):
    """
    /{{PLUGIN_NAME}} rewrite <内容> — 用麦麦的语气重写你的内容。

    适用场景：你有现成的文字，但希望麦麦用自己的语气（分句/错别字/口头禅）说出来。
    """
    command_name = "{{PLUGIN_NAME}}_rewrite"
    command_description = "将文本重写成麦麦的口吻"
    command_pattern = r"^/{{PLUGIN_NAME}}\s+rewrite\s+(?P<raw_text>.+)$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        raw_text = self.matched_groups.get("raw_text", "")
        if not raw_text:
            await self.send_text("❌ 用法：/{{PLUGIN_NAME}} rewrite 要改写的内容")
            return False, "缺少内容", True

        from mai_advanced import AdvancedReplyBuilder

        builder = AdvancedReplyBuilder(self)

        # 用麦麦风格重写（保留分句、错别字风格等）
        ok, components = await builder.rewrite_reply(
            raw_reply=raw_text,
            reason="用户希望将这段文字改成麦麦的自然口吻",
        )

        if ok:
            await builder.send_components(components)
        else:
            # 重写失败时直接发送原始内容
            await self.send_text(raw_text)

        return ok, "重写完成", True


class {{COMMAND_CLASS_NAME}}Debug(BaseCommand):
    """
    /{{PLUGIN_NAME}} prompt — 显示麦麦当前会用什么提示词（调试用）。
    """
    command_name = "{{PLUGIN_NAME}}_prompt_debug"
    command_description = "查看麦麦生成回复时使用的实际提示词（调试）"
    command_pattern = r"^/{{PLUGIN_NAME}}\s+prompt$"

    async def execute(self) -> Tuple[bool, Optional[str], bool]:
        from mai_advanced import PromptModifier

        modifier = PromptModifier(self)
        prompt = await modifier.get_actual_prompt(
            extra_info="[调试请求：请展示你收到的提示词]"
        )

        if prompt:
            # 截断以避免消息过长
            preview = prompt[:500] + ("..." if len(prompt) > 500 else "")
            await self.send_text(f"📝 当前提示词预览：\n\n{preview}")
        else:
            await self.send_text("❌ 获取提示词失败")

        return True, "提示词调试完成", True


# ──────────────────────────────────────────────────────────────────────────────
# 示例 2：回复注入的 Action
# ──────────────────────────────────────────────────────────────────────────────

class {{ACTION_CLASS_NAME}}(BaseAction):
    """
    回复注入演示 Action。

    展示如何在麦麦正常回复的前/后注入自定义内容：
    - 前置：在正常回复前发送一个"思考中..."提示
    - 注入 extra_info：向提示词末尾追加额外上下文
    - 后置：在正常回复后追加一条引导语
    """
    action_name = "{{PLUGIN_NAME}}_inject"
    action_description = "演示回复组件注入：在正常回复前后追加内容"
    activation_type = ActionActivationType.ALWAYS

    action_require = [
        "当用户提出复杂问题需要深入回答时",
        "当需要在回复前添加提示或后置附加信息时",
    ]
    action_parameters = {
        "topic": "用户当前话题的摘要",
        "extra_context": "需要注入到提示词的额外上下文（可选）",
        "reason": "触发原因",
    }
    associated_types = ["text"]

    async def execute(self) -> Tuple[bool, str]:
        topic = self.action_data.get("topic", "")
        extra_context = self.action_data.get("extra_context", "")
        reason = self.action_data.get("reason", "")

        from mai_advanced import AdvancedReplyBuilder, ReplyComponent

        builder = AdvancedReplyBuilder(self)

        # ── 触发正常生成，同时在前后注入内容 ──
        await builder.generate_reply(
            # 向提示词末尾追加额外上下文
            extra_info=extra_context if extra_context else f"当前话题：{topic}",

            # 在正常回复之前发送（前置注入）
            prepend=[
                ReplyComponent.text("🤔 让我想想…", typing=True),
            ],

            # 在正常回复之后发送（后置注入）
            append=[
                ReplyComponent.text("💡 如果你有更多问题，随时告诉我！"),
            ],
        )

        return True, f"回复注入完成（话题：{topic}）"


# ──────────────────────────────────────────────────────────────────────────────
# 示例 3：直接调用 LLM 的 Action
# ──────────────────────────────────────────────────────────────────────────────

class {{ACTION_CLASS_NAME}}DirectLLM(BaseAction):
    """
    直接调用底层 LLM 的 Action（绕过麦麦人格层）。

    适用场景：需要精确的 JSON 输出、代码生成、或完全定制化的分析任务。
    """
    action_name = "{{PLUGIN_NAME}}_direct_llm"
    action_description = "直接调用底层 LLM，完全控制提示词"
    activation_type = ActionActivationType.ALWAYS

    action_require = [
        "当需要精确的结构化输出（如 JSON / 代码）时",
        "当需要完全自定义提示词时",
    ]
    action_parameters = {
        "task": "要执行的任务描述",
        "output_format": "期望的输出格式（如 json, markdown, plain）",
        "reason": "触发原因",
    }
    associated_types = ["text"]

    async def execute(self) -> Tuple[bool, str]:
        task = self.action_data.get("task", "")
        output_format = self.action_data.get("output_format", "plain")

        if not task:
            return False, "缺少任务描述"

        from mai_advanced import PromptModifier

        modifier = PromptModifier(self)

        # 构造高度精确的提示词
        format_hint = {
            "json": "请只输出合法的 JSON，不要添加任何解释或 markdown 代码块。",
            "markdown": "请用 Markdown 格式输出，使用标题和列表。",
            "plain": "请用简洁的纯文本回答，不要使用 markdown。",
        }.get(output_format, "")

        prompt = f"""你是一个专业助手。{format_hint}

任务：{task}"""

        # call_model 不自动发送；用 self.send_text() 发送（BaseAction 内置方法）
        ok, result = await modifier.call_model(
            prompt=prompt,
            temperature=0.3,   # 低温度 = 更确定性的输出
        )

        if ok and result:
            await self.send_text(result)
            return True, "直接 LLM 调用完成"
        else:
            await self.send_text("❌ 生成失败，请稍后重试")
            return False, "LLM 调用失败"


# ──────────────────────────────────────────────────────────────────────────────
# 主插件类
# ──────────────────────────────────────────────────────────────────────────────

@register_plugin
class {{PLUGIN_CLASS_NAME}}(BasePlugin):
    """{{PLUGIN_DISPLAY_NAME}} — 高级 API 演示插件"""

    plugin_name = "{{PLUGIN_NAME}}"
    enable_plugin = True
    dependencies: List[str] = []
    python_dependencies: List[str] = []
    config_file_name = "config.toml"
    config_schema: dict = {}

    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:
        return [
            # Commands
            ({{COMMAND_CLASS_NAME}}.get_command_info(),          {{COMMAND_CLASS_NAME}}),
            ({{COMMAND_CLASS_NAME}}Rewrite.get_command_info(),   {{COMMAND_CLASS_NAME}}Rewrite),
            ({{COMMAND_CLASS_NAME}}Debug.get_command_info(),     {{COMMAND_CLASS_NAME}}Debug),
            # Actions
            ({{ACTION_CLASS_NAME}}.get_action_info(),            {{ACTION_CLASS_NAME}}),
            ({{ACTION_CLASS_NAME}}DirectLLM.get_action_info(),   {{ACTION_CLASS_NAME}}DirectLLM),
        ]

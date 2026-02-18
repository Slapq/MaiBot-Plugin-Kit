"""
mai_advanced.prompt_modifier - 提示词修改与 LLM 直接调用工具

提供对底层 LLM 的精细控制：
- 列出可用模型，按需选择
- 直接调用任意模型生成内容（不经过麦麦人格层）
- 带工具调用的 LLM 生成
"""

from __future__ import annotations
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger("mai_advanced.prompt_modifier")


class PromptModifier:
    """
    提示词修改器 — 直接操控底层 LLM，完全控制提示词。

    使用场景：
    - 需要使用特定模型（如更强的推理模型）
    - 需要完全不同的提示词（不走麦麦人格/上下文）
    - 需要使用工具调用（function calling）
    - 需要获取纯 JSON / 代码输出

    在 Action 或 Command 的 execute() 中实例化：
        modifier = PromptModifier(self)
    """

    def __init__(self, plugin_component):
        """
        Args:
            plugin_component: BaseAction 或 BaseCommand 的实例（即 self）
        """
        self._comp = plugin_component

    @property
    def _stream_id(self) -> str:
        return self._comp.stream_id

    @property
    def _chat_stream(self):
        return getattr(self._comp.message, "chat_stream", None)

    # ── 1. 查询可用模型 ───────────────────────────────────────────────────────

    def get_available_models(self) -> Dict[str, Any]:
        """
        获取系统配置的所有可用模型。

        Returns:
            Dict[str, TaskConfig] — key 为模型名，value 为模型配置对象

        示例：
            models = modifier.get_available_models()
            for name, config in models.items():
                print(f"模型: {name}")
        """
        from src.plugin_system.apis import llm_api
        return llm_api.get_available_models()

    def get_default_model(self) -> Optional[Any]:
        """
        获取默认（第一个）可用模型配置。

        Returns:
            TaskConfig 对象，或 None（无可用模型时）
        """
        models = self.get_available_models()
        if not models:
            return None
        return next(iter(models.values()))

    # ── 2. 使用自定义提示词调用指定模型 ─────────────────────────────────────

    async def call_model(
        self,
        prompt: str,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        request_type: str = "plugin.advanced",
    ) -> Tuple[bool, str]:
        """
        直接调用 LLM 模型，完全控制提示词。

        不经过麦麦人格层，也不附带聊天上下文。
        适用于：结构化输出、代码生成、纯粹的问答等。

        Args:
            prompt:       完整提示词（包含 system 和 user 部分）
            model_name:   模型名称（None 则使用第一个可用模型）
            temperature:  生成温度（None 使用默认）
            max_tokens:   最大 token 数（None 使用默认）
            request_type: 请求类型标识（用于日志）

        Returns:
            (success, generated_text)

        示例：
            ok, result = await modifier.call_model(
                prompt="请用 JSON 格式返回：{\"city\": \"北京\", \"weather\": \"晴\"}",
                temperature=0.1,
            )
        """
        from src.plugin_system.apis import llm_api

        models = self.get_available_models()
        if not models:
            logger.error("[PromptModifier] 没有可用的模型")
            return False, ""

        if model_name and model_name in models:
            model_config = models[model_name]
        else:
            if model_name:
                logger.warning(f"[PromptModifier] 模型 '{model_name}' 不存在，使用默认模型")
            model_config = next(iter(models.values()))

        success, content, reasoning, used_model = await llm_api.generate_with_model(
            prompt=prompt,
            model_config=model_config,
            request_type=request_type,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not success:
            logger.warning(f"[PromptModifier] 模型 {used_model} 生成失败")
            return False, content

        return True, content

    # ── 3. 注入额外上下文到提示词 ────────────────────────────────────────────

    async def generate_with_extra_context(
        self,
        extra_info: str,
        reply_to: str = "",
        enable_tool: bool = False,
        return_prompt: bool = False,
    ) -> Tuple[bool, List[Tuple[str, Any]], Optional[str]]:
        """
        在麦麦默认提示词中注入额外上下文，然后生成回复。

        与 AdvancedReplyBuilder.generate_reply(extra_info=...) 等价，
        但此方法返回原始 reply_set，不自动发送消息，更适合需要进一步处理的场景。

        Args:
            extra_info:    要注入到提示词末尾的文本
            reply_to:      回复目标，格式 "发送者:消息内容"
            enable_tool:   是否启用内置工具
            return_prompt: 是否返回实际提示词

        Returns:
            (success, reply_set, prompt_or_none)

        示例：
            # 注入额外知识，让麦麦基于此知识回答
            ok, reply_set, _ = await modifier.generate_with_extra_context(
                extra_info="以下是今日新闻摘要：[新闻内容...]\\n\\n请基于以上内容回答用户问题"
            )
            if ok:
                from src.plugin_system.apis import send_api
                for rtype, rcontent in reply_set:
                    if rtype == "text":
                        await send_api.text_to_stream(rcontent, self._stream_id)
        """
        from src.plugin_system.apis import generator_api

        return await generator_api.generate_reply(
            chat_stream=self._chat_stream,
            extra_info=extra_info,
            reply_to=reply_to,
            enable_tool=enable_tool,
            return_prompt=return_prompt,
        )

    # ── 4. 带工具调用的 LLM 生成 ─────────────────────────────────────────────

    async def call_model_with_tools(
        self,
        prompt: str,
        tool_names: Optional[List[str]] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Tuple[bool, str, Optional[List[Any]]]:
        """
        使用工具调用（function calling）模式调用 LLM。

        Args:
            prompt:      提示词
            tool_names:  要启用的工具名称列表（None 则启用全部）
            model_name:  模型名称
            temperature: 生成温度
            max_tokens:  最大 token 数

        Returns:
            (success, text_content, tool_calls_or_none)

        示例：
            ok, content, tool_calls = await modifier.call_model_with_tools(
                prompt="请帮我搜索今天的天气",
                tool_names=["web_search"],
            )
            if tool_calls:
                for call in tool_calls:
                    print(f"工具调用: {call.name}({call.arguments})")
        """
        from src.plugin_system.apis import llm_api, tool_api

        models = self.get_available_models()
        if not models:
            return False, "", None

        model_config = models.get(model_name) or next(iter(models.values()))

        # 获取可用工具定义
        try:
            all_tool_defs = tool_api.get_llm_available_tool_definitions()
        except Exception:
            all_tool_defs = []

        if tool_names and all_tool_defs:
            tool_options = [t for t in all_tool_defs if t.get("name") in tool_names]
        else:
            tool_options = all_tool_defs if all_tool_defs else None

        try:
            success, content, reasoning, used_model, tool_calls = (
                await llm_api.generate_with_model_with_tools(
                    prompt=prompt,
                    model_config=model_config,
                    tool_options=tool_options,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )
            return success, content, tool_calls
        except Exception as e:
            logger.error(f"[PromptModifier] 工具调用失败：{e}")
            return False, str(e), None

    # ── 5. 获取实际提示词（调试用）──────────────────────────────────────────

    async def get_actual_prompt(self, extra_info: str = "") -> Optional[str]:
        """
        获取麦麦生成回复时实际使用的提示词（return_prompt=True）。

        不会发送任何消息，仅用于调试/记录。

        Returns:
            提示词字符串，或 None
        """
        from src.plugin_system.apis import generator_api

        _, _, prompt = await generator_api.generate_reply(
            chat_stream=self._chat_stream,
            extra_info=extra_info,
            return_prompt=True,
        )
        return prompt

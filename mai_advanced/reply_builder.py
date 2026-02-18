"""
mai_advanced.reply_builder - 回复组件注入与构建工具

提供对麦麦回复系统的高级控制，包括：
- 自定义回复集合构建
- 在正常生成回复的基础上注入额外内容
- 手动构造并发送多组件回复
"""

from __future__ import annotations
import logging
from typing import List, Tuple, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    # 仅类型检查时导入，避免运行时循环依赖
    pass

logger = logging.getLogger("mai_advanced.reply_builder")


# ──────────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────────

class ReplyComponent:
    """
    回复组件 — 单个可发送的消息单元。

    Attributes:
        type:    消息类型："text" / "emoji" / "image" / "command" / "custom"
        content: 消息内容（文本字符串 或 base64 图片/表情）
        extra:   附加参数（如 typing=True, reply_to="发送者:内容"）
    """

    def __init__(self, type_: str, content: str, **extra):
        self.type = type_
        self.content = content
        self.extra = extra

    # ── 快捷工厂方法 ──────────────────────────────────────────────────────────

    @classmethod
    def text(cls, content: str, typing: bool = False, reply_to: str = "") -> "ReplyComponent":
        """创建文本组件"""
        return cls("text", content, typing=typing, reply_to=reply_to)

    @classmethod
    def emoji(cls, base64_data: str) -> "ReplyComponent":
        """创建表情包组件"""
        return cls("emoji", base64_data)

    @classmethod
    def image(cls, base64_data: str) -> "ReplyComponent":
        """创建图片组件"""
        return cls("image", base64_data)

    @classmethod
    def from_tuple(cls, t: Tuple[str, Any]) -> "ReplyComponent":
        """从 reply_set 元组创建组件"""
        return cls(t[0], t[1])

    def __repr__(self) -> str:
        preview = self.content[:40] + "..." if len(self.content) > 40 else self.content
        return f"ReplyComponent(type={self.type!r}, content={preview!r})"


# ──────────────────────────────────────────────────────────────────────────────
# 主类
# ──────────────────────────────────────────────────────────────────────────────

class AdvancedReplyBuilder:
    """
    高级回复构建器 — 注入/拦截/扩展麦麦的回复。

    在 Action 或 Command 的 execute() 中实例化：

        builder = AdvancedReplyBuilder(self)

    主要能力：
    1. generate_reply()         — 触发正常回复生成，可追加/前置自定义组件
    2. generate_custom_reply()  — 使用完全自定义提示词生成回复
    3. send_components()        — 直接发送一组 ReplyComponent
    4. inject_before/after()    — 在正常回复前/后插入内容

    示例（Action.execute()）：
        builder = AdvancedReplyBuilder(self)

        # 在正常回复前追加一条提示
        await builder.inject_before(ReplyComponent.text("🤔 思考中..."))

        # 触发正常回复生成并发送
        await builder.generate_reply(extra_info="请用俏皮的语气回复")

        # 发送完毕
        return True, "完成"
    """

    def __init__(self, plugin_component):
        """
        Args:
            plugin_component: BaseAction 或 BaseCommand 的实例（即 self）
        """
        self._comp = plugin_component

    @property
    def _stream_id(self) -> str:
        """
        返回当前聊天流 ID。
        BaseAction → self.chat_id（文档确认）
        BaseCommand → self.chat_id 或 self.stream_id（兼容两种写法）
        """
        for attr in ("stream_id", "chat_id"):
            v = getattr(self._comp, attr, None)
            if v:
                return v
        return ""

    @property
    def _chat_stream(self):
        """
        返回 ChatStream 对象。
        BaseAction  → self.chat_stream（文档：直接属性）
        BaseCommand → self.message.chat_stream（hello_world 示例用法）
        """
        # 优先尝试直接属性（BaseAction）
        cs = getattr(self._comp, "chat_stream", None)
        if cs is not None:
            return cs
        # 兜底：通过 message 对象（BaseCommand）
        msg = getattr(self._comp, "message", None)
        if msg is not None:
            return getattr(msg, "chat_stream", None)
        return None

    # ── 1. 生成正常回复（可附加内容）────────────────────────────────────────────

    async def generate_reply(
        self,
        extra_info: str = "",
        reply_to: str = "",
        prepend: Optional[List[ReplyComponent]] = None,
        append: Optional[List[ReplyComponent]] = None,
        enable_tool: bool = False,
        return_prompt: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """
        触发正常的 generate_reply，可在回复前/后注入自定义组件。

        Args:
            extra_info:   追加到提示词末尾的附加信息（注入提示词）
            reply_to:     指定回复目标，格式 "发送者名:消息内容"
            prepend:      在正常回复之前发送的组件列表
            append:       在正常回复之后发送的组件列表
            enable_tool:  是否启用内置工具
            return_prompt: 是否返回实际使用的提示词

        Returns:
            (success, prompt_if_requested)
        """
        from src.plugin_system.apis import generator_api, send_api

        # 先发送前置组件
        if prepend:
            await self.send_components(prepend)

        # 生成正常回复
        success, reply_set, prompt = await generator_api.generate_reply(
            chat_stream=self._chat_stream,
            extra_info=extra_info,
            reply_to=reply_to,
            enable_tool=enable_tool,
            return_prompt=return_prompt,
        )

        if success:
            for reply_type, reply_content in reply_set:
                if reply_type == "text":
                    await send_api.text_to_stream(reply_content, self._stream_id)
                elif reply_type == "emoji":
                    await send_api.emoji_to_stream(reply_content, self._stream_id)
                elif reply_type == "image":
                    await send_api.image_to_stream(reply_content, self._stream_id)
                else:
                    await send_api.custom_to_stream(reply_type, reply_content, self._stream_id)

        # 再发送后置组件
        if append:
            await self.send_components(append)

        return success, prompt if return_prompt else None

    # ── 2. 完全自定义提示词回复 ──────────────────────────────────────────────

    async def generate_custom_reply(
        self,
        prompt: str,
        send_result: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        使用完全自定义提示词调用 LLM 生成回复（绕过默认人格/上下文）。

        适用场景：
        - 角色扮演模式（临时切换人格）
        - 专业问答（如"你是一个法律顾问"）
        - 结构化生成（JSON / 代码 / 表格）

        Args:
            prompt:      完整的自定义提示词
            send_result: 是否自动将结果发送到会话

        Returns:
            (success, generated_text)

        示例：
            ok, text = await builder.generate_custom_reply(
                prompt="你是一个厨师，请给出一道简单的家常菜食谱"
            )
        """
        from src.plugin_system.apis import generator_api, send_api

        result_text = await generator_api.generate_response_custom(
            chat_stream=self._chat_stream,
            prompt=prompt,
        )

        if result_text is None:
            logger.warning("[AdvancedReplyBuilder] generate_response_custom 返回 None")
            return False, None

        if send_result:
            await send_api.text_to_stream(result_text, self._stream_id)

        return True, result_text

    # ── 3. 重写回复 ──────────────────────────────────────────────────────────

    async def rewrite_reply(
        self,
        raw_reply: str,
        reason: str = "",
        reply_to: str = "",
    ) -> Tuple[bool, List[ReplyComponent]]:
        """
        将原始文本通过麦麦的风格化处理器重写（保持麦麦语气/分句/错别字风格）。

        适用场景：
        - 你有现成的内容，但希望麦麦用自己的语气说出来
        - 将 API 返回的格式化文本转成麦麦自然语气

        Args:
            raw_reply: 原始回复文本（未风格化）
            reason:    重写原因（帮助模型理解目的）
            reply_to:  回复目标，格式 "发送者:消息内容"

        Returns:
            (success, components_list)

        示例：
            ok, components = await builder.rewrite_reply(
                raw_reply="天气晴好，温度25摄氏度，适合外出",
                reason="将天气预报改成麦麦的口吻"
            )
            if ok:
                await builder.send_components(components)
        """
        from src.plugin_system.apis import generator_api, send_api

        success, reply_set, _ = await generator_api.rewrite_reply(
            chat_stream=self._chat_stream,
            raw_reply=raw_reply,
            reason=reason,
            reply_to=reply_to,
        )

        components = [ReplyComponent.from_tuple(t) for t in reply_set] if success else []
        return success, components

    # ── 4. 直接发送组件列表 ──────────────────────────────────────────────────

    async def send_components(self, components: List[ReplyComponent]) -> bool:
        """
        按顺序发送一组 ReplyComponent。

        Args:
            components: 要发送的组件列表

        Returns:
            是否全部成功

        示例：
            await builder.send_components([
                ReplyComponent.text("结果如下："),
                ReplyComponent.image(base64_chart),
                ReplyComponent.text("如有疑问请告诉我！"),
            ])
        """
        from src.plugin_system.apis import send_api

        all_ok = True
        for comp in components:
            if comp.type == "text":
                ok = await send_api.text_to_stream(
                    comp.content,
                    self._stream_id,
                    typing=comp.extra.get("typing", False),
                    reply_to=comp.extra.get("reply_to", ""),
                )
            elif comp.type == "emoji":
                ok = await send_api.emoji_to_stream(comp.content, self._stream_id)
            elif comp.type == "image":
                ok = await send_api.image_to_stream(comp.content, self._stream_id)
            else:
                ok = await send_api.custom_to_stream(
                    comp.type,
                    comp.content,
                    self._stream_id,
                    display_message=comp.extra.get("display_message", ""),
                )
            all_ok = all_ok and ok
        return all_ok

    # ── 5. 便捷方法 ──────────────────────────────────────────────────────────

    async def inject_before(self, *components: ReplyComponent) -> None:
        """在当前位置插入内容（通常在 generate_reply 之前调用）"""
        await self.send_components(list(components))

    async def inject_after(self, *components: ReplyComponent) -> None:
        """在当前位置追加内容（通常在 generate_reply 之后调用）"""
        await self.send_components(list(components))

    async def get_prompt_preview(self, extra_info: str = "") -> Optional[str]:
        """
        获取本次生成会使用的提示词（不发送回复）。

        适用于调试，了解模型实际接收到的提示词内容。

        Returns:
            提示词字符串，或 None（生成失败时）
        """
        from src.plugin_system.apis import generator_api

        _, _, prompt = await generator_api.generate_reply(
            chat_stream=self._chat_stream,
            extra_info=extra_info,
            return_prompt=True,
        )
        return prompt

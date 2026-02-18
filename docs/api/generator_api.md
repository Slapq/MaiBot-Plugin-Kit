# ✨ 回复生成器 API

> **来源**：`src.plugin_system.apis.generator_api`

回复生成器 API 使用麦麦完整的回复生成流程，包括上下文感知、人设、表情包选择等。  
与 `llm_api` 的区别：这里生成的是"麦麦的回复"，而不是裸 LLM 输出。

## 导入方式

```python
from src.plugin_system import generator_api
# 或
from src.plugin_system.apis import generator_api
```

---

## 主要功能

### 1. 生成回复（完整流程）

```python
result_status, data = await generator_api.generate_reply(
    chat_stream=self.chat_stream,     # ChatStream 对象（推荐）
    # chat_id="stream_id",            # 或用 chat_id（备用）
    reply_to="",                      # 回复目标，格式："{发送者的person_name:消息内容}"
    extra_info="",                    # 附加信息（会加入上下文）
    enable_tool=False,                # 是否启用 Tool
    enable_splitter=True,             # 是否启用文本分割
    enable_chinese_typo=True,         # 是否模拟中文错字（拟人化）
    return_prompt=False,              # 是否返回使用的提示词
    request_type="plugin.generate",   # 用于日志记录
)

# result_status: bool
# data: 包含 data.reply_set.reply_data 的对象
if result_status and data:
    for reply_seg in data.reply_set.reply_data:
        content = reply_seg.content
        # reply_seg.type: "text" / "emoji" / "image" 等
        await self.send_text(content)
```

### 2. 重写已有回复

适合在插件中先生成文字，再用麦麦的表达风格重写：

```python
result_status, data = await generator_api.rewrite_reply(
    chat_stream=self.chat_stream,
    raw_reply="需要重写的原始文本",     # 原始内容
    reason="为什么重写（给 LLM 看的）", # 重写原因
    reply_to="",                       # 可选回复目标
    enable_splitter=True,
    enable_chinese_typo=True,
)

if result_status and data:
    for reply_seg in data.reply_set.reply_data:
        await self.send_text(reply_seg.content)
```

### 3. 自定义提示词生成

```python
content = await generator_api.generate_response_custom(
    chat_stream=self.chat_stream,
    prompt="你是一个古代诗人，请用五言绝句回复：" + user_message,
)
if content:
    await self.send_text(content)
```

---

## 实战示例

### 命令插件：用麦麦口吻复述内容

```python
class RephraseCommand(BaseCommand):
    command_name = "rephrase"
    command_description = "用麦麦的口吻重新表达一段话"
    command_pattern = r"^/rephrase\s+(?P<text>.+)$"

    async def execute(self):
        from src.plugin_system import generator_api

        text = self.matched_groups.get("text", "")

        result_status, data = await generator_api.rewrite_reply(
            chat_stream=self.message.chat_stream,
            raw_reply=text,
            reason="用户请求用麦麦的风格重新表达这段话",
        )

        if result_status and data:
            for seg in data.reply_set.reply_data:
                await self.send_text(seg.content)
        else:
            await self.send_text(f"（麦麦版本）{text}")

        return True, "重述成功", True
```

### Action 插件：主动发起话题

```python
class TopicAction(BaseAction):
    action_name = "start_topic"
    action_description = "主动发起一个有趣的话题"
    activation_type = ActionActivationType.RANDOM
    random_activation_probability = 0.1
    action_require = ["当聊天沉寂一段时间时", "当想活跃气氛时"]
    associated_types = ["text"]
    action_parameters = {"topic": "要聊的话题"}

    async def execute(self):
        from src.plugin_system import generator_api

        topic = self.action_data.get("topic", "今天发生了什么有趣的事")

        content = await generator_api.generate_response_custom(
            chat_stream=self.chat_stream,
            prompt=f"请自然地发起关于「{topic}」的话题，用麦麦的口吻，不超过 50 字",
        )

        if content:
            await self.send_text(content)

        return True, f"发起了话题：{topic}"
```

---

## 注意事项

- `generate_reply` 会读取聊天历史、人设等上下文，消耗 Token 较多
- `rewrite_reply` 适合"把程序生成的结果转化成自然语言"的场景
- `generate_response_custom` 不含上下文，适合独立的文本生成任务
- 如果 `result_status` 为 False，不要强行发送，会导致空消息

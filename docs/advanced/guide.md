# 高级功能指南

本指南介绍如何使用 `mai_advanced` 扩展层实现超越基础模板的高级功能，包括：

- **自定义提示词回复** — 完全控制 LLM 的输入
- **回复组件注入** — 在正常回复的前/后插入内容
- **回复重写** — 用麦麦的语气说出你的内容
- **直接调用底层 LLM** — 不经过人格/上下文层

---

## 快速开始

### 安装 Advanced 模板

```bash
python -m mai_plugin_cli create my_plugin --template advanced
```

这会生成包含所有高级功能示例的完整插件。

---

## `mai_advanced` 模块说明

### 导入方式

```python
from mai_advanced import AdvancedReplyBuilder, ReplyComponent, PromptModifier
```

> ⚠️ `mai_advanced` 需要放在 MaiBot 的 `plugins/` 同级目录（或安装为包）。  
> 更简单的方式：把 `mai_advanced/` 目录复制到你的插件目录旁。

---

## 功能一：自定义提示词回复

适用于：临时角色扮演、专业问答、完全不想用麦麦人格的场景。

```python
from mai_advanced import AdvancedReplyBuilder

class MyAction(BaseAction):
    async def execute(self):
        builder = AdvancedReplyBuilder(self)

        # 构造完全自定义的提示词
        ok, result = await builder.generate_custom_reply(
            prompt="""你是一个专业的中医师。
用户问：头疼怎么办？
请给出 3 条实用建议。""",
            send_result=True,  # 自动发送
        )

        return ok, "完成"
```

**底层 API：** `generator_api.generate_response_custom(chat_stream, prompt)`

---

## 功能二：提示词注入（在原有提示词中追加信息）

适用于：想保留麦麦的人格和上下文，但需要追加额外知识或指令。

```python
builder = AdvancedReplyBuilder(self)

# extra_info 会追加到麦麦默认提示词的末尾
await builder.generate_reply(
    extra_info="以下是今日新闻摘要：[新闻内容...]\n\n请基于以上内容回答"
)
```

**底层 API：** `generator_api.generate_reply(..., extra_info="...", return_prompt=True)`

---

## 功能三：回复组件注入（前置/后置）

适用于：在麦麦正常回复的前/后追加自定义内容。

```python
from mai_advanced import AdvancedReplyBuilder, ReplyComponent

builder = AdvancedReplyBuilder(self)

await builder.generate_reply(
    extra_info="请用热情的语气回复",

    # 在正常回复【之前】发送
    prepend=[
        ReplyComponent.text("🤔 正在思考...", typing=True),
    ],

    # 在正常回复【之后】发送
    append=[
        ReplyComponent.text("💡 如有疑问请继续问我！"),
    ],
)
```

### ReplyComponent 类型

| 类型 | 创建方式 | 说明 |
|------|----------|------|
| 文本 | `ReplyComponent.text("内容")` | 普通文本，支持 `typing=True` 和 `reply_to` |
| 表情包 | `ReplyComponent.emoji(base64)` | 发送表情包 |
| 图片 | `ReplyComponent.image(base64)` | 发送图片 |
| 自定义 | `ReplyComponent("type", "content")` | 任意消息类型 |

---

## 功能四：回复重写

适用于：你有现成的文字（如 API 返回的格式化内容），希望麦麦用自己的语气说出来。

```python
builder = AdvancedReplyBuilder(self)

# 获取外部数据（如天气 API）
weather_data = "北京：晴，25°C，微风"

# 用麦麦风格重写（保留分句、语气等个性化特征）
ok, components = await builder.rewrite_reply(
    raw_reply=weather_data,
    reason="将天气信息转成麦麦的口吻"
)

if ok:
    await builder.send_components(components)
```

**底层 API：** `generator_api.rewrite_reply(chat_stream, raw_reply, reason, reply_to)`

---

## 功能五：直接调用底层 LLM

适用于：需要精确控制模型参数、使用特定模型、获取 JSON/代码等结构化输出。

```python
from mai_advanced import PromptModifier

modifier = PromptModifier(self)

# 列出可用模型
models = modifier.get_available_models()
print(list(models.keys()))  # ['gpt-4o', 'deepseek-v3', ...]

# 调用指定模型
ok, result = await modifier.call_model(
    prompt="请用 JSON 格式返回北京的天气：{\"city\": ..., \"temp\": ...}",
    model_name="deepseek-v3",   # 指定模型（None 则用默认）
    temperature=0.1,             # 低温度 = 确定性更强
    max_tokens=500,
)

if ok:
    import json
    data = json.loads(result)
```

**底层 API：** `llm_api.generate_with_model(prompt, model_config, temperature, max_tokens)`

---

## 功能六：带工具调用的 LLM（Function Calling）

```python
ok, content, tool_calls = await modifier.call_model_with_tools(
    prompt="请搜索今天的头条新闻",
    tool_names=["web_search"],    # 只启用这个工具
)

if tool_calls:
    for call in tool_calls:
        print(f"工具: {call.name}，参数: {call.arguments}")
```

**底层 API：** `llm_api.generate_with_model_with_tools(...)`

---

## 功能七：获取实际提示词（调试）

```python
modifier = PromptModifier(self)
prompt = await modifier.get_actual_prompt(
    extra_info="[调试模式]"
)
print(prompt[:500])
```

**底层 API：** `generator_api.generate_reply(..., return_prompt=True)`

---

## 完整 API 速查表

### AdvancedReplyBuilder

| 方法 | 说明 | 底层 API |
|------|------|----------|
| `generate_reply(extra_info, prepend, append)` | 带注入的正常回复生成 | `generator_api.generate_reply` |
| `generate_custom_reply(prompt)` | 完全自定义提示词回复 | `generator_api.generate_response_custom` |
| `rewrite_reply(raw_reply, reason)` | 用麦麦风格重写内容 | `generator_api.rewrite_reply` |
| `send_components(components)` | 发送组件列表 | `send_api.text/emoji/image_to_stream` |
| `inject_before(*components)` | 在当前位置前置注入 | `send_api` |
| `inject_after(*components)` | 在当前位置后置注入 | `send_api` |
| `get_prompt_preview(extra_info)` | 获取当前会用的提示词 | `generator_api.generate_reply(return_prompt=True)` |

### PromptModifier

| 方法 | 说明 | 底层 API |
|------|------|----------|
| `get_available_models()` | 列出所有可用模型 | `llm_api.get_available_models` |
| `call_model(prompt, model_name, temperature)` | 直接调用模型 | `llm_api.generate_with_model` |
| `call_model_with_tools(prompt, tool_names)` | 带工具调用的 LLM | `llm_api.generate_with_model_with_tools` |
| `generate_with_extra_context(extra_info)` | 注入上下文并生成 | `generator_api.generate_reply` |
| `get_actual_prompt(extra_info)` | 获取实际提示词 | `generator_api.generate_reply(return_prompt=True)` |

---

## 注意事项

1. **不能直接修改麦麦的"主动回复"** — 麦麦在没有 Action/Command 触发的情况下自动产生的回复，插件目前无法直接拦截和修改，只能通过 Action 在触发时控制。

2. **`extra_info` 和 `generate_response_custom` 的区别：**
   - `extra_info`：在现有提示词末尾**追加**内容，麦麦的人格、上下文都保留
   - `generate_response_custom`：使用**全新提示词**，不附带任何上下文

3. **`rewrite_reply` 的风格化处理**：会经过麦麦的分句器和错别字模块，适合希望保留麦麦语气的场景。

4. **异步要求**：所有方法均为 `async`，必须在 `async def execute()` 中用 `await` 调用。

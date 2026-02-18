# AdvancedReplyBuilder API 参考

`AdvancedReplyBuilder` 是 `mai_advanced` 模块的核心类，提供对麦麦回复流程的高级控制。

## 导入

```python
from mai_advanced import AdvancedReplyBuilder, ReplyComponent
```

## 实例化

在 Action 或 Command 的 `execute()` 方法中实例化：

```python
async def execute(self):
    builder = AdvancedReplyBuilder(self)  # 传入 self
    ...
```

---

## 方法列表

### `generate_reply()`

在正常回复的基础上，支持前置/后置注入和提示词追加。

```python
async def generate_reply(
    self,
    extra_info: str = "",
    reply_to: str = "",
    prepend: Optional[List[ReplyComponent]] = None,
    append: Optional[List[ReplyComponent]] = None,
    enable_tool: bool = False,
    return_prompt: bool = False,
) -> Tuple[bool, Optional[str]]
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `extra_info` | `str` | 追加到提示词末尾的文本（注入额外上下文） |
| `reply_to` | `str` | 回复目标，格式 `"发送者:消息"` |
| `prepend` | `List[ReplyComponent]` | 在正常回复**之前**发送的组件 |
| `append` | `List[ReplyComponent]` | 在正常回复**之后**发送的组件 |
| `enable_tool` | `bool` | 是否启用内置工具 |
| `return_prompt` | `bool` | 是否返回实际使用的提示词 |

**返回：** `(success: bool, prompt: Optional[str])`

**示例：**
```python
# 最简单的注入
await builder.generate_reply(
    extra_info="请用活泼俏皮的语气回复",
    prepend=[ReplyComponent.text("🤔 思考中…", typing=True)],
    append=[ReplyComponent.text("如有疑问请告诉我！")],
)
```

---

### `generate_custom_reply()`

使用完全自定义的提示词生成回复，绕过麦麦的人格和聊天上下文。

```python
async def generate_custom_reply(
    self,
    prompt: str,
    send_result: bool = True,
) -> Tuple[bool, Optional[str]]
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `prompt` | `str` | 完整的自定义提示词 |
| `send_result` | `bool` | 是否自动发送结果（默认 True） |

**返回：** `(success: bool, generated_text: Optional[str])`

**底层 API：** `generator_api.generate_response_custom()`

**示例：**
```python
ok, text = await builder.generate_custom_reply(
    prompt="你是一个古代诗人，请用七言绝句回答：春天来了",
    send_result=True,
)
```

---

### `rewrite_reply()`

将原始文本通过麦麦的风格化处理器重写（保留分句/错别字/语气）。

```python
async def rewrite_reply(
    self,
    raw_reply: str,
    reason: str = "",
    reply_to: str = "",
) -> Tuple[bool, List[ReplyComponent]]
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `raw_reply` | `str` | 原始文本（未风格化） |
| `reason` | `str` | 重写原因（帮助模型理解目的） |
| `reply_to` | `str` | 回复目标 |

**返回：** `(success: bool, components: List[ReplyComponent])`

**底层 API：** `generator_api.rewrite_reply()`

**示例：**
```python
ok, components = await builder.rewrite_reply(
    raw_reply="今天北京天气晴，温度25°C，适合出门",
    reason="将天气预报改成麦麦的自然口吻"
)
if ok:
    await builder.send_components(components)
```

---

### `send_components()`

按顺序发送一组 `ReplyComponent`。

```python
async def send_components(
    self,
    components: List[ReplyComponent],
) -> bool
```

**返回：** 是否全部成功

**示例：**
```python
await builder.send_components([
    ReplyComponent.text("结果："),
    ReplyComponent.image(base64_image),
    ReplyComponent.text("完成了！"),
])
```

---

### `inject_before()` / `inject_after()`

在当前位置前置/后置发送内容（语法糖，等价于 `send_components()`）。

```python
async def inject_before(self, *components: ReplyComponent) -> None
async def inject_after(self, *components: ReplyComponent) -> None
```

**示例：**
```python
await builder.inject_before(ReplyComponent.text("准备中…"))
# ... 其他操作 ...
await builder.inject_after(ReplyComponent.text("完成！"))
```

---

### `get_prompt_preview()`

获取当前生成会用到的提示词（调试用，不发送消息）。

```python
async def get_prompt_preview(
    self,
    extra_info: str = "",
) -> Optional[str]
```

**返回：** 提示词字符串，或 `None`

**示例：**
```python
prompt = await builder.get_prompt_preview()
print(prompt[:500])
```

---

## 完整使用示例

```python
from mai_advanced import AdvancedReplyBuilder, ReplyComponent

class WeatherAction(BaseAction):
    action_name = "weather_action"
    
    async def execute(self) -> Tuple[bool, str]:
        builder = AdvancedReplyBuilder(self)
        
        # 1. 获取天气数据
        weather = "北京：晴，25°C，东南风3级"
        
        # 2. 先发送一个"查询中"的提示
        await builder.inject_before(
            ReplyComponent.text("🌤️ 正在查询天气...", typing=True)
        )
        
        # 3. 用麦麦的语气重写天气信息并发送
        ok, components = await builder.rewrite_reply(
            raw_reply=weather,
            reason="将天气信息用麦麦的语气表达出来"
        )
        if ok:
            await builder.send_components(components)
        
        # 4. 在最后追加一条引导
        await builder.inject_after(
            ReplyComponent.text("想了解其他城市？告诉我吧！")
        )
        
        return True, "天气查询完成"
```

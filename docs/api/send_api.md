# 📤 发送 API

`send_api` 模块负责向聊天流发送各种类型的消息。

## 导入方式

```python
from src.plugin_system import send_api
```

在 Action/Command 组件内部，可以直接使用 `self.send_text()` 等便捷方法。

---

## 函数参考

### `text_to_stream()`

向指定聊天流发送文本消息。

```python
async def text_to_stream(
    text: str,
    stream_id: str,
    typing: bool = False,
    set_reply: bool = False,
    reply_message: Optional[DatabaseMessages] = None,
    storage_message: bool = True,
) -> bool
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `text` | `str` | 必填 | 要发送的文本内容 |
| `stream_id` | `str` | 必填 | 聊天流 ID（在组件中用 `self.stream_id`） |
| `typing` | `bool` | `False` | 是否模拟打字延迟 |
| `set_reply` | `bool` | `False` | 是否引用回复某条消息 |
| `reply_message` | `DatabaseMessages \| None` | `None` | 要引用的消息对象 |
| `storage_message` | `bool` | `True` | 是否将消息存入数据库 |

**返回值：** `bool` —— 发送是否成功

**示例：**

```python
# 在 Action/Command 中
async def execute(self):
    await self.send_text("你好！")  # 简写方式

# 或者直接调用 API
await send_api.text_to_stream("你好！", self.stream_id)

# 带打字效果
await send_api.text_to_stream("正在思考...", self.stream_id, typing=True)
```

---

### `image_to_stream()`

向指定聊天流发送图片。

```python
async def image_to_stream(
    image_base64: str,
    stream_id: str,
    storage_message: bool = True,
    set_reply: bool = False,
    reply_message: Optional[DatabaseMessages] = None,
) -> bool
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `image_base64` | `str` | 图片的 base64 编码字符串 |
| `stream_id` | `str` | 聊天流 ID |

**示例：**

```python
import base64

# 从文件读取图片
with open("image.png", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode("utf-8")

await self.send_image(img_base64)  # 简写方式
# 或
await send_api.image_to_stream(img_base64, self.stream_id)
```

---

### `emoji_to_stream()`

向指定聊天流发送表情包。

```python
async def emoji_to_stream(
    emoji_base64: str,
    stream_id: str,
    storage_message: bool = True,
) -> bool
```

**示例：**

```python
# 使用 emoji_api 选择随机表情包
from src.plugin_system import emoji_api

emoji_base64 = await emoji_api.get_random_emoji()
if emoji_base64:
    await self.send_emoji(emoji_base64)
```

---

### `custom_to_stream()`

发送自定义类型消息（支持任意消息类型）。

```python
async def custom_to_stream(
    message_type: str,
    content: str | Dict,
    stream_id: str,
    display_message: str = "",
    typing: bool = False,
    storage_message: bool = True,
) -> bool
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `message_type` | `str` | 消息类型（`"text"`, `"image"`, `"voice"`, `"video"` 等） |
| `content` | `str \| Dict` | 消息内容 |

**示例：**

```python
# 发送语音消息（base64）
await send_api.custom_to_stream("voice", voice_base64, self.stream_id)

# 发送视频消息
await send_api.custom_to_stream("video", video_base64, self.stream_id)
```

---

### `custom_reply_set_to_stream()`

发送由 `ReplySetModel` 构成的混合消息集（通常由生成器 API 返回）。

```python
async def custom_reply_set_to_stream(
    reply_set: ReplySetModel,
    stream_id: str,
    typing: bool = False,
    storage_message: bool = True,
) -> bool
```

**示例：**

```python
from src.plugin_system import generator_api, send_api

# 使用麦麦风格生成器生成回复
success, llm_data = await generator_api.generate_reply(
    chat_id=self.stream_id,
    extra_info="请用开心的语气回复",
)
if success and llm_data and llm_data.reply_set:
    await send_api.custom_reply_set_to_stream(
        llm_data.reply_set, self.stream_id
    )
```

---

## 组件内便捷方法

在 `BaseAction` 和 `BaseCommand` 中，以下方法是对 `send_api` 的封装：

| 便捷方法 | 等同于 |
|---------|--------|
| `await self.send_text(text)` | `send_api.text_to_stream(text, self.stream_id)` |
| `await self.send_image(base64)` | `send_api.image_to_stream(base64, self.stream_id)` |
| `await self.send_emoji(base64)` | `send_api.emoji_to_stream(base64, self.stream_id)` |

## 常见问题

::: tip 如何发送多条消息？
直接多次调用 `send_text` 即可，消息会依次发送：
```python
await self.send_text("第一条消息")
await self.send_text("第二条消息")
```
:::

::: warning 图片格式
发送图片时必须是 base64 编码的字符串，不要包含 `data:image/png;base64,` 前缀。
:::

# 📤 发送 API

> **来源**：`src.plugin_system.apis.send_api`

发送 API 负责向聊天流发送各种类型的消息。

## 导入方式

```python
# 在插件组件外部使用（独立调用）
from src.plugin_system import send_api
# 或
from src.plugin_system.apis import send_api
```

在 `BaseAction` / `BaseCommand` 组件内部，直接调用 `self.send_*()` 系列方法即可，无需导入。

---

## 组件内置发送方法（推荐）

### BaseAction 可用方法

```python
# 发送文本（typing=True 会显示"正在输入"）
await self.send_text(content: str, reply_to: str = "", reply_to_platform_id: str = "", typing: bool = False) -> bool

# 发送表情包（base64 无头格式）
await self.send_emoji(emoji_base64: str) -> bool

# 发送图片（base64 无头格式）
await self.send_image(image_base64: str) -> bool

# 发送自定义消息类型
await self.send_custom(message_type: str, content: str, typing: bool = False, reply_to: str = "") -> bool

# 发送命令消息（用于控制 Adapter）
await self.send_command(command_name: str, args: dict = None, display_message: str = "", storage_message: bool = True) -> bool
```

### BaseCommand 可用方法

```python
# 发送文本
await self.send_text(content: str, reply_to: str = "") -> bool

# 发送表情包
await self.send_emoji(emoji_base64: str) -> bool

# 发送图片
await self.send_image(image_base64: str) -> bool

# 发送指定类型消息
await self.send_type(message_type: str, content: str, display_message: str = "", typing: bool = False, reply_to: str = "") -> bool

# 发送命令消息
await self.send_command(command_name: str, args: dict = None, display_message: str = "", storage_message: bool = True) -> bool

# 合并转发（发送多条消息合并为一个）
await self.send_forward(messages: list) -> bool
```

#### `send_forward` 消息格式

```python
from src.plugin_system import ReplyContentType

# 每条消息格式：(QQ号字符串, 昵称字符串, [(ReplyContentType.类型, 内容)])
await self.send_forward([
    ("10001", "用户A", [(ReplyContentType.TEXT, "消息1")]),
    ("10002", "用户B", [(ReplyContentType.IMAGE, image_base64)]),
])
```

---

## 直接调用 send_api（不在组件内）

```python
from src.plugin_system import send_api

# 发送文本到指定聊天流
await send_api.text_to_stream(
    text="Hello!",
    stream_id=chat_stream.stream_id,
    typing=False,
    reply_to="",          # 格式："发送者:消息内容"
    storage_message=True,
) -> bool

# 发送表情包
await send_api.emoji_to_stream(
    emoji_base64="...",
    stream_id=chat_stream.stream_id,
    storage_message=True,
) -> bool

# 发送图片
await send_api.image_to_stream(
    image_base64="...",
    stream_id=chat_stream.stream_id,
    storage_message=True,
) -> bool

# 发送自定义类型消息
await send_api.custom_to_stream(
    message_type="text",  # "text"/"emoji"/"image"/"voice"/"command"/"music" 等
    content="内容",
    stream_id=chat_stream.stream_id,
    display_message="",
    typing=False,
    reply_to="",
    storage_message=True,
    show_log=True,
) -> bool
```

---

## 支持的消息类型

| 类型 | 说明 | 内容格式 |
|------|------|---------|
| `text` | 文本消息 | 字符串 |
| `emoji` | 表情包 | base64 无头字符串 |
| `image` | 图片 | base64 无头字符串 |
| `reply` | 回复特定消息 | 消息 ID |
| `voice` | 语音（wav） | base64 无头字符串 |
| `voiceurl` | 语音 URL | URL 字符串 |
| `music` | 网易云音乐 | 音乐 ID |
| `videourl` | 视频 URL | URL 字符串 |
| `file` | 文件 | 文件路径 |
| `command` | 命令（控制 Adapter） | 命令字典 |

> ⚠️ 不同 Adapter 支持的消息类型可能不同。以 MaiBot-NapCat-Adapter 为准。

---

## 实战示例

### 发送带表情的文字

```python
async def execute(self) -> Tuple[bool, str]:
    from src.plugin_system import emoji_api

    # 随机获取一个表情包
    result = await emoji_api.get_random()
    if result:
        emoji_b64, desc, emotion = result[0]
        await self.send_emoji(emoji_b64)

    await self.send_text("今天天气不错！😊")
    return True, "发送成功"
```

### 回复指定消息

```python
async def execute(self) -> Tuple[bool, Optional[str], bool]:
    # reply_to 格式："发送者名字:消息内容"
    await self.send_text("收到！", reply_to="用户:你好")
    return True, "回复成功", True
```

### 合并转发多张图片

```python
from src.plugin_system import ReplyContentType, emoji_api

async def execute(self) -> Tuple[bool, Optional[str], bool]:
    emojis = await emoji_api.get_random(5)
    images = [(ReplyContentType.IMAGE, e[0]) for e in emojis]
    success = await self.send_forward([
        ("0", "神秘用户", images)
    ])
    return (True, "已发送", True) if success else (False, "失败", False)
```

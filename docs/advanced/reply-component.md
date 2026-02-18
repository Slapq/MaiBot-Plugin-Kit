# ReplyComponent API 参考

`ReplyComponent` 是一个轻量的数据类，代表单个可发送的消息单元。

## 导入

```python
from mai_advanced import ReplyComponent
```

---

## 快捷工厂方法

### `ReplyComponent.text()`

```python
@classmethod
def text(cls, content: str, typing: bool = False, reply_to: str = "") -> ReplyComponent
```

| 参数 | 说明 |
|------|------|
| `content` | 文本内容 |
| `typing` | 是否显示"正在输入"动画 |
| `reply_to` | 回复目标，格式 `"发送者:消息"` |

**示例：**
```python
# 普通文本
ReplyComponent.text("你好！")

# 带正在输入动画
ReplyComponent.text("思考中...", typing=True)

# 回复指定消息
ReplyComponent.text("好的！", reply_to="用户:帮我查天气")
```

---

### `ReplyComponent.emoji()`

```python
@classmethod
def emoji(cls, base64_data: str) -> ReplyComponent
```

**示例：**
```python
from src.plugin_system.apis import emoji_api

result = await emoji_api.get_by_emotion("happy")
if result:
    emoji_b64, desc, emotion = result
    comp = ReplyComponent.emoji(emoji_b64)
```

---

### `ReplyComponent.image()`

```python
@classmethod
def image(cls, base64_data: str) -> ReplyComponent
```

**示例：**
```python
import base64

with open("chart.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()
comp = ReplyComponent.image(b64)
```

---

### `ReplyComponent.from_tuple()`

从 `reply_set` 元组创建组件（用于处理 `generator_api` 返回值）。

```python
@classmethod
def from_tuple(cls, t: Tuple[str, Any]) -> ReplyComponent
```

**示例：**
```python
success, reply_set, _ = await generator_api.generate_reply(...)
components = [ReplyComponent.from_tuple(t) for t in reply_set]
```

---

### 自定义类型

直接实例化可创建任意消息类型：

```python
# 发送视频（如果平台支持）
comp = ReplyComponent("video", base64_video_data)

# 发送文件
comp = ReplyComponent("file", base64_file_data, display_message="点击下载")

# 自定义命令
comp = ReplyComponent("command", "some_command_data")
```

---

## 与 send_api 的对应关系

| ReplyComponent 类型 | 底层调用 |
|---------------------|----------|
| `"text"` | `send_api.text_to_stream()` |
| `"emoji"` | `send_api.emoji_to_stream()` |
| `"image"` | `send_api.image_to_stream()` |
| 其他 | `send_api.custom_to_stream()` |

---

## 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `type` | `str` | 消息类型 |
| `content` | `str` | 消息内容 |
| `extra` | `dict` | 附加参数（如 `typing`, `reply_to`, `display_message`） |

---

## 发送组件列表

使用 `AdvancedReplyBuilder.send_components()` 发送一组组件：

```python
builder = AdvancedReplyBuilder(self)

await builder.send_components([
    ReplyComponent.text("分析结果："),
    ReplyComponent.image(chart_b64),
    ReplyComponent.text("数据来源：内部统计"),
])
```

或者直接用 `inject_before()` / `inject_after()`：

```python
await builder.inject_before(
    ReplyComponent.text("🔍 正在查询...", typing=True)
)
```

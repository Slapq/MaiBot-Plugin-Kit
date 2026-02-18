# 💬 消息 API

`message_api` 模块提供消息查询、格式化的能力，可以读取历史消息记录。

## 导入方式

```python
from src.plugin_system import message_api
```

---

## 消息查询函数

### `get_recent_messages()`

获取指定聊天中最近一段时间的消息（最常用）。

```python
def get_recent_messages(
    chat_id: str,
    hours: float = 24.0,
    limit: int = 100,
    limit_mode: str = "latest",
    filter_mai: bool = False,
) -> List[DatabaseMessages]
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `chat_id` | `str` | 聊天流 ID（用 `self.stream_id`） |
| `hours` | `float` | 最近多少小时（默认 24 小时） |
| `limit` | `int` | 最多返回多少条（0 = 不限制） |
| `filter_mai` | `bool` | 是否过滤掉麦麦自己发的消息 |

**示例：**

```python
# 获取最近 2 小时的消息
messages = message_api.get_recent_messages(
    chat_id=self.stream_id,
    hours=2.0,
    limit=50,
    filter_mai=True,  # 排除麦麦自己的消息
)

# 格式化为可读文本
text = message_api.build_readable_messages_to_str(messages)
print(text)
```

---

### `get_messages_by_time_in_chat()`

获取指定时间范围内的消息。

```python
def get_messages_by_time_in_chat(
    chat_id: str,
    start_time: float,
    end_time: float,
    limit: int = 0,
    limit_mode: str = "latest",
    filter_mai: bool = False,
    filter_command: bool = False,
) -> List[DatabaseMessages]
```

**示例：**

```python
import time

# 获取过去 1 小时的消息
now = time.time()
messages = message_api.get_messages_by_time_in_chat(
    chat_id=self.stream_id,
    start_time=now - 3600,
    end_time=now,
    limit=100,
    filter_command=True,  # 过滤命令消息
)
```

---

### `get_messages_before_time_in_chat()`

获取某时间点之前的消息。

```python
def get_messages_before_time_in_chat(
    chat_id: str,
    timestamp: float,
    limit: int = 0,
    filter_mai: bool = False,
) -> List[DatabaseMessages]
```

**示例：**

```python
# 获取最近 20 条消息
messages = message_api.get_messages_before_time_in_chat(
    chat_id=self.stream_id,
    timestamp=time.time(),
    limit=20,
)
```

---

## 消息格式化函数

### `build_readable_messages_to_str()`

将消息列表格式化为人类可读的文本字符串。

```python
def build_readable_messages_to_str(
    messages: List[DatabaseMessages],
    replace_bot_name: bool = True,
    timestamp_mode: str = "relative",
    read_mark: float = 0.0,
    truncate: bool = False,
    show_actions: bool = False,
) -> str
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `replace_bot_name` | `bool` | 将麦麦的名字替换为"你" |
| `timestamp_mode` | `str` | `"relative"`（相对时间）或 `"absolute"` |
| `read_mark` | `float` | 已读标记时间戳（用于显示未读分隔线） |
| `truncate` | `bool` | 是否截断长消息 |

**示例：**

```python
messages = message_api.get_recent_messages(self.stream_id, hours=1.0)
text = message_api.build_readable_messages_to_str(
    messages,
    timestamp_mode="relative",
    truncate=True,
)
# 输出示例：
# 5分钟前 张三：你好！
# 3分钟前 李四：在吗？
# 刚刚 麦麦：在的，有什么事？
```

---

## DatabaseMessages 字段说明

消息查询函数返回 `DatabaseMessages` 对象列表，包含以下字段：

```python
message.message_id          # 消息 ID
message.time                # 消息时间戳（float）
message.processed_plain_text  # 消息文本内容
message.user_info.user_id   # 发送者 ID
message.user_info.user_nickname  # 发送者昵称
message.user_info.platform  # 平台（如 "qq"）
message.chat_info.platform  # 聊天平台
message.chat_info.group_info.group_id  # 群组 ID（如有）
```

---

## 实用示例

### 统计群活跃度

```python
import time
from src.plugin_system import message_api

async def execute(self):
    # 获取今天的消息
    now = time.time()
    messages = message_api.get_messages_by_time_in_chat(
        chat_id=self.stream_id,
        start_time=now - 86400,  # 24小时前
        end_time=now,
    )
    
    # 统计发言人数
    unique_senders = set(
        msg.user_info.user_id for msg in messages
    )
    
    await self.send_text(
        f"📊 今日统计：\n"
        f"消息总数：{len(messages)} 条\n"
        f"参与人数：{len(unique_senders)} 人"
    )
    return True, "统计完成"
```

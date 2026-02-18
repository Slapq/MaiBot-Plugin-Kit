# 💬 聊天流 API

> **来源**：`src.plugin_system.apis.chat_api`

查询和管理当前活跃的聊天流（群聊/私聊）。

## 导入方式

```python
from src.plugin_system import chat_api
from src.plugin_system.apis import chat_api
```

---

## 获取聊天流

```python
# 获取所有聊天流（默认 QQ 平台）
streams = chat_api.get_all_streams(platform="qq")

# 获取所有群聊流
group_streams = chat_api.get_group_streams(platform="qq")

# 获取所有私聊流
private_streams = chat_api.get_private_streams(platform="qq")

# 跨平台查询（使用 SpecialTypes）
from src.plugin_system.apis.chat_api import SpecialTypes
all_streams = chat_api.get_all_streams(platform=SpecialTypes.ALL_PLATFORMS)
```

---

## 查找特定聊天流

```python
# 根据群 ID 查找
stream = chat_api.get_stream_by_group_id(
    group_id="123456789",
    platform="qq"
)

# 根据用户 ID 查找私聊流
stream = chat_api.get_stream_by_user_id(
    user_id="987654321",
    platform="qq"
)
# 未找到时返回 None
```

---

## 聊天流信息

```python
# 判断群聊/私聊/未知
stream_type = chat_api.get_stream_type(stream)
# 返回："group" / "private" / "unknown"

# 获取详细信息
info = chat_api.get_stream_info(stream)
# info["stream_id"]   聊天流 ID
# info["platform"]    平台
# info["type"]        类型
# info["group_id"]    群号（群聊）
# info["group_name"]  群名（群聊）
# info["user_id"]     用户 ID（私聊）
# info["user_name"]   用户名（私聊）

# 统计摘要
summary = chat_api.get_streams_summary()
# summary["total_streams"]
# summary["group_streams"]
# summary["private_streams"]
# summary["qq_streams"]
```

---

## 实战示例：定时广播

```python
import asyncio
from src.plugin_system import chat_api, send_api

async def broadcast_to_all_groups(message: str):
    """向所有群发送消息（谨慎使用！）"""
    group_streams = chat_api.get_group_streams(platform="qq")
    for stream in group_streams:
        await send_api.text_to_stream(
            text=message,
            stream_id=stream.stream_id,
            storage_message=True,
        )
        await asyncio.sleep(1)  # 避免发送过快
```

### 在 EventHandler 中获取聊天流信息

```python
class MyHandler(BaseEventHandler):
    event_type = EventType.ON_MESSAGE
    handler_name = "my_handler"
    handler_description = "处理消息事件"

    async def execute(self, message):
        if not message:
            return True, True, None, None, None
        
        # 从消息获取聊天流
        stream = message.chat_stream
        stream_type = chat_api.get_stream_type(stream)
        
        if stream_type == "group":
            info = chat_api.get_stream_info(stream)
            group_name = info.get("group_name", "未知群")
            # 处理群消息...
        
        return True, True, None, None, None
```

---

## 注意事项

- `get_stream_by_group_id` 未找到时返回 `None`，使用前检查
- 在 `BaseAction` / `BaseCommand` 组件内，直接用 `self.chat_stream` 即可
- 大部分函数参数不合法时会抛出异常，需要 try/except 处理

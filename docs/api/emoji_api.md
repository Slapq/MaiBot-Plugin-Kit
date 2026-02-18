# 😊 表情包 API

> **来源**：`src.plugin_system.apis.emoji_api`

操作麦麦的表情包库（获取、注册、删除）。

## 导入方式

```python
from src.plugin_system import emoji_api
# 或
from src.plugin_system.apis import emoji_api
```

---

## 获取表情包

### 按描述获取

```python
result = await emoji_api.get_by_description("开心大笑")
# 返回：Optional[Tuple[str, str, str]]
#       (base64无头字符串, 描述, 情感标签) 或 None
if result:
    emoji_b64, description, emotion = result
    await self.send_emoji(emoji_b64)
```

### 按情感标签获取

```python
result = await emoji_api.get_by_emotion("开心")
# 返回：Optional[Tuple[str, str, str]] 或 None
```

### 随机获取（支持批量）

```python
results = await emoji_api.get_random(count=3)
# 返回：List[Tuple[str, str, str]]
for emoji_b64, desc, emotion in results:
    print(f"{desc} [{emotion}]")
```

### 获取全部

```python
all_emojis = await emoji_api.get_all()
# 返回：List[Tuple[str, str, str]]
```

---

## 统计信息

```python
count = emoji_api.get_count()           # 总数量：int
info = emoji_api.get_info()             # 详细信息：dict
#   info["current_count"]   当前数量
#   info["max_count"]       最大容量
#   info["available_emojis"] 可用数量

emotions = emoji_api.get_emotions()      # 所有情感标签（去重）：List[str]
descriptions = emoji_api.get_descriptions()  # 所有描述：List[str]
```

---

## 管理表情包

### 注册新表情包

```python
result = await emoji_api.register_emoji(emoji_base64)
# 返回：dict
# {
#   "success": bool,
#   "description": "表情包描述",
#   "emotions": ["开心", "大笑"],
#   "replaced": bool,    # True 表示替换了旧的
#   "message": "错误信息（失败时）"
# }
```

### 删除表情包

```python
import base64, hashlib

# 计算 MD5 哈希
image_bytes = base64.b64decode(emoji_base64)
emoji_hash = hashlib.md5(image_bytes).hexdigest()

result = await emoji_api.delete_emoji(emoji_hash)
# 返回：dict
# {
#   "success": bool,
#   "description": "被删除的描述",
#   "count_before": 10,
#   "count_after": 9,
#   "message": "错误信息（失败时）"
# }
```

---

## 实战示例

### 随机发送5张表情包（合并转发）

```python
from src.plugin_system import ReplyContentType, emoji_api

class RandomEmojiCommand(BaseCommand):
    command_name = "random_emoji"
    command_description = "发送随机表情包"
    command_pattern = r"^/random_emoji$"

    async def execute(self):
        emojis = await emoji_api.get_random(5)
        if not emojis:
            await self.send_text("暂无表情包 😅")
            return False, "无表情包", True

        success = await self.send_forward([
            ("0", "神秘用户",
             [(ReplyContentType.IMAGE, e[0]) for e in emojis])
        ])
        return (True, "发送成功", True) if success else (False, "发送失败", True)
```

### Action：在合适时机发表情

```python
class EmojiAction(BaseAction):
    action_name = "send_emoji"
    action_description = "在合适的时候发送一个表情包"
    activation_type = ActionActivationType.RANDOM
    random_activation_probability = 0.15
    action_require = ["表达情绪时", "增加趣味性", "不要连续发送"]
    associated_types = ["emoji"]
    action_parameters = {"emotion": "表情的情感，如：开心/难过/愤怒"}

    async def execute(self) -> Tuple[bool, str]:
        emotion = self.action_data.get("emotion", "开心")
        result = await emoji_api.get_by_emotion(emotion)
        if result:
            await self.send_emoji(result[0])
            return True, f"发送了 {emotion} 表情"
        return False, "未找到表情包"
```

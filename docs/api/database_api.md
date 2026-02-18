# 🗄️ 数据库 API

> **来源**：`src.plugin_system.apis.database_api`

通用数据库操作接口，基于 Peewee ORM。

## 导入方式

```python
from src.plugin_system import database_api
from src.plugin_system.apis import database_api
```

数据库模型类在：
```python
from src.common.database.database_model import Messages, ActionRecords
```

---

## 主要功能

### 1. 通用查询 `db_query`

```python
result = await database_api.db_query(
    model_class=Messages,           # Peewee 模型类
    data=None,                      # 创建/更新时的数据字典
    query_type="get",               # "get" / "create" / "update" / "delete" / "count"
    filters={"chat_id": "xxx"},     # 过滤条件
    limit=10,                       # 最多返回条数
    order_by=["-time"],             # 排序字段，"-" 前缀表示降序
    single_result=False,            # True 时返回单个 dict 而非列表
)
```

**返回值（按 query_type）：**
- `"get"` → `List[dict]` 或 `dict`（single_result=True 时）
- `"create"` → `dict`（创建的记录）
- `"update"` / `"delete"` → `int`（受影响行数）
- `"count"` → `int`

### 2. 保存（创建或更新）`db_save`

```python
record = await database_api.db_save(
    model_class=ActionRecords,
    data={
        "action_id": "my_action_123",
        "time": time.time(),
        "action_name": "MyAction",
        "action_done": True,
    },
    key_field="action_id",         # 用于查找现有记录的字段
    key_value="my_action_123",     # 对应的值（存在则更新，不存在则创建）
)
# 返回：dict 或 None（失败时）
```

### 3. 简化查询 `db_get`

```python
# 查单条
record = await database_api.db_get(
    model_class=ActionRecords,
    filters={"action_id": "my_action_123"},
    single_result=True,
)

# 查多条（最近10条）
records = await database_api.db_get(
    model_class=Messages,
    filters={"chat_id": self.chat_id},
    limit=10,
    order_by="-time",
)
```

### 4. 存储 Action 信息（专用）

```python
# 在 Action.execute() 中直接调用（推荐用 self.store_action_info）
await database_api.store_action_info(
    chat_stream=self.chat_stream,
    action_build_into_prompt=True,      # 是否加入麦麦的提示词上下文
    action_prompt_display="发送了问候",  # 在提示词中显示的文本
    action_done=True,
    thinking_id=self.thinking_id,
    action_data=self.action_data,
    action_name=self.action_name,
)
```

---

## 实战示例：积分系统

```python
import time
from src.plugin_system import database_api
from src.common.database.database_model import ActionRecords


class AddScoreCommand(BaseCommand):
    command_name = "score"
    command_description = "查看积分"
    command_pattern = r"^/score$"

    async def execute(self):
        user_id = str(self.message.sender_id if hasattr(self.message, 'sender_id') else "unknown")
        
        # 查询积分（用 ActionRecords 或自定义模型）
        # 注意：最好用自定义数据库或文件存储用户数据
        # 这里只演示 db_get 用法
        records = await database_api.db_get(
            ActionRecords,
            filters={"action_name": f"score_{user_id}"},
            limit=1,
            order_by="-time",
        )

        score = len(records) if records else 0
        await self.send_text(f"你的积分：{score}")
        return True, "查询积分", True
```

---

## 注意事项

- 所有函数均为异步，必须 `await`
- `model_class` 必须是 Peewee 模型类，来自 `src.common.database.database_model`
- 插件建议使用 `action_name` 字段加前缀区分自己的数据
- 直接操作 `Messages` 表时要注意不要破坏麦麦的消息历史

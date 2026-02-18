# 👤 个人信息 API

> **来源**：`src.plugin_system.apis.person_api`

获取麦麦认识的用户信息（昵称、印象、历史等）。

## 导入方式

```python
from src.plugin_system import person_api
# 或
from src.plugin_system.apis import person_api
```

---

## 主要功能

### 1. 获取 person_id

`person_id` 是平台无关的用户唯一标识（MD5 哈希）：

```python
person_id = person_api.get_person_id(
    platform="qq",
    user_id=123456,     # int 类型
)
# 返回：str（MD5 哈希字符串）
```

在 Action 中，`self.user_id` 是字符串形式的 QQ 号，需先转换：

```python
person_id = person_api.get_person_id("qq", int(self.user_id))
```

### 2. 查询单个字段

```python
nickname = await person_api.get_person_value(
    person_id=person_id,
    field_name="nickname",
    default="未知用户",   # 不存在时的默认值
)
```

### 3. 批量查询多个字段

```python
values = await person_api.get_person_values(
    person_id=person_id,
    field_names=["nickname", "impression", "know_times"],
    default_dict={
        "nickname": "未知用户",
        "know_times": 0,
    },
)
# 返回：dict，key 为字段名，value 为字段值
nickname = values["nickname"]
impression = values.get("impression", "")
```

### 4. 判断用户是否已知

```python
known = await person_api.is_person_known(
    platform="qq",
    user_id=123456,
)
# 返回：bool
```

### 5. 通过用户名查 person_id

```python
person_id = person_api.get_person_id_by_name("用户昵称")
# 返回：str，未找到时返回空字符串
```

---

## 常用字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `nickname` | `str` | 用户昵称 |
| `impression` | `str` | 麦麦对此人的印象描述 |
| `points` | `list` | 用户特征点列表 |
| `know_times` | `int` | 见过几次 |
| `platform` | `str` | 平台标识 |
| `user_id` | `str` | 平台内用户 ID |

更多字段参见 `src.common.database.database_model.PersonInfo`。

---

## 实战示例

```python
class GreetAction(BaseAction):
    action_name = "personalized_greet"
    action_description = "用个性化的方式问候用户"
    activation_type = ActionActivationType.KEYWORD
    activation_keywords = ["你好", "hi", "hello"]
    action_require = ["当有人打招呼时", "用个性化方式回应"]
    associated_types = ["text"]
    action_parameters = {}

    async def execute(self) -> Tuple[bool, str]:
        from src.plugin_system import person_api

        # 获取用户 person_id
        person_id = person_api.get_person_id("qq", int(self.user_id))

        # 查询昵称和印象
        values = await person_api.get_person_values(
            person_id,
            ["nickname", "impression"],
            {"nickname": self.user_nickname},
        )
        nickname = values["nickname"]
        impression = values.get("impression", "")

        if impression:
            await self.send_text(f"嗨，{nickname}！{impression[:20]}")
        else:
            await self.send_text(f"你好，{nickname}！第一次见面呢 😊")

        return True, f"问候了 {nickname}"
```

---

## 注意事项

- `person_id` 与平台无关，同一用户在不同平台有不同 `person_id`
- 部分查询是异步的，必须 `await`
- 批量查询（`get_person_values`）性能优于单个查询

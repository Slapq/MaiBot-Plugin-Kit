# 🧩 组件管理 API

> **来源**：`src.plugin_system.apis.component_manage_api`

查询、启用、禁用插件组件（Action / Command / Tool / EventHandler）。

## 导入方式

```python
from src.plugin_system import component_manage_api
from src.plugin_system.apis import component_manage_api
```

---

## 查询组件

### 获取所有插件信息

```python
plugins = component_manage_api.get_all_plugin_info()
# 返回：Dict[str, PluginInfo]，key 为插件名
```

### 获取指定插件信息

```python
plugin = component_manage_api.get_plugin_info("hello_world_plugin")
# 返回：PluginInfo 或 None
```

### 按名称查询组件

```python
from src.plugin_system.base.component_types import ComponentType

action = component_manage_api.get_component_info(
    component_name="hello_greeting",
    component_type=ComponentType.ACTION,
)
# 返回：ActionInfo / CommandInfo / EventHandlerInfo 或 None
```

### 按类型获取所有组件

```python
# 获取所有 Action
actions = component_manage_api.get_components_info_by_type(ComponentType.ACTION)
# 返回：Dict[str, ActionInfo]

# 获取所有启用的 Command
enabled_commands = component_manage_api.get_enabled_components_info_by_type(ComponentType.COMMAND)
```

**ComponentType 枚举值**：
- `ComponentType.ACTION`
- `ComponentType.COMMAND`
- `ComponentType.TOOL`
- `ComponentType.EVENT_HANDLER`

### 按名称查询特定类型

```python
action_info = component_manage_api.get_registered_action_info("hello_greeting")
command_info = component_manage_api.get_registered_command_info("time")
tool_info = component_manage_api.get_registered_tool_info("compare_numbers")
handler_info = component_manage_api.get_registered_event_handler_info("print_message_handler")
```

---

## 启用/禁用组件

### 全局启用

```python
success = component_manage_api.globally_enable_component(
    component_name="my_action",
    component_type=ComponentType.ACTION,
)
# 返回：bool
```

### 全局禁用（异步）

```python
success = await component_manage_api.globally_disable_component(
    component_name="my_action",
    component_type=ComponentType.ACTION,
)
# 返回：bool
```

### 局部启用（仅对指定聊天流生效）

```python
success = component_manage_api.locally_enable_component(
    component_name="my_action",
    component_type=ComponentType.ACTION,
    stream_id=self.chat_id,
)
```

### 局部禁用（仅对指定聊天流生效）

```python
success = component_manage_api.locally_disable_component(
    component_name="my_action",
    component_type=ComponentType.ACTION,
    stream_id=self.chat_id,
)
```

### 查询某聊天流中禁用的组件

```python
disabled = component_manage_api.get_locally_disabled_components(
    stream_id=self.chat_id,
    component_type=ComponentType.COMMAND,
)
# 返回：List[str]（组件名列表）
```

---

## 实战示例：开关命令

```python
class ToggleActionCommand(BaseCommand):
    command_name = "toggle_action"
    command_description = "在当前群启用/禁用某个 Action"
    command_pattern = r"^/toggle\s+(?P<name>\S+)\s+(?P<state>on|off)$"

    async def execute(self):
        from src.plugin_system import component_manage_api
        from src.plugin_system.base.component_types import ComponentType

        name = self.matched_groups.get("name", "")
        state = self.matched_groups.get("state", "on")
        stream_id = self.message.stream_id

        if state == "off":
            success = component_manage_api.locally_disable_component(
                name, ComponentType.ACTION, stream_id
            )
            msg = f"已在本群禁用 {name}" if success else f"禁用失败，{name} 不存在"
        else:
            success = component_manage_api.locally_enable_component(
                name, ComponentType.ACTION, stream_id
            )
            msg = f"已在本群启用 {name}" if success else f"启用失败，{name} 不存在"

        await self.send_text(msg)
        return True, msg, True
```

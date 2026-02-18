# 🔌 插件管理 API

> **来源**：`src.plugin_system.apis.plugin_manage_api`

动态加载、卸载、重载插件，以及管理插件目录。

## 导入方式

```python
from src.plugin_system import plugin_manage_api
from src.plugin_system.apis import plugin_manage_api
```

---

## 查询插件

```python
# 列出所有已加载的插件
loaded = plugin_manage_api.list_loaded_plugins()
# 返回：List[str]（插件名列表）

# 列出所有已注册的插件（包括未启用的）
registered = plugin_manage_api.list_registered_plugins()
# 返回：List[str]

# 获取插件文件路径
path = plugin_manage_api.get_plugin_path("hello_world_plugin")
# 返回：str（路径字符串），插件不存在时 raise ValueError
```

---

## 加载/卸载/重载插件

### 加载插件

```python
success, count = plugin_manage_api.load_plugin("my_new_plugin")
# 返回：Tuple[bool, int]
# success: 是否成功
# count: 成功加载的组件数
```

### 卸载插件（异步）

```python
success = await plugin_manage_api.remove_plugin("my_plugin")
# 返回：bool
```

### 重载插件（异步，修改代码后热更新）

```python
success = await plugin_manage_api.reload_plugin("my_plugin")
# 返回：bool
```

---

## 插件目录管理

```python
# 添加新的插件目录
success = plugin_manage_api.add_plugin_directory("/path/to/extra_plugins")
# 返回：bool

# 重新扫描所有插件目录（加载新发现的插件）
loaded_count, failed_count = plugin_manage_api.rescan_plugin_directory()
# 返回：Tuple[int, int]
```

---

## 实战示例：热重载命令

```python
class ReloadCommand(BaseCommand):
    command_name = "reload"
    command_description = "热重载指定插件"
    command_pattern = r"^/reload\s+(?P<name>\S+)$"

    async def execute(self):
        from src.plugin_system import plugin_manage_api

        plugin_name = self.matched_groups.get("name", "")
        if not plugin_name:
            await self.send_text("用法：/reload <插件名>")
            return True, "无插件名", True

        # 检查插件是否存在
        loaded = plugin_manage_api.list_loaded_plugins()
        if plugin_name not in loaded:
            await self.send_text(f"插件 {plugin_name} 未加载")
            return True, "插件不存在", True

        await self.send_text(f"正在重载 {plugin_name}...")
        success = await plugin_manage_api.reload_plugin(plugin_name)

        msg = f"✅ {plugin_name} 重载成功" if success else f"❌ {plugin_name} 重载失败"
        await self.send_text(msg)
        return True, msg, True
```

---

## 注意事项

- 卸载/重载是异步操作，必须 `await`
- 重载会重新执行插件的 `__init__` 和组件注册
- 谨慎调用 `remove_plugin`，卸载后所有组件立即失效

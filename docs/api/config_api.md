# ⚙️ 配置 API

> **来源**：`src.plugin_system.apis.config_api` 和 `src.plugin_system.ConfigField`

## 一、插件配置（推荐方式）

### 定义配置 Schema

在 `BasePlugin` 子类中定义 `config_schema`，MaiBot 会自动生成 `config.toml`：

```python
from src.plugin_system import ConfigField

class MyPlugin(BasePlugin):
    config_file_name = "config.toml"

    # 可选：为每个 section 添加注释
    config_section_descriptions = {
        "plugin": "插件基本配置",
        "feature": "功能配置",
    }

    config_schema = {
        "plugin": {
            "enabled": ConfigField(type=bool, default=True, description="是否启用"),
            "config_version": ConfigField(type=str, default="1.0.0", description="配置版本"),
        },
        "feature": {
            "timeout": ConfigField(type=int, default=30, description="超时秒数"),
            "messages": ConfigField(type=list, default=["默认消息1", "默认消息2"], description="回复消息列表"),
            "prefix": ConfigField(type=str, default="[前缀]", description="消息前缀"),
        },
    }
```

**不要手动创建 config.toml！** MaiBot 会在首次运行时自动生成。

### 在组件中读取配置

`BaseAction` 和 `BaseCommand` 均提供 `self.get_config(key, default)`：

```python
class MyAction(BaseAction):
    async def execute(self):
        # 使用 "section.key" 格式
        enabled = self.get_config("plugin.enabled", True)
        timeout = self.get_config("feature.timeout", 30)
        messages = self.get_config("feature.messages", ["默认"])
        prefix = self.get_config("feature.prefix", "")
```

---

## 二、读取全局配置

```python
from src.plugin_system import config_api

# 读取 MaiBot 全局配置（只读！）
bot_name = config_api.get_global_config("bot.nickname", "MaiBot")
```

```python
from src.plugin_system.apis import config_api

# 读取插件自身配置字典中的值
value = config_api.get_plugin_config(
    plugin_config=self.config,    # 插件配置字典
    key="feature.timeout",
    default=30,
)
```

---

## ConfigField 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `type` | `type` | 数据类型（`str`/`int`/`float`/`bool`/`list`/`dict`） |
| `default` | `Any` | 默认值 |
| `description` | `str` | 配置项说明（会写入 toml 注释） |

---

## 自动生成的 config.toml 示例

上面的 `config_schema` 会自动生成：

```toml
# my_plugin - 自动生成的配置文件

# 插件基本配置
[plugin]
# 是否启用
enabled = true
# 配置版本
config_version = "1.0.0"

# 功能配置
[feature]
# 超时秒数
timeout = 30
# 回复消息列表
messages = ["默认消息1", "默认消息2"]
# 消息前缀
prefix = "[前缀]"
```

---

## 注意事项

- `config_api.get_global_config()` 只读，插件不能修改全局配置
- 配置键名大小写敏感
- 频繁读取的配置建议在插件初始化时缓存

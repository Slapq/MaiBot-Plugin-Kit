# 📜 日志 API

> **来源**：`src.common.logger.get_logger`

麦麦使用 `structlog` 进行结构化日志记录。插件必须使用此系统，不要用 `print()`。

## 获取 Logger

```python
from src.common.logger import get_logger

# 在模块顶部定义，传入插件名作为标识
logger = get_logger("my_plugin_name")
```

## 日志级别

```python
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告")
logger.error("错误")
logger.critical("严重错误")
```

## 格式化日志（推荐）

```python
# 使用 f-string
logger.info(f"[my_plugin] 收到命令，用户={user_id}，内容={content}")

# 使用关键字参数（structlog 风格）
logger.info("收到命令", user_id=user_id, content=content)
```

## 捕获异常

```python
try:
    result = await some_operation()
except Exception as e:
    logger.error(f"[my_plugin] 操作失败: {e}")
    # 或者记录完整堆栈
    logger.exception(f"[my_plugin] 操作失败")
```

## 规范用法示例

```python
from src.common.logger import get_logger

logger = get_logger("my_plugin")

class MyCommand(BaseCommand):
    command_name = "mycommand"
    command_description = "示例命令"
    command_pattern = r"^/mycommand$"

    async def execute(self):
        logger.info(f"[my_plugin] Command 触发，stream={self.message.stream_id}")
        try:
            result = await do_something()
            logger.info(f"[my_plugin] 执行成功：{result}")
            await self.send_text(str(result))
            return True, "成功", True
        except Exception as e:
            logger.error(f"[my_plugin] 执行失败：{e}")
            await self.send_text("执行出错，请稍后重试")
            return False, str(e), True
```

## 日志命名规范

| 场景 | 推荐格式 |
|------|---------|
| 模块初始化 | `logger = get_logger("plugin_name")` |
| 日志前缀 | `logger.info(f"[plugin_name] 消息")` |
| 错误日志 | 包含用户/聊天 ID 以便排查 |

## 注意

- `get_logger` 返回 `structlog.stdlib.BoundLogger` 实例
- 日志输出到控制台（彩色）和 `logs/` 目录（按日期）
- Debug 级别日志生产环境可能不显示，取决于 MaiBot 配置

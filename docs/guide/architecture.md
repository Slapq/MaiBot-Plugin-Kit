# 🏗️ 插件架构

本文介绍 MaiBot 插件的整体结构设计，帮助你理解插件的工作原理。

## 插件目录结构

每个插件是一个独立目录，包含以下文件：

```
my_plugin/
├── _manifest.json    ← 插件元数据（必须）
├── plugin.py         ← 插件主文件（必须）
├── config.toml       ← 插件配置（可选）
├── requirements.txt  ← 依赖声明（可选）
└── README.md         ← 插件说明（推荐）
```

## 组件类型

MaiBot 插件支持三种核心组件类型：

### 1. Command 组件（命令）

响应用户输入的特定命令，例如 `/ping`、`/weather 北京`。

```python
class MyCommand(BaseCommand):
    command = Command(
        entry_commands={"mycommand"},
        command_generator="生成回复的提示词"
    )
    async def execute(self):
        await self.send_text("命令执行成功！")
        return True, "ok", True
```

**特点：**
- 由用户主动触发
- 支持正则参数捕获
- 可打断消息队列

### 2. Action 组件（行为）

让麦麦在合适的时机主动发出某些行为，例如检测到特定话题时主动分享内容。

```python
class MyAction(BaseAction):
    action = Action(
        action_name="my_action",
        action_description="当...时触发",
        action_parameters="...",
    )
    async def execute(self):
        await self.send_text("麦麦主动说话了！")
        return ActionResponse(
            action="my_action",
            reasoning="触发原因",
            action_data=""
        )
```

**特点：**
- 由 LLM 判断是否触发
- 适合上下文感知型行为
- 无需用户显式触发

### 3. Tool 组件（工具）

供 LLM 在生成回复过程中调用的工具函数。

```python
class MyTool(BaseTool):
    # 工具定义
    tool_name = "my_tool"
    tool_description = "工具功能描述"
```

## _manifest.json 说明

```json
{
  "manifest_version": 1,
  "name": "插件名称",
  "version": "1.0.0",
  "description": "插件描述",
  "author": "作者名",
  "dependencies": {
    "plugin_key": "组件类路径"
  }
}
```

| 字段 | 必须 | 说明 |
|------|------|------|
| `manifest_version` | ✅ | 固定为 `1` |
| `name` | ✅ | 插件显示名称 |
| `version` | ✅ | 语义化版本号 |
| `description` | ✅ | 插件简短描述 |
| `author` | ✅ | 作者名称 |
| `dependencies` | ✅ | 组件注册字典 |

## 插件加载流程

```
MaiBot 启动
    ↓
扫描 plugins/ 目录
    ↓
读取 _manifest.json
    ↓
动态导入 plugin.py
    ↓
注册 Command / Action / Tool 组件
    ↓
等待触发
```

## 下一步

- 📤 查看 [发送 API](/api/send_api)
- 🤖 了解 [LLM API](/api/llm_api)
- 📦 学习如何 [发布插件](/guide/publish)

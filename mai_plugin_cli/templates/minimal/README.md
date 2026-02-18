# {{PLUGIN_DISPLAY_NAME}}

{{PLUGIN_DESCRIPTION}}

## 作者

{{PLUGIN_AUTHOR}}

## 版本

{{PLUGIN_VERSION}}

## 安装

将本目录复制到 MaiBot 的 `plugins/` 目录下，重启 MaiBot 即可。

```
MaiBot/
└── plugins/
    └── {{PLUGIN_NAME}}/
        ├── _manifest.json
        ├── plugin.py
        └── README.md
```

## 开发指南

### 添加 Action（麦麦自主行为）

```python
from src.plugin_system import BaseAction, ActionActivationType

class MyAction(BaseAction):
    action_name = "my_action"
    action_description = "描述这个行为的作用"
    activation_type = ActionActivationType.ALWAYS
    action_parameters = {"param1": "参数说明"}
    action_require = ["需要这个行为时使用"]
    associated_types = ["text"]

    async def execute(self):
        await self.send_text("Hello from my action!")
        return True, "执行成功"
```

### 添加 Command（响应用户命令）

```python
from src.plugin_system import BaseCommand

class MyCommand(BaseCommand):
    command_name = "my_command"
    command_description = "命令描述"
    command_pattern = r"^/mycommand$"

    async def execute(self):
        await self.send_text("执行了命令！")
        return True, "成功", True
```

## 参考文档

- [完整 API 文档](https://maibot-plugin-kit.pages.dev/)
- [MaiBot 官方文档](https://docs.mai-mai.org/)
- [插件示例仓库](https://github.com/Mai-with-u/plugin-repo)

# 🤖 LLM API

> **来源**：`src.plugin_system.apis.llm_api`

LLM API 提供直接调用大语言模型的能力（不走麦麦的回复生成器，直接裸调）。

## 导入方式

```python
from src.plugin_system import llm_api
# 或
from src.plugin_system.apis import llm_api
```

---

## 主要功能

### 1. 查询可用模型

```python
models = llm_api.get_available_models()
# 返回：Dict[str, TaskConfig]
# key 为模型名称，value 为 TaskConfig 对象
```

### 2. 用模型生成内容

```python
success, content, reasoning, model_name = await llm_api.generate_with_model(
    prompt="你的提示词",
    model_config=models["model_name"],   # 从 get_available_models() 获取
    request_type="plugin.generate",      # 可选，用于日志记录
    temperature=0.8,                     # 可选，影响随机性（0~2）
    max_tokens=500,                      # 可选，最大生成 token 数
)
# 返回：Tuple[bool, str, str, str]
# → (是否成功, 生成内容, 推理过程, 实际使用的模型名)
```

### 3. 带 Tool 的生成

```python
from src.plugin_system import tool_api

tools = tool_api.get_llm_available_tool_definitions()

success, content, reasoning, model_name, tool_calls = await llm_api.generate_with_model_with_tools(
    prompt="你的提示词",
    model_config=models["model_name"],
    tool_options=tools,                  # 传入工具列表
    request_type="plugin.generate",
    temperature=0.8,
    max_tokens=500,
)
# 返回：Tuple[bool, str, str, str, List[ToolCall] | None]
```

---

## 完整示例

```python
from src.plugin_system import (
    BaseCommand, ComponentInfo, ConfigField,
    llm_api,
)
from src.common.logger import get_logger

logger = get_logger("my_llm_plugin")


class AskCommand(BaseCommand):
    command_name = "ask"
    command_description = "向 AI 提问"
    command_pattern = r"^/ask\s+(?P<question>.+)$"

    async def execute(self):
        question = self.matched_groups.get("question", "")
        if not question:
            await self.send_text("请输入问题，例如：/ask 什么是黑洞？")
            return True, "无问题", True

        # 获取可用模型
        models = llm_api.get_available_models()
        if not models:
            await self.send_text("暂无可用模型")
            return False, "无模型", True

        model_config = list(models.values())[0]  # 使用第一个模型

        # 调用 LLM
        success, content, reasoning, model_name = await llm_api.generate_with_model(
            prompt=f"请简洁回答：{question}",
            model_config=model_config,
            request_type="plugin.ask",
            temperature=0.7,
            max_tokens=300,
        )

        if success and content:
            await self.send_text(content)
            logger.info(f"[ask] 使用模型 {model_name} 回答了：{question}")
        else:
            await self.send_text("抱歉，生成回答失败了 😅")

        return True, f"回答了问题：{question}", True
```

---

## 注意事项

- 每次调用都会消耗 API Token，注意控制频率
- `request_type` 用于日志分析，建议填写有意义的字符串
- 模型列表由 MaiBot 配置文件决定，插件无法直接指定模型名称（需从 `get_available_models()` 获取）
- 与 `generator_api` 的区别：`llm_api` 是裸调 LLM，不考虑上下文；`generator_api` 是完整的回复生成流程，包含上下文、人设等

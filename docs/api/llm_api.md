# 🤖 LLM API

`llm_api` 模块提供与大语言模型（LLM）直接交互的能力。

## 导入方式

```python
from src.plugin_system import llm_api
```

---

## 函数参考

### `get_available_models()`

获取所有在 MaiBot 配置文件中定义的可用模型配置。

```python
def get_available_models() -> Dict[str, TaskConfig]
```

**返回值：** 模型名称到 `TaskConfig` 的字典

**示例：**

```python
models = llm_api.get_available_models()
for name, config in models.items():
    print(f"模型: {name}")

# 获取特定模型配置
models = llm_api.get_available_models()
my_model = models.get("utils")  # 使用 utils 任务的模型
```

---

### `generate_with_model()`

使用指定模型生成文本内容。

```python
async def generate_with_model(
    prompt: str,
    model_config: TaskConfig,
    request_type: str = "plugin.generate",
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> Tuple[bool, str, str, str]
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| `prompt` | `str` | 提示词 |
| `model_config` | `TaskConfig` | 模型配置（从 `get_available_models()` 获取） |
| `request_type` | `str` | 请求类型标识（用于日志记录） |
| `temperature` | `float \| None` | 温度参数（控制随机性，0-2） |
| `max_tokens` | `int \| None` | 最大 token 数 |

**返回值：** `(成功, 生成内容, 推理过程, 模型名称)`

**示例：**

```python
from src.plugin_system import llm_api

# 获取可用模型
models = llm_api.get_available_models()
model = models.get("utils")  # 或其他模型名

if model:
    success, content, reasoning, model_name = await llm_api.generate_with_model(
        prompt="请用一句话介绍你自己",
        model_config=model,
    )
    if success:
        await self.send_text(content)
```

---

### `generate_with_model_with_tools()`

使用模型和工具调用生成内容（支持 Function Calling）。

```python
async def generate_with_model_with_tools(
    prompt: str,
    model_config: TaskConfig,
    tool_options: List[Dict[str, Any]] | None = None,
    request_type: str = "plugin.generate",
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> Tuple[bool, str, str, str, List[ToolCall] | None]
```

**返回值：** `(成功, 生成内容, 推理过程, 模型名称, 工具调用列表)`

**示例：**

```python
# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

models = llm_api.get_available_models()
model = models.get("utils")

success, content, reasoning, model_name, tool_calls = \
    await llm_api.generate_with_model_with_tools(
        prompt="上海今天天气怎么样？",
        model_config=model,
        tool_options=tools,
    )

if tool_calls:
    for call in tool_calls:
        print(f"工具调用：{call.function.name}({call.function.arguments})")
```

---

## 实用示例

### 翻译功能

```python
async def execute(self):
    text = self.action_data.get("text", "")
    
    models = llm_api.get_available_models()
    model = models.get("utils")
    if not model:
        await self.send_text("❌ 模型不可用")
        return False, "模型不可用"
    
    success, result, _, _ = await llm_api.generate_with_model(
        prompt=f"请将以下文本翻译成英文，只返回翻译结果：\n{text}",
        model_config=model,
    )
    
    if success:
        await self.send_text(f"翻译结果：{result}")
    return success, "翻译完成"
```

### 内容审核

```python
async def execute(self):
    message = self.action_data.get("message", "")
    
    models = llm_api.get_available_models()
    model = models.get("utils")
    
    success, result, _, _ = await llm_api.generate_with_model(
        prompt=f"判断以下内容是否含有不当信息，只回答'是'或'否'：\n{message}",
        model_config=model,
        temperature=0.1,  # 低温度，更确定性的回答
    )
    
    is_inappropriate = success and "是" in result
    return True, f"审核完成：{'不当' if is_inappropriate else '正常'}"
```

::: tip 何时使用 LLM API vs 生成器 API？
- **LLM API**：直接调用模型，完全控制 prompt，适合翻译、分析、判断等结构化任务
- **生成器 API**：使用麦麦的风格化生成器，回复更拟人化，适合麦麦对话回复
:::

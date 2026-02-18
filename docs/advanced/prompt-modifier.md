# PromptModifier API 参考

`PromptModifier` 提供对底层 LLM 的直接访问，完全绕过麦麦的人格/上下文层，适用于需要精确控制提示词的高级场景。

## 导入

```python
from mai_advanced import PromptModifier
```

## 实例化

```python
async def execute(self):
    modifier = PromptModifier(self)  # 传入 self
    ...
```

---

## 方法列表

### `get_available_models()`

获取系统配置的所有可用 LLM 模型。

```python
def get_available_models(self) -> Dict[str, TaskConfig]
```

**返回：** `{模型名: TaskConfig}` 字典

**示例：**
```python
models = modifier.get_available_models()
for name in models.keys():
    print(name)  # 如 "gpt-4o", "deepseek-v3"
```

---

### `get_default_model()`

获取第一个可用的默认模型配置。

```python
def get_default_model(self) -> Optional[TaskConfig]
```

---

### `call_model()`

直接调用指定 LLM 模型，完全控制提示词内容。

```python
async def call_model(
    self,
    prompt: str,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    request_type: str = "plugin.advanced",
) -> Tuple[bool, str]
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `prompt` | `str` | 完整提示词 |
| `model_name` | `str` | 模型名称（`None` 则用默认模型） |
| `temperature` | `float` | 生成温度（0.0~1.0，越小越确定） |
| `max_tokens` | `int` | 最大输出 token 数 |
| `request_type` | `str` | 日志标识符 |

**返回：** `(success: bool, generated_text: str)`

**底层 API：** `llm_api.generate_with_model()`

**示例：**
```python
# 生成 JSON
ok, result = await modifier.call_model(
    prompt='请返回 JSON：{"city": "北京", "weather": "晴", "temp": 25}',
    temperature=0.0,   # 完全确定性输出
    max_tokens=200,
)
if ok:
    import json
    data = json.loads(result)

# 使用特定模型
ok, code = await modifier.call_model(
    prompt="用 Python 写一个冒泡排序",
    model_name="deepseek-v3",
    temperature=0.2,
)
```

---

### `call_model_with_tools()`

使用工具调用（Function Calling）模式调用 LLM。

```python
async def call_model_with_tools(
    self,
    prompt: str,
    tool_names: Optional[List[str]] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> Tuple[bool, str, Optional[List[ToolCall]]]
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `prompt` | `str` | 提示词 |
| `tool_names` | `List[str]` | 要启用的工具名（`None` 则启用全部） |
| `model_name` | `str` | 模型名称 |
| `temperature` | `float` | 生成温度 |
| `max_tokens` | `int` | 最大 token 数 |

**返回：** `(success: bool, text_content: str, tool_calls: Optional[List[ToolCall]])`

**底层 API：** `llm_api.generate_with_model_with_tools()`

**示例：**
```python
ok, content, tool_calls = await modifier.call_model_with_tools(
    prompt="帮我查一下今天北京的天气",
    tool_names=["web_search"],
)
if tool_calls:
    for call in tool_calls:
        print(f"调用工具: {call.name}")
        print(f"参数: {call.arguments}")
```

---

### `generate_with_extra_context()`

在麦麦默认提示词中注入额外上下文，返回原始 `reply_set`（不自动发送）。

```python
async def generate_with_extra_context(
    self,
    extra_info: str,
    reply_to: str = "",
    enable_tool: bool = False,
    return_prompt: bool = False,
) -> Tuple[bool, List[Tuple[str, Any]], Optional[str]]
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `extra_info` | `str` | 追加到提示词末尾的文本 |
| `reply_to` | `str` | 回复目标 |
| `enable_tool` | `bool` | 是否启用工具 |
| `return_prompt` | `bool` | 是否返回提示词 |

**返回：** `(success, reply_set, prompt_or_none)`

> 💡 与 `AdvancedReplyBuilder.generate_reply()` 的区别：此方法返回原始 `reply_set`，**不自动发送**，适合需要进一步处理回复内容的场景。

**示例：**
```python
from src.plugin_system.apis import send_api

ok, reply_set, prompt = await modifier.generate_with_extra_context(
    extra_info="以下是背景知识：[知识内容...]\n\n请基于以上知识回答问题",
    return_prompt=True,
)
if ok:
    # 过滤掉表情包，只发文字
    for rtype, rcontent in reply_set:
        if rtype == "text":
            await send_api.text_to_stream(rcontent, self.stream_id)
```

---

### `get_actual_prompt()`

获取麦麦生成回复时实际使用的完整提示词（调试用，不发送消息）。

```python
async def get_actual_prompt(
    self,
    extra_info: str = "",
) -> Optional[str]
```

**返回：** 提示词字符串，或 `None`

**示例：**
```python
prompt = await modifier.get_actual_prompt()
# 记录到日志
self.logger.info(f"当前提示词长度: {len(prompt)} 字符")
```

---

## 使用场景对比

| 场景 | 推荐方法 | 说明 |
|------|----------|------|
| 专业回答（医生/律师/厨师） | `generate_custom_reply()` | 完全自定义，不带人格 |
| 注入外部知识（新闻/数据库） | `generate_with_extra_context()` | 保留人格，追加知识 |
| 获取 JSON/代码输出 | `call_model(temperature=0.0)` | 直接 LLM，精确控制 |
| 使用外部工具（搜索/计算） | `call_model_with_tools()` | Function Calling |
| 调试当前提示词内容 | `get_actual_prompt()` | 只读，不发送 |

---

## 完整示例：天气助手 Action

```python
from mai_advanced import PromptModifier
from src.plugin_system.apis import send_api
import json

class WeatherLLMAction(BaseAction):
    action_name = "weather_llm"
    
    async def execute(self) -> Tuple[bool, str]:
        modifier = PromptModifier(self)
        
        city = self.action_data.get("city", "北京")
        
        # 1. 先用结构化模式从 LLM 获取天气分析
        ok, raw_json = await modifier.call_model(
            prompt=f"""分析以下天气数据并返回 JSON（不要 markdown）：
城市：{city}
数据：晴，25°C，东南风3级，湿度40%

返回格式：{{"summary": "一句话总结", "advice": "出行建议", "emoji": "天气表情"}}""",
            temperature=0.1,
        )
        
        if not ok:
            await send_api.text_to_stream("天气查询失败", self.stream_id)
            return False, "LLM 失败"
        
        try:
            data = json.loads(raw_json)
            message = f"{data['emoji']} {city}天气：{data['summary']}\n💡 {data['advice']}"
        except json.JSONDecodeError:
            message = raw_json  # 解析失败就直接发原始内容
        
        # 2. 用提示词注入方式让麦麦用自己的语气发出去
        ok2, reply_set, _ = await modifier.generate_with_extra_context(
            extra_info=f"天气信息：{message}\n\n请用你的语气告诉用户这个天气信息。"
        )
        
        if ok2:
            for rtype, rcontent in reply_set:
                if rtype == "text":
                    await send_api.text_to_stream(rcontent, self.stream_id)
        else:
            await send_api.text_to_stream(message, self.stream_id)
        
        return True, f"{city}天气查询完成"
```

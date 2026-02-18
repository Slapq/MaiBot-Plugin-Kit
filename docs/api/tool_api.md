# 🔧 Tool 组件 & Tool API

> **来源**：`src.plugin_system.BaseTool` / `src.plugin_system.apis.tool_api`

Tool 组件扩展麦麦的**信息获取**能力，供 LLM 在回复时主动调用（区别于 Action 是扩展"行为"能力）。

## Tool vs Action vs Command

| 特征 | Action | Command | Tool |
|-----|-------|---------|------|
| 触发方 | 麦麦智能决策 | 用户输入命令 | LLM 生成回复时自主调用 |
| 主要用途 | 扩展麦麦行为 | 响应用户指令 | 扩展麦麦信息获取 |
| 典型场景 | 发表情、禁言 | /time /help | 查天气、搜索、计算 |

---

## 定义 Tool 组件

```python
from typing import Any, Dict, List, Optional, Tuple
from src.plugin_system import BaseTool, ToolParamType


class WeatherTool(BaseTool):
    """天气查询工具"""

    name = "weather_query"
    description = "查询指定城市的实时天气信息，包括温度、湿度、天气状况"
    available_for_llm = True  # 是否对 LLM 可见

    # 参数定义格式：(参数名, 类型, 描述, 是否必须, 枚举值或None)
    parameters = [
        ("city", ToolParamType.STRING, "要查询的城市名称，如：北京", True, None),
        ("unit", ToolParamType.STRING, "温度单位", False, ["celsius", "fahrenheit"]),
    ]

    async def execute(self, function_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        工具执行逻辑

        Args:
            function_args: LLM 传入的参数字典，键名与 parameters 中的参数名一致

        Returns:
            {"name": self.name, "content": 结果字符串}
        """
        city = function_args.get("city", "")
        unit = function_args.get("unit", "celsius")

        try:
            # 你的实现逻辑
            result = f"{city} 当前温度：25°C，天气晴朗 ☀️"
            return {"name": self.name, "content": result}
        except Exception as e:
            return {"name": self.name, "content": f"查询失败：{str(e)}"}
```

## ToolParamType 枚举

| 值 | 对应 JSON Schema 类型 |
|----|---------------------|
| `ToolParamType.STRING` | `string` |
| `ToolParamType.INTEGER` | `integer` |
| `ToolParamType.FLOAT` | `number` |
| `ToolParamType.BOOLEAN` | `boolean` |

## 注册 Tool

```python
@register_plugin
class MyPlugin(BasePlugin):
    ...
    def get_plugin_components(self):
        return [
            (WeatherTool.get_tool_info(), WeatherTool),
        ]
```

---

## tool_api：查询已注册工具

```python
from src.plugin_system import tool_api
# 或
from src.plugin_system.apis import tool_api

# 获取指定工具实例
tool = tool_api.get_tool_instance("weather_query")
if tool:
    result = await tool.execute({"city": "北京"})

# 获取所有 LLM 可用的工具定义（OpenAI 格式）
tools_defs = tool_api.get_llm_available_tool_definitions()
# 返回：List[Tuple[str, Dict]]
# 每个元素是 (工具名, 工具定义字典)
```

## 在 LLM API 中使用 Tool

```python
from src.plugin_system import llm_api, tool_api

# 获取所有工具定义
all_tools = tool_api.get_llm_available_tool_definitions()

# 选择部分工具
weather_tools = [(name, defn) for name, defn in all_tools if "weather" in name]

# 带 Tool 调用模型
success, content, reasoning, model_name, tool_calls = await llm_api.generate_with_model_with_tools(
    prompt="北京今天天气怎么样？",
    model_config=model_config,
    tool_options=weather_tools,
)

if tool_calls:
    for call in tool_calls:
        tool_instance = tool_api.get_tool_instance(call.name)
        if tool_instance:
            result = await tool_instance.execute(call.arguments)
```

---

## 最佳实践

### 命名规范

```python
# ✅ 清晰命名
name = "weather_query"
name = "stock_price_check"
name = "web_search"

# ❌ 避免
name = "tool1"
name = "wq"
```

### 错误处理

```python
async def execute(self, function_args: Dict[str, Any]) -> Dict[str, Any]:
    try:
        result = await self._do_something(function_args)
        return {"name": self.name, "content": result}
    except ValueError as e:
        return {"name": self.name, "content": f"参数错误：{e}"}
    except Exception as e:
        return {"name": self.name, "content": f"执行失败，请稍后重试"}
```

### 格式化输出（让 LLM 更易理解）

```python
def _format_result(self, data: dict) -> str:
    return f"""
🌤️ {data['city']} 天气
━━━━━━━━━━
🌡️ 温度：{data['temp']}°C
☁️ 状况：{data['condition']}
💧 湿度：{data['humidity']}%
    """.strip()
```

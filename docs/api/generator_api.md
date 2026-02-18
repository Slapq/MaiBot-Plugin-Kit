# ✨ 回复生成器 API

`generator_api` 模块提供麦麦风格的智能回复生成能力，生成的内容会经过拟人化处理（分句、错字、语气词等）。

> **接口来源**：MaiBot 官方源码 `src/plugin_system/apis/generator_api.py`  
> **适用版本**：MaiBot ≥ 0.8.0

## 导入方式

```python
from src.plugin_system.apis import generator_api
# 或
from src.plugin_system import generator_api
```

---

## 返回值说明

**所有生成函数统一返回格式（v0.8.0+）：**

```python
Tuple[bool, List[Tuple[str, Any]], Optional[str]]
# (是否成功, 回复集合, 使用的 prompt)
```

**回复集合** `reply_set` 是一个 `(reply_type, reply_content)` 元组列表：

```python
# 示例结构
reply_set = [
    ("text",  "很高兴见到你！"),
    ("emoji", "<base64编码的表情包>"),
    ("text",  "有什么可以帮助你的吗？"),
]
```

支持的 `reply_type`：`"text"` / `"emoji"` / `"image"` / `"mixed"`

**发送方法（在生成成功后遍历）：**

```python
if success:
    for reply_type, reply_content in reply_set:
        if reply_type == "text":
            await self.send_text(reply_content)
        elif reply_type in ("emoji", "image"):
            await self.send_image(reply_content)
```

---

## 函数参考

### `generate_reply()`

生成麦麦风格的完整回复，经过拟人化处理。

```python
async def generate_reply(
    chat_stream=None,           # 聊天流对象（优先使用）
    chat_id: str = None,        # 聊天流 ID（备用，即 stream_id）
    action_data: dict = None,   # 包含 reply_to / extra_info 的字典（向下兼容）
    reply_to: str = "",         # 回复目标，格式："发送者的person_name:消息内容"
    extra_info: str = "",       # 附加上下文信息
    available_actions: dict = None,  # 可用动作字典
    enable_tool: bool = False,  # 是否启用工具调用
    enable_splitter: bool = True,    # 是否拆分为多条消息
    enable_chinese_typo: bool = True, # 是否添加中文错字（更拟人）
    return_prompt: bool = False,     # 是否返回使用的 prompt
    request_type: str = "generator_api",
) -> Tuple[bool, List[Tuple[str, Any]], Optional[str]]
```

**示例：**

```python
from src.plugin_system.apis import generator_api

async def execute(self):
    success, reply_set, prompt = await generator_api.generate_reply(
        chat_stream=self.message.chat_stream,  # 使用 chat_stream（推荐）
        extra_info="用户今天心情很好，请用活泼的语气回复",
        reply_to="小明:你好呀",
    )
    
    if success:
        for reply_type, reply_content in reply_set:
            if reply_type == "text":
                await self.send_text(reply_content)
            elif reply_type in ("emoji", "image"):
                await self.send_image(reply_content)
        return True, "回复成功"
    
    # 生成失败时的备用处理
    await self.send_text("（麦麦想了想，没说话）")
    return False, "生成失败"
```

---

### `rewrite_reply()`

将已有内容重写为麦麦风格（适合先获取数据再风格化输出）。

```python
async def rewrite_reply(
    chat_stream=None,           # 聊天流对象（优先使用）
    chat_id: str = None,        # 聊天流 ID（备用）
    raw_reply: str = "",        # 原始回复内容（将被重写）
    reason: str = "",           # 重写原因（提供上下文）
    reply_to: str = "",         # 回复目标
    reply_data: dict = None,    # 包含 raw_reply/reason/reply_to 的字典（向下兼容）
    enable_splitter: bool = True,
    enable_chinese_typo: bool = True,
    return_prompt: bool = False,
) -> Tuple[bool, List[Tuple[str, Any]], Optional[str]]
```

**示例：**

```python
# 获取天气数据后，用麦麦风格重写
weather_raw = "上海今天晴天，气温25℃，湿度60%"

success, reply_set, _ = await generator_api.rewrite_reply(
    chat_stream=self.message.chat_stream,
    raw_reply=weather_raw,
    reason="用户询问上海天气",
)

if success:
    for reply_type, reply_content in reply_set:
        if reply_type == "text":
            await self.send_text(reply_content)
else:
    # 降级处理：直接发送原始数据
    await self.send_text(weather_raw)
```

---

### `generate_response_custom()`

使用完全自定义的 prompt 生成回复（不走拟人化处理，直接返回字符串）。

```python
async def generate_response_custom(
    chat_stream=None,
    chat_id: str = None,
    prompt: str = "",           # 完全自定义的提示词
    request_type: str = "generator_api",
) -> Optional[str]             # 返回生成的文本，失败时返回 None
```

**示例：**

```python
result = await generator_api.generate_response_custom(
    chat_stream=self.message.chat_stream,
    prompt="请生成一首关于春天的四言绝句",
)
if result:
    await self.send_text(result)
```

---

### `get_replyer()`

获取底层回复器对象（高级用法）。

```python
def get_replyer(
    chat_stream=None,
    chat_id: str = None,
    request_type: str = "replyer",
) -> Optional[DefaultReplyer]
```

---

## 完整流程示例

以下是一个完整的天气查询 Action：

```python
from typing import Tuple
from src.plugin_system import BaseAction, ActionActivationType
from src.plugin_system.apis import generator_api


class WeatherAction(BaseAction):
    action_name = "get_weather"
    action_description = "查询指定城市的天气并以麦麦风格回复"
    activation_type = ActionActivationType.ALWAYS
    action_parameters = {"city": "要查询天气的城市名"}
    action_require = ["当用户询问某个城市天气时"]
    associated_types = ["text"]

    async def execute(self) -> Tuple[bool, str]:
        city = self.action_data.get("city", "上海")
        
        # 1. 获取天气数据
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://wttr.in/{city}?format=3&lang=zh",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    weather_raw = await resp.text()
        except Exception as e:
            await self.send_text(f"❌ 获取天气失败：{str(e)}")
            return False, str(e)
        
        # 2. 用麦麦风格重写天气信息
        success, reply_set, _ = await generator_api.rewrite_reply(
            chat_stream=self.message.chat_stream,
            raw_reply=weather_raw,
            reason=f"用户询问{city}的天气",
        )
        
        if success:
            for reply_type, reply_content in reply_set:
                if reply_type == "text":
                    await self.send_text(reply_content)
        else:
            # 降级处理：直接发送原始数据
            await self.send_text(weather_raw)
        
        return True, f"查询了{city}的天气"
```

---

## 注意事项

1. **优先使用 `chat_stream`**：`self.message.chat_stream` 是最稳定的参数，避免使用 `chat_id`
2. **异步操作**：所有生成函数都是 `async`，必须使用 `await`
3. **回复集合遍历**：新版（≥ 0.8.0）返回 `List[Tuple[str, Any]]`，不再是 `LLMGenerationDataModel`
4. **降级处理**：LLM 可能因配额或网络问题失败，务必准备 `else` 分支
5. **`enable_chinese_typo`**：如果需要准确输出（如 JSON、代码），设为 `False`

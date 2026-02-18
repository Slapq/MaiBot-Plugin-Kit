# 🤖 MaiBot Plugin Kit

**麦麦插件开发工具包** — 让每个人都能轻松开发麦麦插件

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![MaiBot](https://img.shields.io/badge/MaiBot-0.7.0+-green.svg)](https://github.com/Mai-with-u/MaiBot)

---

## 📦 包含什么

| 模块 | 说明 |
|------|------|
| `mai_plugin_cli` | 脚手架命令行工具，一键创建/验证/打包插件 |
| `mai_js_bridge` | JavaScript 插件桥接器，让 JS 开发者也能写麦麦插件 |
| `mai_script` | MaiScript DSL 编译器，零代码生成插件 |
| `docs/` | 完整的 VitePress 文档站点 |

---

## 🚀 三分钟快速开始

### 方式一：Python 开发者（mai CLI）

```bash
# 克隆项目
git clone https://github.com/your-repo/MaiBot-Plugin-Kit.git
cd MaiBot-Plugin-Kit

# 交互式创建插件
python -m mai_plugin_cli create my_plugin

# 或指定模板
python -m mai_plugin_cli create my_plugin -t action    # Action 插件
python -m mai_plugin_cli create my_plugin -t command   # Command 插件
python -m mai_plugin_cli create my_plugin -t full      # 完整插件

# 验证插件
python -m mai_plugin_cli validate ./my_plugin

# 打包发布
python -m mai_plugin_cli pack ./my_plugin
```

### 方式二：JavaScript 开发者（JS Bridge）

```bash
# 创建 JS 桥接插件
python -m mai_plugin_cli create my_js_plugin -t js_bridge

# 编辑 plugin.js
```

```javascript
// plugin.js
mai.command({
  name: "ping",
  description: "测试命令",
  pattern: /^\/ping$/,
  async execute(ctx) {
    await ctx.sendText("🏓 Pong！");
    return { success: true };
  }
});
```

**要求：** 系统需安装 Node.js 14+

### 方式三：零编程基础（MaiScript）

```yaml
# my_plugin.mai
plugin:
  name: "我的第一个插件"
  author: "你的名字"

commands:
  - name: "打招呼"
    match: "/hello"
    reply: "你好！😊 {user_name}！"

  - name: "查时间"
    match: "/time"
    python: |
      import datetime
      reply = f"现在是 {datetime.datetime.now().strftime('%H:%M')}"

actions:
  - name: "开心回应"
    when:
      - "当有人分享好消息时"
    reply: "太棒了！🎉"
```

```bash
# 一键编译为完整插件
python -m mai_plugin_cli run-maiscript my_plugin.mai

# 输出插件目录：./my_plugin/
# 将其复制到 MaiBot/plugins/ 目录，重启 MaiBot 即可！
```

---

## 📋 模板对比

| 模板 | 适合人群 | 功能 |
|------|---------|------|
| `minimal` | Python 进阶者 | 最简骨架，从零手写 |
| `action` | Python 基础者 | 麦麦自主行为（LLM 触发） |
| `command` | Python 基础者 | 响应固定命令（精确触发） |
| `full` | Python 进阶者 | Action + Command + Tool + Event 全家桶 |
| `js_bridge` | JS 开发者 | JavaScript 编写，Python 桥接 |

---

## 📚 插件开发核心概念

### 组件类型

- **Action**：麦麦自主决定是否使用的行为。LLM 根据 `action_require` 判断触发时机
- **Command**：响应用户输入的固定命令（通过正则匹配），无需 LLM 参与
- **Tool**：在 LLM 生成回复前提供额外信息（如查数据库、获取天气）
- **EventHandler**：监听系统事件（新成员加入等）

### 文件结构

```
my_plugin/
├── _manifest.json    插件元数据（必须）
├── plugin.py         插件主文件
└── README.md         说明文档（推荐）
```

### `_manifest.json` 格式

```json
{
  "manifest_version": 1,
  "name": "我的插件",
  "version": "1.0.0",
  "description": "插件描述",
  "author": {
    "name": "作者名称"
  },
  "license": "MIT",
  "host_application": {
    "min_version": "0.7.0"
  },
  "categories": ["Other"],
  "keywords": [],
  "plugin_info": {
    "is_built_in": false,
    "plugin_type": "general",
    "components": []
  }
}
```

---

## 🔧 CLI 命令参考

```
mai create <name>              创建新插件（交互式）
mai create <name> -t <tmpl>   使用指定模板创建
mai validate <path>            验证插件结构和 manifest
mai pack <path>                打包为 zip 文件
mai list-templates             列出所有可用模板
mai run-maiscript <file.mai>   编译 MaiScript 文件
```

---

## 📖 可用 API 概览

### 发送消息

```python
await self.send_text("文本")               # 发送文本
await self.send_image(base64_str)          # 发送图片
await self.send_emoji(base64_str)          # 发送表情包
```

### AI 生成

```python
from src.plugin_system import generator_api, llm_api, send_api

# 使用麦麦风格生成回复
success, data = await generator_api.generate_reply(
    chat_id=self.stream_id,
    extra_info="请用开心的语气回复",
)
if success:
    await send_api.custom_reply_set_to_stream(data.reply_set, self.stream_id)

# 直接调用 LLM
models = llm_api.get_available_models()
model = models.get("utils")
ok, result, _, _ = await llm_api.generate_with_model("你好！", model)
```

### 读取历史消息

```python
from src.plugin_system import message_api

messages = message_api.get_recent_messages(self.stream_id, hours=1.0)
text = message_api.build_readable_messages_to_str(messages)
```

### 读取配置

```python
value = self.get_config("section.key", "默认值")
```

---

## 🌐 文档站点

```bash
cd docs
npm install
npm run dev     # 启动本地文档服务器
npm run build   # 构建静态文档
```

---

## 📁 项目结构

```
MaiBot-Plugin-Kit/
├── mai_plugin_cli/               🛠️ 脚手架工具
│   ├── commands/                  CLI 子命令实现
│   │   ├── create.py              创建插件
│   │   ├── validate.py            验证插件
│   │   ├── pack.py                打包插件
│   │   ├── list_templates.py      列出模板
│   │   └── run_maiscript.py       编译 MaiScript
│   └── templates/                 插件模板
│       ├── minimal/               最简模板
│       ├── action/                Action 模板
│       ├── command/               Command 模板
│       ├── full/                  完整功能模板
│       └── js_bridge/             JS 桥接模板
│
├── mai_js_bridge/                ⚡ JS 桥接器
│   ├── bridge.py                  核心桥接逻辑
│   ├── js_context.py              JS 执行上下文
│   └── sdk/
│       └── mai-sdk.js             JS 侧 SDK
│
├── mai_script/                   ✨ MaiScript 编译器
│   ├── parser.py                  YAML 解析器
│   └── compiler.py                代码生成器
│
└── docs/                         📚 文档站点（VitePress）
    ├── guide/                     使用指南
    ├── api/                       API 参考
    ├── js/                        JS 插件文档
    └── maiscript/                 MaiScript 文档
```

---

## 💡 示例插件

### 最简示例（MaiScript）

```yaml
plugin:
  name: "Hello World"
  author: "开发者"

commands:
  - name: "你好"
    match: "/hello"
    reply: "Hello, World! 👋"
```

### Python Action 示例

```python
class WeatherAction(BaseAction):
    action_name = "weather_check"
    action_description = "查询天气信息"
    activation_type = ActionActivationType.ALWAYS
    action_parameters = {"city": "要查询的城市名"}
    action_require = ["当用户询问天气时", "当用户提到某个城市的天气时"]
    associated_types = ["text"]

    async def execute(self):
        city = self.action_data.get("city", "上海")
        # 在此调用天气 API ...
        await self.send_text(f"🌤 {city} 今天天气晴，25℃")
        return True, f"查询了{city}的天气"
```

### JavaScript 示例

```javascript
mai.command({
  name: "roll_dice",
  pattern: /^\/roll(?:\s+(\d+))?$/,
  async execute(ctx) {
    const sides = parseInt(ctx.getMatch(1)) || 6;
    const result = Math.ceil(Math.random() * sides);
    await ctx.sendText(`🎲 d${sides} = ${result}`);
    return { success: true };
  }
});
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

- [反馈问题](https://github.com/Mai-with-u/MaiBot-Plugin-Kit/issues)
- [查看文档](https://maibot-plugin-kit.pages.dev/)
- [MaiBot 主项目](https://github.com/Mai-with-u/MaiBot)

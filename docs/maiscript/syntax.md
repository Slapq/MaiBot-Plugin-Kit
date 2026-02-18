# 📝 MaiScript 语法手册

MaiScript 文件使用 YAML 格式，以 `.mai` 为后缀。

## 文件结构

```yaml
# 插件基本信息（必填）
plugin:
  name: "插件名称"
  version: "1.0.0"
  author: "你的名字"
  description: "插件描述"

# 命令列表（可选）
commands:
  - name: "命令名"
    match: "触发词"
    reply: "回复内容"

# 自主行为列表（可选）
actions:
  - name: "行为名"
    when:
      - "触发条件"
    reply: "回复内容"

# 配置项（可选）
config:
  section:
    key: "默认值"
```

---

## plugin 节（必填）

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 插件名称（中文英文均可） |
| `version` | ❌ | 版本号（默认 "1.0.0"） |
| `author` | ❌ | 作者名称 |
| `description` | ❌ | 插件描述 |
| `categories` | ❌ | 分类列表（见下方） |

**categories 可选值：**
- `Entertainment & Interaction` — 娱乐互动
- `Utility Tools` — 实用工具
- `Content Generation` — 内容生成
- `Group Management` — 群管理
- `Multimedia` — 多媒体
- `Other` — 其他

---

## commands 节

每个命令是一个列表项，包含以下字段：

### match 语法

| 写法 | 说明 | 示例 |
|------|------|------|
| `/command` | 精确匹配命令 | `/ping` |
| `/cmd {param}` | 带一个参数 | `/echo {content}` |
| `/cmd {p1} {p2}` | 带多个参数 | `/calc {a} and {b}` |
| `^正则表达式$` | 直接使用正则 | `^/help$` |

### 响应类型

**reply** — 直接回复文本（最简单）

```yaml
commands:
  - name: "问好"
    match: "/hi"
    reply: "你好！今天天气真不错"
```

在 reply 中可以使用以下变量：
- `{user_name}` — 发送者的昵称
- `{param}` — match 中定义的参数名

```yaml
  - name: "点名"
    match: "/call {name}"
    reply: "{user_name} 叫了 {name} 一声！"
```

---

**python** — 运行 Python 代码

```yaml
commands:
  - name: "骰子"
    match: "/roll"
    python: |
      import random
      result = random.randint(1, 6)
      reply = f"🎲 你掷出了 {result} 点！"
```

> 💡 最后设置 `reply` 变量，系统会自动发送它的值。

---

**http_get** — 发起 HTTP GET 请求

```yaml
commands:
  - name: "查天气"
    match: "/weather {city}"
    http_get:
      url: "https://wttr.in/{city}?format=3&lang=zh"
    reply: "🌤 {city}：{http_response}"
```

URL 中可以使用 match 定义的参数（如 `{city}`）。
请求结果存储在 `{http_response}` 变量中。

---

**llm_prompt** — 调用 LLM 生成内容

```yaml
commands:
  - name: "写诗"
    match: "/poem {topic}"
    llm_prompt: |
      请以"{topic}"为主题，写一首简短的现代诗。
      风格：清新自然，朗朗上口。
```

---

## actions 节

Action 由麦麦的 LLM 根据对话上下文自动决定是否触发。

### 必填字段

| 字段 | 说明 |
|------|------|
| `name` | Action 名称（唯一标识） |
| `when` | 触发条件列表（越具体越好，至少一条） |

以及以下响应类型之一：`reply` / `python` / `http_get` / `llm_prompt`

### 可选字段

| 字段 | 说明 |
|------|------|
| `params` | LLM 需要提取的参数（键: 参数描述） |
| `description` | Action 的详细描述（辅助 LLM 理解） |
| `types` | 关联的消息类型（默认 `["text"]`） |

### 完整示例

```yaml
actions:
  - name: "查询用户天气"
    description: "当用户提到某个城市并询问天气时查询"
    when:
      - "当用户问某个城市的天气时"
      - "当用户说'帮我看看XX天气'"
    params:
      city: "用户提到的城市名称"
    http_get:
      url: "https://wttr.in/{city}?format=3"
    reply: "{city} 的天气：{http_response}"
```

---

## config 节（可选）

定义插件的可配置参数，系统会生成 `config.toml` 模板：

```yaml
config:
  messages:
    greeting: "你好！"
    farewell: "再见！"
  limits:
    max_requests: 10
```

---

## 完整示例

```yaml
plugin:
  name: "多功能小助手"
  version: "1.0.0"
  author: "小明"
  description: "一个展示各种功能的示例插件"
  categories:
    - "Utility Tools"
    - "Entertainment & Interaction"

commands:
  - name: "帮助"
    match: "/help"
    reply: |
      📖 命令列表：
      /help - 显示帮助
      /hi - 打招呼
      /roll - 掷骰子
      /weather {城市} - 查天气

  - name: "打招呼"
    match: "/hi"
    reply: "你好，{user_name}！☀️"

  - name: "掷骰子"
    match: "/roll"
    python: |
      import random
      n = random.randint(1, 6)
      reply = f"🎲 {n} 点！{'棒！' if n >= 4 else '哦...'}"

  - name: "查天气"
    match: "/weather {city}"
    http_get:
      url: "https://wttr.in/{city}?format=3&lang=zh"
    reply: "🌤 {city}：{http_response}"

actions:
  - name: "加油打气"
    when:
      - "当有人表示沮丧或失落时"
      - "当有人说自己失败了或很难过时"
    reply: "没关系的，失败是成功之母！加油！💪"

  - name: "分享快乐"
    when:
      - "当有人分享好消息时"
      - "当群里有人庆祝时"
    reply: "太棒了！恭喜恭喜！🎉🎊"
```

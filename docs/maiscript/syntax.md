# MaiScript 语法参考

## 文件结构

`.mai` 文件是标准 YAML 格式，顶层包含以下块：

```yaml
plugin:      # 必须：插件基本信息
  ...

commands:    # 可选：命令列表（用户输入触发）
  - ...

actions:     # 可选：行为列表（麦麦自主触发）
  - ...

config:      # 可选：配置项（生成 config.toml）
  ...
```

---

## `plugin` 块

描述插件基本信息。

```yaml
plugin:
  name: "插件显示名称"          # 必须，可以是中文
  version: "1.0.0"             # 可选，默认 1.0.0
  author: "你的名字"            # 可选
  description: "插件简短描述"   # 可选
  categories:                  # 可选，插件分类
    - "Entertainment & Interaction"
  keywords:                    # 可选，搜索关键词
    - "greeting"
    - "hello"
```

### 支持的分类（categories）

- `Group Management` - 群管理
- `Entertainment & Interaction` - 娱乐与互动
- `Utility Tools` - 实用工具
- `Content Generation` - 内容生成
- `Multimedia` - 多媒体
- `External Integration` - 外部集成
- `Data Analysis & Insights` - 数据分析
- `Other` - 其他

---

## `commands` 块

定义命令列表。每个命令在用户输入匹配时触发。

### 基础结构

```yaml
commands:
  - name: "命令显示名称"     # 必须
    match: "/命令"           # 必须，触发这条命令的用户输入
    description: "命令说明"  # 可选
    reply: "回复内容"        # 响应方式（四选一，见下方）
```

### `match` 字段

`match` 支持两种格式：

**1. 简单文本（自动转为正则）**

```yaml
match: "/hello"              # 精确匹配 /hello
match: "/weather {city}"     # 匹配 /weather 北京，{city} 作为参数
```

**2. 正则表达式（以 ^ 开头）**

```yaml
match: "^/ping$"             # 精确匹配
match: "^/(hello|hi)$"       # 匹配 /hello 或 /hi
```

### 响应方式（四选一）

**方式 1：固定回复（`reply`）**

```yaml
commands:
  - name: "打招呼"
    match: "/hello"
    reply: "你好！{user_name} 同学 😊"
    # 支持模板变量：{user_name} = 用户昵称
```

**方式 2：Python 代码（`python`）**

```yaml
commands:
  - name: "当前时间"
    match: "/time"
    python: |
      import datetime
      now = datetime.datetime.now()
      reply = f"现在是 {now.strftime('%H:%M:%S')} ⏰"
    # 在 python 块中设置 reply 变量即可发送
```

**方式 3：HTTP 请求（`http_get`）**

```yaml
commands:
  - name: "查天气"
    match: "/weather {city}"
    http_get:
      url: "https://wttr.in/{city}?format=3&lang=zh"
    reply: "🌤️ {http_response}"
    # {http_response} = HTTP 响应内容
    # {city} = 从 match 中提取的参数
```

**方式 4：LLM 回复（`llm_prompt`）**

```yaml
commands:
  - name: "智能回答"
    match: "/ask {question}"
    llm_prompt: |
      用户提了一个问题：{question}
      请用简洁友好的语气回答（不超过100字）。
```

---

## `actions` 块

定义行为列表。麦麦会根据 `when` 条件自主决定是否触发。

### 基础结构

```yaml
actions:
  - name: "行为名称"    # 必须
    when:              # 必须：什么情况下触发（LLM 判断）
      - "条件描述1"
      - "条件描述2"
    reply: "回复内容"  # 响应方式（同 command，四选一）
```

### 带自定义参数的行为

```yaml
actions:
  - name: "天气提醒"
    when:
      - "当用户询问今天适不适合出行时"
      - "当聊到户外活动相关话题时"
    params:
      city: "用户提到的城市名"    # LLM 从对话中提取这个参数
    http_get:
      url: "https://wttr.in/{city}?format=3&lang=zh"
    reply: "刚查了一下 {city} 的天气：{http_response}"
```

### 指定消息类型（`types`）

```yaml
actions:
  - name: "发表情"
    when:
      - "当气氛轻松愉快时"
    types:
      - "emoji"    # 告诉 LLM 这个行为会发表情包
    python: |
      # 发送表情包的逻辑
      reply = "😂"
```

可选类型：`text`、`emoji`、`image`、`reply`、`voice`

---

## `config` 块

定义配置项，会生成 `config.toml` 文件供用户修改。

```yaml
config:
  plugin:
    greeting_message:
      default: "你好！"
      description: "默认问候语"
    enabled:
      default: true
      description: "是否启用插件"
  weather:
    api_key:
      default: ""
      description: "天气 API Key（留空使用免费接口）"
```

在 Python 代码块中，通过 `self.get_config("section.key", 默认值)` 读取。

---

## 完整示例

```yaml
plugin:
  name: "多功能助手"
  version: "1.0.0"
  author: "小明"
  description: "天气查询 + 随机名言 + 聊天记录"
  categories:
    - "Utility Tools"

commands:
  # 命令 1：固定回复
  - name: "帮助"
    match: "/help"
    reply: |
      我能做这些：
      /weather 城市 - 查天气
      /quote - 随机名言
      /time - 当前时间

  # 命令 2：HTTP 请求
  - name: "天气"
    match: "/weather {city}"
    description: "查询指定城市天气"
    http_get:
      url: "https://wttr.in/{city}?format=3&lang=zh"
    reply: "🌤️ {http_response}"

  # 命令 3：Python 代码
  - name: "时间"
    match: "/time"
    python: |
      import datetime
      now = datetime.datetime.now()
      reply = f"⏰ 现在是 {now.strftime('%Y-%m-%d %H:%M:%S')}"

  # 命令 4：LLM 智能回复
  - name: "建议"
    match: "/ask {question}"
    llm_prompt: |
      用户问：{question}
      请给出简洁、友好、有帮助的回答（不超过150字）。

actions:
  # 行为 1：鼓励用户
  - name: "鼓励"
    when:
      - "当用户表达沮丧、失落或困难时"
      - "当用户说'好难''不想做了'等情绪词时"
    reply: "加油！困难只是暂时的，你一定可以的！💪"

  # 行为 2：分享天气（主动触发）
  - name: "天气分享"
    when:
      - "当群里有人讨论出行计划时"
      - "当谈到明天的活动安排时"
    params:
      city: "提到的城市，默认北京"
    http_get:
      url: "https://wttr.in/{city}?format=3&lang=zh"
    reply: "顺便查了一下 {city} 的天气：{http_response} 供参考～"

config:
  plugin:
    enabled:
      default: true
      description: "是否启用插件"
```

---

## 编译

```bash
mai run-maiscript my_plugin.mai
```

生成的 `plugin.py` 是完整的 Python 源代码，你可以继续修改它添加更复杂的功能。

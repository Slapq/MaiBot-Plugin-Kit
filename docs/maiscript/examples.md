# MaiScript 实用示例

所有示例均可直接用 `mai run-maiscript 文件名.mai` 编译运行。

---

## 示例 1：Hello World

最简单的插件，响应 `/hello` 命令：

```yaml
plugin:
  name: "Hello World"
  author: "我"
  description: "最简单的示例插件"

commands:
  - name: "打招呼"
    match: "/hello"
    reply: "你好！欢迎使用麦麦 😊"
```

---

## 示例 2：带参数的命令

用 `{参数名}` 在 `match` 中定义参数：

```yaml
plugin:
  name: "复读机"
  description: "把你说的话重复一遍"

commands:
  - name: "复读"
    match: "/echo {text}"
    reply: "你刚才说：{text}"
```

用法：用户输入 `/echo 今天天气不错` → 麦麦回复 `你刚才说：今天天气不错`

---

## 示例 3：天气查询（HTTP 请求）

```yaml
plugin:
  name: "天气查询"
  description: "实时查询城市天气"

commands:
  - name: "查天气"
    match: "/weather {city}"
    description: "查询指定城市天气"
    http_get:
      url: "https://wttr.in/{city}?format=3&lang=zh"
    reply: "🌤️ {http_response}"

actions:
  - name: "主动查天气"
    when:
      - "当有人讨论出行计划时"
      - "当聊到户外活动时"
    params:
      city: "提到的城市名"
    http_get:
      url: "https://wttr.in/{city}?format=3&lang=zh"
    reply: "顺便查了一下 {city} 的天气：{http_response}"
```

---

## 示例 4：时间与计算（Python 代码块）

```yaml
plugin:
  name: "小工具"
  description: "时间、随机数等小工具"

commands:
  - name: "当前时间"
    match: "/time"
    python: |
      import datetime
      now = datetime.datetime.now()
      reply = f"⏰ 现在是 {now.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)"

  - name: "随机数"
    match: "/random {max}"
    python: |
      import random
      try:
          n = int(max) if max else 100
          result = random.randint(1, n)
          reply = f"🎲 {result}（范围 1~{n}）"
      except:
          reply = "❌ 请输入有效的数字，例如：/random 100"

  - name: "抛硬币"
    match: "/coin"
    python: |
      import random
      result = "正面 🌕" if random.random() > 0.5 else "反面 🌑"
      reply = f"硬币落下：{result}"
```

---

## 示例 5：LLM 智能回复

让麦麦用自定义提示词回答问题：

```yaml
plugin:
  name: "AI 助手"
  description: "自定义提示词智能回答"

commands:
  - name: "提问"
    match: "/ask {question}"
    llm_prompt: |
      用户向你提了一个问题：{question}
      
      请用简洁、友好、准确的方式回答，不超过 150 字。
      如果是敏感或不适当的问题，礼貌地拒绝回答。

  - name: "翻译"
    match: "/translate {text}"
    llm_prompt: |
      请将以下文本翻译成英文：
      {text}
      
      只输出翻译结果，不要加任何解释。

  - name: "摘要"
    match: "/summary {text}"
    llm_prompt: |
      请用 3 句话以内总结以下内容：
      {text}
```

---

## 示例 6：麦麦自主行为（Actions）

```yaml
plugin:
  name: "情绪助手"
  description: "麦麦根据对话情绪自动反应"

actions:
  - name: "鼓励用户"
    when:
      - "当用户表达沮丧、压力大或困难时"
      - "当有人说'好难''累了''不想做了'"
    reply: "加油！每个困难都是成长的机会 💪 我相信你能克服它！"

  - name: "一起庆祝"
    when:
      - "当用户分享好消息或取得成就时"
      - "当有人说'成功了''搞定了''通过了'"
    reply: "太棒了！🎉 恭喜你！这是你努力的结果，继续保持！"

  - name: "分享笑话"
    when:
      - "当聊天气氛轻松，大家都在开玩笑时"
      - "当有人说'讲个笑话'"
    llm_prompt: |
      请讲一个简短、无害、有趣的笑话（不超过3句话）。
      要求：适合所有年龄段，不涉及政治和敏感话题。
```

---

## 示例 7：带配置的插件

```yaml
plugin:
  name: "可配置问好"
  description: "问候语可以在配置文件中修改"

commands:
  - name: "问好"
    match: "/hi"
    python: |
      # 使用配置文件中的问候语
      msg = self.get_config("greeting.message", "你好！")
      emoji = self.get_config("greeting.emoji", "😊")
      reply = f"{msg} {emoji}"

config:
  greeting:
    message:
      default: "你好！欢迎来到这里"
      description: "问候语文本"
    emoji:
      default: "😊"
      description: "问候表情"
```

生成插件后，用户可在 `config.toml` 中修改：
```toml
[greeting]
message = "哈喽！很高兴见到你"
emoji = "🎉"
```

---

## 示例 8：综合功能插件

```yaml
plugin:
  name: "群助手"
  version: "1.0.0"
  author: "小明"
  description: "综合功能群服务机器人"
  categories:
    - "Utility Tools"
  keywords:
    - "assistant"
    - "tools"

commands:
  - name: "帮助"
    match: "/help"
    reply: |
      📖 群助手命令列表：
      /weather 城市 - 查天气
      /time - 当前时间  
      /roll 数字 - 掷骰子
      /ask 问题 - AI 回答

  - name: "天气"
    match: "/weather {city}"
    http_get:
      url: "https://wttr.in/{city}?format=3&lang=zh"
    reply: "🌤️ {http_response}"

  - name: "时间"
    match: "/time"
    python: |
      import datetime
      reply = datetime.datetime.now().strftime("⏰ %Y-%m-%d %H:%M:%S")

  - name: "骰子"
    match: "/roll {max}"
    python: |
      import random
      try:
          n = int(max) if max else 6
          reply = f"🎲 掷出了 {random.randint(1, n)}（1~{n}）"
      except:
          reply = "❌ 请输入数字，如：/roll 20"

  - name: "AI回答"
    match: "/ask {question}"
    llm_prompt: |
      用户问：{question}
      请简洁地回答（不超过100字）。

actions:
  - name: "欢迎新人"
    when:
      - "当有新成员加入群聊时"
      - "当有人第一次发言并自我介绍时"
    reply: "欢迎新朋友！😊 有什么不懂的可以发 /help 查看我的功能哦～"

  - name: "鼓励"
    when:
      - "当有人表达困难或压力时"
    reply: "加油！💪 困难只是暂时的！"
```

---

## 编译与部署

```bash
# 编译任意示例
mai run-maiscript 示例文件.mai

# 或指定输出目录
mai run-maiscript 示例文件.mai -o ./plugins/

# 部署到 MaiBot
cp -r 生成的目录/ ../MaiBot/plugins/
```

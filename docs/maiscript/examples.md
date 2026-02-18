# 💡 MaiScript 示例集合

这里收录了常用的 MaiScript 插件示例，可以直接复制使用。

## 基础示例

### 打招呼机器人

```yaml
plugin:
  name: "打招呼"
  author: "我"
  version: "1.0.0"

commands:
  - name: "hello"
    match: "/hello"
    reply: "你好！我是麦麦 😊"
```

---

### 复读机

```yaml
plugin:
  name: "复读机"
  author: "我"

commands:
  - name: "echo"
    match: "/echo {content}"
    reply: "你说：{content}"
```

---

### 骰子

```yaml
plugin:
  name: "骰子"
  author: "我"

commands:
  - name: "roll"
    match: "/roll"
    python: |
      import random
      n = random.randint(1, 6)
      reply = f"🎲 你掷出了 {n} 点！"
```

---

## 实用工具

### 查询当前时间

```yaml
plugin:
  name: "查时间"
  author: "我"

commands:
  - name: "time"
    match: "/time"
    python: |
      import datetime
      now = datetime.datetime.now()
      reply = f"⏰ 现在是 {now.strftime('%Y-%m-%d %H:%M:%S')}"
```

---

### 查天气（调用 wttr.in）

```yaml
plugin:
  name: "查天气"
  author: "我"

commands:
  - name: "weather"
    match: "/weather {city}"
    http_get:
      url: "https://wttr.in/{city}?format=3&lang=zh"
    reply: "🌤 {city} 天气：{http_response}"
```

---

### 翻译（调用 LibreTranslate）

```yaml
plugin:
  name: "翻译"
  author: "我"

commands:
  - name: "translate"
    match: "/translate {text}"
    http_post:
      url: "https://libretranslate.de/translate"
      body:
        q: "{text}"
        source: "zh"
        target: "en"
    reply: "🌐 翻译结果：{http_response.translatedText}"
```

---

## Action 示例

### 鼓励人

```yaml
plugin:
  name: "鼓励师"
  author: "我"

actions:
  - name: "encourage"
    when:
      - "当有人说心情不好时"
      - "当有人表示沮丧或难过时"
    reply: "加油！你是最棒的！💪 遇到困难很正常，我相信你一定能克服的！"
```

---

### 庆祝好消息

```yaml
plugin:
  name: "庆祝"
  author: "我"

actions:
  - name: "celebrate"
    when:
      - "当有人分享好消息或成就时"
      - "当群里有人考试通过或升职时"
    reply: "🎉 恭喜恭喜！太厉害了！"
```

---

## 多命令插件

一个插件可以包含多个命令：

```yaml
plugin:
  name: "工具箱"
  author: "我"
  version: "1.0.0"
  description: "常用工具合集"

commands:
  - name: "ping"
    match: "/ping"
    reply: "pong! 🏓"

  - name: "time"
    match: "/time"
    python: |
      import datetime
      reply = datetime.datetime.now().strftime('%H:%M:%S')

  - name: "hello"
    match: "/hello {name}"
    reply: "你好，{name}！😊"

actions:
  - name: "morning"
    when:
      - "当有人说早上好时"
    reply: "早上好！今天也要加油哦 ☀️"
```

---

## 注意事项

::: tip 提示
- `match` 字段中的 `{变量名}` 会自动捕获参数
- `python` 字段的代码块最后需要设置 `reply` 变量作为输出
- `http_get` / `http_post` 的响应存储在 `{http_response}` 变量中
:::

::: warning 注意
MaiScript 适合编写简单插件。复杂逻辑（数据库操作、多步交互等）请使用 Python 开发。
:::

## 下一步

- 📝 查看完整 [语法手册](/maiscript/syntax)
- 🚀 了解如何 [快速开始](/guide/quickstart)

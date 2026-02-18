# ✨ MaiScript 介绍

**MaiScript** 是专为编程零基础的用户设计的插件开发语言。

你只需要写一个简单的 YAML 文件，就能创建一个功能完整的麦麦插件——无需学习 Python，无需了解异步编程。

## 为什么需要 MaiScript？

| | 传统 Python 开发 | MaiScript |
|---|---|---|
| **需要的技能** | Python + 异步编程 | 只需会打字 |
| **最少代码量** | ~50 行 | 5 行 YAML |
| **学习曲线** | 陡峭 | 几乎没有 |
| **适合人群** | 程序员 | 所有人 |
| **功能限制** | 无限制 | 基础功能 |

## 一个最简单的例子

```yaml
plugin:
  name: "我的第一个插件"
  author: "你的名字"

commands:
  - name: "打招呼"
    match: "/hello"
    reply: "你好！😊"
```

就这样！保存为 `my_plugin.mai`，然后运行：

```bash
python -m mai_plugin_cli run-maiscript my_plugin.mai
```

一个完整的 MaiBot 插件就生成好了！

## 能做什么

### 1. 响应命令
用户输入 `/hello` 时，麦麦自动回复：
```yaml
commands:
  - name: "打招呼"
    match: "/hello"
    reply: "你好！😊"
```

### 2. 带参数的命令
用户输入 `/echo 你好世界`，麦麦重复这句话：
```yaml
commands:
  - name: "重复"
    match: "/echo {content}"
    reply: "你说：{content}"
```

### 3. 自主行为（Action）
麦麦在合适的时机主动触发：
```yaml
actions:
  - name: "开心回应"
    when:
      - "当有人分享好消息时"
      - "当大家都在开心聊天时"
    reply: "哇！太棒了！🎉"
```

### 4. HTTP 请求
调用外部 API 获取数据：
```yaml
commands:
  - name: "查天气"
    match: "/weather {city}"
    http_get:
      url: "https://wttr.in/{city}?format=3"
    reply: "🌤 {city} 的天气：{http_response}"
```

### 5. 内嵌 Python 代码
需要复杂逻辑时，可以内嵌简单的 Python：
```yaml
commands:
  - name: "查时间"
    match: "/time"
    python: |
      import datetime
      now = datetime.datetime.now()
      reply = f"现在是 {now.strftime('%H:%M:%S')}"
```

## 下一步

- 📝 查看完整的 [语法手册](/maiscript/syntax)
- 💡 浏览 [示例集合](/maiscript/examples)

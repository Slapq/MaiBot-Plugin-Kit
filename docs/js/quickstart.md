# ⚡ JS 插件快速开始

**JS 桥接插件**允许你用 JavaScript 编写插件逻辑，无需了解 Python 的 class / async 写法。

## 工作原理

```
用户消息 → MaiBot → Python 层（plugin.py）→ Node.js 子进程（plugin.js）→ 执行 JS 逻辑
```

- **`plugin.js`**：你唯一需要编写的文件，用 `mai.command()` / `mai.reply()` / `mai.action()` 注册逻辑
- **`plugin.py`**：Python 胶水层，自动加载并桥接 JS（通常不需要修改）

## 前置条件

- **Node.js 16+**（必须安装，命令行中 `node --version` 有输出）
- Python 3.10+

---

## 第一步：创建插件

```bash
mai create my_plugin -t js_bridge -y
```

目录结构：

```
my_plugin/
├── _manifest.json   ← 插件元信息（名称、版本等）
├── plugin.py        ← Python 加载器（通常不需要动它）
└── plugin.js        ← 在这里写你的插件逻辑 ✏️
```

---

## 第二步：编写 plugin.js

打开 `plugin.js`，这里完全是 JavaScript。

### 最简单：一行固定回复

```javascript
// 用户发 /ping 时，麦麦回复 "Pong! 🏓"
mai.reply('/ping', 'Pong! 🏓');
```

### 带逻辑的命令

```javascript
// 掷骰子：/roll 或 /roll 20
mai.command(/^\/roll(?:\s+(\d+))?$/, async (ctx) => {
  const max    = parseInt(ctx.match(1), 10) || 6;
  const result = Math.floor(Math.random() * max) + 1;
  await ctx.send(`🎲 你掷出了 ${result}（1-${max}）`);
});
```

### 从正则里提取内容

```javascript
// /echo 你好  →  麦麦回复：你说：你好
mai.command(/^\/echo\s+(.+)$/, async (ctx) => {
  const text = ctx.match(1);         // 拿第 1 个括号里匹配到的内容
  await ctx.send(`你说：${text}`);
});
```

### 调用网络 API（Node.js 18+ 内置 fetch）

```javascript
mai.command(/^\/weather\s+(\S+)$/, async (ctx) => {
  const city = ctx.match(1);
  try {
    const res  = await fetch(`https://wttr.in/${encodeURIComponent(city)}?format=3`);
    const text = await res.text();
    await ctx.send(`🌤️ ${text.trim()}`);
  } catch (err) {
    await ctx.send(`❌ 查询失败：${err.message}`);
    ctx.logError(err.message);
  }
});
```

### Action：麦麦自主触发

```javascript
mai.action({
  name:        'send_encouragement',
  description: '当有人沮丧时给出鼓励',
  require:     ['当有人表达沮丧、失落时'],
  parameters:  { name: '对方的名字（可选）' },
  types:       ['text'],

  execute: async (ctx) => {
    const name = ctx.param('name', '朋友');
    await ctx.send(`加油 ${name}！困难只是暂时的 💪`);
    return { success: true };
  },
});
```

---

## 第三步：验证并部署

```bash
# 验证格式
mai validate ./my_plugin

# 复制到 MaiBot plugins 目录
cp -r my_plugin/ ../MaiBot/plugins/
```

重启 MaiBot，插件即生效。

---

## 完整示例：每日一句

下面是一个真实可用的完整 `plugin.js`：

```javascript
// 每日一句激励插件

// 固定命令：/inspire
mai.command(/^\/inspire$/, async (ctx) => {
  const quotes = [
    '每一天都是新的开始。🌅',
    '相信自己，你能做到！✨',
    '困难让我们更强大。💪',
    '今天的努力是明天的礼物。🎁',
  ];
  const q = quotes[Math.floor(Math.random() * quotes.length)];
  await ctx.send(q);
});

// Action：麦麦在适当时机主动发送
mai.action({
  name:        'daily_quote',
  description: '发送今日激励语',
  require:     ['当聊天气氛沉闷或有人需要鼓励时'],
  types:       ['text'],

  execute: async (ctx) => {
    const quotes = [
      '每一天都是新的开始。🌅',
      '相信自己，你能做到！✨',
    ];
    await ctx.send(quotes[Math.floor(Math.random() * quotes.length)]);
    return { success: true };
  },
});
```

---

## API 速查

### 注册

| 函数 | 说明 |
|------|------|
| `mai.reply(pattern, text)` | 固定文本回复，最简单 |
| `mai.command(pattern, fn)` | 带逻辑的命令（箭头函数） |
| `mai.command(config)` | 带完整元数据的命令 |
| `mai.action(config)` | LLM 自主触发的行为 |

### ctx 上下文

| 方法 / 属性 | 说明 |
|-------------|------|
| `await ctx.send(text)` | 发送文本 |
| `await ctx.sendImage(base64)` | 发送图片 |
| `ctx.match(n)` | 获取正则第 n 个捕获组（Command 专用）|
| `ctx.param(key, default?)` | 获取 LLM 参数（Action 专用）|
| `ctx.config(key, default?)` | 读取配置文件 |
| `ctx.log(...args)` | 输出日志 |
| `ctx.stream_id` | 当前聊天流 ID |

> 📖 完整 API 参见 [JS SDK 参考](/js/api)

---

## 注意事项

- **Node.js 必须在 PATH 中** — 命令行 `node --version` 能输出版本号就行
- **每次调用启动新进程** — 不要依赖全局变量存状态
- **30 秒超时** — 超时会被强制终止
- **使用 CommonJS** — `require('fs')` 可用，`import` 不可用（除非加 `--input-type=module`）
- **不要 console.log** — 用 `ctx.log()` 输出日志（`console.log` 会污染 stdout，破坏协议）

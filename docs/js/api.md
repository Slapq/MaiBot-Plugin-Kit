# JS SDK API 参考

`mai-sdk.js` 向 `plugin.js` 暴露两个全局对象：`mai`（注册器）和 `ctx`（执行上下文）。

---

## `mai` 注册器

在 `plugin.js` 顶层调用，告诉麦麦你的插件能做什么。

### `mai.reply(pattern, text)`

**最简单的 API** — 固定文本回复，一行搞定。

```javascript
mai.reply('/ping',  'Pong! 🏓');
mai.reply(/^hi$/i, '你好！😊');
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `pattern` | `string \| RegExp` | 触发条件（字符串会自动转为正则） |
| `text` | `string` | 要发送的固定文本 |

---

### `mai.command(pattern, fn)` <Badge type="tip" text="推荐" />

注册带逻辑的命令，用箭头函数接收 `ctx`。

```javascript
// 简洁风格 ✅
mai.command(/^\/roll(?:\s+(\d+))?$/, async (ctx) => {
  const max    = parseInt(ctx.match(1), 10) || 6;
  const result = Math.floor(Math.random() * max) + 1;
  await ctx.send(`🎲 ${result}`);
});
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `pattern` | `string \| RegExp` | 匹配用户输入的正则（或固定字符串）|
| `fn` | `async (ctx) => any` | 执行函数 |

---

### `mai.command(config)`

带完整元数据的命令（在需要给组件起名、写描述时使用）。

```javascript
mai.command({
  name:        'roll_dice',           // 组件内部名称（默认自动生成）
  description: '掷骰子',              // 可选，帮助 LLM 理解
  pattern:     /^\/roll(?:\s+(\d+))?$/,

  execute: async (ctx) => {           // 注意：这里用 execute: async (ctx) => {}
    const max    = parseInt(ctx.match(1), 10) || 6;
    const result = Math.floor(Math.random() * max) + 1;
    await ctx.send(`🎲 你掷出了 ${result}（1-${max}）`);
    return { success: true };         // 可省略，默认视为成功
  },
});
```

`config` 字段：

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `name` | `string` | 否 | 组件名（自动生成）|
| `description` | `string` | 否 | 功能描述 |
| `pattern` | `string \| RegExp` | 否 | 匹配正则 |
| `execute` | `async (ctx) => any` | **是** | 执行函数（箭头函数）|

---

### `mai.action(config)`

注册由麦麦 LLM 自主决定触发的行为。

```javascript
mai.action({
  name:        'send_encouragement',
  description: '当有人沮丧时给出鼓励',    // LLM 用这个判断何时触发
  require: [                              // 触发条件列表
    '当有人表达沮丧或失落时',
    '当需要情绪支持时',
  ],
  parameters: {                           // LLM 会提取并传入的参数
    name:   '对方的名字（可选）',
    reason: '触发原因',
  },
  types: ['text'],                        // 发送的消息类型

  execute: async (ctx) => {
    const name = ctx.param('name', '朋友');
    await ctx.send(`加油 ${name}！💪`);
    return { success: true };
  },
});
```

`config` 字段：

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| `name` | `string` | 否 | 组件名 |
| `description` | `string` | 否 | 向 LLM 描述功能 |
| `require` | `string[]` | 否 | 触发条件（越具体越好）|
| `parameters` | `{ [key]: string }` | 否 | LLM 提取参数的定义 |
| `types` | `string[]` | 否 | 消息类型，如 `['text']` |
| `execute` | `async (ctx) => any` | **是** | 执行函数 |

---

## `ctx` 上下文对象

在 `execute` 的箭头函数参数中使用。

### 发送消息

#### `await ctx.send(text)` <Badge type="tip" text="推荐" />

发送文本消息（`sendText` 的简写）。

```javascript
await ctx.send('你好！');
await ctx.send(`当前时间：${new Date().toLocaleTimeString('zh-CN')}`);
```

#### `await ctx.sendText(text)`

`ctx.send()` 的完整名称，与 `send()` 完全等价。

#### `await ctx.sendImage(base64)`

发送图片，传入 Base64 字符串（**不含** `data:image/png;base64,` 前缀）。

```javascript
const { readFileSync } = require('fs');
const b64 = readFileSync('./image.png').toString('base64');
await ctx.sendImage(b64);
```

#### `await ctx.sendEmoji(base64)`

发送表情包，格式与 `sendImage` 相同。

---

### 获取数据

#### `ctx.match(n)`

获取 Command 正则的第 n 个捕获组（从 **1** 开始编号）。

```javascript
// pattern: /^\/roll(?:\s+(\d+))?$/
const num = ctx.match(1);    // 返回字符串或 null
const max = parseInt(num, 10) || 6;
```

> **仅在 Command 中有效。** Action 中使用 `ctx.param()`。

别名：`ctx.getMatch(n)` — 与 `ctx.match(n)` 完全等价。

---

#### `ctx.param(key, defaultValue?)`

获取 Action 的 LLM 参数（在 `parameters` 字段中定义的 key）。

```javascript
const city = ctx.param('city');           // 未传则返回 null
const city = ctx.param('city', '北京');   // 带默认值
```

> **仅在 Action 中有效。**

别名：`ctx.getParam(key, defaultValue?)` — 与 `ctx.param()` 完全等价。

---

#### `ctx.config(key, defaultValue?)`

读取插件配置（来自 `config.toml`，由 Python 层传入）。

```javascript
const reply  = ctx.config('command.reply', '默认回复');
const prefix = ctx.config('bot.prefix', '!');
// key 格式：section.key → 对应 config.toml 中 [section] / key = "..."
```

别名：`ctx.getConfig(key, defaultValue?)` — 完全等价。

---

### 日志

#### `ctx.log(...args)`

输出普通日志到 stderr（不影响消息输出）。

```javascript
ctx.log('处理完成', '用时', Date.now() - start, 'ms');
// → [JS:my_plugin] 处理完成 用时 42 ms
```

#### `ctx.logError(...args)`

输出错误日志到 stderr。

```javascript
ctx.logError('请求失败', err.message);
// → [JS:my_plugin] ERROR: 请求失败 timeout
```

---

### 其他属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `ctx.stream_id` | `string` | 当前聊天流 ID |
| `ctx.plugin_name` | `string` | 插件名称（`_manifest.json` 中的 `name`）|

---

## `execute` 返回值

函数可以不写 `return`（视为成功），也可以返回：

```javascript
return { success: true,  log: '可选的日志描述' };  // 成功
return { success: false, log: '出错原因' };          // 失败
```

未捕获的异常会被桥接器自动拦截并返回 `{ success: false }`。

---

## 新旧 API 对照

| 新（推荐）| 旧（兼容）| 说明 |
|-----------|----------|------|
| `ctx.send(text)` | `ctx.sendText(text)` | 发文本 |
| `ctx.match(n)` | `ctx.getMatch(n)` | 获取正则捕获组 |
| `ctx.param(key)` | `ctx.getParam(key)` | 获取 Action 参数 |
| `ctx.config(key)` | `ctx.getConfig(key)` | 读取配置 |
| `mai.command(pattern, fn)` | `mai.command({ execute(ctx){} })` | 注册命令 |

旧方法仍然完全可用，不会被删除。

---

## 限制与注意事项

| 项目 | 说明 |
|------|------|
| **执行超时** | 每次调用最多 30 秒 |
| **模块系统** | CommonJS（`require`），不支持 `import` |
| **无状态** | 每次调用启动新进程，全局变量不跨调用保留 |
| **禁止 console.log** | 会污染 stdout 通信协议，请用 `ctx.log()` |
| **Node.js 版本** | 建议 18+（内置 `fetch`）；16+ 基础功能可用 |

# JS SDK API 参考

本页面列出 `mai-sdk.js` 提供的所有 API，基于 `mai_js_bridge/sdk/mai-sdk.js` 源码。

## 注册函数

### `mai.command(config)`

注册一个命令组件（响应用户输入的特定文本）。

```javascript
mai.command({
  name: "ping",                    // 必须：命令唯一名称（英文）
  description: "测试连接",          // 可选：命令描述（帮助 LLM 理解）
  pattern: /^\/ping$/,             // 可选：正则表达式（用于匹配用户输入）

  async execute(ctx) {
    // 你的逻辑
    return { success: true, log: "可选日志" };
  }
});
```

**注意**：`pattern` 字段用于在桥接层让 Python 动态生成 `command_pattern`。实际匹配由 MaiBot Python 侧完成，`ctx.getMatch()` 返回匹配到的捕获组。

---

### `mai.action(config)`

注册一个行为组件（由麦麦的 LLM 决策系统自主选择触发）。

```javascript
mai.action({
  name: "my_action",              // 必须：行为唯一名称（英文）
  description: "行为的功能描述",   // 可选：LLM 用这个理解何时调用
  require: [                      // 可选：触发条件列表（LLM 判断依据）
    "当场景符合时",
    "避免频繁使用"
  ],
  parameters: {                   // 可选：LLM 会传入的参数及说明
    param_name: "参数描述",
  },
  types: ["text"],                // 可选：发送的消息类型（默认 ["text"]）

  async execute(ctx) {
    // 你的逻辑
    return { success: true };
  }
});
```

---

## `ctx` 上下文对象

在 `execute(ctx)` 函数中使用。

### 发送消息

#### `ctx.sendText(text)`

发送文本消息。

```javascript
await ctx.sendText("你好！");
await ctx.sendText(`当前时间：${new Date().toLocaleTimeString()}`);
```

#### `ctx.sendImage(base64)`

发送图片，内容为不含 `data:image/...;base64,` 头部的 Base64 字符串。

```javascript
const fs = require('fs');
const imageData = fs.readFileSync('/path/to/image.png').toString('base64');
await ctx.sendImage(imageData);
```

#### `ctx.sendEmoji(base64)`

发送表情包，格式与 `sendImage` 相同。

```javascript
await ctx.sendEmoji(emojiBase64);
```

---

### 获取数据

#### `ctx.getParam(key, defaultValue?)`

获取 Action 的 LLM 参数（在 `parameters` 中定义的字段）。

```javascript
const city = ctx.getParam("city");           // 没有则返回 null
const city = ctx.getParam("city", "北京");   // 带默认值
```

**仅在 Action 中有效。** Command 中无 LLM 参数，请使用 `getMatch()`。

#### `ctx.getMatch(group)`

获取 Command 正则表达式的捕获组内容（从 1 开始编号）。

```javascript
// pattern: /^\/roll\s+(\d+)$/
const maxVal = ctx.getMatch(1);   // 获取 (\d+) 匹配到的内容
```

返回字符串或 `null`（未匹配或不存在）。

**仅在 Command 中有效。**

#### `ctx.getConfig(key, defaultValue?)`

读取插件配置（来自 `config.toml`，需要在 `plugin.py` 中传入）。

```javascript
const reply = ctx.getConfig("command.reply", "默认回复");
// key 格式：section.key（对应 config.toml 中的 [section] / key = "value"）
```

---

### 日志

#### `ctx.log(message)`

输出普通日志（写入 stderr，前缀为 `[JS:插件名]`）。

```javascript
ctx.log("处理完成");
// 输出：[JS:my_plugin] 处理完成
```

#### `ctx.logError(message)`

输出错误日志（前缀 `[JS:插件名] ERROR:`）。

```javascript
ctx.logError("请求失败：timeout");
// 输出：[JS:my_plugin] ERROR: 请求失败：timeout
```

---

### 其他属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `ctx.stream_id` | string | 当前聊天流 ID |
| `ctx.plugin_name` | string | 插件名称（`_manifest.json` 中的 `name`）|

---

## `execute` 返回值

```javascript
return {
  success: true,     // 必须：是否执行成功
  log: "日志信息",   // 可选：日志描述
};
```

如果执行过程中 JS 抛出未捕获的异常，桥接器会自动返回 `{ success: false, log: 错误信息 }`。

---

## 完整模板

```javascript
// plugin.js 完整模板

// ── 命令示例 ──────────────────────────────────────────────────────────
mai.command({
  name: "my_command",
  description: "命令功能描述",
  pattern: /^\/my_command(?:\s+(.+))?$/,

  async execute(ctx) {
    const arg = ctx.getMatch(1);    // 获取可选参数
    const config = ctx.getConfig("command.reply", "默认回复");

    try {
      if (arg) {
        await ctx.sendText(`你输入了：${arg}`);
      } else {
        await ctx.sendText(config);
      }
      ctx.log("命令执行成功");
      return { success: true, log: "success" };
    } catch (err) {
      ctx.logError(`执行失败：${err.message}`);
      await ctx.sendText("❌ 执行出错，请稍后重试");
      return { success: false, log: err.message };
    }
  }
});


// ── Action 示例 ──────────────────────────────────────────────────────
mai.action({
  name: "my_action",
  description: "行为功能描述，让 LLM 知道何时使用",
  require: [
    "当场景合适时使用",
    "不要频繁触发",
  ],
  parameters: {
    content: "要发送的内容",
    reason: "触发原因",
  },
  types: ["text"],

  async execute(ctx) {
    const content = ctx.getParam("content", "Hello!");

    try {
      await ctx.sendText(content);
      ctx.log("Action 执行成功");
      return { success: true };
    } catch (err) {
      ctx.logError(err.message);
      return { success: false, log: err.message };
    }
  }
});
```

---

## 限制与注意事项

| 项目 | 说明 |
|------|------|
| **执行超时** | 每次调用最多 30 秒，超时强制终止 |
| **模块系统** | 使用 CommonJS（`require`）而非 ES Modules（`import`）|
| **无状态** | 每次调用启动新进程，全局变量不跨调用保留 |
| **标准输入输出** | 不要向 `stdout` 直接打印，结果通过 return 返回；日志用 `ctx.log()` 写到 stderr |
| **Node.js 版本** | 建议 Node.js 18+（内置 `fetch`）；16+ 基础功能可用 |

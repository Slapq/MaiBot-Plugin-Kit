# ⚡ JS 插件快速开始

**JS 桥接插件**允许你用 JavaScript 编写插件逻辑，适合前端开发者或不熟悉 Python 的用户。

## 工作原理

```
用户消息 → MaiBot → Python 层（plugin.py）→ Node.js 子进程（plugin.js）→ 执行 JS 逻辑
                                          ↑
                                   mai_js_bridge 桥接器
```

- **Python 层** (`plugin.py`)：加载 JS 文件，动态生成对应的 MaiBot 组件类
- **JS 层** (`plugin.js`)：用 `mai.command()` / `mai.action()` 注册逻辑，通过 `ctx` 对象与 MaiBot 交互

## 前置条件

- **Node.js 16+**（必须安装）
- Python 3.10+
- MaiBot Plugin Kit

```bash
# 检查 Node.js
node --version
# 如果未安装，去 https://nodejs.org/ 下载
```

---

## 第一步：创建 JS 桥接插件

```bash
mai create my_js_plugin -t js_bridge -y
```

生成的目录结构：
```
my_js_plugin/
├── _manifest.json   ← 插件描述
├── plugin.py        ← Python 加载器（通常不需要修改）
└── plugin.js        ← 在这里写你的插件逻辑！
```

---

## 第二步：编写 plugin.js

打开 `my_js_plugin/plugin.js`，这里是你真正需要编写的文件：

```javascript
// plugin.js - 你的插件逻辑

// 注册一个命令：/ping
mai.command({
  name: "ping",
  description: "测试插件是否正常工作",
  pattern: /^\/ping$/,    // 正则匹配用户输入

  async execute(ctx) {
    await ctx.sendText("Pong! 🏓 JS 插件运行正常！");
    ctx.log("ping 命令执行成功");
    return { success: true, log: "pong!" };
  }
});

// 注册一个命令：/roll [数字]（随机骰子）
mai.command({
  name: "roll_dice",
  description: "掷骰子",
  pattern: /^\/roll(?:\s+(\d+))?$/,  // 可选参数

  async execute(ctx) {
    const maxVal = parseInt(ctx.getMatch(1)) || 6;  // 获取第1个捕获组
    const result = Math.floor(Math.random() * maxVal) + 1;
    await ctx.sendText(`🎲 你掷出了 ${result}（1-${maxVal}）`);
    return { success: true };
  }
});

// 注册一个 Action：麦麦在合适时机自主触发
mai.action({
  name: "send_motivation",
  description: "发送励志消息",
  require: [
    "当有人表达沮丧或失落时",
    "当聊天气氛低落需要鼓励时"
  ],
  parameters: {
    reason: "触发原因",
    name: "对方的名字（可选）"
  },
  types: ["text"],

  async execute(ctx) {
    const name = ctx.getParam("name") || "朋友";
    const messages = [
      `加油 ${name}！困难只是暂时的 💪`,
      `${name}，你已经做得很好了！继续加油！✨`,
      `相信自己，${name}！每一步都算数！🌟`
    ];
    const msg = messages[Math.floor(Math.random() * messages.length)];
    await ctx.sendText(msg);
    return { success: true };
  }
});
```

---

## 第三步：验证并部署

```bash
# 验证插件
mai validate ./my_js_plugin

# 部署到 MaiBot
cp -r my_js_plugin/ ../MaiBot/plugins/
# 重启 MaiBot
```

---

## plugin.js API 参考

所有逻辑写在 `mai.command()` 或 `mai.action()` 的 `execute(ctx)` 函数中。

### `ctx` 上下文对象

#### 发送消息

```javascript
// 发送文本
await ctx.sendText("你好！");

// 发送图片（base64 编码，不含头部）
await ctx.sendImage("iVBORw0KGgo...");

// 发送表情包（base64 编码）
await ctx.sendEmoji("iVBORw0KGgo...");
```

#### 获取参数

```javascript
// Action 参数（LLM 生成的参数）
const city = ctx.getParam("city");        // 获取指定参数
const city = ctx.getParam("city", "北京"); // 带默认值

// Command 正则捕获组
const group1 = ctx.getMatch(1);   // 第 1 个括号里的内容
const group2 = ctx.getMatch(2);   // 第 2 个括号里的内容
```

#### 读取配置

```javascript
// 读取 config.toml 中的配置项
const msg = ctx.getConfig("command.reply", "默认回复");
// 支持点号路径，如 "section.key"
```

#### 日志输出

```javascript
ctx.log("普通日志");       // 输出到 stderr
ctx.logError("错误信息");  // 输出到 stderr（标记 ERROR）
```

#### 其他属性

```javascript
ctx.stream_id    // 当前聊天流 ID
ctx.plugin_name  // 插件名称
```

### `execute` 返回值

```javascript
return {
  success: true,    // 是否执行成功
  log: "描述信息",   // 可选，日志描述
};
```

---

## 完整示例：天气查询

```javascript
// weather.js - 天气查询 JS 插件

mai.command({
  name: "weather_query",
  description: "查询天气信息",
  pattern: /^\/weather\s+(\S+)$/,  // /weather 城市名

  async execute(ctx) {
    const city = ctx.getMatch(1);
    if (!city) {
      await ctx.sendText("用法：/weather 城市名");
      return { success: false };
    }

    try {
      // 动态导入 fetch（Node.js 18+ 内置）
      const url = `https://wttr.in/${encodeURIComponent(city)}?format=3&lang=zh`;
      const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
      const text = await res.text();
      await ctx.sendText(`🌤️ ${text.trim()}`);
      ctx.log(`查询 ${city} 天气成功`);
      return { success: true };
    } catch (err) {
      await ctx.sendText(`❌ 查询失败：${err.message}`);
      ctx.logError(`天气查询失败：${err.message}`);
      return { success: false, log: err.message };
    }
  }
});
```

---

## 注意事项

1. **Node.js 必须安装** 且在 PATH 中可访问（命令行 `node --version` 有输出）
2. **每次调用都启动新进程**：JS 插件不维持状态，避免用全局变量存储持久数据
3. **30 秒超时**：如果 JS 执行超过 30 秒会被强制终止
4. **`require()` 可用**：可以使用 Node.js 内置模块（`path`、`fs` 等）
5. **不支持 ES Modules**：使用 CommonJS 语法（`require` 而非 `import`）

---

## 下一步

- 📖 [JS API 完整参考](/js/api)
- 🐍 [切换到 Python 插件](/guide/quickstart)（功能更完整）

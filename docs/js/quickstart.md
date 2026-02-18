# ⚡ JavaScript 插件快速开始

JS Bridge 允许你用 **JavaScript** 编写麦麦插件，无需深入学习 Python 异步编程。

## 前置要求

- Node.js 14+（用于运行 JS 代码）
- Python 3.9+（用于 MaiBot 运行环境）

检查 Node.js 是否已安装：
```bash
node --version
```

## 创建 JS 插件

```bash
python -m mai_plugin_cli create my_js_plugin -t js_bridge
```

目录结构：
```
my_js_plugin/
├── _manifest.json   插件元数据
├── plugin.py        Python 桥接层（不需要修改）
├── plugin.js        ⭐ 你的插件逻辑（主要编辑这里）
└── README.md        说明文档
```

## 编辑 plugin.js

打开 `plugin.js`，使用 `mai` 全局对象注册你的插件：

### 注册命令（Command）

```javascript
// 响应 /ping 命令
mai.command({
  name: "my_ping",
  description: "测试插件",
  pattern: /^\/ping$/,

  async execute(ctx) {
    await ctx.sendText("🏓 Pong！插件运行正常！");
    return { success: true, log: "ping 成功" };
  }
});
```

### 注册带参数的命令

```javascript
// 响应 /say 内容
mai.command({
  name: "my_say",
  description: "让麦麦说话",
  pattern: /^\/say\s+(.+)$/,  // (.+) 捕获参数

  async execute(ctx) {
    const content = ctx.getMatch(1);  // 获取第一个捕获组
    if (!content) {
      await ctx.sendText("❌ 用法：/say 你想让我说的话");
      return { success: false };
    }
    await ctx.sendText(content);
    return { success: true };
  }
});
```

### 注册 Action（麦麦自主行为）

```javascript
mai.action({
  name: "my_greet",
  description: "在合适的时机打招呼",
  
  require: [
    "当有新人加入时",
    "当有人主动打招呼时",
  ],
  
  parameters: {
    "user_name": "要打招呼的用户名字",
  },
  
  types: ["text"],

  async execute(ctx) {
    const name = ctx.getParam("user_name", "朋友");
    await ctx.sendText(`你好，${name}！欢迎！😊`);
    return { success: true, log: `向 ${name} 打招呼` };
  }
});
```

## 可用 API

所有 API 通过 `ctx` 对象访问：

```javascript
// 发送消息
await ctx.sendText("文本消息");
await ctx.sendImage("base64字符串");
await ctx.sendEmoji("base64字符串");

// 获取参数（Action 专用）
const value = ctx.getParam("param_name", "默认值");

// 获取正则捕获（Command 专用）
const match1 = ctx.getMatch(1);  // 第一个捕获组
const match2 = ctx.getMatch(2);  // 第二个捕获组

// 获取配置
const msg = ctx.getConfig("section.key", "默认值");

// 输出日志
ctx.log("这条日志会显示在控制台");
ctx.logError("这是错误日志");
```

## 注意事项

::: warning JS 插件的限制
- JS 插件运行在 Node.js 子进程中，**无法直接访问** MaiBot 内部的数据库和配置
- 如果需要 HTTP 请求，可以使用 Node.js 内置的 `fetch`（Node.js 18+）或 `require('https')`
- 每次执行会启动新的 Node.js 进程，性能比 Python 插件略低
:::

::: tip 推荐使用场景
- 简单的命令响应（/help /ping 等）
- 前端开发者熟悉的 JavaScript 场景
- 快速原型开发
:::

## 完整示例

```javascript
/**
 * 小工具插件 - JavaScript 版本
 */

// 帮助命令
mai.command({
  name: "tools_help",
  description: "显示帮助信息",
  pattern: /^\/tools$/,

  async execute(ctx) {
    await ctx.sendText(
      "🛠️ 小工具插件\n" +
      "/tools      - 显示此帮助\n" +
      "/roll       - 掷骰子\n" +
      "/flip       - 抛硬币\n" +
      "/pick A B C - 随机选择"
    );
    return { success: true };
  }
});

// 掷骰子
mai.command({
  name: "tools_roll",
  description: "掷一个骰子",
  pattern: /^\/roll$/,

  async execute(ctx) {
    const result = Math.ceil(Math.random() * 6);
    const emoji = ["", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"][result];
    await ctx.sendText(`🎲 掷出了 ${emoji} ${result} 点！`);
    return { success: true };
  }
});

// 抛硬币
mai.command({
  name: "tools_flip",
  description: "抛一枚硬币",
  pattern: /^\/flip$/,

  async execute(ctx) {
    const result = Math.random() < 0.5 ? "正面 🪙" : "反面 🔄";
    await ctx.sendText(`硬币结果：${result}`);
    return { success: true };
  }
});

// 随机选择
mai.command({
  name: "tools_pick",
  description: "从选项中随机选一个",
  pattern: /^\/pick\s+(.+)$/,

  async execute(ctx) {
    const input = ctx.getMatch(1);
    if (!input) {
      await ctx.sendText("❌ 用法：/pick 选项1 选项2 选项3");
      return { success: false };
    }
    const options = input.trim().split(/\s+/);
    if (options.length < 2) {
      await ctx.sendText("❌ 请至少提供 2 个选项");
      return { success: false };
    }
    const chosen = options[Math.floor(Math.random() * options.length)];
    await ctx.sendText(`🎯 我选择：${chosen}`);
    return { success: true };
  }
});
```

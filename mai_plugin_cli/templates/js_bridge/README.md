# {{PLUGIN_DISPLAY_NAME}} - JS Bridge 插件

{{PLUGIN_DESCRIPTION}}

## 作者

{{PLUGIN_AUTHOR}}

## 版本

{{PLUGIN_VERSION}}

## 简介

这是一个 **JavaScript 桥接插件**，你只需要编辑 `plugin.js` 文件即可实现插件功能，无需深入了解 Python 异步编程。

## 文件说明

```
{{PLUGIN_NAME}}/
├── _manifest.json   插件元数据（必须）
├── plugin.py        Python 桥接层（不需要修改）
├── plugin.js        ⭐ 你的插件逻辑（主要编辑这里）
└── README.md        说明文档
```

## 快速开始

编辑 `plugin.js` 文件，使用 `mai` 对象注册命令和行为：

### 注册命令

```javascript
mai.command({
  name: "my_command",
  description: "命令描述",
  pattern: /^\/mycommand$/,       // 匹配用户输入

  async execute(ctx) {
    await ctx.sendText("命令执行成功！");
    return { success: true };
  }
});
```

### 注册 Action（麦麦自主行为）

```javascript
mai.action({
  name: "my_action",
  description: "行为描述",
  require: ["触发条件1", "触发条件2"],
  parameters: { "param1": "参数说明" },
  types: ["text"],

  async execute(ctx) {
    const value = ctx.getParam("param1", "默认值");
    await ctx.sendText(`执行了：${value}`);
    return { success: true };
  }
});
```

## 可用 API

| 方法 | 说明 |
|------|------|
| `ctx.sendText(text)` | 发送文本消息 |
| `ctx.sendImage(base64)` | 发送图片（base64编码） |
| `ctx.sendEmoji(base64)` | 发送表情包 |
| `ctx.getConfig(key, default)` | 读取配置文件中的值 |
| `ctx.log(msg)` | 输出日志 |
| `ctx.getParam(key, default)` | 获取 LLM 传入的 Action 参数 |
| `ctx.getMatch(group)` | 获取正则捕获组（Command 专用） |

## 安装

1. 将整个 `{{PLUGIN_NAME}}/` 目录复制到 MaiBot 的 `plugins/` 目录
2. 确保 `mai_js_bridge` 模块可被访问（包含在 MaiBot-Plugin-Kit 中）
3. 重启 MaiBot

## 参考文档

- [JS Bridge 完整文档](https://maibot-plugin-kit.pages.dev/js/)
- [MaiBot 官方文档](https://docs.mai-mai.org/)

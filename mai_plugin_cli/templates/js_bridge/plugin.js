/**
 * {{PLUGIN_DISPLAY_NAME}} - JavaScript 插件
 *
 * 在这里用 JavaScript 编写你的插件逻辑！
 * 通过 mai 对象访问 MaiBot 的 API。
 *
 * 作者：{{PLUGIN_AUTHOR}}
 * 版本：{{PLUGIN_VERSION}}
 *
 * 可用 API：
 *   ctx.sendText(text)           发送文本消息
 *   ctx.sendImage(base64)        发送图片（base64 编码）
 *   ctx.sendEmoji(base64)        发送表情包
 *   ctx.getConfig(key, default)  读取配置值（key 支持 "section.key" 格式）
 *   ctx.log(message)             输出调试日志（写入 stderr，不影响输出）
 *   ctx.logError(message)        输出错误日志
 *   ctx.getParam(key, default)   获取 LLM 传入的参数（Action 专用）
 *   ctx.getMatch(group)          获取正则捕获组（Command 专用，从 1 开始）
 */

// ============================================================
// 注册一个 Command（响应固定命令）
// ============================================================

mai.command({
  name: "{{PLUGIN_NAME}}_ping",                     // 命令唯一名称
  description: "测试插件是否正常运行",                // 描述
  pattern: /^\/{{PLUGIN_NAME}}$/,                   // 匹配的正则

  async execute(ctx) {
    ctx.log("收到 {{PLUGIN_NAME}} 命令！");
    await ctx.sendText("🏓 Pong！{{PLUGIN_DISPLAY_NAME}} 正在运行！");
    return { success: true, log: "ping 成功" };
  }
});


// ============================================================
// 注册一个带参数的 Command
// ============================================================

mai.command({
  name: "{{PLUGIN_NAME}}_echo",
  description: "重复用户说的话",
  pattern: /^\/echo\s+(.+)$/,                       // 捕获参数

  async execute(ctx) {
    const text = ctx.getMatch(1);                    // 获取捕获组 1
    if (!text) {
      await ctx.sendText("❌ 用法：/echo 要重复的内容");
      return { success: false };
    }
    await ctx.sendText(`你说：${text}`);
    return { success: true, log: `echo: ${text}` };
  }
});


// ============================================================
// 注册一个 Action（麦麦自主触发）
// ============================================================

mai.action({
  name: "{{PLUGIN_NAME}}_greet",
  description: "当有人打招呼时发送问候",
  
  // LLM 触发条件（越具体越好）
  require: [
    "当有人向你问好时",
    "当对话开始时",
    "遇到新朋友时",
  ],

  // LLM 会提取并传入的参数
  parameters: {
    "user_name": "要问候的用户名字（如果知道的话）",
    "reason":    "触发此动作的原因",
  },

  // 关联的消息类型
  types: ["text"],

  async execute(ctx) {
    const userName = ctx.getParam("user_name", "朋友");
    ctx.log(`向 ${userName} 打招呼`);
    await ctx.sendText(`你好呀，${userName}！很高兴认识你！😊`);
    return { success: true, log: `问候了 ${userName}` };
  }
});


// ============================================================
// 自定义：你的功能区域
// ============================================================

// 在这里添加更多 command 和 action！
// 
// 示例：HTTP 请求
//
// mai.command({
//   name: "weather",
//   description: "查询天气",
//   pattern: /^\/weather\s+(.+)$/,
//   async execute(ctx) {
//     const city = ctx.getMatch(1);
//     // 注意：JS 插件中暂不支持直接发起 HTTP 请求
//     // 需要通过 ctx.callPython("fetch_weather", {city}) 调用 Python 函数
//     await ctx.sendText(`正在查询 ${city} 的天气...`);
//     return { success: true };
//   }
// });

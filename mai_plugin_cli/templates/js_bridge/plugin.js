/**
 * {{PLUGIN_DISPLAY_NAME}} - JavaScript 插件
 *
 * 在这里用 JavaScript 编写你的插件逻辑！
 * 通过 mai 对象注册命令和行为，用 ctx 对象与麦麦交互。
 *
 * 作者：{{PLUGIN_AUTHOR}}
 * 版本：{{PLUGIN_VERSION}}
 */


// ============================================================
// 🚀 极简写法：固定文本回复（一行搞定）
// ============================================================

mai.reply('/{{PLUGIN_NAME}}', '🏓 Pong！{{PLUGIN_DISPLAY_NAME}} 正在运行！');


// ============================================================
// ⚡ 命令（Command）：响应用户输入
// ============================================================

// 写法 A：简洁箭头函数（推荐）
mai.command(/^\/echo\s+(.+)$/, async (ctx) => {
  const text = ctx.match(1);          // 获取第 1 个正则捕获组
  await ctx.send(`你说：${text}`);
});

// 写法 B：带元数据的完整配置
mai.command({
  name: '{{PLUGIN_NAME}}_roll',
  description: '掷骰子',
  pattern: /^\/roll(?:\s+(\d+))?$/,  // /roll 或 /roll 20

  execute: async (ctx) => {
    const max = parseInt(ctx.match(1), 10) || 6;
    const result = Math.floor(Math.random() * max) + 1;
    await ctx.send(`🎲 你掷出了 ${result}（1-${max}）`);
    return { success: true };
  },
});


// ============================================================
// 🤖 行为（Action）：麦麦自主触发
// ============================================================

mai.action({
  name: '{{PLUGIN_NAME}}_greet',
  description: '当有人打招呼时发送问候',

  // 告诉 LLM 什么情况下触发这个行为
  require: [
    '当有人向你问好时',
    '当对话开始时',
  ],

  // LLM 会提取并传入的参数（可选）
  parameters: {
    user_name: '要问候的用户名字',
  },

  types: ['text'],

  execute: async (ctx) => {
    const name = ctx.param('user_name', '朋友');  // ctx.param() 获取 LLM 参数
    await ctx.send(`你好呀，${name}！😊`);
    return { success: true };
  },
});


// ============================================================
// 💡 更多示例（取消注释即可使用）
// ============================================================

// 查询天气（需要 Node.js 18+ 内置 fetch）
//
// mai.command(/^\/weather\s+(\S+)$/, async (ctx) => {
//   const city = ctx.match(1);
//   try {
//     const res  = await fetch(`https://wttr.in/${city}?format=3`);
//     const text = await res.text();
//     await ctx.send(`🌤️ ${text.trim()}`);
//   } catch (err) {
//     await ctx.send(`❌ 查询失败：${err.message}`);
//   }
// });

// 读取配置文件的值
//
// mai.command(/^\/config$/, async (ctx) => {
//   const val = ctx.config('section.key', '默认值');
//   await ctx.send(`当前配置：${val}`);
// });

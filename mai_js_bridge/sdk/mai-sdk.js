/**
 * mai-sdk.js - MaiBot JS 插件 SDK（Node.js 运行时）
 *
 * 在 Node.js 子进程中运行，负责：
 * 1. 提供 mai 全局对象（注册器）
 * 2. 存储 command/action 定义
 * 3. 执行指定组件的 execute 函数
 * 4. 通过 stdout 返回消息队列给 Python
 *
 * 支持两种注册风格：
 *
 *   // 简洁风格（推荐新手）
 *   mai.reply('/ping', 'Pong! 🏓');
 *   mai.command(/^\/roll\s*(\d+)?$/, async (ctx) => {
 *     const max = parseInt(ctx.match(1)) || 6;
 *     await ctx.send(`🎲 ${Math.floor(Math.random() * max) + 1}`);
 *   });
 *
 *   // 完整配置风格（推荐进阶用户）
 *   mai.command({
 *     name: 'ping',
 *     pattern: /^\/ping$/,
 *     execute: async (ctx) => {
 *       await ctx.sendText('Pong!');
 *       return { success: true };
 *     }
 *   });
 */

'use strict';

// ─── 辅助工具 ────────────────────────────────────────────────────────────────

let _idCounter = 0;
function uid() { return `auto_${++_idCounter}`; }

/** 将 string/RegExp/pattern 标准化为可存储的格式 */
function normalizePattern(p) {
  if (!p) return null;
  if (p instanceof RegExp) return p;
  if (typeof p === 'string') {
    // 如果以 ^ 或 / 开头，当作正则字符串处理
    if (p.startsWith('/') || p.startsWith('^')) {
      return new RegExp(p);
    }
    // 否则当作固定命令前缀，自动加 ^ 和 $
    const escaped = p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return new RegExp(`^${escaped}$`);
  }
  return null;
}


// ─── 注册器 ──────────────────────────────────────────────────────────────────

function createRegistrar() {
  const commands = new Map();
  const actions  = new Map();

  const mai = {

    // ── mai.command() ──────────────────────────────────────────────────────
    //
    //  用法 1：mai.command(pattern, handler)
    //    pattern  - 字符串 / 正则，用于匹配用户输入
    //    handler  - async (ctx) => { ... }
    //
    //  用法 2：mai.command(config)
    //    config   - { name?, description?, pattern?, execute }
    //
    command(patternOrConfig, handler) {
      let cfg;

      if (typeof patternOrConfig === 'function') {
        // mai.command(handler) - 无 pattern，匹配所有
        cfg = { execute: patternOrConfig };
      } else if (typeof patternOrConfig === 'string' || patternOrConfig instanceof RegExp) {
        // mai.command(pattern, handler)
        if (typeof handler !== 'function') throw new TypeError('mai.command(pattern, handler) 的第二个参数必须是函数');
        cfg = { pattern: patternOrConfig, execute: handler };
      } else if (patternOrConfig && typeof patternOrConfig === 'object') {
        // mai.command({ name, description, pattern, execute })
        cfg = patternOrConfig;
      } else {
        throw new TypeError('mai.command() 参数错误');
      }

      if (typeof cfg.execute !== 'function') throw new TypeError(`命令 ${cfg.name || '?'} 必须有 execute 函数`);
      cfg.name = cfg.name || uid();
      cfg.pattern = normalizePattern(cfg.pattern);
      commands.set(cfg.name, cfg);
    },

    // ── mai.reply() ────────────────────────────────────────────────────────
    //
    //  最简 API：固定文本回复
    //    mai.reply('/ping', 'Pong! 🏓');
    //    mai.reply(/^\/version$/, '当前版本：1.0.0');
    //
    reply(pattern, text, name) {
      if (typeof text !== 'string') throw new TypeError('mai.reply() 第二个参数必须是字符串');
      this.command({
        name: name || uid(),
        pattern: normalizePattern(pattern),
        execute: async (ctx) => {
          await ctx.sendText(text);
          return { success: true };
        },
      });
    },

    // ── mai.action() ──────────────────────────────────────────────────────
    //
    //  用法 1：mai.action(handler)
    //  用法 2：mai.action(config)
    //    config   - { name?, description?, require?, parameters?, types?, execute }
    //
    action(configOrHandler) {
      let cfg;

      if (typeof configOrHandler === 'function') {
        cfg = { execute: configOrHandler };
      } else if (configOrHandler && typeof configOrHandler === 'object') {
        cfg = configOrHandler;
      } else {
        throw new TypeError('mai.action() 参数错误');
      }

      if (typeof cfg.execute !== 'function') throw new TypeError(`action ${cfg.name || '?'} 必须有 execute 函数`);
      cfg.name = cfg.name || uid();
      actions.set(cfg.name, cfg);
    },
  };

  return { mai, commands, actions };
}


// ─── 执行上下文 ctx ───────────────────────────────────────────────────────────

function createContext(contextData) {
  const msgs = [];
  const { stream_id, plugin_name, action_data = {}, matched_groups = [] } = contextData;

  const ctx = {
    stream_id,
    plugin_name,

    // ── 发送消息 ──────────────────────────────────────────────────────────

    /** 发送文本消息 */
    async sendText(text) {
      if (text != null) msgs.push({ type: 'text', content: String(text) });
    },

    /** sendText 的简写别名 */
    async send(text) {
      return this.sendText(text);
    },

    /** 发送图片（base64 编码，不含 data:image/...;base64, 前缀）*/
    async sendImage(base64) {
      if (base64) msgs.push({ type: 'image', content: String(base64) });
    },

    /** 发送表情包（base64 编码）*/
    async sendEmoji(base64) {
      if (base64) msgs.push({ type: 'emoji', content: String(base64) });
    },

    // ── 读取参数 ──────────────────────────────────────────────────────────

    /**
     * 获取 Command 正则的捕获组内容（从 1 开始编号）
     *   ctx.match(1)  // 第 1 个括号捕获的内容
     */
    match(group) {
      const idx = parseInt(group, 10) - 1;
      return (idx >= 0 && idx < matched_groups.length) ? (matched_groups[idx] || null) : null;
    },

    /**
     * getMatch(group) - match() 的完整名称别名，兼容旧代码
     */
    getMatch(group) { return this.match(group); },

    /**
     * 获取 Action 的 LLM 参数
     *   ctx.param('city')         // 无默认值，未传则 null
     *   ctx.param('city', '北京') // 有默认值
     */
    param(key, defaultValue = null) {
      return Object.prototype.hasOwnProperty.call(action_data, key)
        ? action_data[key]
        : defaultValue;
    },

    /** getParam() - param() 的完整名称别名 */
    getParam(key, defaultValue = null) { return this.param(key, defaultValue); },

    /**
     * 读取插件配置值
     *   ctx.config('section.key', '默认值')
     */
    config(key, defaultValue = null) {
      const cfg = contextData.config || {};
      const parts = String(key).split('.');
      let val = cfg;
      for (const part of parts) {
        if (val && typeof val === 'object' && Object.prototype.hasOwnProperty.call(val, part)) {
          val = val[part];
        } else {
          return defaultValue;
        }
      }
      return val !== undefined ? val : defaultValue;
    },

    /** getConfig() - config() 的完整名称别名 */
    getConfig(key, defaultValue = null) { return this.config(key, defaultValue); },

    // ── 日志 ──────────────────────────────────────────────────────────────

    /** 输出普通日志到 stderr */
    log(...args) {
      process.stderr.write(`[JS:${plugin_name}] ${args.join(' ')}\n`);
    },

    /** 输出错误日志到 stderr */
    logError(...args) {
      process.stderr.write(`[JS:${plugin_name}] ERROR: ${args.join(' ')}\n`);
    },

    // ── 内部 ──────────────────────────────────────────────────────────────
    _getMessages() { return msgs; },
  };

  return ctx;
}


// ─── 组件执行 ─────────────────────────────────────────────────────────────────

async function executeComponent(registrations, componentName, contextData) {
  const { commands, actions } = registrations;
  const component = commands.get(componentName) || actions.get(componentName);

  if (!component) {
    return { success: false, log: `未找到组件：${componentName}`, messages: [] };
  }

  const ctx = createContext(contextData);

  try {
    const result = await component.execute(ctx);
    return {
      success: result?.success !== false,
      log:     result?.log || '',
      messages: ctx._getMessages(),
    };
  } catch (err) {
    ctx.logError(`执行失败：${err.message || err}`);
    return {
      success:  false,
      log:      String(err),
      messages: ctx._getMessages(),
    };
  }
}


module.exports = { createRegistrar, createContext, executeComponent };

/**
 * mai-sdk.js - MaiBot JS 插件 SDK（Node.js 运行时）
 *
 * 在 Node.js 子进程中运行，负责：
 * 1. 提供 mai 全局对象（注册器）
 * 2. 存储 command/action 定义
 * 3. 执行指定组件的 execute 方法
 * 4. 通过 stdout 返回消息队列给 Python
 */

'use strict';

/**
 * 创建注册器 - 返回带有 mai 全局对象的注册系统
 */
function createRegistrar() {
  const commands = new Map();
  const actions = new Map();

  const mai = {
    /**
     * 注册命令
     * @param {Object} config - 命令配置
     * @param {string} config.name - 命令唯一名称
     * @param {string} config.description - 命令描述
     * @param {RegExp} config.pattern - 匹配正则
     * @param {Function} config.execute - 执行函数 async (ctx) => {success, log}
     */
    command(config) {
      if (!config.name) throw new Error('command 必须有 name 字段');
      if (typeof config.execute !== 'function') throw new Error(`command ${config.name} 必须有 execute 函数`);
      commands.set(config.name, config);
    },

    /**
     * 注册 Action
     * @param {Object} config - Action 配置
     * @param {string} config.name - Action 唯一名称
     * @param {string} config.description - Action 描述
     * @param {string[]} config.require - 触发条件
     * @param {Object} config.parameters - 参数定义
     * @param {string[]} config.types - 关联消息类型
     * @param {Function} config.execute - 执行函数 async (ctx) => {success, log}
     */
    action(config) {
      if (!config.name) throw new Error('action 必须有 name 字段');
      if (typeof config.execute !== 'function') throw new Error(`action ${config.name} 必须有 execute 函数`);
      actions.set(config.name, config);
    },
  };

  return { mai, commands, actions };
}


/**
 * 创建执行上下文（ctx 对象）
 * @param {Object} contextData - Python 传入的上下文数据
 */
function createContext(contextData) {
  const messages = [];  // 收集要发送的消息
  const { stream_id, plugin_name, action_data = {}, matched_groups = [] } = contextData;

  const ctx = {
    stream_id,
    plugin_name,

    /**
     * 发送文本消息
     */
    async sendText(text) {
      if (text) {
        messages.push({ type: 'text', content: String(text) });
      }
    },

    /**
     * 发送图片（base64 编码）
     */
    async sendImage(base64) {
      if (base64) {
        messages.push({ type: 'image', content: String(base64) });
      }
    },

    /**
     * 发送表情包（base64 编码）
     */
    async sendEmoji(base64) {
      if (base64) {
        messages.push({ type: 'emoji', content: String(base64) });
      }
    },

    /**
     * 获取 Action 参数（LLM 传入）
     */
    getParam(key, defaultValue = null) {
      return key in action_data ? action_data[key] : defaultValue;
    },

    /**
     * 获取 Command 正则捕获组
     * @param {number} group - 捕获组序号（从 1 开始）
     */
    getMatch(group) {
      const idx = parseInt(group) - 1;
      if (idx < 0 || idx >= matched_groups.length) return null;
      return matched_groups[idx] || null;
    },

    /**
     * 获取配置值（需要 Python 侧提前传入）
     */
    getConfig(key, defaultValue = null) {
      const config = contextData.config || {};
      // 支持点号分隔的路径，如 "section.key"
      const parts = key.split('.');
      let val = config;
      for (const part of parts) {
        if (val && typeof val === 'object' && part in val) {
          val = val[part];
        } else {
          return defaultValue;
        }
      }
      return val !== undefined ? val : defaultValue;
    },

    /**
     * 输出日志
     */
    log(message) {
      process.stderr.write(`[JS:${plugin_name}] ${message}\n`);
    },

    /**
     * 输出错误日志
     */
    logError(message) {
      process.stderr.write(`[JS:${plugin_name}] ERROR: ${message}\n`);
    },

    // 内部：获取已收集的消息列表
    _getMessages() {
      return messages;
    },
  };

  return ctx;
}


/**
 * 执行指定组件
 * @param {Object} registrations - createRegistrar() 的返回值
 * @param {string} componentName - 组件名称
 * @param {Object} contextData - Python 传入的上下文数据
 */
async function executeComponent(registrations, componentName, contextData) {
  const { commands, actions } = registrations;

  // 查找组件
  let component = commands.get(componentName) || actions.get(componentName);
  if (!component) {
    return {
      success: false,
      log: `未找到组件：${componentName}`,
      messages: [],
    };
  }

  const ctx = createContext(contextData);

  try {
    const result = await component.execute(ctx);
    const messages = ctx._getMessages();

    return {
      success: result?.success !== false,
      log: result?.log || '',
      messages,
    };
  } catch (err) {
    ctx.logError(`执行失败：${err.message || err}`);
    return {
      success: false,
      log: String(err),
      messages: ctx._getMessages(),
    };
  }
}


module.exports = {
  createRegistrar,
  createContext,
  executeComponent,
};

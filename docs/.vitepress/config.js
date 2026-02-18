import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'MaiBot Plugin Kit',
  description: '麦麦插件开发工具包 - 完整文档',
  lang: 'zh-CN',
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '快速开始', link: '/guide/quickstart' },
      { text: 'API 参考', link: '/api/send_api' },
      { text: 'MaiScript', link: '/maiscript/intro' },
      { text: 'JS 插件', link: '/js/quickstart' },
    ],
    sidebar: [
      {
        text: '📖 指南',
        items: [
          { text: '快速开始', link: '/guide/quickstart' },
          { text: '插件架构详解', link: '/guide/architecture' },
          { text: '发布插件', link: '/guide/publish' },
        ],
      },
      {
        text: '📡 API 参考',
        items: [
          { text: '📤 发送消息', link: '/api/send_api' },
          { text: '📨 消息 API', link: '/api/message_api' },
          { text: '🤖 LLM API', link: '/api/llm_api' },
          { text: '✨ 回复生成器 API', link: '/api/generator_api' },
          { text: '💬 聊天流 API', link: '/api/chat_api' },
          { text: '👤 个人信息 API', link: '/api/person_api' },
          { text: '😊 表情包 API', link: '/api/emoji_api' },
          { text: '⚙️ 配置 API', link: '/api/config_api' },
          { text: '🔧 Tool 组件 API', link: '/api/tool_api' },
          { text: '🗄️ 数据库 API', link: '/api/database_api' },
          { text: '📜 日志 API', link: '/api/logging_api' },
          { text: '🧩 组件管理 API', link: '/api/component_manage_api' },
          { text: '🔌 插件管理 API', link: '/api/plugin_manage_api' },
        ],
      },
      {
        text: '🚀 进阶功能',
        items: [
          { text: '进阶开发指南', link: '/advanced/guide' },
          { text: 'ReplyBuilder', link: '/advanced/reply-builder' },
          { text: 'PromptModifier', link: '/advanced/prompt-modifier' },
          { text: 'ReplyComponent', link: '/advanced/reply-component' },
        ],
      },
      {
        text: '✨ MaiScript（零代码）',
        items: [
          { text: '介绍', link: '/maiscript/intro' },
          { text: '语法参考', link: '/maiscript/syntax' },
          { text: '示例', link: '/maiscript/examples' },
        ],
      },
      {
        text: '🌐 JS 插件',
        items: [
          { text: '快速开始', link: '/js/quickstart' },
          { text: 'JS API 参考', link: '/js/api' },
        ],
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Slapq/MaiBot-Plugin-Kit' },
    ],
    search: { provider: 'local' },
    editLink: {
      pattern: 'https://github.com/Slapq/MaiBot-Plugin-Kit/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页',
    },
    footer: {
      message: '基于 MIT 协议发布',
      copyright: 'Copyright © 2025 MaiBot-Plugin-Kit',
    },
  },
})

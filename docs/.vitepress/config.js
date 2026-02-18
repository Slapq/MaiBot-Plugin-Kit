import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'MaiBot Plugin Kit',
  description: '麦麦插件开发工具包 - 完整文档',
  lang: 'zh-CN',
  base: '/MaiBot-Plugin-Kit/',
  
  head: [
    ['meta', { charset: 'utf-8' }],
    ['meta', { name: 'viewport', content: 'width=device-width, initial-scale=1' }],
  ],

  themeConfig: {
    logo: '🤖',
    siteTitle: 'MaiBot Plugin Kit',
    
    nav: [
      { text: '🏠 首页', link: '/' },
      { text: '📖 快速开始', link: '/guide/quickstart' },
      { text: '📚 API 文档', link: '/api/send_api' },
      { text: '⚡ JS 插件', link: '/js/quickstart' },
      { text: '✨ MaiScript', link: '/maiscript/intro' },
      { text: '🚀 高级功能', link: '/advanced/guide' },
      {
        text: '🔗 外部链接',
        items: [
          { text: 'MaiBot 官方文档', link: 'https://docs.mai-mai.org/' },
          { text: 'GitHub', link: 'https://github.com/Mai-with-u/MaiBot' },
          { text: '插件仓库', link: 'https://github.com/Mai-with-u/plugin-repo' },
        ]
      }
    ],

    sidebar: {
      '/guide/': [
        {
          text: '快速开始',
          items: [
            { text: '🚀 安装与入门', link: '/guide/quickstart' },
            { text: '🏗️ 插件架构', link: '/guide/architecture' },
            { text: '📦 发布插件', link: '/guide/publish' },
          ]
        }
      ],
      '/api/': [
        {
          text: '消息发送',
          items: [
            { text: '📤 发送 API', link: '/api/send_api' },
            { text: '💬 消息 API', link: '/api/message_api' },
          ]
        },
        {
          text: 'AI 生成',
          items: [
            { text: '✨ 回复生成器 API', link: '/api/generator_api' },
            { text: '🤖 LLM API', link: '/api/llm_api' },
          ]
        },
        {
          text: '数据与关系',
          items: [
            { text: '👤 人物信息 API', link: '/api/person_api' },
            { text: '🗄️ 数据库 API', link: '/api/database_api' },
            { text: '⚙️ 配置 API', link: '/api/config_api' },
          ]
        },
        {
          text: '其他',
          items: [
            { text: '😊 表情包 API', link: '/api/emoji_api' },
            { text: '💬 聊天流 API', link: '/api/chat_api' },
            { text: '📜 日志 API', link: '/api/logging_api' },
          ]
        }
      ],
      '/js/': [
        {
          text: 'JS 插件开发',
          items: [
            { text: '⚡ 快速开始', link: '/js/quickstart' },
            { text: '📖 JS SDK 参考', link: '/js/api' },
          ]
        }
      ],
      '/maiscript/': [
        {
          text: 'MaiScript',
          items: [
            { text: '✨ 介绍', link: '/maiscript/intro' },
            { text: '📝 语法手册', link: '/maiscript/syntax' },
            { text: '💡 示例集合', link: '/maiscript/examples' },
          ]
        }
      ],
      '/advanced/': [
        {
          text: '🚀 高级功能',
          items: [
            { text: '高级功能指南', link: '/advanced/guide' },
          ]
        },
        {
          text: '🔧 mai_advanced 模块',
          items: [
            { text: 'AdvancedReplyBuilder', link: '/advanced/reply-builder' },
            { text: 'PromptModifier', link: '/advanced/prompt-modifier' },
            { text: 'ReplyComponent', link: '/advanced/reply-component' },
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/Mai-with-u/MaiBot' }
    ],

    footer: {
      message: '基于 GPL-3.0 协议发布',
      copyright: 'Copyright © 2025 MaiBot 社区'
    },

    search: {
      provider: 'local'
    }
  }
})

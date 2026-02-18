---
layout: home

hero:
  name: "MaiBot Plugin Kit"
  text: "麦麦插件开发工具包"
  tagline: 让每个人都能轻松为麦麦开发插件——不论你是 Python 大神、JS 爱好者还是编程零基础的小白
  actions:
    - theme: brand
      text: 🚀 快速开始
      link: /guide/quickstart
    - theme: alt
      text: ✨ MaiScript（小白专用）
      link: /maiscript/intro
    - theme: alt
      text: 📚 API 参考
      link: /api/send_api

features:
  - icon: 🛠️
    title: 脚手架工具 (mai CLI)
    details: 一条命令创建插件项目，交互式选择模板，自动生成所有文件结构。支持验证和打包。

  - icon: 🎭
    title: 五种插件模板
    details: minimal / action / command / full / js_bridge，覆盖所有开发场景，注释详尽，开箱即用。

  - icon: ⚡
    title: JavaScript 插件支持
    details: 用 JavaScript 编写插件逻辑！通过 Node.js 桥接器与 MaiBot 交互，适合前端开发者。

  - icon: ✨
    title: MaiScript —— 零代码开发
    details: 专为小白设计的声明式语言。用 YAML 配置命令和行为，自动编译为 Python 插件，无需任何编程经验。

  - icon: 📚
    title: 完整 API 文档
    details: 从 MaiBot 源码中提取的全部 API 参考，中文注释，包含大量代码示例和最佳实践。

  - icon: 🔍
    title: 插件验证工具
    details: 一键检查插件结构、manifest 格式、Python 语法，快速发现并修复问题。
---

## 快速选择你的方式

<div class="card-grid">

### 🐍 Python 开发者
**使用 mai CLI + 模板快速开始**

```bash
# 安装脚手架
pip install mai-plugin-cli  # 或直接使用源码

# 创建插件（选择 action 模板）
python -m mai_plugin_cli create my_plugin -t action

# 验证插件
python -m mai_plugin_cli validate ./my_plugin
```

→ [快速开始指南](/guide/quickstart)

---

### ⚡ JavaScript 开发者
**使用 JS Bridge 模板**

```bash
# 创建 JS 桥接插件
python -m mai_plugin_cli create my_plugin -t js_bridge

# 编辑 plugin.js
```

```javascript
mai.command({
  name: "ping",
  pattern: /^\/ping$/,
  async execute(ctx) {
    await ctx.sendText("Pong! 🏓");
    return { success: true };
  }
});
```

→ [JS 插件文档](/js/quickstart)

---

### ✨ 零编程基础
**使用 MaiScript**

```yaml
# my_plugin.mai
plugin:
  name: "我的插件"
  author: "你的名字"

commands:
  - name: "打招呼"
    match: "/hello"
    reply: "你好呀！😊"

actions:
  - name: "开心回应"
    when:
      - "当有人分享好消息时"
    reply: "太棒了！🎉"
```

```bash
# 一键编译为插件
python -m mai_plugin_cli run-maiscript my_plugin.mai
```

→ [MaiScript 文档](/maiscript/intro)

</div>

# ✨ MaiScript 介绍

**MaiScript** 是 MaiBot Plugin Kit 提供的**零代码插件描述语言**。

你只需要写一个 YAML 文件（`.mai`），描述你的插件想做什么，MaiScript 就会自动编译成完整的 Python 插件目录——无需任何编程基础。

## 为什么需要 MaiScript？

直接写 Python 插件需要：
- 了解类的继承、异步函数、正则表达式
- 知道哪些属性和方法可用
- 处理错误、导入模块等样板代码

MaiScript 让你只关注**你的插件做什么**：

```yaml
# 这就是一个完整的 MaiScript 插件！
plugin:
  name: "每日一言"
  author: "我"
  description: "每天给群友说一句励志名言"

commands:
  - name: "名言"
    match: "/quote"
    reply: "人生是场旅行，不是竞赛！🌟"
```

编译一条命令：
```bash
mai run-maiscript daily_quote.mai
```

就会生成可以直接放进 MaiBot 运行的插件目录！

---

## 安装与使用

MaiScript 随 MaiBot Plugin Kit 内置，无需额外安装。

```bash
# 安装工具包（如未安装）
cd MaiBot-Plugin-Kit
pip install -e .

# 安装 YAML 解析库（MaiScript 必须）
pip install pyyaml
```

### 编译命令

```bash
# 基本用法
mai run-maiscript 你的文件.mai

# 指定输出目录
mai run-maiscript 你的文件.mai -o ./输出目录/

# 直接用 Python 模块
python -m mai_plugin_cli run-maiscript 你的文件.mai
```

---

## 第一个 MaiScript 插件

### 第一步：创建 `.mai` 文件

新建 `hello.mai`：

```yaml
plugin:
  name: "打招呼"
  version: "1.0.0"
  author: "你的名字"
  description: "回应 /hello 命令"

commands:
  - name: "问好"
    match: "/hello"
    reply: "你好！我是麦麦，很高兴认识你 😊"
```

### 第二步：编译

```bash
mai run-maiscript hello.mai
```

输出：
```
✅ 编译成功！插件目录：hello/
   - _manifest.json
   - plugin.py（包含 1 个命令，0 个 Action）
   - README.md

🚀 将 hello/ 目录复制到 MaiBot/plugins/ 目录并重启 MaiBot 即可！
```

### 第三步：查看生成的文件

```
hello/
├── _manifest.json    ← 自动生成的插件描述
├── plugin.py         ← 自动生成的 Python 代码
└── README.md         ← 自动生成的说明文档
```

`plugin.py` 是完整可运行的 Python 代码，你也可以在这个基础上继续修改。

### 第四步：部署到 MaiBot

```bash
cp -r hello/ ../MaiBot/plugins/
# 然后重启 MaiBot
```

---

## MaiScript 能做什么

| 功能 | 说明 |
|------|------|
| **命令**（command） | 响应 `/命令` 这类用户输入 |
| **行为**（action） | 麦麦在合适时机自主触发的行为 |
| **固定回复** | 直接配置回复文本 |
| **Python 代码** | 内嵌 Python 逻辑（用于计算/处理数据） |
| **HTTP 请求** | 调用外部 API（天气/新闻/随机图片等） |
| **LLM 回复** | 用自定义提示词让麦麦生成回复 |
| **配置系统** | 支持 TOML 配置文件 |

---

## 下一步

- � [完整语法参考](/maiscript/syntax)
- 💡 [实用示例](/maiscript/examples)

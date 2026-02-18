# 📖 JS SDK 参考

`mai-sdk.js` 提供了在 JS 插件中与麦麦交互的完整 API。

## 引入 SDK

```javascript
// 在 plugin.js 中（SDK 由桥接器自动注入到沙箱环境）
// 直接使用全局 mai 对象即可
```

## mai 对象 API

### 消息发送

#### `mai.sendText(text)`

发送纯文本消息。

```javascript
await mai.sendText("你好！");
```

#### `mai.sendImage(base64OrUrl)`

发送图片。

```javascript
await mai.sendImage("https://example.com/image.png");
// 或 base64 格式
await mai.sendImage("data:image/png;base64,...");
```

#### `mai.sendAt(userId, text)`

@某人并附带消息。

```javascript
await mai.sendAt("123456", "请注意！");
```

---

### 消息读取

#### `mai.message`

当前消息对象，包含：

```javascript
{
  text: "用户发送的消息文本",
  sender: {
    id: "123456",
    name: "用户昵称"
  },
  groupId: "群号（群聊时）",
  messageId: "消息ID"
}
```

示例：

```javascript
const text = mai.message.text;
const senderId = mai.message.sender.id;
```

---

### LLM 接口

#### `mai.callLLM(prompt, options?)`

调用大语言模型生成回复。

```javascript
const response = await mai.callLLM("帮我写一首关于春天的诗");
await mai.sendText(response);
```

选项（options）：

```javascript
const response = await mai.callLLM("你的问题", {
  temperature: 0.8,  // 随机性（0-2）
  maxTokens: 500     // 最大生成长度
});
```

---

### HTTP 请求

#### `mai.fetch(url, options?)`

发送 HTTP 请求。

```javascript
// GET 请求
const data = await mai.fetch("https://api.example.com/data");

// POST 请求
const result = await mai.fetch("https://api.example.com/post", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ key: "value" })
});
```

---

### 存储

#### `mai.store.get(key)`

读取持久化数据。

```javascript
const count = await mai.store.get("click_count") || 0;
```

#### `mai.store.set(key, value)`

写入持久化数据。

```javascript
await mai.store.set("click_count", count + 1);
```

---

### 日志

#### `mai.log(message)`

输出日志（会显示在 MaiBot 控制台）。

```javascript
mai.log("插件初始化完成");
mai.log("错误：" + error.message);
```

---

## 完整示例

```javascript
// plugin.js - 计数器插件

async function onMessage() {
  const text = mai.message.text.trim();
  
  if (text === "/count") {
    let count = await mai.store.get("count") || 0;
    count++;
    await mai.store.set("count", count);
    await mai.sendText(`已被触发 ${count} 次 🔢`);
    return true;
  }
  
  if (text === "/reset") {
    await mai.store.set("count", 0);
    await mai.sendText("计数已重置 ✅");
    return true;
  }
  
  return false;
}
```

## 下一步

- ⚡ 回到 [JS 插件快速开始](/js/quickstart)
- 📖 了解 [插件架构](/guide/architecture)

"""
MaiScript 解析器

负责解析 .mai 文件（YAML 格式），验证语法并返回结构化数据。

MaiScript 语法示例：
---
plugin:
  name: "我的插件"
  version: "1.0.0"
  author: "你的名字"
  description: "插件描述"

commands:
  - name: "打招呼"
    match: "/hello"
    reply: "你好呀！{user_name} 同学"

  - name: "查时间"
    match: "/time"
    python: |
      import datetime
      result = datetime.datetime.now().strftime("%H:%M:%S")
      reply = f"现在是 {result}"

actions:
  - name: "随机表情"
    when:
      - "当对话变得轻松愉快时"
      - "当有人分享有趣的事情时"
    reply: "哈哈哈！😂"

  - name: "天气查询"
    when:
      - "当用户询问天气时"
    params:
      city: "用户提到的城市名"
    http_get:
      url: "https://wttr.in/{city}?format=3"
    reply: "天气信息：{http_response}"
"""

import re
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


class MaiScriptValidationError(Exception):
    """MaiScript 语法验证错误"""
    pass


class MaiScriptParser:
    """MaiScript (.mai) 文件解析器"""

    REQUIRED_PLUGIN_FIELDS = ["name"]
    ALLOWED_CATEGORIES = [
        "Group Management",
        "Entertainment & Interaction",
        "Utility Tools",
        "Content Generation",
        "Multimedia",
        "External Integration",
        "Data Analysis & Insights",
        "Other",
    ]

    def parse_file(self, file_path) -> Dict[str, Any]:
        """
        解析 .mai 文件。
        
        Args:
            file_path: .mai 文件路径
        
        Returns:
            解析后的结构化数据字典
        
        Raises:
            MaiScriptValidationError: 语法验证失败
            FileNotFoundError: 文件不存在
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在：{file_path}")

        content = file_path.read_text(encoding="utf-8")
        return self.parse_string(content, source=str(file_path))

    def parse_string(self, content: str, source: str = "<string>") -> Dict[str, Any]:
        """
        解析 MaiScript 字符串。
        
        Args:
            content: MaiScript 文本内容
            source: 来源描述（用于错误信息）
        
        Returns:
            解析后的结构化数据字典
        """
        if not _HAS_YAML:
            raise ImportError(
                "解析 MaiScript 需要 PyYAML 库。\n"
                "请运行：pip install pyyaml"
            )

        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise MaiScriptValidationError(f"YAML 格式错误（{source}）：{e}")

        if not isinstance(data, dict):
            raise MaiScriptValidationError(f"{source}：顶层必须是一个 YAML 字典")

        # 验证并规范化数据
        return self._validate_and_normalize(data, source)

    def _validate_and_normalize(self, data: Dict, source: str) -> Dict:
        """验证并规范化解析结果"""
        result = {}

        # 解析 plugin 部分
        plugin_raw = data.get("plugin", {})
        if not isinstance(plugin_raw, dict):
            raise MaiScriptValidationError(f"{source}：plugin 必须是一个字典")

        result["plugin"] = self._parse_plugin_info(plugin_raw, source)

        # 解析 commands 部分
        commands_raw = data.get("commands", [])
        if not isinstance(commands_raw, list):
            raise MaiScriptValidationError(f"{source}：commands 必须是一个列表")
        result["commands"] = [self._parse_command(cmd, i, source) for i, cmd in enumerate(commands_raw)]

        # 解析 actions 部分
        actions_raw = data.get("actions", [])
        if not isinstance(actions_raw, list):
            raise MaiScriptValidationError(f"{source}：actions 必须是一个列表")
        result["actions"] = [self._parse_action(act, i, source) for i, act in enumerate(actions_raw)]

        # 解析 config 部分（可选）
        config_raw = data.get("config", {})
        result["config"] = config_raw if isinstance(config_raw, dict) else {}

        return result

    def _parse_plugin_info(self, plugin: Dict, source: str) -> Dict:
        """解析插件基本信息"""
        for field in self.REQUIRED_PLUGIN_FIELDS:
            if not plugin.get(field):
                raise MaiScriptValidationError(
                    f"{source}：plugin.{field} 是必填字段"
                )

        name = str(plugin["name"])
        # 将中文名转为安全的内部标识符
        internal_name = self._to_safe_name(name)

        return {
            "name": name,
            "internal_name": internal_name,
            "version": str(plugin.get("version", "1.0.0")),
            "author": str(plugin.get("author", "未知作者")),
            "description": str(plugin.get("description", f"{name} 插件")),
            "categories": plugin.get("categories", ["Other"]),
            "keywords": plugin.get("keywords", []),
        }

    def _parse_command(self, cmd: Dict, idx: int, source: str) -> Dict:
        """解析单个 command 定义"""
        if not isinstance(cmd, dict):
            raise MaiScriptValidationError(
                f"{source}：commands[{idx}] 必须是一个字典"
            )

        name = cmd.get("name")
        match = cmd.get("match")

        if not name:
            raise MaiScriptValidationError(
                f"{source}：commands[{idx}] 必须有 name 字段"
            )
        if not match:
            raise MaiScriptValidationError(
                f"{source}：commands[{idx}]（{name}）必须有 match 字段"
            )

        # 将 match 转为正则表达式
        pattern = self._match_to_pattern(match)
        internal_name = self._to_safe_name(name)

        parsed = {
            "name": name,
            "internal_name": internal_name,
            "match": match,
            "pattern": pattern,
            "description": cmd.get("description", f"响应 {match} 命令"),
        }

        # 确定响应类型
        if "reply" in cmd:
            parsed["type"] = "reply"
            parsed["reply"] = str(cmd["reply"])
        elif "python" in cmd:
            parsed["type"] = "python"
            parsed["python"] = str(cmd["python"])
        elif "llm_prompt" in cmd:
            parsed["type"] = "llm_prompt"
            parsed["llm_prompt"] = str(cmd["llm_prompt"])
            parsed["reply_template"] = cmd.get("reply", "{llm_response}")
        elif "http_get" in cmd:
            parsed["type"] = "http_get"
            parsed["http_get"] = cmd["http_get"]
            parsed["reply"] = cmd.get("reply", "{http_response}")
        else:
            raise MaiScriptValidationError(
                f"{source}：commands[{idx}]（{name}）必须有 reply/python/llm_prompt/http_get 之一"
            )

        return parsed

    def _parse_action(self, act: Dict, idx: int, source: str) -> Dict:
        """解析单个 action 定义"""
        if not isinstance(act, dict):
            raise MaiScriptValidationError(
                f"{source}：actions[{idx}] 必须是一个字典"
            )

        name = act.get("name")
        when = act.get("when", [])

        if not name:
            raise MaiScriptValidationError(
                f"{source}：actions[{idx}] 必须有 name 字段"
            )
        if not when:
            raise MaiScriptValidationError(
                f"{source}：actions[{idx}]（{name}）必须有 when 字段（触发条件列表）"
            )
        if isinstance(when, str):
            when = [when]

        internal_name = self._to_safe_name(name)
        params = act.get("params", {})

        parsed = {
            "name": name,
            "internal_name": internal_name,
            "when": when,
            "description": act.get("description", f"当 {when[0]} 时执行"),
            "params": params if isinstance(params, dict) else {},
            "types": act.get("types", ["text"]),
        }

        # 确定响应类型
        if "reply" in act:
            parsed["type"] = "reply"
            parsed["reply"] = str(act["reply"])
        elif "python" in act:
            parsed["type"] = "python"
            parsed["python"] = str(act["python"])
        elif "llm_prompt" in act:
            parsed["type"] = "llm_prompt"
            parsed["llm_prompt"] = str(act["llm_prompt"])
            parsed["reply_template"] = act.get("reply", "{llm_response}")
        elif "http_get" in act:
            parsed["type"] = "http_get"
            parsed["http_get"] = act["http_get"]
            parsed["reply"] = act.get("reply", "{http_response}")
        else:
            raise MaiScriptValidationError(
                f"{source}：actions[{idx}]（{name}）必须有 reply/python/llm_prompt/http_get 之一"
            )

        return parsed

    def _match_to_pattern(self, match: str) -> str:
        """将简化的 match 语法转为正则表达式"""
        # 如果已经是正则（以 ^ 开头），直接使用
        if match.startswith("^"):
            return match

        # 提取参数占位符 {param}
        # 如 "/weather {city}" → r"^/weather\s+(.+)$"
        params = re.findall(r'\{(\w+)\}', match)

        # 转义正则特殊字符（保留占位符位置）
        escaped = re.escape(match)

        # 还原占位符（re.escape 会把 { } 变成 \{ \}）
        for param in params:
            escaped = escaped.replace(r'\{' + param + r'\}', r'(.+)')

        # 允许命令后跟空格
        return f"^{escaped}$"

    @staticmethod
    def _to_safe_name(name: str) -> str:
        """将任意名称转为安全的 Python 标识符"""
        # 将非字母数字字符替换为下划线
        safe = re.sub(r'[^\w]', '_', name, flags=re.UNICODE)
        # 去除前后下划线
        safe = safe.strip('_')
        # 如果以数字开头，加前缀
        if safe and safe[0].isdigit():
            safe = 'cmd_' + safe
        return safe or 'unnamed'

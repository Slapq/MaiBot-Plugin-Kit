"""
JsBridgeLoader - JS 插件加载器

负责：
1. 解析 JS 文件，提取 mai.command() 和 mai.action() 的注册信息
2. 动态生成对应的 Python BaseAction / BaseCommand 类
3. 在 execute() 时通过 Node.js 子进程执行 JS 逻辑
"""

import json
import re
import subprocess
import sys
import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import List, Tuple, Type, Dict, Any, Optional

logger = logging.getLogger("mai_js_bridge")

# JS SDK 路径
_SDK_PATH = Path(__file__).parent / "sdk" / "mai-sdk.js"


def _has_node() -> bool:
    """检查系统是否安装了 Node.js"""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _parse_js_registrations(js_content: str) -> Dict[str, List[Dict]]:
    """
    解析 JS 文件中所有 mai.reply() / mai.command() / mai.action() 注册信息。

    支持所有写法：
      mai.reply('/ping', 'Pong!')                    → auto_reply_0
      mai.reply('/ping', 'Pong!', 'ping_cmd')        → ping_cmd
      mai.command(/pattern/, async (ctx) => { ... }) → auto_cmd_0
      mai.command({ name: 'roll', ... })             → roll
      mai.command(async (ctx) => { ... })            → auto_cmd_N (catch-all)
      mai.action({ name: 'greet', ... })             → greet

    返回格式：
    {
        "commands": [{"name": ..., "description": ..., "pattern": ...}],
        "actions": [{"name": ..., "description": ..., "require": [...], ...}]
    }
    """
    registrations = {"commands": [], "actions": []}
    _auto_cmd_idx = [0]
    _auto_reply_idx = [0]

    # ── 1. mai.reply(pattern, text) 或 mai.reply(pattern, text, name) ─────────
    for m in re.finditer(
        r'mai\.reply\s*\(\s*'
        r'(["\'/][^,]+?)'          # 第一参数：pattern（字符串/正则）
        r'\s*,\s*'
        r'(["\'][^"\']*["\'])'     # 第二参数：reply 文本
        r'(?:\s*,\s*(["\']([^"\']+)["\']))?'  # 可选第三参数：name
        r'\s*\)',
        js_content,
    ):
        pattern_raw = m.group(1).strip()
        reply_text  = m.group(2).strip().strip('"\'')
        explicit_name = m.group(4)

        if explicit_name:
            name = explicit_name
        else:
            name = f"auto_reply_{_auto_reply_idx[0]}"
            _auto_reply_idx[0] += 1

        # 提取正则
        if pattern_raw.startswith('/'):
            pat = re.search(r'^/(.+?)/([gimsuy]*)$', pattern_raw)
            pattern_str = pat.group(1) if pat else pattern_raw[1:-1]
        else:
            pattern_str = re.escape(pattern_raw.strip('"\''))

        registrations["commands"].append({
            "name": name,
            "description": f"固定回复：{reply_text[:30]}",
            "pattern": pattern_str,
            "_reply_text": reply_text,
            "_is_simple_reply": True,
        })

    # ── 2. mai.command({ name: ..., ... }) 对象配置写法 ────────────────────────
    for m in re.finditer(
        r'mai\.command\s*\(\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
        js_content,
        re.DOTALL,
    ):
        block = m.group(1)
        cmd_info = _extract_object_fields(block)
        if cmd_info.get("name"):
            registrations["commands"].append(cmd_info)

    # ── 3. mai.command(pattern, fn) 简洁写法（箭头函数） ─────────────────────
    # 注意：正则字面量内可能含 \/ 转义斜杠，用 (?:[^/\\]|\\.)+ 匹配
    for m in re.finditer(
        r'mai\.command\s*\(\s*'
        r'(/(?:[^/\\]|\\.)+/[gimsuy]*'     # /regex/flags  支持内部 \/
        r'|"[^"]+"|\'[^\']+\')'            # 或普通字符串
        r'\s*,\s*(?:async\s+)?\(',
        js_content,
    ):
        pattern_raw = m.group(1).strip()
        if pattern_raw.startswith('/'):
            # 提取最后一个未转义的 / 之前的内容
            pat = re.search(r'^/((?:[^/\\]|\\.)+)/([gimsuy]*)$', pattern_raw)
            pattern_str = pat.group(1) if pat else pattern_raw[1:-1]
        else:
            pattern_str = pattern_raw.strip('"\'')

        name = f"auto_cmd_{_auto_cmd_idx[0]}"
        _auto_cmd_idx[0] += 1
        registrations["commands"].append({
            "name": name,
            "description": f"命令：{pattern_str[:40]}",
            "pattern": pattern_str,
        })

    # ── 4. mai.command(fn) catch-all 写法 ─────────────────────────────────────
    for m in re.finditer(
        r'mai\.command\s*\(\s*(?:async\s+)?\(ctx\)',
        js_content,
    ):
        name = f"auto_cmd_{_auto_cmd_idx[0]}"
        _auto_cmd_idx[0] += 1
        registrations["commands"].append({
            "name": name,
            "description": "catch-all 命令",
            "pattern": r"^.*$",
        })

    # ── 5. mai.action({ name: ..., ... }) 对象配置写法 ────────────────────────
    for m in re.finditer(
        r'mai\.action\s*\(\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
        js_content,
        re.DOTALL,
    ):
        block = m.group(1)
        act_info = _extract_object_fields(block)
        if act_info.get("name"):
            registrations["actions"].append(act_info)

    # 去重（同名组件只保留最后一个）
    seen = {}
    for cmd in registrations["commands"]:
        seen[cmd["name"]] = cmd
    registrations["commands"] = list(seen.values())

    return registrations


def _extract_object_fields(block: str) -> Dict[str, Any]:
    """从 JS 对象字面量文本中提取关键字段"""
    fields = {}

    name_m = re.search(r'name\s*:\s*["\']([^"\']+)["\']', block)
    if name_m:
        fields["name"] = name_m.group(1)

    desc_m = re.search(r'description\s*:\s*["\']([^"\']+)["\']', block)
    if desc_m:
        fields["description"] = desc_m.group(1)

    pat_m = re.search(r'pattern\s*:\s*/([^/]+)/([gimsuy]*)', block)
    if pat_m:
        fields["pattern"] = pat_m.group(1)
        fields["pattern_flags"] = pat_m.group(2)

    req_m = re.search(r'require\s*:\s*\[([^\]]+)\]', block, re.DOTALL)
    if req_m:
        items = re.findall(r'["\']([^"\']+)["\']', req_m.group(1))
        fields["require"] = items

    params_m = re.search(r'parameters\s*:\s*\{([^}]+)\}', block, re.DOTALL)
    if params_m:
        param_keys = re.findall(r'["\']?(\w+)["\']?\s*:', params_m.group(1))
        param_descs = re.findall(r':\s*["\']([^"\']+)["\']', params_m.group(1))
        params = {}
        for k, v in zip(param_keys, param_descs):
            params[k] = v
        fields["parameters"] = params

    types_m = re.search(r'types\s*:\s*\[([^\]]+)\]', block)
    if types_m:
        items = re.findall(r'["\']([^"\']+)["\']', types_m.group(1))
        fields["types"] = items

    return fields


def _run_js_execute(js_file: str, component_name: str, context_data: Dict) -> Dict:
    """
    通过 Node.js 子进程执行 JS 插件的 execute 方法。

    Args:
        js_file: JS 文件路径
        component_name: 要执行的组件名称
        context_data: 上下文数据（stream_id, action_data, matched_groups 等）

    Returns:
        执行结果字典（{success, log, messages}）
    """
    if not _has_node():
        logger.error("[JsBridge] Node.js 未安装，无法执行 JS 插件")
        return {"success": False, "log": "Node.js 未安装", "messages": []}

    runner_script = f"""
const path = require('path');
const fs = require('fs');

// 加载 SDK
const sdkPath = {json.dumps(str(_SDK_PATH))};
const sdk = require(sdkPath);

// 上下文数据
const contextData = {json.dumps(context_data)};

// 创建 mai 全局对象（注册器）
const registrations = sdk.createRegistrar();
global.mai = registrations.mai;

// 加载插件文件
const pluginPath = {json.dumps(js_file)};
require(pluginPath);

// 执行指定组件
const componentName = {json.dumps(component_name)};
sdk.executeComponent(registrations, componentName, contextData)
  .then(result => {{
    process.stdout.write(JSON.stringify(result));
    process.exit(0);
  }})
  .catch(err => {{
    process.stdout.write(JSON.stringify({{
      success: false,
      log: String(err),
      messages: []
    }}));
    process.exit(1);
  }});
"""

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".js",
            delete=False,
            encoding="utf-8",
        ) as tf:
            tf.write(runner_script)
            runner_path = tf.name

        result = subprocess.run(
            ["node", runner_path],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
        )

        os.unlink(runner_path)

        if result.returncode != 0:
            logger.error(f"[JsBridge] Node.js 执行失败：{result.stderr}")
            return {"success": False, "log": result.stderr, "messages": []}

        output = result.stdout.strip()
        if output:
            return json.loads(output)
        return {"success": True, "log": "", "messages": []}

    except subprocess.TimeoutExpired:
        logger.error("[JsBridge] JS 执行超时（30s）")
        return {"success": False, "log": "执行超时", "messages": []}
    except Exception as e:
        logger.error(f"[JsBridge] 执行 JS 时出错：{e}")
        return {"success": False, "log": str(e), "messages": []}


class JsBridgeLoader:
    """
    JS 插件加载器。

    解析 JS 文件，生成 Python 组件类，这些类在执行时会通过 Node.js 运行 JS 代码。

    使用示例（在 plugin.py 中）：
        from mai_js_bridge import JsBridgeLoader
        loader = JsBridgeLoader(
            js_file=__file__.replace('.py', '.js'),
            plugin_name="my_plugin"
        )

        # 或使用别名：
        from mai_js_bridge import JsBridgePlugin
        plugin = JsBridgePlugin(js_file=..., plugin_name=...)
    """

    def __init__(self, js_file: str, plugin_name: str = "js_plugin"):
        self.js_file = str(Path(js_file).resolve())
        self.plugin_name = plugin_name
        self._registrations: Optional[Dict] = None

    def _load_registrations(self) -> Dict:
        """加载并解析 JS 文件中的注册信息"""
        if self._registrations is not None:
            return self._registrations

        js_path = Path(self.js_file)
        if not js_path.exists():
            logger.error(f"[JsBridge] JS 文件不存在：{self.js_file}")
            return {"commands": [], "actions": []}

        try:
            js_content = js_path.read_text(encoding="utf-8")
            self._registrations = _parse_js_registrations(js_content)
            logger.info(
                f"[JsBridge] 解析 {js_path.name}："
                f"{len(self._registrations['commands'])} 个命令，"
                f"{len(self._registrations['actions'])} 个 Action"
            )
            return self._registrations
        except Exception as e:
            logger.error(f"[JsBridge] 解析 JS 文件失败：{e}")
            return {"commands": [], "actions": []}

    def get_components(self) -> List[Tuple[Any, Type]]:
        """
        获取所有组件的 (ComponentInfo, ComponentClass) 元组列表。
        可直接传入 get_plugin_components() 的返回值。
        """
        try:
            from src.plugin_system import (
                BaseAction,
                BaseCommand,
                ActionActivationType,
            )
        except ImportError:
            logger.error("[JsBridge] 无法导入 src.plugin_system，请确保在 MaiBot 目录内运行")
            return []

        regs = self._load_registrations()
        components = []

        for cmd_info in regs.get("commands", []):
            component_class = self._make_command_class(cmd_info, BaseCommand)
            if component_class:
                components.append((component_class.get_command_info(), component_class))

        for act_info in regs.get("actions", []):
            component_class = self._make_action_class(act_info, BaseAction, ActionActivationType)
            if component_class:
                components.append((component_class.get_action_info(), component_class))

        return components

    def _make_command_class(self, cmd_info: Dict, BaseCommand) -> Optional[Type]:
        """动态生成 Command 类"""
        js_file = self.js_file
        plugin_name = self.plugin_name
        name = cmd_info.get("name", "unknown_command")
        description = cmd_info.get("description", "JS Command")
        pattern = cmd_info.get("pattern", "^$")
        flags = cmd_info.get("pattern_flags", "")

        import re as _re
        re_flags = 0
        if "i" in flags:
            re_flags |= _re.IGNORECASE

        class DynamicJsCommand(BaseCommand):
            command_name = name
            command_description = description
            command_pattern = pattern

            async def execute(self):
                context_data = {
                    "stream_id": self.stream_id,
                    "plugin_name": plugin_name,
                    "matched_groups": [],
                    "action_data": {},
                }
                if self.matched:
                    groups = list(self.matched.groups())
                    context_data["matched_groups"] = groups

                from src.plugin_system.apis import send_api

                result = await asyncio.get_running_loop().run_in_executor(
                    None,
                    lambda: _run_js_execute(js_file, name, context_data),
                )

                for msg in result.get("messages", []):
                    msg_type = msg.get("type", "text")
                    content = msg.get("content", "")
                    if msg_type == "text" and content:
                        await send_api.text_to_stream(content, self.stream_id)
                    elif msg_type == "image" and content:
                        await send_api.image_to_stream(content, self.stream_id)
                    elif msg_type == "emoji" and content:
                        await send_api.emoji_to_stream(content, self.stream_id)

                success = result.get("success", False)
                log_msg = result.get("log", "")
                return success, log_msg, True

        DynamicJsCommand.__name__ = f"JsCommand_{name}"
        DynamicJsCommand.__qualname__ = f"JsCommand_{name}"
        return DynamicJsCommand

    def _make_action_class(self, act_info: Dict, BaseAction, ActionActivationType) -> Optional[Type]:
        """动态生成 Action 类"""
        js_file = self.js_file
        plugin_name = self.plugin_name
        name = act_info.get("name", "unknown_action")
        description = act_info.get("description", "JS Action")
        require = act_info.get("require", ["当需要时"])
        parameters = act_info.get("parameters", {"reason": "执行原因"})
        types = act_info.get("types", ["text"])

        class DynamicJsAction(BaseAction):
            action_name = name
            action_description = description
            activation_type = ActionActivationType.ALWAYS
            action_require = require
            action_parameters = parameters
            associated_types = types

            async def execute(self):
                context_data = {
                    "stream_id": self.stream_id,
                    "plugin_name": plugin_name,
                    "matched_groups": [],
                    "action_data": self.action_data,
                }

                from src.plugin_system.apis import send_api

                result = await asyncio.get_running_loop().run_in_executor(
                    None,
                    lambda: _run_js_execute(js_file, name, context_data),
                )

                for msg in result.get("messages", []):
                    msg_type = msg.get("type", "text")
                    content = msg.get("content", "")
                    if msg_type == "text" and content:
                        await send_api.text_to_stream(content, self.stream_id)
                    elif msg_type == "image" and content:
                        await send_api.image_to_stream(content, self.stream_id)
                    elif msg_type == "emoji" and content:
                        await send_api.emoji_to_stream(content, self.stream_id)

                success = result.get("success", False)
                log_msg = result.get("log", "")
                return success, log_msg

        DynamicJsAction.__name__ = f"JsAction_{name}"
        DynamicJsAction.__qualname__ = f"JsAction_{name}"
        return DynamicJsAction


# ─── 公开别名 ─────────────────────────────────────────────────────────────────
# JsBridgePlugin 和 JsBridgeLoader 完全等价，可按喜好选用
JsBridgePlugin = JsBridgeLoader

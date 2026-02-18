"""
MaiScript 编译器

将解析后的 MaiScript 数据编译为完整的 MaiBot 插件目录，
包含 plugin.py 和 _manifest.json。
"""

import json
import re
import textwrap
from pathlib import Path
from typing import Dict, Any

from .parser import MaiScriptParser

# Python 类名生成
def _to_class_name(name: str) -> str:
    """将内部名称转为 Python 类名（CamelCase）"""
    parts = re.split(r'[_\s]+', name)
    return ''.join(p.capitalize() for p in parts if p)


class MaiScriptCompiler:
    """
    MaiScript 编译器。
    
    两种使用方式：
    
    1. 直接编译文件到目录（最常用）：
       compiler = MaiScriptCompiler()
       compiler.compile_file("my_plugin.mai")
    
    2. 先解析，然后获取文件内容字典：
       parser = MaiScriptParser()
       data = parser.parse_file("my_plugin.mai")
       compiler = MaiScriptCompiler(data)
       files_dict = compiler.compile()   # 返回 {filename: content}
       # 或写入磁盘：
       files_dict = compiler.compile(output_dir="./my_plugin")
    """

    def __init__(self, data: Dict[str, Any] = None):
        """
        Args:
            data: 可选，MaiScriptParser.parse_file() 的返回值。
                  如果提供，则 compile() 可直接使用，不需要再传 data。
        """
        self.parser = MaiScriptParser()
        self._data = data

    def compile_file(self, mai_file, output_dir=None) -> Path:
        """
        编译 .mai 文件为插件目录。
        
        Args:
            mai_file: .mai 文件路径
            output_dir: 输出目录（默认为 .mai 文件所在目录）
        
        Returns:
            生成的插件目录路径
        """
        mai_file = Path(mai_file)
        data = self.parser.parse_file(mai_file)

        if output_dir is None:
            output_dir = mai_file.parent / mai_file.stem
        else:
            output_dir = Path(output_dir)

        self._compile_to_disk(data, output_dir)
        return output_dir

    def compile(self, data: Dict[str, Any] = None, output_dir=None):
        """
        编译数据，支持两种返回模式：
        
        - 若提供 output_dir，则写入磁盘并返回 Path
        - 若不提供 output_dir，则返回 {filename: content} 字典
        
        Args:
            data: 解析数据（若 __init__ 已提供则可省略）
            output_dir: 输出目录（可选）
        
        Returns:
            output_dir 不为 None 时返回 Path，否则返回 Dict[str, str]
        """
        if data is None:
            data = self._data
        if data is None:
            raise ValueError("compile() 需要提供 data 参数，或在 __init__() 中传入 data")

        if output_dir is not None:
            output_dir = Path(output_dir)
            self._compile_to_disk(data, output_dir)
            return output_dir
        else:
            # 返回文件内容字典
            return self._compile_to_dict(data)

    def _compile_to_dict(self, data: Dict[str, Any]) -> Dict[str, str]:
        """将解析数据编译为 {filename: content} 字典（不写磁盘，使用临时目录）"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "plugin_output"
            # 编译到临时目录（不打印输出）
            import io, contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                self._compile_to_disk(data, tmp_path)
            # 读取所有生成文件
            result = {}
            for filepath in sorted(tmp_path.rglob("*")):
                if filepath.is_file():
                    result[filepath.name] = filepath.read_text(encoding="utf-8")
            return result

    def _compile_to_disk(self, data: Dict[str, Any], output_dir: Path) -> Path:
        """将解析数据编译并写入磁盘"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        plugin_info = data["plugin"]
        commands = data.get("commands", [])
        actions = data.get("actions", [])
        config = data.get("config", {})

        # 生成文件
        self._write_manifest(output_dir, plugin_info, commands, actions)
        self._write_plugin_py(output_dir, plugin_info, commands, actions, config)

        if config:
            self._write_config_note(output_dir, config)

        self._write_readme(output_dir, plugin_info, commands, actions)

        print(f"✅ 编译成功！插件目录：{output_dir}")
        print(f"   - _manifest.json")
        print(f"   - plugin.py（包含 {len(commands)} 个命令，{len(actions)} 个 Action）")
        if config:
            print(f"   - config_note.md（配置说明）")
        print(f"   - README.md")
        print(f"\n🚀 将 {output_dir.name}/ 目录复制到 MaiBot/plugins/ 目录并重启 MaiBot 即可！\n")

        return output_dir

    def _write_manifest(self, output_dir: Path, plugin_info: Dict, commands, actions):
        """生成 _manifest.json"""
        components = []
        for cmd in commands:
            components.append({
                "type": "command",
                "name": cmd["internal_name"],
                "description": cmd.get("description", cmd["name"]),
            })
        for act in actions:
            components.append({
                "type": "action",
                "name": act["internal_name"],
                "description": act.get("description", act["name"]),
            })

        manifest = {
            "manifest_version": 1,
            "name": plugin_info["name"],
            "version": plugin_info["version"],
            "description": plugin_info["description"],
            "author": {"name": plugin_info["author"]},
            "license": "MIT",
            "host_application": {"min_version": "0.8.0"},
            "keywords": plugin_info.get("keywords", ["maiscript"]),
            "categories": plugin_info.get("categories", ["Other"]),
            "plugin_info": {
                "is_built_in": False,
                "plugin_type": "general",
                "components": components,
            },
        }

        manifest_path = output_dir / "_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

    def _write_plugin_py(self, output_dir: Path, plugin_info: Dict, commands, actions, config):
        """生成 plugin.py"""
        internal_name = plugin_info["internal_name"]
        class_prefix = _to_class_name(internal_name)

        lines = []

        # 文件头注释
        lines.append(f'"""')
        lines.append(f'{plugin_info["name"]} - 由 MaiScript 自动生成')
        lines.append(f'')
        lines.append(f'{plugin_info["description"]}')
        lines.append(f'')
        lines.append(f'作者：{plugin_info["author"]}')
        lines.append(f'版本：{plugin_info["version"]}')
        lines.append(f'')
        lines.append(f'⚠️ 此文件由 mai_script 编译器自动生成，请勿直接修改。')
        lines.append(f'   如需修改，请编辑源 .mai 文件后重新编译。')
        lines.append(f'"""')
        lines.append(f'')
        lines.append(f'from typing import List, Tuple, Type, Optional')
        lines.append(f'from src.plugin_system import (')
        lines.append(f'    BasePlugin,')
        lines.append(f'    register_plugin,')
        lines.append(f'    BaseAction,')
        lines.append(f'    BaseCommand,')
        lines.append(f'    ComponentInfo,')
        lines.append(f'    ActionActivationType,')

        if config:
            lines.append(f'    ConfigField,')
        lines.append(f')')
        lines.append(f'from src.common.logger import get_logger')
        lines.append(f'')
        lines.append(f'logger = get_logger("{internal_name}")')
        lines.append(f'')

        # 检查是否需要 http 支持
        needs_http = any(
            c.get("type") == "http_get" for c in commands + actions
        )
        needs_llm = any(
            c.get("type") == "llm_prompt" for c in commands + actions
        )

        if needs_http:
            lines.append(f'import asyncio')
            lines.append(f'try:')
            lines.append(f'    import aiohttp')
            lines.append(f'    _HAS_AIOHTTP = True')
            lines.append(f'except ImportError:')
            lines.append(f'    _HAS_AIOHTTP = False')
            lines.append(f'')

        # 生成 Command 类
        for cmd in commands:
            lines.extend(self._generate_command_class(cmd, class_prefix, plugin_info))
            lines.append('')

        # 生成 Action 类
        for act in actions:
            lines.extend(self._generate_action_class(act, class_prefix, plugin_info))
            lines.append('')

        # 生成主插件类
        lines.extend(self._generate_plugin_class(
            plugin_info, class_prefix, commands, actions, config
        ))

        plugin_py = output_dir / "plugin.py"
        plugin_py.write_text('\n'.join(lines), encoding='utf-8')

    def _generate_command_class(self, cmd: Dict, prefix: str, plugin_info: Dict) -> List[str]:
        """生成单个 Command 类的代码"""
        class_name = f"{prefix}Cmd{_to_class_name(cmd['internal_name'])}"
        lines = []

        lines.append(f'# ---- Command: {cmd["name"]} ----')
        lines.append(f'class {class_name}(BaseCommand):')
        lines.append(f'    """响应命令：{cmd["name"]}（{cmd["match"]}）"""')
        lines.append(f'    command_name = "{cmd["internal_name"]}"')
        lines.append(f'    command_description = "{cmd.get("description", cmd["name"])}"')
        lines.append(f'    command_pattern = r"{cmd["pattern"]}"')
        lines.append(f'')
        lines.append(f'    async def execute(self) -> Tuple[bool, Optional[str], bool]:')

        cmd_type = cmd.get("type", "reply")

        if cmd_type == "reply":
            reply = cmd["reply"]
            # 处理模板变量
            lines.extend(self._gen_reply_code(reply, "        ", cmd.get("pattern", "")))

        elif cmd_type == "python":
            lines.append(f'        try:')
            for line in cmd["python"].strip().split('\n'):
                lines.append(f'            {line}')
            lines.append(f'            if "reply" in dir():')
            lines.append(f'                await self.send_text(str(reply))')
            lines.append(f'        except Exception as e:')
            lines.append(f'            logger.error(f"[{class_name}] 执行失败：{{e}}")')
            lines.append(f'            await self.send_text(f"❌ 执行失败：{{str(e)}}")')

        elif cmd_type == "http_get":
            http_cfg = cmd["http_get"]
            url = http_cfg.get("url", "") if isinstance(http_cfg, dict) else str(http_cfg)
            reply_tpl = cmd.get("reply", "{http_response}")
            lines.append(f'        if not _HAS_AIOHTTP:')
            lines.append(f'            await self.send_text("❌ 此功能需要安装 aiohttp：pip install aiohttp")')
            lines.append(f'            return False, "缺少 aiohttp", True')
            lines.append(f'        try:')
            lines.append(f'            # 处理 URL 中的参数')
            lines.extend(self._gen_param_extract_code(url, "            ", cmd.get("pattern", "")))
            lines.append(f'            url = f"{url}"')
            lines.append(f'            async with aiohttp.ClientSession() as session:')
            lines.append(f'                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:')
            lines.append(f'                    http_response = await resp.text()')
            reply_filled = reply_tpl.replace('{http_response}', '{http_response}')
            lines.append(f'            await self.send_text(f"{reply_filled}")')
            lines.append(f'        except Exception as e:')
            lines.append(f'            await self.send_text(f"❌ 请求失败：{{str(e)}}")')
            lines.append(f'            return False, str(e), True')

        elif cmd_type == "llm_prompt":
            prompt = cmd["llm_prompt"]
            lines.append(f'        try:')
            lines.append(f'            from src.plugin_system.apis import generator_api')
            lines.append(f'            prompt_text = f"""{prompt}"""')
            lines.append(f'            success, reply_set, _ = await generator_api.generate_reply(')
            lines.append(f'                chat_stream=self.message.chat_stream,')
            lines.append(f'                extra_info=prompt_text,')
            lines.append(f'            )')
            lines.append(f'            if success:')
            lines.append(f'                for reply_type, reply_content in reply_set:')
            lines.append(f'                    if reply_type == "text":')
            lines.append(f'                        await self.send_text(reply_content)')
            lines.append(f'        except Exception as e:')
            lines.append(f'            await self.send_text(f"❌ 生成失败：{{str(e)}}")')
            lines.append(f'            return False, str(e), True')

        lines.append(f'        return True, "{cmd["name"]} 执行成功", True')
        return lines

    def _generate_action_class(self, act: Dict, prefix: str, plugin_info: Dict) -> List[str]:
        """生成单个 Action 类的代码"""
        class_name = f"{prefix}Act{_to_class_name(act['internal_name'])}"
        lines = []

        params = act.get("params", {})
        params_with_reason = {"reason": "执行原因"}
        params_with_reason.update(params)

        lines.append(f'# ---- Action: {act["name"]} ----')
        lines.append(f'class {class_name}(BaseAction):')
        lines.append(f'    """Action：{act["name"]}"""')
        lines.append(f'    action_name = "{act["internal_name"]}"')
        lines.append(f'    action_description = "{act.get("description", act["name"])}"')
        lines.append(f'    activation_type = ActionActivationType.ALWAYS')
        lines.append(f'    action_parameters = {repr(params_with_reason)}')
        lines.append(f'    action_require = {repr(act["when"])}')
        lines.append(f'    associated_types = {repr(act.get("types", ["text"]))}')
        lines.append(f'')
        lines.append(f'    async def execute(self) -> Tuple[bool, str]:')
        lines.append(f'        reason = self.action_data.get("reason", "")')

        # 提取其他参数
        for param_key in params:
            lines.append(f'        {param_key} = self.action_data.get("{param_key}", "")')

        act_type = act.get("type", "reply")

        if act_type == "reply":
            reply = act["reply"]
            lines.extend(self._gen_reply_code(reply, "        ", ""))
            lines.append(f'        return True, "{act["name"]} 执行成功"')

        elif act_type == "python":
            lines.append(f'        try:')
            for line in act["python"].strip().split('\n'):
                lines.append(f'            {line}')
            lines.append(f'            if "reply" in dir():')
            lines.append(f'                await self.send_text(str(reply))')
            lines.append(f'        except Exception as e:')
            lines.append(f'            logger.error(f"[{class_name}] 执行失败：{{e}}")')
            lines.append(f'            return False, str(e)')
            lines.append(f'        return True, "{act["name"]} 执行成功"')

        elif act_type == "http_get":
            http_cfg = act["http_get"]
            url = http_cfg.get("url", "") if isinstance(http_cfg, dict) else str(http_cfg)
            reply_tpl = act.get("reply", "{http_response}")
            lines.append(f'        if not _HAS_AIOHTTP:')
            lines.append(f'            await self.send_text("❌ 此功能需要安装 aiohttp")')
            lines.append(f'            return False, "缺少 aiohttp"')
            lines.append(f'        try:')
            lines.append(f'            url = f"{url}"')
            lines.append(f'            async with aiohttp.ClientSession() as session:')
            lines.append(f'                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:')
            lines.append(f'                    http_response = await resp.text()')
            lines.append(f'            await self.send_text(f"{reply_tpl}")')
            lines.append(f'        except Exception as e:')
            lines.append(f'            await self.send_text(f"❌ 请求失败：{{str(e)}}")')
            lines.append(f'            return False, str(e)')
            lines.append(f'        return True, "{act["name"]} 执行成功"')

        elif act_type == "llm_prompt":
            prompt = act["llm_prompt"]
            lines.append(f'        try:')
            lines.append(f'            from src.plugin_system.apis import generator_api')
            lines.append(f'            extra = f"""{prompt}"""')
            lines.append(f'            success, reply_set, _ = await generator_api.generate_reply(')
            lines.append(f'                chat_stream=self.message.chat_stream,')
            lines.append(f'                extra_info=extra,')
            lines.append(f'            )')
            lines.append(f'            if success:')
            lines.append(f'                for reply_type, reply_content in reply_set:')
            lines.append(f'                    if reply_type == "text":')
            lines.append(f'                        await self.send_text(reply_content)')
            lines.append(f'        except Exception as e:')
            lines.append(f'            logger.error(f"执行失败：{{e}}")')
            lines.append(f'            return False, str(e)')
            lines.append(f'        return True, "{act["name"]} 执行成功"')

        return lines

    def _generate_plugin_class(
        self,
        plugin_info: Dict,
        class_prefix: str,
        commands: List,
        actions: List,
        config: Dict,
    ) -> List[str]:
        """生成主插件类"""
        lines = []
        main_class = f"{class_prefix}Plugin"
        internal_name = plugin_info["internal_name"]

        lines.append(f'# ---- 主插件类 ----')
        lines.append(f'@register_plugin')
        lines.append(f'class {main_class}(BasePlugin):')
        lines.append(f'    """由 MaiScript 生成：{plugin_info["name"]}"""')
        lines.append(f'')
        lines.append(f'    plugin_name = "{internal_name}"')
        lines.append(f'    enable_plugin = True')
        lines.append(f'    dependencies: List[str] = []')

        # 检查是否需要 aiohttp
        needs_http = any(c.get("type") == "http_get" for c in commands + actions)
        if needs_http:
            lines.append(f'    python_dependencies: List[str] = ["aiohttp"]')
        else:
            lines.append(f'    python_dependencies: List[str] = []')

        lines.append(f'    config_file_name = "config.toml"')

        # 配置 schema
        if config:
            lines.append(f'    config_schema: dict = {{')
            for section, fields in config.items():
                lines.append(f'        "{section}": {{')
                if isinstance(fields, dict):
                    for key, value in fields.items():
                        default = repr(value.get("default", "")) if isinstance(value, dict) else repr(value)
                        desc = value.get("description", key) if isinstance(value, dict) else key
                        lines.append(f'            "{key}": ConfigField(type=str, default={default}, description="{desc}"),')
                lines.append(f'        }},')
            lines.append(f'    }}')
        else:
            lines.append(f'    config_schema: dict = {{}}')

        lines.append(f'')
        lines.append(f'    def get_plugin_components(self) -> List[Tuple[ComponentInfo, Type]]:')
        lines.append(f'        """返回所有组件"""')
        lines.append(f'        return [')

        for cmd in commands:
            class_name = f"{class_prefix}Cmd{_to_class_name(cmd['internal_name'])}"
            lines.append(f'            ({class_name}.get_command_info(), {class_name}),')
        for act in actions:
            class_name = f"{class_prefix}Act{_to_class_name(act['internal_name'])}"
            lines.append(f'            ({class_name}.get_action_info(), {class_name}),')

        lines.append(f'        ]')
        return lines

    def _gen_reply_code(self, reply: str, indent: str, pattern: str) -> List[str]:
        """生成 reply 类型的响应代码"""
        lines = []
        # 检查是否有 {user_name} 类的变量
        vars_in_reply = re.findall(r'\{(\w+)\}', reply)

        if "user_name" in vars_in_reply:
            lines.append(f'{indent}user_name = getattr(self.message, "sender_nickname", "朋友") if hasattr(self, "message") and self.message else "朋友"')

        # 从 self.matched_groups 提取命名捕获组参数（正确用法）
        param_vars = [v for v in vars_in_reply if v not in ("user_name",)]
        for pv in param_vars:
            lines.append(f'{indent}{pv} = self.matched_groups.get("{pv}", "")')

        lines.append(f'{indent}await self.send_text(f"{reply}")')
        return lines

    def _gen_param_extract_code(self, url: str, indent: str, pattern: str) -> List[str]:
        """生成 URL 中参数提取的代码（从 matched_groups 取命名组）"""
        lines = []
        params = re.findall(r'\{(\w+)\}', url)
        for param in params:
            lines.append(f'{indent}{param} = self.matched_groups.get("{param}", "")')
        return lines

    def _write_config_note(self, output_dir: Path, config: Dict):
        """生成配置说明文件"""
        lines = ["# 配置说明", ""]
        lines.append("此插件使用以下配置项（在 config.toml 中）：")
        lines.append("")
        for section, fields in config.items():
            lines.append(f"## [{section}]")
            if isinstance(fields, dict):
                for key, value in fields.items():
                    default = value.get("default", "") if isinstance(value, dict) else value
                    desc = value.get("description", key) if isinstance(value, dict) else key
                    lines.append(f"- `{key}` = `{default}` — {desc}")
            lines.append("")
        (output_dir / "config_note.md").write_text('\n'.join(lines), encoding='utf-8')

    def _write_readme(self, output_dir: Path, plugin_info: Dict, commands: List, actions: List):
        """生成 README.md"""
        lines = [f"# {plugin_info['name']}", ""]
        lines.append(plugin_info["description"])
        lines.append("")
        lines.append(f"**作者**：{plugin_info['author']}  ")
        lines.append(f"**版本**：{plugin_info['version']}  ")
        lines.append(f"**生成方式**：MaiScript 自动编译")
        lines.append("")

        if commands:
            lines.append("## 命令列表")
            lines.append("")
            for cmd in commands:
                lines.append(f"- `{cmd['match']}` — {cmd.get('description', cmd['name'])}")
            lines.append("")

        if actions:
            lines.append("## 自主行为（Action）")
            lines.append("")
            for act in actions:
                when_str = "、".join(act["when"][:2])
                lines.append(f"- **{act['name']}**：{when_str}")
            lines.append("")

        lines.append("## 安装")
        lines.append("")
        lines.append(f"将 `{output_dir.name}/` 目录复制到 MaiBot 的 `plugins/` 目录，重启 MaiBot 即可。")

        (output_dir / "README.md").write_text('\n'.join(lines), encoding='utf-8')

"""
mai-plugin-cli 入口
用法:
  python -m mai_plugin_cli create <name>         创建新插件
  python -m mai_plugin_cli validate <path>        验证插件
  python -m mai_plugin_cli pack <path>            打包插件
  python -m mai_plugin_cli list-templates         列出可用模板
  python -m mai_plugin_cli run-maiscript <file>   运行MaiScript文件
"""
import sys
import io

# ─── 强制 UTF-8 输出（修复 Windows GBK 终端的 UnicodeEncodeError）────────────
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from .commands.main import cli

if __name__ == "__main__":
    cli()

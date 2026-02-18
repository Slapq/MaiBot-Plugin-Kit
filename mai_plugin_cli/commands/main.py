"""
mai-plugin-cli 命令行主入口
使用 argparse 实现，无需第三方依赖
"""
import argparse
import sys
from .create import cmd_create
from .validate import cmd_validate
from .pack import cmd_pack
from .list_templates import cmd_list_templates
from .run_maiscript import cmd_run_maiscript

BANNER = r"""
  __  __       _   ____        _       _____ _      _____ 
 |  \/  |     (_) |  _ \      | |     / ____| |    |_   _|
 | \  / | __ _ _  | |_) | ___ | |_   | |    | |      | |  
 | |\/| |/ _` | | |  _ < / _ \| __|  | |    | |      | |  
 | |  | | (_| | | | |_) | (_) | |_   | |____| |____ _| |_ 
 |_|  |_|\__,_|_| |____/ \___/ \__|   \_____|______|_____|
                                                           
  麦麦插件脚手架工具 v1.0.0  —  让插件开发变得简单！
"""


def cli():
    print(BANNER)
    parser = argparse.ArgumentParser(
        prog="mai",
        description="麦麦(MaiBot)插件开发脚手架工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
子命令说明:
  create          创建新插件（支持多种模板）
  validate        验证插件 manifest 和结构
  pack            打包插件为 zip 文件
  list-templates  列出所有可用的插件模板
  run-maiscript   将 MaiScript (.mai) 文件编译为 Python 插件

示例:
  mai create my_plugin                  # 交互式创建插件
  mai create my_plugin -t action        # 使用 action 模板创建
  mai create my_plugin -t js_bridge     # 创建 JS 桥接插件
  mai validate ./my_plugin              # 验证插件结构
  mai pack ./my_plugin                  # 打包插件
  mai run-maiscript ./my_plugin.mai     # 编译 MaiScript 文件
        """,
    )

    subparsers = parser.add_subparsers(dest="command", title="可用命令")

    # create 子命令
    p_create = subparsers.add_parser("create", help="创建新的麦麦插件")
    p_create.add_argument("name", help="插件名称（英文，用下划线分隔，如 my_plugin）")
    p_create.add_argument(
        "-t",
        "--template",
        choices=["minimal", "action", "command", "full", "js_bridge", "advanced"],
        default=None,
        help="使用指定模板（不填则进入交互式选择）",
    )
    p_create.add_argument(
        "-o",
        "--output",
        default=".",
        help="输出目录（默认为当前目录）",
    )
    p_create.add_argument(
        "--author",
        default=None,
        help="插件作者名称",
    )
    p_create.add_argument(
        "--description",
        default=None,
        help="插件描述",
    )
    p_create.add_argument(
        "--version-str",
        default=None,
        dest="version_str",
        help="插件版本号（默认 1.0.0）",
    )
    p_create.add_argument(
        "--yes", "-y",
        action="store_true",
        default=False,
        help="非交互式模式，所有提示使用默认值",
    )

    # validate 子命令
    p_validate = subparsers.add_parser("validate", help="验证插件结构和 manifest")
    p_validate.add_argument("path", help="插件目录路径")

    # pack 子命令
    p_pack = subparsers.add_parser("pack", help="打包插件为 zip 文件")
    p_pack.add_argument("path", help="插件目录路径")
    p_pack.add_argument(
        "-o",
        "--output",
        default=None,
        help="输出 zip 文件路径（默认为插件目录同级）",
    )

    # list-templates 子命令
    subparsers.add_parser("list-templates", help="列出所有可用的插件模板")

    # run-maiscript 子命令
    p_mai = subparsers.add_parser("run-maiscript", help="将 MaiScript (.mai) 文件编译为 Python 插件")
    p_mai.add_argument("file", help="MaiScript 文件路径（.mai）")
    p_mai.add_argument(
        "-o",
        "--output",
        default=None,
        help="输出目录（默认为 .mai 文件所在目录）",
    )

    args = parser.parse_args()

    if args.command == "create":
        cmd_create(args)
    elif args.command == "validate":
        cmd_validate(args)
    elif args.command == "pack":
        cmd_pack(args)
    elif args.command == "list-templates":
        cmd_list_templates(args)
    elif args.command == "run-maiscript":
        cmd_run_maiscript(args)
    else:
        parser.print_help()
        sys.exit(0)

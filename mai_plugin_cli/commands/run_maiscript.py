"""
mai run-maiscript 命令实现
将 MaiScript (.mai) 文件编译为 Python 插件
"""
import sys
import os
from pathlib import Path


def cmd_run_maiscript(args):
    """将 MaiScript 文件编译为 Python 插件"""
    mai_file = Path(args.file)

    if not mai_file.exists():
        print(f"❌ 文件不存在：{mai_file}")
        return

    if mai_file.suffix not in (".mai", ".yaml", ".yml"):
        print(f"⚠️  文件扩展名建议为 .mai，当前为 {mai_file.suffix}")

    # 确定输出目录
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = mai_file.parent / mai_file.stem

    print(f"\n🔧 正在编译 MaiScript 文件：{mai_file}")
    print(f"📂 输出目录：{output_dir}\n")

    # 调用 mai_script 编译器
    try:
        # 将 mai_script 模块路径加入
        kit_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(kit_root))
        from mai_script.compiler import MaiScriptCompiler

        compiler = MaiScriptCompiler()
        compiler.compile_file(mai_file, output_dir)

    except ImportError:
        print("❌ 无法导入 mai_script 模块，请确保 MaiBot-Plugin-Kit 安装正确")
        raise
    except Exception as e:
        print(f"❌ 编译失败：{e}")
        raise

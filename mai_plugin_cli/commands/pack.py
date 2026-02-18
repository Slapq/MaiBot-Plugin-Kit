"""
mai pack 命令实现
打包插件为 zip 文件
"""
import json
import zipfile
import os
from pathlib import Path


IGNORE_PATTERNS = [
    "__pycache__",
    ".git",
    ".DS_Store",
    "*.pyc",
    "*.pyo",
    ".env",
    "node_modules",
    "*.log",
]


def should_ignore(path: Path) -> bool:
    """判断文件/目录是否应被忽略"""
    for pattern in IGNORE_PATTERNS:
        if pattern.startswith("*"):
            if path.name.endswith(pattern[1:]):
                return True
        else:
            if path.name == pattern:
                return True
    return False


def cmd_pack(args):
    """打包插件"""
    plugin_path = Path(args.path).resolve()

    if not plugin_path.exists() or not plugin_path.is_dir():
        print(f"❌ 插件目录不存在：{plugin_path}")
        return

    # 读取插件名称和版本
    manifest_path = plugin_path / "_manifest.json"
    plugin_name = plugin_path.name
    plugin_version = "1.0.0"

    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            plugin_version = manifest.get("version", "1.0.0")
        except Exception:
            pass

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = plugin_path.parent / f"{plugin_name}-v{plugin_version}.zip"

    print(f"\n📦 正在打包插件：{plugin_name} v{plugin_version}")
    print(f"📂 源目录：{plugin_path}")
    print(f"📄 输出文件：{output_path}\n")

    file_count = 0
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for filepath in sorted(plugin_path.rglob("*")):
            # 检查是否应忽略
            skip = False
            for part in filepath.parts:
                if should_ignore(Path(part)):
                    skip = True
                    break
            if skip:
                continue

            if filepath.is_file():
                arcname = plugin_name + "/" + str(filepath.relative_to(plugin_path))
                zf.write(filepath, arcname)
                print(f"  + {arcname}")
                file_count += 1

    size_kb = output_path.stat().st_size / 1024
    print(f"\n✅ 打包完成！共 {file_count} 个文件，大小：{size_kb:.1f} KB")
    print(f"📦 输出文件：{output_path}\n")

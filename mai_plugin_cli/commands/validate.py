"""
mai validate 命令实现
验证插件结构和 manifest
"""
import json
import os
from pathlib import Path


REQUIRED_FILES = ["_manifest.json", "plugin.py"]
REQUIRED_MANIFEST_FIELDS = ["manifest_version", "name", "version", "description", "author"]
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


def cmd_validate(args):
    """验证插件结构"""
    plugin_path = Path(args.path)

    print(f"\n🔍 正在验证插件：{plugin_path.resolve()}\n")

    errors = []
    warnings = []

    # 检查目录是否存在
    if not plugin_path.exists():
        print(f"❌ 路径不存在：{plugin_path}")
        return
    if not plugin_path.is_dir():
        print(f"❌ 路径不是目录：{plugin_path}")
        return

    # 检查必要文件
    print("📂 检查文件结构...")
    for fname in REQUIRED_FILES:
        fpath = plugin_path / fname
        if fpath.exists():
            print(f"  ✅ {fname}")
        else:
            errors.append(f"缺少必要文件：{fname}")
            print(f"  ❌ {fname}（缺失）")

    # 检查 JS 桥接插件
    plugin_js = plugin_path / "plugin.js"
    if plugin_js.exists():
        print(f"  ✅ plugin.js（JS 桥接插件）")

    # 检查 manifest
    manifest_path = plugin_path / "_manifest.json"
    if manifest_path.exists():
        print("\n📋 检查 manifest.json...")
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # 检查必要字段
            for field in REQUIRED_MANIFEST_FIELDS:
                if field == "author":
                    if "author" not in manifest:
                        errors.append("manifest 缺少 author 字段")
                        print("  ❌ author（缺失）")
                    elif not manifest["author"].get("name"):
                        errors.append("manifest 的 author.name 不能为空")
                        print("  ❌ author.name（为空）")
                    else:
                        print(f"  ✅ author.name = {manifest['author']['name']}")
                else:
                    if field not in manifest or not manifest[field]:
                        errors.append(f"manifest 缺少必要字段：{field}")
                        print(f"  ❌ {field}（缺失或为空）")
                    else:
                        val = manifest[field]
                        if isinstance(val, str) and len(val) > 30:
                            val = val[:30] + "..."
                        print(f"  ✅ {field} = {val}")

            # 检查可选字段
            print("\n📋 检查可选字段...")
            optional = ["license", "keywords", "homepage_url", "repository_url"]
            for field in optional:
                if field in manifest and manifest[field]:
                    print(f"  ✅ {field}")
                else:
                    warnings.append(f"建议填写可选字段：{field}")
                    print(f"  ⚠️  {field}（未填写，建议填写）")

            # 检查 categories
            if "categories" in manifest:
                cats = manifest["categories"]
                for cat in cats:
                    if cat not in ALLOWED_CATEGORIES:
                        errors.append(f"无效的分类标识符：'{cat}'，请使用规定的英文分类")
                        print(f"  ❌ categories 包含无效分类：{cat}")
                    else:
                        print(f"  ✅ categories: {cat}")

            # 检查 host_application
            if "host_application" in manifest:
                ha = manifest["host_application"]
                if "min_version" not in ha:
                    warnings.append("建议填写 host_application.min_version")
                else:
                    min_v = ha.get("min_version", "0.0.0")
                    max_v = ha.get("max_version", "最新")
                    # 版本比较：低于 0.8.0 给出警告
                    try:
                        parts = [int(x) for x in min_v.split(".")]
                        if parts < [0, 8, 0]:
                            warnings.append(
                                f"host_application.min_version = {min_v}，"
                                f"建议设为 0.8.0（当前 MaiBot 插件系统最低兼容版本）"
                            )
                            print(f"  ⚠️  兼容版本：{min_v} ~ {max_v}（建议最低版本 ≥ 0.8.0）")
                        else:
                            print(f"  ✅ 兼容版本：{min_v} ~ {max_v}")
                    except (ValueError, AttributeError):
                        print(f"  ✅ 兼容版本：{min_v} ~ {max_v}")

            # 检查 manifest_version
            if manifest.get("manifest_version") != 1:
                errors.append(f"manifest_version 必须为 1，当前为：{manifest.get('manifest_version')}")

        except json.JSONDecodeError as e:
            errors.append(f"manifest.json 格式错误：{e}")
            print(f"  ❌ JSON 格式错误：{e}")

    # 检查 plugin.py 语法
    plugin_py = plugin_path / "plugin.py"
    if plugin_py.exists():
        print("\n🐍 检查 plugin.py 语法...")
        try:
            import ast
            content = plugin_py.read_text(encoding="utf-8")
            ast.parse(content)
            print("  ✅ Python 语法正确")
        except SyntaxError as e:
            errors.append(f"plugin.py 语法错误：{e}")
            print(f"  ❌ 语法错误：{e}")

    # 检查 config.toml（不应手动创建）
    config_toml = plugin_path / "config.toml"
    if config_toml.exists():
        warnings.append("发现 config.toml 文件，建议由系统自动生成而非手动创建")

    # 输出汇总
    print("\n" + "=" * 50)
    if not errors:
        print(f"✅ 验证通过！共 {len(warnings)} 个警告")
    else:
        print(f"❌ 验证失败！共 {len(errors)} 个错误，{len(warnings)} 个警告")

    if errors:
        print("\n❌ 错误：")
        for e in errors:
            print(f"   - {e}")

    if warnings:
        print("\n⚠️  警告：")
        for w in warnings:
            print(f"   - {w}")

    print()

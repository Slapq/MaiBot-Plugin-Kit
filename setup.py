"""
MaiBot Plugin Kit 安装脚本

可选安装：
  pip install .                    # 只安装脚手架工具
  pip install .[js]                # 包含 JS Bridge 支持
  pip install .[maiscript]         # 包含 MaiScript 支持
  pip install .[all]               # 安装所有功能
"""

from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="mai-plugin-kit",
    version="1.0.0",
    description="MaiBot 插件开发工具包 - 脚手架、JS桥接、MaiScript",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MaiBot Community",
    python_requires=">=3.9",
    packages=find_packages(exclude=["docs*", "tests*"]),
    package_data={
        "mai_plugin_cli": [
            "templates/**/*",
            "templates/**/.*",
        ],
        "mai_js_bridge": [
            "sdk/*.js",
        ],
    },
    include_package_data=True,
    install_requires=[],  # 无必须依赖
    extras_require={
        "maiscript": ["pyyaml>=6.0"],
        "js": [],  # Node.js 需要系统级安装，不在此管理
        "all": ["pyyaml>=6.0"],
    },
    entry_points={
        "console_scripts": [
            "mai=mai_plugin_cli.commands.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords="maibot plugin development scaffold",
    project_urls={
        "Documentation": "https://maibot-plugin-kit.pages.dev/",
        "Source": "https://github.com/Mai-with-u/MaiBot-Plugin-Kit",
        "Bug Reports": "https://github.com/Mai-with-u/MaiBot-Plugin-Kit/issues",
    },
)

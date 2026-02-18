"""
mai_script - MaiScript DSL 解析器与编译器

MaiScript 是一种基于 YAML 的声明式语言，专为非程序员设计。
无需编写 Python 代码，通过简单的 YAML 配置即可创建麦麦插件。

使用方式：
    from mai_script import MaiScriptCompiler
    
    compiler = MaiScriptCompiler()
    compiler.compile_file("my_plugin.mai", output_dir="./my_plugin")
"""

from .compiler import MaiScriptCompiler
from .parser import MaiScriptParser

__version__ = "1.0.0"
__all__ = ["MaiScriptCompiler", "MaiScriptParser"]

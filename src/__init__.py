"""
测试用例生成器主包
"""

__version__ = "0.1.0"
__author__ = "Test Case Generator Team"
__description__ = "基于AI的PRD文档测试用例生成工具"

# 导入核心模块
from . import models
from . import interfaces
from . import services
from . import parsers
from . import generators
from . import ui
from . import utils

__all__ = [
    'models', 'interfaces', 'services', 'parsers', 
    'generators', 'ui', 'utils'
]
#!/usr/bin/env python3
"""
应用程序主入口
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.main_window import MainWindow
from src.utils.constants import APP_NAME


def setup_application():
    """设置应用程序"""
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("Test Case Generator Team")
    
    # 设置默认字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    # 高DPI支持在Qt6中默认启用，无需手动设置属性
    
    return app


def main():
    """主函数"""
    try:
        # 设置应用程序
        app = setup_application()
        
        # 创建主窗口
        main_window = MainWindow()
        main_window.show()
        
        # 运行应用程序
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
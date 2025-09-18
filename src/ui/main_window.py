"""
主窗口实现，提供整体界面布局和核心功能
"""

import sys
import os
from typing import Optional, List
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QToolBar, QStatusBar, QLabel, QProgressBar,
    QMessageBox, QApplication, QTabWidget, QTextEdit, QGroupBox,
    QFileDialog, QDialog
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QAction, QIcon, QPixmap, QFont

from ..utils.constants import MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, APP_NAME, APP_VERSION
from ..utils.config_helper import ConfigHelper
from ..models.data_models import TestCase, ParsedContent, StructuredInfo
from .file_upload_widget import FileUploadWidget
from .test_case_display_widget import TestCaseDisplayWidget
from .progress_widget import ProgressWidget
from .settings_dialog import SettingsDialog
from .processing_thread import ProcessingThread


class MainWindow(QMainWindow):
    """主窗口类，提供整体界面布局和核心功能"""
    
    # 信号定义
    file_uploaded = pyqtSignal(str)  # 文件上传信号
    test_cases_generated = pyqtSignal(list)  # 测试用例生成信号
    settings_changed = pyqtSignal(dict)  # 设置变更信号
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 配置管理器
        self.config = ConfigHelper()
        
        # 数据存储
        self.current_files: List[str] = []
        self.parsed_content: Optional[ParsedContent] = None
        self.structured_info: Optional[StructuredInfo] = None
        self.test_cases: List[TestCase] = []
        
        # 工作线程
        self.processing_thread: Optional[ProcessingThread] = None
        
        # 初始化UI
        self._init_ui()
        self._init_menu_bar()
        self._init_tool_bar()
        self._init_status_bar()
        self._connect_signals()
        self._apply_theme()
        self._restore_window_state()
        
        # 设置窗口属性
        self._setup_window_properties()
    
    def _init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧面板
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([400, 880])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
    
    def _create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        panel.setMaximumWidth(450)
        panel.setMinimumWidth(350)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 文件上传区域
        file_group = QGroupBox("文件上传")
        file_layout = QVBoxLayout(file_group)
        
        self.file_upload_widget = FileUploadWidget()
        file_layout.addWidget(self.file_upload_widget)
        
        layout.addWidget(file_group)
        
        # 处理进度区域
        progress_group = QGroupBox("处理进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_widget = ProgressWidget()
        progress_layout.addWidget(self.progress_widget)
        
        layout.addWidget(progress_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        panel = QWidget()
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # 文档预览标签页
        self.document_tab = self._create_document_tab()
        self.tab_widget.addTab(self.document_tab, "文档预览")
        
        # 测试用例标签页
        self.test_case_tab = self._create_test_case_tab()
        self.tab_widget.addTab(self.test_case_tab, "测试用例")
        
        # 统计报告标签页
        self.report_tab = self._create_report_tab()
        self.tab_widget.addTab(self.report_tab, "统计报告")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def _create_document_tab(self) -> QWidget:
        """创建文档预览标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 文档内容显示
        self.document_text = QTextEdit()
        self.document_text.setReadOnly(True)
        self.document_text.setPlaceholderText("请上传文档文件，这里将显示识别的文档内容...")
        
        # 设置字体
        font = QFont("Microsoft YaHei", 10)
        self.document_text.setFont(font)
        
        layout.addWidget(self.document_text)
        
        return tab
    
    def _create_test_case_tab(self) -> QWidget:
        """创建测试用例标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 测试用例显示组件
        self.test_case_display = TestCaseDisplayWidget()
        layout.addWidget(self.test_case_display)
        
        return tab
    
    def _create_report_tab(self) -> QWidget:
        """创建统计报告标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 报告内容显示
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        self.report_text.setPlaceholderText("生成测试用例后，这里将显示详细的统计报告...")
        
        # 设置字体
        font = QFont("Consolas", 9)
        self.report_text.setFont(font)
        
        layout.addWidget(self.report_text)
        
        return tab
    
    def _init_menu_bar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 打开文件
        open_action = QAction("打开文件(&O)", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("打开PRD文档文件")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # 导出测试用例
        export_action = QAction("导出测试用例(&E)", self)
        export_action.setShortcut("Ctrl+E")
        export_action.setStatusTip("导出生成的测试用例")
        export_action.triggered.connect(self._export_test_cases)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("退出应用程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具(&T)")
        
        # 设置
        settings_action = QAction("设置(&S)", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.setStatusTip("打开设置对话框")
        settings_action.triggered.connect(self._open_settings)
        tools_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 关于
        about_action = QAction("关于(&A)", self)
        about_action.setStatusTip("关于测试用例生成器")
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _init_tool_bar(self):
        """初始化工具栏"""
        toolbar = self.addToolBar("主工具栏")
        toolbar.setMovable(False)
        
        # 打开文件
        open_action = QAction("打开", self)
        open_action.setStatusTip("打开PRD文档文件")
        open_action.triggered.connect(self._open_file)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # 开始处理
        start_action = QAction("开始", self)
        start_action.setStatusTip("开始生成测试用例")
        start_action.triggered.connect(self._start_processing)
        toolbar.addAction(start_action)
        
        # 停止处理
        stop_action = QAction("停止", self)
        stop_action.setStatusTip("停止处理")
        stop_action.triggered.connect(self._stop_processing)
        toolbar.addAction(stop_action)
        
        toolbar.addSeparator()
        
        # 导出
        export_action = QAction("导出", self)
        export_action.setStatusTip("导出测试用例")
        export_action.triggered.connect(self._export_test_cases)
        toolbar.addAction(export_action)
        
        toolbar.addSeparator()
        
        # 设置
        settings_action = QAction("设置", self)
        settings_action.setStatusTip("打开设置")
        settings_action.triggered.connect(self._open_settings)
        toolbar.addAction(settings_action)
    
    def _init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
        
        # 添加永久状态信息
        self.status_label = QLabel("未加载文件")
        self.status_bar.addPermanentWidget(self.status_label)
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 文件上传组件信号
        self.file_upload_widget.files_selected.connect(self._on_files_selected)
        
        # 测试用例显示组件信号
        self.test_case_display.test_case_modified.connect(self._on_test_case_modified)
        
        # 进度组件信号
        self.progress_widget.progress_completed.connect(self._on_progress_completed)
        self.progress_widget.progress_cancelled.connect(self._on_progress_cancelled)
    
    def _apply_theme(self):
        """应用主题样式"""
        theme = self.config.theme
        
        if theme == "dark":
            self._apply_dark_theme()
        else:
            self._apply_light_theme()
    
    def _apply_light_theme(self):
        """应用浅色主题"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #2196F3;
            }
        """)
    
    def _apply_dark_theme(self):
        """应用深色主题"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #404040;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #2b2b2b;
                border-bottom: 2px solid #2196F3;
            }
        """)
    
    def _setup_window_properties(self):
        """设置窗口属性"""
        # 设置窗口图标（如果有的话）
        # self.setWindowIcon(QIcon("icon.png"))
        
        # 设置窗口标志
        self.setWindowFlags(Qt.WindowType.Window)
        
        # 居中显示
        self._center_window()
    
    def _restore_window_state(self):
        """恢复窗口状态"""
        if self.config.remember_window_state:
            # 恢复窗口大小
            width = self.config.window_width or MIN_WINDOW_WIDTH
            height = self.config.window_height or MIN_WINDOW_HEIGHT
            self.resize(width, height)
    
    def _center_window(self):
        """窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def _save_window_state(self):
        """保存窗口状态"""
        if self.config.remember_window_state and self.config.config_manager:
            self.config.update_ui_config(
                window_width=self.width(),
                window_height=self.height()
            )
    
    # 槽函数实现
    def _on_files_selected(self, files: List[str]):
        """文件选择处理"""
        self.current_files = files
        self.status_label.setText(f"已选择 {len(files)} 个文件")
        
        # 更新状态栏
        if files:
            file_names = [Path(f).name for f in files]
            self.status_bar.showMessage(f"已选择文件: {', '.join(file_names)}")
        else:
            self.status_bar.showMessage("就绪")
    
    def _start_processing(self):
        """开始处理"""
        if not self.current_files:
            QMessageBox.warning(self, "警告", "请先选择要处理的文件")
            return
        
        # 检查配置
        if not self._check_configuration():
            return
        
        # 更新UI状态
        self.file_upload_widget.set_enabled(False)
        
        # 重置进度
        self.progress_widget.reset()
        self.progress_widget.start_processing(5)  # 5个步骤
        
        # 清空之前的结果
        self.document_text.clear()
        self.test_case_display.clear()
        self.report_text.clear()
        
        # 启动处理线程
        self.processing_thread = ProcessingThread(self.current_files)
        self.processing_thread.progress_updated.connect(self.progress_widget.update_progress)
        self.processing_thread.document_parsed.connect(self._on_document_parsed)
        self.processing_thread.test_cases_generated.connect(self._on_test_cases_generated)
        self.processing_thread.processing_completed.connect(self._on_processing_completed)
        self.processing_thread.error_occurred.connect(self._on_error_occurred)
        
        self.processing_thread.start()
        
        self.status_bar.showMessage("正在处理文件...")
    
    def _stop_processing(self):
        """停止处理"""
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.stop()
            self.processing_thread.wait()
        
        # 恢复UI状态
        self.file_upload_widget.set_enabled(True)
        self.progress_widget.cancel_processing("处理已停止")
        
        self.status_bar.showMessage("处理已停止")
    
    def _export_test_cases(self):
        """导出测试用例"""
        if not self.test_cases:
            QMessageBox.warning(self, "警告", "没有可导出的测试用例")
            return
        
        # 这里应该打开导出对话框，暂时显示提示
        QMessageBox.information(self, "导出", "导出功能待实现")
    
    def _open_file(self):
        """打开文件对话框"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("支持的文件 (*.png *.jpg *.jpeg *.pdf *.docx);;所有文件 (*.*)")
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            self.file_upload_widget.set_files(files)
    
    def _open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 重新应用主题
            self._apply_theme()
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
            f"{APP_NAME} v{APP_VERSION}\n\n"
            "基于AI的PRD文档测试用例生成工具\n\n"
            "支持PNG、JPG、PDF、DOCX格式\n"
            "自动OCR识别和智能用例生成\n\n"
            "© 2024 Test Case Generator Team")
    
    def _check_configuration(self) -> bool:
        """检查配置是否完整"""
        # 检查API密钥
        if not self.config.openai_api_key and not self.config.claude_api_key:
            reply = QMessageBox.question(
                self, 
                "配置不完整", 
                "未配置API密钥，无法使用AI功能。\n是否现在配置？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._open_settings()
                return False
            else:
                return False
        
        return True
    
    def _on_document_parsed(self, content: str):
        """文档解析完成"""
        self.document_text.setPlainText(content)
        self.tab_widget.setCurrentIndex(0)  # 切换到文档预览
    
    def _on_test_cases_generated(self, test_cases: List[TestCase]):
        """测试用例生成完成"""
        self.test_cases = test_cases
        self.test_case_display.set_test_cases(test_cases)
        self.tab_widget.setCurrentIndex(1)  # 切换到测试用例
    
    def _on_processing_completed(self, report: str):
        """处理完成"""
        # 显示报告
        self.report_text.setPlainText(report)
        
        # 恢复UI状态
        self.file_upload_widget.set_enabled(True)
        self.progress_widget.complete_processing(f"处理完成，生成了 {len(self.test_cases)} 个测试用例")
        
        self.status_bar.showMessage(f"处理完成，生成了 {len(self.test_cases)} 个测试用例")
        
        # 显示完成提示
        QMessageBox.information(self, "完成", 
            f"测试用例生成完成！\n\n"
            f"共生成 {len(self.test_cases)} 个测试用例\n"
            f"请查看测试用例标签页")
    
    def _on_error_occurred(self, error_message: str):
        """处理错误"""
        # 恢复UI状态
        self.file_upload_widget.set_enabled(True)
        self.progress_widget.error_occurred(error_message)
        
        self.status_bar.showMessage("处理失败")
        
        # 显示错误信息
        QMessageBox.critical(self, "错误", f"处理过程中发生错误:\n\n{error_message}")
    
    def _on_test_case_modified(self, test_case: TestCase):
        """测试用例修改处理"""
        # 更新测试用例列表中的对应项
        for i, case in enumerate(self.test_cases):
            if case.id == test_case.id:
                self.test_cases[i] = test_case
                break
    
    def _on_progress_completed(self):
        """进度完成处理"""
        pass
    
    def _on_progress_cancelled(self):
        """进度取消处理"""
        self._stop_processing()
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止处理线程
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.stop()
            self.processing_thread.wait()
        
        # 保存窗口状态
        self._save_window_state()
        
        # 检查是否有未保存的修改
        if self.test_case_display.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "未保存的修改",
                "有测试用例修改未保存，确定要退出吗？",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Save:
                # 这里应该保存修改，暂时跳过
                pass
        
        event.accept()
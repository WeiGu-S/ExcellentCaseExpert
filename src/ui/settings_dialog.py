#!/usr/bin/env python3
"""
设置对话框，提供API密钥配置和其他设置选项
"""

from typing import Dict, Any, Optional
import json

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QGroupBox, QFormLayout,
    QComboBox, QSpinBox, QCheckBox, QTextEdit, QMessageBox,
    QDialogButtonBox, QScrollArea, QFrame, QSlider, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from ..utils.config_helper import ConfigHelper
from ..models.data_models import LLMProvider


class SettingsDialog(QDialog):
    """设置对话框"""
    
    # 信号定义
    settings_changed = pyqtSignal(dict)  # 设置变更信号
    
    def __init__(self, parent=None):
        """初始化设置对话框"""
        super().__init__(parent)
        
        # 配置管理器
        self.config = ConfigHelper()
        
        # 设置变更标记
        self.has_changes = False
        
        # 初始化UI
        self._init_ui()
        self._load_settings()
        self._connect_signals()
        
        # 设置对话框属性
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(600, 500)
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # API配置标签页
        self.api_tab = self._create_api_tab()
        self.tab_widget.addTab(self.api_tab, "API配置")
        
        # OCR配置标签页
        self.ocr_tab = self._create_ocr_tab()
        self.tab_widget.addTab(self.ocr_tab, "OCR配置")
        
        # 界面配置标签页
        self.ui_tab = self._create_ui_tab()
        self.tab_widget.addTab(self.ui_tab, "界面配置")
        
        # 高级配置标签页
        self.advanced_tab = self._create_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "高级配置")
        
        # 按钮区域
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        
        # 自定义按钮文本
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("确定")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")
        button_box.button(QDialogButtonBox.StandardButton.Apply).setText("应用")
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).setText("恢复默认")
        
        # 连接按钮信号
        button_box.accepted.connect(self._accept_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self._restore_defaults)
        
        layout.addWidget(button_box)
        
        self.button_box = button_box
    
    def _create_api_tab(self) -> QWidget:
        """创建API配置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # OpenAI配置组
        openai_group = QGroupBox("OpenAI配置")
        openai_layout = QFormLayout(openai_group)
        
        # API密钥 - 直接显示，不加密
        self.openai_api_key = QLineEdit()
        self.openai_api_key.setPlaceholderText("输入OpenAI API密钥")
        openai_layout.addRow("API密钥:", self.openai_api_key)
        
        # 基础URL
        self.openai_base_url = QLineEdit()
        self.openai_base_url.setPlaceholderText("https://api.openai.com/v1")
        openai_layout.addRow("基础URL:", self.openai_base_url)
        
        # 模型
        self.openai_model = QComboBox()
        self.openai_model.addItems([
            "gpt-4o",
            "gpt-4o-mini", 
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ])
        self.openai_model.setEditable(True)
        openai_layout.addRow("模型:", self.openai_model)
        
        # 超时设置
        self.openai_timeout = QSpinBox()
        self.openai_timeout.setRange(10, 300)
        self.openai_timeout.setSuffix(" 秒")
        openai_layout.addRow("超时时间:", self.openai_timeout)
        
        layout.addWidget(openai_group)
        
        # Claude配置组
        claude_group = QGroupBox("Claude配置")
        claude_layout = QFormLayout(claude_group)
        
        # API密钥 - 直接显示，不加密
        self.claude_api_key = QLineEdit()
        self.claude_api_key.setPlaceholderText("输入Claude API密钥")
        claude_layout.addRow("API密钥:", self.claude_api_key)
        
        # 基础URL
        self.claude_base_url = QLineEdit()
        self.claude_base_url.setPlaceholderText("https://api.anthropic.com")
        claude_layout.addRow("基础URL:", self.claude_base_url)
        
        # 模型
        self.claude_model = QComboBox()
        self.claude_model.addItems([
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ])
        self.claude_model.setEditable(True)
        claude_layout.addRow("模型:", self.claude_model)
        
        # 超时设置
        self.claude_timeout = QSpinBox()
        self.claude_timeout.setRange(10, 300)
        self.claude_timeout.setSuffix(" 秒")
        claude_layout.addRow("超时时间:", self.claude_timeout)
        
        layout.addWidget(claude_group)
        
        # 默认提供商
        default_group = QGroupBox("默认设置")
        default_layout = QFormLayout(default_group)
        
        self.default_provider = QComboBox()
        self.default_provider.addItem("OpenAI", LLMProvider.OPENAI.value)
        self.default_provider.addItem("Claude", LLMProvider.CLAUDE.value)
        default_layout.addRow("默认提供商:", self.default_provider)
        
        layout.addWidget(default_group)
        
        # 测试连接按钮
        test_layout = QHBoxLayout()
        
        self.test_openai_btn = QPushButton("测试OpenAI连接")
        self.test_openai_btn.clicked.connect(self._test_openai_connection)
        test_layout.addWidget(self.test_openai_btn)
        
        self.test_claude_btn = QPushButton("测试Claude连接")
        self.test_claude_btn.clicked.connect(self._test_claude_connection)
        test_layout.addWidget(self.test_claude_btn)
        
        layout.addLayout(test_layout)
        
        layout.addStretch()
        
        return tab
    
    def _create_ocr_tab(self) -> QWidget:
        """创建OCR配置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Tesseract配置组
        tesseract_group = QGroupBox("Tesseract配置")
        tesseract_layout = QFormLayout(tesseract_group)
        
        # 可执行文件路径
        tesseract_path_layout = QHBoxLayout()
        
        self.tesseract_path = QLineEdit()
        self.tesseract_path.setPlaceholderText("Tesseract可执行文件路径")
        tesseract_path_layout.addWidget(self.tesseract_path)
        
        browse_tesseract_btn = QPushButton("浏览")
        browse_tesseract_btn.clicked.connect(self._browse_tesseract_path)
        tesseract_path_layout.addWidget(browse_tesseract_btn)
        
        tesseract_layout.addRow("可执行文件:", tesseract_path_layout)
        
        # 语言
        self.tesseract_lang = QLineEdit()
        self.tesseract_lang.setPlaceholderText("chi_sim+eng")
        tesseract_layout.addRow("识别语言:", self.tesseract_lang)
        
        # 配置参数
        self.tesseract_config = QTextEdit()
        self.tesseract_config.setMaximumHeight(80)
        self.tesseract_config.setPlaceholderText("--oem 3 --psm 6")
        tesseract_layout.addRow("配置参数:", self.tesseract_config)
        
        layout.addWidget(tesseract_group)
        
        # PaddleOCR配置组
        paddle_group = QGroupBox("PaddleOCR配置")
        paddle_layout = QFormLayout(paddle_group)
        
        # 启用PaddleOCR
        self.enable_paddle = QCheckBox("启用PaddleOCR")
        paddle_layout.addRow("", self.enable_paddle)
        
        # 语言
        self.paddle_lang = QComboBox()
        self.paddle_lang.addItems(["ch", "en", "ch+en"])
        paddle_layout.addRow("识别语言:", self.paddle_lang)
        
        # 使用GPU
        self.paddle_use_gpu = QCheckBox("使用GPU加速")
        paddle_layout.addRow("", self.paddle_use_gpu)
        
        layout.addWidget(paddle_group)
        
        # OCR通用配置
        general_group = QGroupBox("通用配置")
        general_layout = QFormLayout(general_group)
        
        # 重试次数
        self.ocr_retry_count = QSpinBox()
        self.ocr_retry_count.setRange(1, 10)
        general_layout.addRow("重试次数:", self.ocr_retry_count)
        
        # 超时时间
        self.ocr_timeout = QSpinBox()
        self.ocr_timeout.setRange(10, 300)
        self.ocr_timeout.setSuffix(" 秒")
        general_layout.addRow("超时时间:", self.ocr_timeout)
        
        # 图像预处理
        self.enable_image_enhance = QCheckBox("启用图像增强")
        general_layout.addRow("", self.enable_image_enhance)
        
        layout.addWidget(general_group)
        
        layout.addStretch()
        
        return tab
    
    def _create_ui_tab(self) -> QWidget:
        """创建界面配置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 主题配置组
        theme_group = QGroupBox("主题配置")
        theme_layout = QFormLayout(theme_group)
        
        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("浅色主题", "light")
        self.theme_combo.addItem("深色主题", "dark")
        self.theme_combo.addItem("跟随系统", "system")
        theme_layout.addRow("主题:", self.theme_combo)
        
        # 字体大小
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setSuffix(" pt")
        theme_layout.addRow("字体大小:", self.font_size)
        
        layout.addWidget(theme_group)
        
        # 窗口配置组
        window_group = QGroupBox("窗口配置")
        window_layout = QFormLayout(window_group)
        
        # 窗口大小
        self.window_width = QSpinBox()
        self.window_width.setRange(800, 3840)
        self.window_width.setSuffix(" px")
        window_layout.addRow("窗口宽度:", self.window_width)
        
        self.window_height = QSpinBox()
        self.window_height.setRange(600, 2160)
        self.window_height.setSuffix(" px")
        window_layout.addRow("窗口高度:", self.window_height)
        
        # 记住窗口状态
        self.remember_window_state = QCheckBox("记住窗口大小和位置")
        window_layout.addRow("", self.remember_window_state)
        
        layout.addWidget(window_group)
        
        # 显示配置组
        display_group = QGroupBox("显示配置")
        display_layout = QFormLayout(display_group)
        
        # 显示启动画面
        self.show_splash = QCheckBox("显示启动画面")
        display_layout.addRow("", self.show_splash)
        
        # 显示状态栏
        self.show_statusbar = QCheckBox("显示状态栏")
        display_layout.addRow("", self.show_statusbar)
        
        # 显示工具栏
        self.show_toolbar = QCheckBox("显示工具栏")
        display_layout.addRow("", self.show_toolbar)
        
        layout.addWidget(display_group)
        
        layout.addStretch()
        
        return tab
    
    def _create_advanced_tab(self) -> QWidget:
        """创建高级配置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 性能配置组
        performance_group = QGroupBox("性能配置")
        performance_layout = QFormLayout(performance_group)
        
        # 并发处理数
        self.max_workers = QSpinBox()
        self.max_workers.setRange(1, 16)
        performance_layout.addRow("最大并发数:", self.max_workers)
        
        # 内存限制
        self.memory_limit = QSpinBox()
        self.memory_limit.setRange(512, 8192)
        self.memory_limit.setSuffix(" MB")
        performance_layout.addRow("内存限制:", self.memory_limit)
        
        # 缓存大小
        self.cache_size = QSpinBox()
        self.cache_size.setRange(10, 1000)
        self.cache_size.setSuffix(" MB")
        performance_layout.addRow("缓存大小:", self.cache_size)
        
        layout.addWidget(performance_group)
        
        # 日志配置组
        logging_group = QGroupBox("日志配置")
        logging_layout = QFormLayout(logging_group)
        
        # 日志级别
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        logging_layout.addRow("日志级别:", self.log_level)
        
        # 日志文件路径
        log_path_layout = QHBoxLayout()
        
        self.log_file_path = QLineEdit()
        self.log_file_path.setPlaceholderText("日志文件保存路径")
        log_path_layout.addWidget(self.log_file_path)
        
        browse_log_btn = QPushButton("浏览")
        browse_log_btn.clicked.connect(self._browse_log_path)
        log_path_layout.addWidget(browse_log_btn)
        
        logging_layout.addRow("日志文件:", log_path_layout)
        
        # 保留日志天数
        self.log_retention_days = QSpinBox()
        self.log_retention_days.setRange(1, 365)
        self.log_retention_days.setSuffix(" 天")
        logging_layout.addRow("保留天数:", self.log_retention_days)
        
        layout.addWidget(logging_group)
        
        # 数据配置组
        data_group = QGroupBox("数据配置")
        data_layout = QFormLayout(data_group)
        
        # 自动保存
        self.auto_save = QCheckBox("自动保存配置")
        data_layout.addRow("", self.auto_save)
        
        # 备份配置
        self.backup_config = QCheckBox("备份配置文件")
        data_layout.addRow("", self.backup_config)
        
        # 导入/导出配置
        import_export_layout = QHBoxLayout()
        
        import_btn = QPushButton("导入配置")
        import_btn.clicked.connect(self._import_config)
        import_export_layout.addWidget(import_btn)
        
        export_btn = QPushButton("导出配置")
        export_btn.clicked.connect(self._export_config)
        import_export_layout.addWidget(export_btn)
        
        data_layout.addRow("配置管理:", import_export_layout)
        
        layout.addWidget(data_group)
        
        layout.addStretch()
        
        return tab
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 监听所有输入控件的变化
        for tab_index in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(tab_index)
            self._connect_tab_signals(tab)
    
    def _connect_tab_signals(self, widget):
        """递归连接标签页中所有控件的信号"""
        for child in widget.findChildren((QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox)):
            if isinstance(child, QLineEdit):
                child.textChanged.connect(self._mark_changed)
            elif isinstance(child, QTextEdit):
                child.textChanged.connect(self._mark_changed)
            elif isinstance(child, QComboBox):
                child.currentTextChanged.connect(self._mark_changed)
            elif isinstance(child, QSpinBox):
                child.valueChanged.connect(self._mark_changed)
            elif isinstance(child, QCheckBox):
                child.toggled.connect(self._mark_changed)
    
    def _mark_changed(self):
        """标记设置已更改"""
        self.has_changes = True
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(True)
    
    def _load_settings(self):
        """加载设置"""
        # API配置
        self.openai_api_key.setText(self.config.openai_api_key or "")
        self.openai_base_url.setText(self.config.openai_base_url or "")
        self.openai_model.setCurrentText(self.config.openai_model or "gpt-4o-mini")
        self.openai_timeout.setValue(self.config.openai_timeout or 60)
        
        self.claude_api_key.setText(self.config.claude_api_key or "")
        self.claude_base_url.setText(self.config.claude_base_url or "")
        self.claude_model.setCurrentText(self.config.claude_model or "claude-3-5-sonnet-20241022")
        self.claude_timeout.setValue(self.config.claude_timeout or 60)
        
        # 设置默认提供商
        if self.config.default_llm_provider:
            provider_index = self.default_provider.findData(self.config.default_llm_provider.value)
            if provider_index >= 0:
                self.default_provider.setCurrentIndex(provider_index)
        
        # OCR配置
        self.tesseract_path.setText(self.config.tesseract_path or "")
        self.tesseract_lang.setText(self.config.tesseract_lang or "chi_sim+eng")
        self.tesseract_config.setPlainText(self.config.tesseract_config or "--oem 3 --psm 6")
        
        self.enable_paddle.setChecked(self.config.enable_paddle_ocr or False)
        self.paddle_lang.setCurrentText(self.config.paddle_lang or "ch")
        self.paddle_use_gpu.setChecked(self.config.paddle_use_gpu or False)
        
        self.ocr_retry_count.setValue(self.config.ocr_retry_count or 3)
        self.ocr_timeout.setValue(self.config.ocr_timeout or 30)
        self.enable_image_enhance.setChecked(self.config.enable_image_enhance or True)
        
        # UI配置
        theme_index = self.theme_combo.findData(self.config.theme or "light")
        if theme_index >= 0:
            self.theme_combo.setCurrentIndex(theme_index)
        
        self.font_size.setValue(self.config.font_size or 10)
        self.window_width.setValue(self.config.window_width or 1280)
        self.window_height.setValue(self.config.window_height or 720)
        self.remember_window_state.setChecked(self.config.remember_window_state or True)
        self.show_splash.setChecked(self.config.show_splash or True)
        self.show_statusbar.setChecked(self.config.show_statusbar or True)
        self.show_toolbar.setChecked(self.config.show_toolbar or True)
        
        # 高级配置
        self.max_workers.setValue(self.config.max_workers or 4)
        self.memory_limit.setValue(self.config.memory_limit or 1024)
        self.cache_size.setValue(self.config.cache_size or 100)
        self.log_level.setCurrentText(self.config.log_level or "INFO")
        self.log_file_path.setText(self.config.log_file_path or "")
        self.log_retention_days.setValue(self.config.log_retention_days or 30)
        self.auto_save.setChecked(self.config.auto_save or True)
        self.backup_config.setChecked(self.config.backup_config or True)
        
        # 重置更改标记
        self.has_changes = False
        self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
    
    def _save_settings(self) -> bool:
        """保存设置"""
        try:
            # 收集所有设置
            settings = self._collect_settings()
            
            # 验证设置
            if not self._validate_settings(settings):
                return False
            
            # 保存到配置管理器
            self.config.update_llm_config(
                openai_api_key=settings['openai_api_key'],
                openai_base_url=settings['openai_base_url'],
                openai_model=settings['openai_model'],
                openai_timeout=settings['openai_timeout'],
                claude_api_key=settings['claude_api_key'],
                claude_base_url=settings['claude_base_url'],
                claude_model=settings['claude_model'],
                claude_timeout=settings['claude_timeout'],
                default_provider=LLMProvider(settings['default_provider'])
            )
            
            self.config.update_ocr_config(
                tesseract_path=settings['tesseract_path'],
                tesseract_lang=settings['tesseract_lang'],
                tesseract_config=settings['tesseract_config'],
                enable_paddle_ocr=settings['enable_paddle'],
                paddle_lang=settings['paddle_lang'],
                paddle_use_gpu=settings['paddle_use_gpu'],
                retry_count=settings['ocr_retry_count'],
                timeout=settings['ocr_timeout'],
                enable_image_enhance=settings['enable_image_enhance']
            )
            
            self.config.update_ui_config(
                theme=settings['theme'],
                font_size=settings['font_size'],
                window_width=settings['window_width'],
                window_height=settings['window_height'],
                remember_window_state=settings['remember_window_state'],
                show_splash=settings['show_splash'],
                show_statusbar=settings['show_statusbar'],
                show_toolbar=settings['show_toolbar']
            )
            
            # 发送设置变更信号
            self.settings_changed.emit(settings)
            
            # 重置更改标记
            self.has_changes = False
            self.button_box.button(QDialogButtonBox.StandardButton.Apply).setEnabled(False)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存设置时发生错误:\n{str(e)}")
            return False
    
    def _collect_settings(self) -> Dict[str, Any]:
        """收集所有设置"""
        return {
            # API配置
            'openai_api_key': self.openai_api_key.text().strip(),
            'openai_base_url': self.openai_base_url.text().strip(),
            'openai_model': self.openai_model.currentText().strip(),
            'openai_timeout': self.openai_timeout.value(),
            'claude_api_key': self.claude_api_key.text().strip(),
            'claude_base_url': self.claude_base_url.text().strip(),
            'claude_model': self.claude_model.currentText().strip(),
            'claude_timeout': self.claude_timeout.value(),
            'default_provider': self.default_provider.currentData(),
            
            # OCR配置
            'tesseract_path': self.tesseract_path.text().strip(),
            'tesseract_lang': self.tesseract_lang.text().strip(),
            'tesseract_config': self.tesseract_config.toPlainText().strip(),
            'enable_paddle': self.enable_paddle.isChecked(),
            'paddle_lang': self.paddle_lang.currentText(),
            'paddle_use_gpu': self.paddle_use_gpu.isChecked(),
            'ocr_retry_count': self.ocr_retry_count.value(),
            'ocr_timeout': self.ocr_timeout.value(),
            'enable_image_enhance': self.enable_image_enhance.isChecked(),
            
            # UI配置
            'theme': self.theme_combo.currentData(),
            'font_size': self.font_size.value(),
            'window_width': self.window_width.value(),
            'window_height': self.window_height.value(),
            'remember_window_state': self.remember_window_state.isChecked(),
            'show_splash': self.show_splash.isChecked(),
            'show_statusbar': self.show_statusbar.isChecked(),
            'show_toolbar': self.show_toolbar.isChecked(),
            
            # 高级配置
            'max_workers': self.max_workers.value(),
            'memory_limit': self.memory_limit.value(),
            'cache_size': self.cache_size.value(),
            'log_level': self.log_level.currentText(),
            'log_file_path': self.log_file_path.text().strip(),
            'log_retention_days': self.log_retention_days.value(),
            'auto_save': self.auto_save.isChecked(),
            'backup_config': self.backup_config.isChecked()
        }
    
    def _validate_settings(self, settings: Dict[str, Any]) -> bool:
        """验证设置"""
        # 验证API密钥
        if not settings['openai_api_key'] and not settings['claude_api_key']:
            QMessageBox.warning(self, "验证失败", "至少需要配置一个API密钥")
            return False
        
        # 验证URL格式
        for url_key in ['openai_base_url', 'claude_base_url']:
            url = settings[url_key]
            if url and not (url.startswith('http://') or url.startswith('https://')):
                QMessageBox.warning(self, "验证失败", f"{url_key}格式不正确，必须以http://或https://开头")
                return False
        
        return True
    
    def _accept_settings(self):
        """接受设置"""
        if self.has_changes:
            if self._save_settings():
                self.accept()
        else:
            self.accept()
    
    def _apply_settings(self):
        """应用设置"""
        self._save_settings()
    
    def _restore_defaults(self):
        """恢复默认设置"""
        reply = QMessageBox.question(
            self, 
            "确认恢复", 
            "确定要恢复所有设置为默认值吗？\n这将清除所有自定义配置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 重置配置管理器
            self.config.reset_to_defaults()
            
            # 重新加载设置
            self._load_settings()
            
            QMessageBox.information(self, "恢复完成", "所有设置已恢复为默认值")
    

    
    def _test_openai_connection(self):
        """测试OpenAI连接"""
        api_key = self.openai_api_key.text().strip()
        if not api_key:
            QMessageBox.warning(self, "测试失败", "请先输入OpenAI API密钥")
            return
        
        # 这里应该实际测试连接，暂时显示提示
        QMessageBox.information(self, "测试连接", "OpenAI连接测试功能待实现")
    
    def _test_claude_connection(self):
        """测试Claude连接"""
        api_key = self.claude_api_key.text().strip()
        if not api_key:
            QMessageBox.warning(self, "测试失败", "请先输入Claude API密钥")
            return
        
        # 这里应该实际测试连接，暂时显示提示
        QMessageBox.information(self, "测试连接", "Claude连接测试功能待实现")
    
    def _browse_tesseract_path(self):
        """浏览Tesseract路径"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Tesseract可执行文件",
            "",
            "可执行文件 (*.exe);;所有文件 (*.*)"
        )
        
        if file_path:
            self.tesseract_path.setText(file_path)
    
    def _browse_log_path(self):
        """浏览日志路径"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "选择日志文件保存位置",
            "test_case_generator.log",
            "日志文件 (*.log);;所有文件 (*.*)"
        )
        
        if file_path:
            self.log_file_path.setText(file_path)
    
    def _import_config(self):
        """导入配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入配置文件",
            "",
            "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # 这里应该实际导入配置，暂时显示提示
                QMessageBox.information(self, "导入配置", "配置导入功能待实现")
                
            except Exception as e:
                QMessageBox.critical(self, "导入失败", f"导入配置文件时发生错误:\n{str(e)}")
    
    def _export_config(self):
        """导出配置"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出配置文件",
            "config.json",
            "JSON文件 (*.json);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                # 收集当前设置
                settings = self._collect_settings()
                
                # 导出到文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "导出成功", f"配置已导出到:\n{file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出配置文件时发生错误:\n{str(e)}")
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.has_changes:
            reply = QMessageBox.question(
                self,
                "未保存的更改",
                "设置已更改但未保存，确定要关闭吗？",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if self._save_settings():
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
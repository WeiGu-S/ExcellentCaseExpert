#!/usr/bin/env python3
"""
文件上传组件，支持拖拽和点击上传
"""

import os
from typing import List, Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QProgressBar, QFrame,
    QFileDialog, QMessageBox, QGroupBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QUrl, QTimer
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont, QPalette

from ..utils.constants import SUPPORTED_FILE_TYPES, MAX_FILE_SIZE_MB


class FileUploadWidget(QWidget):
    """文件上传组件"""
    
    # 信号定义
    files_selected = pyqtSignal(list)  # 文件选择信号
    upload_progress = pyqtSignal(int)  # 上传进度信号
    upload_completed = pyqtSignal(list)  # 上传完成信号
    upload_error = pyqtSignal(str)  # 上传错误信号
    
    def __init__(self, parent=None):
        """初始化文件上传组件"""
        super().__init__(parent)
        
        # 状态变量
        self.selected_files: List[str] = []
        self.is_uploading = False
        
        # 初始化UI
        self._init_ui()
        self._setup_drag_drop()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 拖拽区域
        self.drop_area = self._create_drop_area()
        layout.addWidget(self.drop_area)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 选择文件按钮
        self.select_button = QPushButton("选择文件")
        self.select_button.setMinimumHeight(35)
        self.select_button.clicked.connect(self._select_files)
        button_layout.addWidget(self.select_button)
        
        # 清空按钮
        self.clear_button = QPushButton("清空")
        self.clear_button.setMinimumHeight(35)
        self.clear_button.setEnabled(False)
        self.clear_button.clicked.connect(self._clear_files)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        
        # 文件列表
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        self.file_list.setAlternatingRowColors(True)
        layout.addWidget(self.file_list)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("请选择或拖拽文件到上方区域")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addWidget(self.status_label)
    
    def _create_drop_area(self) -> QFrame:
        """创建拖拽区域"""
        drop_area = QFrame()
        drop_area.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        drop_area.setLineWidth(2)
        drop_area.setMinimumHeight(120)
        drop_area.setStyleSheet("""
            QFrame {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            QFrame:hover {
                border-color: #2196F3;
                background-color: #f0f8ff;
            }
        """)
        
        # 拖拽区域布局
        layout = QVBoxLayout(drop_area)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 图标标签（使用文字代替图标）
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 32px; color: #666666;")
        layout.addWidget(icon_label)
        
        # 提示文字
        hint_label = QLabel("拖拽文件到此处或点击选择文件")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("font-size: 14px; color: #666666; font-weight: bold;")
        layout.addWidget(hint_label)
        
        # 支持格式提示
        format_label = QLabel("支持格式: PNG, JPG, PDF, DOCX")
        format_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        format_label.setStyleSheet("font-size: 11px; color: #999999;")
        layout.addWidget(format_label)
        
        return drop_area
    
    def _setup_drag_drop(self):
        """设置拖拽功能"""
        self.setAcceptDrops(True)
        self.drop_area.setAcceptDrops(True)
    
    def _connect_signals(self):
        """连接信号和槽"""
        self.upload_progress.connect(self.progress_bar.setValue)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否包含支持的文件类型
            urls = event.mimeData().urls()
            valid_files = []
            
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if self._is_supported_file(file_path):
                        valid_files.append(file_path)
            
            if valid_files:
                event.acceptProposedAction()
                self._highlight_drop_area(True)
            else:
                event.ignore()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self._highlight_drop_area(False)
        super().dragLeaveEvent(event)
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件"""
        self._highlight_drop_area(False)
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            files = []
            
            for url in urls:
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if self._is_supported_file(file_path):
                        files.append(file_path)
            
            if files:
                self._add_files(files)
                event.acceptProposedAction()
            else:
                QMessageBox.warning(self, "警告", "没有找到支持的文件格式")
        
        event.ignore()
    
    def _highlight_drop_area(self, highlight: bool):
        """高亮拖拽区域"""
        if highlight:
            self.drop_area.setStyleSheet("""
                QFrame {
                    border: 2px dashed #2196F3;
                    border-radius: 10px;
                    background-color: #e3f2fd;
                }
            """)
        else:
            self.drop_area.setStyleSheet("""
                QFrame {
                    border: 2px dashed #cccccc;
                    border-radius: 10px;
                    background-color: #f9f9f9;
                }
                QFrame:hover {
                    border-color: #2196F3;
                    background-color: #f0f8ff;
                }
            """)
    
    def _select_files(self):
        """选择文件对话框"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter(self._get_file_filter())
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            self._add_files(files)
    
    def _add_files(self, files: List[str]):
        """添加文件到列表"""
        valid_files = []
        invalid_files = []
        
        for file_path in files:
            if self._validate_file(file_path):
                if file_path not in self.selected_files:
                    valid_files.append(file_path)
                    self.selected_files.append(file_path)
            else:
                invalid_files.append(file_path)
        
        # 更新文件列表显示
        if valid_files:
            self._update_file_list()
            self.files_selected.emit(self.selected_files)
        
        # 显示无效文件警告
        if invalid_files:
            invalid_names = [Path(f).name for f in invalid_files]
            QMessageBox.warning(
                self, 
                "文件验证失败", 
                f"以下文件不符合要求:\n\n{chr(10).join(invalid_names)}\n\n"
                f"请确保文件格式正确且大小不超过 {MAX_FILE_SIZE_MB}MB"
            )
    
    def _update_file_list(self):
        """更新文件列表显示"""
        self.file_list.clear()
        
        for file_path in self.selected_files:
            file_info = Path(file_path)
            file_size = file_info.stat().st_size / (1024 * 1024)  # MB
            
            item_text = f"{file_info.name} ({file_size:.1f}MB)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            
            # 设置图标（使用文字表示）
            if file_info.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                item.setText(f"🖼️ {item_text}")
            elif file_info.suffix.lower() == '.pdf':
                item.setText(f"📄 {item_text}")
            elif file_info.suffix.lower() == '.docx':
                item.setText(f"📝 {item_text}")
            
            self.file_list.addItem(item)
        
        # 更新状态
        count = len(self.selected_files)
        if count == 0:
            self.status_label.setText("请选择或拖拽文件到上方区域")
            self.clear_button.setEnabled(False)
        else:
            self.status_label.setText(f"已选择 {count} 个文件")
            self.clear_button.setEnabled(True)
    
    def _clear_files(self):
        """清空文件列表"""
        self.selected_files.clear()
        self._update_file_list()
        self.files_selected.emit([])
    
    def _validate_file(self, file_path: str) -> bool:
        """验证文件"""
        try:
            file_info = Path(file_path)
            
            # 检查文件是否存在
            if not file_info.exists():
                return False
            
            # 检查文件格式
            if not self._is_supported_file(file_path):
                return False
            
            # 检查文件大小
            file_size_mb = file_info.stat().st_size / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _is_supported_file(self, file_path: str) -> bool:
        """检查是否为支持的文件类型"""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in SUPPORTED_FILE_TYPES
    
    def _get_file_filter(self) -> str:
        """获取文件过滤器"""
        filters = []
        
        # 图片文件
        filters.append("图片文件 (*.png *.jpg *.jpeg)")
        
        # PDF文件
        filters.append("PDF文件 (*.pdf)")
        
        # Word文档
        filters.append("Word文档 (*.docx)")
        
        # 所有支持的文件
        all_types = " ".join([f"*{ext}" for ext in SUPPORTED_FILE_TYPES])
        filters.insert(0, f"所有支持的文件 ({all_types})")
        
        # 所有文件
        filters.append("所有文件 (*.*)")
        
        return ";;".join(filters)
    
    def set_files(self, files: List[str]):
        """设置文件列表（外部调用）"""
        self.selected_files.clear()
        self._add_files(files)
    
    def get_files(self) -> List[str]:
        """获取当前选择的文件"""
        return self.selected_files.copy()
    
    def clear(self):
        """清空组件"""
        self._clear_files()
    
    def set_enabled(self, enabled: bool):
        """设置组件启用状态"""
        self.select_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled and len(self.selected_files) > 0)
        self.setAcceptDrops(enabled)
    
    def show_progress(self, show: bool = True):
        """显示/隐藏进度条"""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setValue(0)
    
    def update_progress(self, value: int):
        """更新进度"""
        self.progress_bar.setValue(value)
        if value >= 100:
            QTimer.singleShot(1000, lambda: self.show_progress(False))
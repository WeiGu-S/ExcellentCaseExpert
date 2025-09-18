#!/usr/bin/env python3
"""
进度显示组件，显示处理进度和状态信息
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QTextEdit, QFrame, QScrollArea, QGroupBox, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette


class ProgressWidget(QWidget):
    """进度显示组件"""
    
    # 信号定义
    progress_completed = pyqtSignal()  # 进度完成信号
    progress_cancelled = pyqtSignal()  # 进度取消信号
    
    def __init__(self, parent=None):
        """初始化进度组件"""
        super().__init__(parent)
        
        # 状态变量
        self.is_processing = False
        self.start_time: Optional[datetime] = None
        self.current_step = 0
        self.total_steps = 0
        self.step_messages: List[str] = []
        
        # 定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_elapsed_time)
        
        # 初始化UI
        self._init_ui()
        self._reset_display()
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 总体进度区域
        overall_group = QGroupBox("总体进度")
        overall_layout = QVBoxLayout(overall_group)
        
        # 进度条
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        self.overall_progress.setValue(0)
        self.overall_progress.setTextVisible(True)
        overall_layout.addWidget(self.overall_progress)
        
        # 状态信息
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("font-weight: bold; color: #333333;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.time_label = QLabel("00:00:00")
        self.time_label.setStyleSheet("font-family: monospace; color: #666666;")
        status_layout.addWidget(self.time_label)
        
        overall_layout.addLayout(status_layout)
        
        layout.addWidget(overall_group)
        
        # 步骤进度区域
        steps_group = QGroupBox("处理步骤")
        steps_layout = QVBoxLayout(steps_group)
        
        # 当前步骤信息
        current_step_layout = QHBoxLayout()
        
        self.step_label = QLabel("步骤 0/0")
        self.step_label.setStyleSheet("font-weight: bold;")
        current_step_layout.addWidget(self.step_label)
        
        current_step_layout.addStretch()
        
        self.step_progress = QProgressBar()
        self.step_progress.setMinimum(0)
        self.step_progress.setMaximum(100)
        self.step_progress.setValue(0)
        self.step_progress.setMaximumWidth(150)
        current_step_layout.addWidget(self.step_progress)
        
        steps_layout.addLayout(current_step_layout)
        
        # 当前步骤描述
        self.current_step_label = QLabel("等待开始...")
        self.current_step_label.setWordWrap(True)
        self.current_step_label.setStyleSheet("color: #666666; padding: 5px;")
        steps_layout.addWidget(self.current_step_label)
        
        layout.addWidget(steps_group)
        
        # 详细日志区域
        log_group = QGroupBox("处理日志")
        log_layout = QVBoxLayout(log_group)
        
        # 日志显示
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                font-family: monospace;
                font-size: 11px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        # 日志控制按钮
        log_button_layout = QHBoxLayout()
        
        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.setMaximumWidth(80)
        self.clear_log_btn.clicked.connect(self._clear_log)
        log_button_layout.addWidget(self.clear_log_btn)
        
        log_button_layout.addStretch()
        
        self.auto_scroll_btn = QPushButton("自动滚动")
        self.auto_scroll_btn.setMaximumWidth(80)
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        log_button_layout.addWidget(self.auto_scroll_btn)
        
        log_layout.addLayout(log_button_layout)
        
        layout.addWidget(log_group)
        
        # 添加弹性空间
        layout.addStretch()
    
    def start_processing(self, total_steps: int = 5):
        """开始处理"""
        self.is_processing = True
        self.start_time = datetime.now()
        self.current_step = 0
        self.total_steps = total_steps
        self.step_messages.clear()
        
        # 重置进度
        self.overall_progress.setValue(0)
        self.step_progress.setValue(0)
        
        # 更新显示
        self.status_label.setText("处理中...")
        self.status_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.step_label.setText(f"步骤 0/{total_steps}")
        self.current_step_label.setText("正在初始化...")
        
        # 启动定时器
        self.update_timer.start(1000)  # 每秒更新一次
        
        # 添加开始日志
        self._add_log("开始处理", "INFO")
    
    def update_progress(self, step: int, step_name: str, step_progress: int = 0, message: str = ""):
        """更新进度"""
        if not self.is_processing:
            return
        
        self.current_step = step
        
        # 更新总体进度
        overall_progress = int((step / self.total_steps) * 100)
        self.overall_progress.setValue(overall_progress)
        
        # 更新步骤进度
        self.step_progress.setValue(step_progress)
        self.step_label.setText(f"步骤 {step}/{self.total_steps}")
        self.current_step_label.setText(step_name)
        
        # 添加日志
        if message:
            self._add_log(f"[步骤{step}] {message}", "INFO")
        else:
            self._add_log(f"[步骤{step}] {step_name}", "INFO")
        
        # 保存步骤信息
        if len(self.step_messages) < step:
            self.step_messages.extend([""] * (step - len(self.step_messages)))
        if step > 0:
            self.step_messages[step - 1] = step_name
    
    def complete_step(self, step: int, message: str = ""):
        """完成步骤"""
        if not self.is_processing:
            return
        
        # 更新步骤进度为100%
        self.step_progress.setValue(100)
        
        # 添加完成日志
        log_message = message or f"步骤{step}完成"
        self._add_log(f"✓ {log_message}", "SUCCESS")
    
    def complete_processing(self, message: str = "处理完成"):
        """完成处理"""
        if not self.is_processing:
            return
        
        self.is_processing = False
        
        # 更新进度为100%
        self.overall_progress.setValue(100)
        self.step_progress.setValue(100)
        
        # 更新状态
        self.status_label.setText("完成")
        self.status_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        self.current_step_label.setText(message)
        
        # 停止定时器
        self.update_timer.stop()
        
        # 添加完成日志
        self._add_log(f"✓ {message}", "SUCCESS")
        
        # 发送完成信号
        self.progress_completed.emit()
    
    def cancel_processing(self, message: str = "处理已取消"):
        """取消处理"""
        if not self.is_processing:
            return
        
        self.is_processing = False
        
        # 更新状态
        self.status_label.setText("已取消")
        self.status_label.setStyleSheet("font-weight: bold; color: #f44336;")
        self.current_step_label.setText(message)
        
        # 停止定时器
        self.update_timer.stop()
        
        # 添加取消日志
        self._add_log(f"✗ {message}", "ERROR")
        
        # 发送取消信号
        self.progress_cancelled.emit()
    
    def error_occurred(self, error_message: str):
        """发生错误"""
        if not self.is_processing:
            return
        
        self.is_processing = False
        
        # 更新状态
        self.status_label.setText("错误")
        self.status_label.setStyleSheet("font-weight: bold; color: #f44336;")
        self.current_step_label.setText("处理过程中发生错误")
        
        # 停止定时器
        self.update_timer.stop()
        
        # 添加错误日志
        self._add_log(f"✗ 错误: {error_message}", "ERROR")
    
    def reset(self):
        """重置进度"""
        self.is_processing = False
        self.start_time = None
        self.current_step = 0
        self.total_steps = 0
        self.step_messages.clear()
        
        # 停止定时器
        self.update_timer.stop()
        
        # 重置显示
        self._reset_display()
    
    def _reset_display(self):
        """重置显示"""
        # 重置进度条
        self.overall_progress.setValue(0)
        self.step_progress.setValue(0)
        
        # 重置标签
        self.status_label.setText("就绪")
        self.status_label.setStyleSheet("font-weight: bold; color: #333333;")
        self.time_label.setText("00:00:00")
        self.step_label.setText("步骤 0/0")
        self.current_step_label.setText("等待开始...")
        
        # 清空日志
        self.log_text.clear()
    
    def _update_elapsed_time(self):
        """更新已用时间"""
        if not self.start_time:
            return
        
        elapsed = datetime.now() - self.start_time
        
        # 格式化时间显示
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60
        seconds = elapsed.seconds % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.time_label.setText(time_str)
    
    def _add_log(self, message: str, level: str = "INFO"):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 根据级别设置颜色
        if level == "SUCCESS":
            color = "#4CAF50"
        elif level == "ERROR":
            color = "#f44336"
        elif level == "WARNING":
            color = "#ff9800"
        else:
            color = "#333333"
        
        # 格式化日志
        log_entry = f"<span style='color: #666666;'>[{timestamp}]</span> " \
                   f"<span style='color: {color};'>{message}</span>"
        
        # 添加到日志显示
        self.log_text.append(log_entry)
        
        # 自动滚动到底部
        if self.auto_scroll_btn.isChecked():
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def _clear_log(self):
        """清空日志"""
        self.log_text.clear()
    
    def get_progress_info(self) -> Dict:
        """获取进度信息"""
        elapsed_time = None
        if self.start_time:
            elapsed_time = datetime.now() - self.start_time
        
        return {
            'is_processing': self.is_processing,
            'current_step': self.current_step,
            'total_steps': self.total_steps,
            'overall_progress': self.overall_progress.value(),
            'step_progress': self.step_progress.value(),
            'elapsed_time': elapsed_time,
            'step_messages': self.step_messages.copy()
        }
    
    def set_step_names(self, step_names: List[str]):
        """设置步骤名称"""
        self.total_steps = len(step_names)
        self.step_messages = step_names.copy()
        self.step_label.setText(f"步骤 0/{self.total_steps}")
    
    def is_busy(self) -> bool:
        """是否正在处理"""
        return self.is_processing
#!/usr/bin/env python3
"""
测试用例显示组件，按模块-功能点层级展示用例
"""

from typing import List, Dict, Optional, Any
from collections import defaultdict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QSplitter, QLabel, QPushButton, QGroupBox, QTabWidget,
    QScrollArea, QFrame, QHeaderView, QMenu, QMessageBox, QInputDialog,
    QComboBox, QSpinBox, QCheckBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QBrush, QAction

from ..models.data_models import TestCase, TestCaseType, Priority
from ..utils.constants import TEST_CASE_FIELDS


class TestCaseDisplayWidget(QWidget):
    """测试用例显示组件"""
    
    # 信号定义
    test_case_selected = pyqtSignal(TestCase)  # 测试用例选择信号
    test_case_modified = pyqtSignal(TestCase)  # 测试用例修改信号
    test_cases_exported = pyqtSignal(list)  # 测试用例导出信号
    
    def __init__(self, parent=None):
        """初始化测试用例显示组件"""
        super().__init__(parent)
        
        # 数据存储
        self.test_cases: List[TestCase] = []
        self.current_test_case: Optional[TestCase] = None
        self.modified_cases: Dict[str, TestCase] = {}
        
        # 初始化UI
        self._init_ui()
        self._setup_tree_widget()
        self._connect_signals()
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧：测试用例树
        left_panel = self._create_tree_panel()
        splitter.addWidget(left_panel)
        
        # 右侧：测试用例详情
        right_panel = self._create_detail_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([400, 600])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
    
    def _create_tree_panel(self) -> QWidget:
        """创建测试用例树面板"""
        panel = QWidget()
        panel.setMaximumWidth(450)
        panel.setMinimumWidth(300)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 标题和统计
        header_layout = QHBoxLayout()
        
        title_label = QLabel("测试用例列表")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        self.count_label = QLabel("0 个用例")
        self.count_label.setStyleSheet("color: #666666; font-size: 12px;")
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # 过滤器
        filter_layout = QHBoxLayout()
        
        # 类型过滤
        self.type_filter = QComboBox()
        self.type_filter.addItem("所有类型", "")
        self.type_filter.addItem("功能测试", TestCaseType.FUNCTIONAL.value)
        self.type_filter.addItem("界面测试", TestCaseType.UI.value)
        self.type_filter.addItem("性能测试", TestCaseType.PERFORMANCE.value)
        self.type_filter.addItem("安全测试", TestCaseType.SECURITY.value)
        self.type_filter.addItem("兼容性测试", TestCaseType.COMPATIBILITY.value)
        self.type_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        # 优先级过滤
        self.priority_filter = QComboBox()
        self.priority_filter.addItem("所有优先级", "")
        self.priority_filter.addItem("高", Priority.HIGH.value)
        self.priority_filter.addItem("中", Priority.MEDIUM.value)
        self.priority_filter.addItem("低", Priority.LOW.value)
        self.priority_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.priority_filter)
        
        layout.addLayout(filter_layout)
        
        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索测试用例...")
        self.search_box.textChanged.connect(self._apply_filters)
        layout.addWidget(self.search_box)
        
        # 测试用例树
        self.tree_widget = QTreeWidget()
        layout.addWidget(self.tree_widget)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.expand_all_btn = QPushButton("展开全部")
        self.expand_all_btn.clicked.connect(self.tree_widget.expandAll)
        button_layout.addWidget(self.expand_all_btn)
        
        self.collapse_all_btn = QPushButton("折叠全部")
        self.collapse_all_btn.clicked.connect(self.tree_widget.collapseAll)
        button_layout.addWidget(self.collapse_all_btn)
        
        layout.addLayout(button_layout)
        
        return panel
    
    def _create_detail_panel(self) -> QWidget:
        """创建测试用例详情面板"""
        panel = QWidget()
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 标题栏
        header_layout = QHBoxLayout()
        
        self.detail_title = QLabel("请选择测试用例")
        self.detail_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.detail_title)
        
        header_layout.addStretch()
        
        # 编辑按钮
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self._toggle_edit_mode)
        header_layout.addWidget(self.edit_btn)
        
        # 保存按钮
        self.save_btn = QPushButton("保存")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self._save_changes)
        header_layout.addWidget(self.save_btn)
        
        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_changes)
        header_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(header_layout)
        
        # 详情内容
        self.detail_scroll = QScrollArea()
        self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.setFrameStyle(QFrame.Shape.NoFrame)
        
        self.detail_content = QWidget()
        self.detail_layout = QVBoxLayout(self.detail_content)
        self.detail_scroll.setWidget(self.detail_content)
        
        layout.addWidget(self.detail_scroll)
        
        # 初始化详情表单
        self._init_detail_form()
        
        return panel
    
    def _setup_tree_widget(self):
        """设置测试用例树"""
        # 设置列
        self.tree_widget.setHeaderLabels(["测试用例", "类型", "优先级", "状态"])
        
        # 设置列宽
        header = self.tree_widget.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # 设置选择模式
        self.tree_widget.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        
        # 启用右键菜单
        self.tree_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)
    
    def _init_detail_form(self):
        """初始化详情表单"""
        # 清空现有内容
        for i in reversed(range(self.detail_layout.count())):
            self.detail_layout.itemAt(i).widget().setParent(None)
        
        # 创建表单字段
        self.form_fields = {}
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout(basic_group)
        
        # 测试用例ID
        self.form_fields['id'] = QLineEdit()
        self.form_fields['id'].setReadOnly(True)
        basic_layout.addWidget(QLabel("测试用例ID:"))
        basic_layout.addWidget(self.form_fields['id'])
        
        # 测试用例标题
        self.form_fields['title'] = QLineEdit()
        basic_layout.addWidget(QLabel("标题:"))
        basic_layout.addWidget(self.form_fields['title'])
        
        # 模块
        self.form_fields['module'] = QLineEdit()
        basic_layout.addWidget(QLabel("模块:"))
        basic_layout.addWidget(self.form_fields['module'])
        
        # 功能点
        self.form_fields['function'] = QLineEdit()
        basic_layout.addWidget(QLabel("功能点:"))
        basic_layout.addWidget(self.form_fields['function'])
        
        # 类型
        self.form_fields['type'] = QComboBox()
        for test_type in TestCaseType:
            self.form_fields['type'].addItem(test_type.value, test_type)
        basic_layout.addWidget(QLabel("类型:"))
        basic_layout.addWidget(self.form_fields['type'])
        
        # 优先级
        self.form_fields['priority'] = QComboBox()
        for priority in Priority:
            self.form_fields['priority'].addItem(priority.value, priority)
        basic_layout.addWidget(QLabel("优先级:"))
        basic_layout.addWidget(self.form_fields['priority'])
        
        self.detail_layout.addWidget(basic_group)
        
        # 测试内容组
        content_group = QGroupBox("测试内容")
        content_layout = QVBoxLayout(content_group)
        
        # 前置条件
        self.form_fields['preconditions'] = QTextEdit()
        self.form_fields['preconditions'].setMaximumHeight(80)
        content_layout.addWidget(QLabel("前置条件:"))
        content_layout.addWidget(self.form_fields['preconditions'])
        
        # 测试步骤
        self.form_fields['steps'] = QTextEdit()
        self.form_fields['steps'].setMaximumHeight(120)
        content_layout.addWidget(QLabel("测试步骤:"))
        content_layout.addWidget(self.form_fields['steps'])
        
        # 预期结果
        self.form_fields['expected_result'] = QTextEdit()
        self.form_fields['expected_result'].setMaximumHeight(80)
        content_layout.addWidget(QLabel("预期结果:"))
        content_layout.addWidget(self.form_fields['expected_result'])
        
        self.detail_layout.addWidget(content_group)
        
        # 设置所有字段为只读
        self._set_form_readonly(True)
    
    def _connect_signals(self):
        """连接信号和槽"""
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        
        # 连接表单字段变化信号
        for field_name, widget in self.form_fields.items():
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._on_field_changed)
            elif isinstance(widget, QTextEdit):
                widget.textChanged.connect(self._on_field_changed)
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self._on_field_changed)
    
    def set_test_cases(self, test_cases: List[TestCase]):
        """设置测试用例列表"""
        self.test_cases = test_cases
        self.modified_cases.clear()
        self._update_tree()
        self._update_count_label()
    
    def _update_tree(self):
        """更新测试用例树"""
        self.tree_widget.clear()
        
        if not self.test_cases:
            return
        
        # 按模块和功能点分组
        grouped_cases = self._group_test_cases()
        
        # 创建树节点
        for module_name, functions in grouped_cases.items():
            module_item = QTreeWidgetItem([module_name, "", "", ""])
            module_item.setFont(0, QFont("", -1, QFont.Weight.Bold))
            module_item.setBackground(0, QBrush(QColor("#f0f0f0")))
            
            for function_name, cases in functions.items():
                function_item = QTreeWidgetItem([function_name, "", "", ""])
                function_item.setFont(0, QFont("", -1, QFont.Weight.Bold))
                function_item.setBackground(0, QBrush(QColor("#f8f8f8")))
                
                for case in cases:
                    if self._should_show_case(case):
                        case_item = self._create_case_item(case)
                        function_item.addChild(case_item)
                
                if function_item.childCount() > 0:
                    module_item.addChild(function_item)
            
            if module_item.childCount() > 0:
                self.tree_widget.addTopLevelItem(module_item)
        
        # 展开第一级
        self.tree_widget.expandToDepth(0)
    
    def _group_test_cases(self) -> Dict[str, Dict[str, List[TestCase]]]:
        """按模块和功能点分组测试用例"""
        grouped = defaultdict(lambda: defaultdict(list))
        
        for case in self.test_cases:
            module = case.module or "未分类模块"
            function = case.function or "未分类功能"
            grouped[module][function].append(case)
        
        return dict(grouped)
    
    def _create_case_item(self, test_case: TestCase) -> QTreeWidgetItem:
        """创建测试用例树节点"""
        item = QTreeWidgetItem([
            test_case.title,
            test_case.type.value if test_case.type else "",
            test_case.priority.value if test_case.priority else "",
            "已修改" if test_case.id in self.modified_cases else "正常"
        ])
        
        # 存储测试用例数据
        item.setData(0, Qt.ItemDataRole.UserRole, test_case)
        
        # 设置颜色
        if test_case.id in self.modified_cases:
            item.setForeground(0, QBrush(QColor("#ff9800")))
        
        # 根据优先级设置颜色
        if test_case.priority == Priority.HIGH:
            item.setForeground(1, QBrush(QColor("#f44336")))
        elif test_case.priority == Priority.MEDIUM:
            item.setForeground(1, QBrush(QColor("#ff9800")))
        else:
            item.setForeground(1, QBrush(QColor("#4caf50")))
        
        return item
    
    def _should_show_case(self, test_case: TestCase) -> bool:
        """判断是否应该显示测试用例（根据过滤条件）"""
        # 类型过滤
        type_filter = self.type_filter.currentData()
        if type_filter and test_case.type and test_case.type.value != type_filter:
            return False
        
        # 优先级过滤
        priority_filter = self.priority_filter.currentData()
        if priority_filter and test_case.priority and test_case.priority.value != priority_filter:
            return False
        
        # 搜索过滤
        search_text = self.search_box.text().lower()
        if search_text:
            searchable_text = f"{test_case.title} {test_case.module} {test_case.function}".lower()
            if search_text not in searchable_text:
                return False
        
        return True
    
    def _apply_filters(self):
        """应用过滤器"""
        self._update_tree()
        self._update_count_label()
    
    def _update_count_label(self):
        """更新计数标签"""
        visible_count = 0
        
        def count_visible_items(item):
            nonlocal visible_count
            if item.data(0, Qt.ItemDataRole.UserRole):  # 是测试用例节点
                visible_count += 1
            for i in range(item.childCount()):
                count_visible_items(item.child(i))
        
        for i in range(self.tree_widget.topLevelItemCount()):
            count_visible_items(self.tree_widget.topLevelItem(i))
        
        total_count = len(self.test_cases)
        if visible_count == total_count:
            self.count_label.setText(f"{total_count} 个用例")
        else:
            self.count_label.setText(f"{visible_count}/{total_count} 个用例")
    
    def _on_selection_changed(self):
        """选择变化处理"""
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            self._clear_detail()
            return
        
        item = selected_items[0]
        test_case = item.data(0, Qt.ItemDataRole.UserRole)
        
        if test_case:
            self._show_test_case_detail(test_case)
        else:
            self._clear_detail()
    
    def _show_test_case_detail(self, test_case: TestCase):
        """显示测试用例详情"""
        self.current_test_case = test_case
        
        # 更新标题
        self.detail_title.setText(f"测试用例详情 - {test_case.title}")
        
        # 填充表单
        self.form_fields['id'].setText(test_case.id or "")
        self.form_fields['title'].setText(test_case.title or "")
        self.form_fields['module'].setText(test_case.module or "")
        self.form_fields['function'].setText(test_case.function or "")
        
        # 设置下拉框
        if test_case.type:
            type_index = self.form_fields['type'].findData(test_case.type)
            if type_index >= 0:
                self.form_fields['type'].setCurrentIndex(type_index)
        
        if test_case.priority:
            priority_index = self.form_fields['priority'].findData(test_case.priority)
            if priority_index >= 0:
                self.form_fields['priority'].setCurrentIndex(priority_index)
        
        # 设置文本区域
        self.form_fields['preconditions'].setPlainText(test_case.preconditions or "")
        self.form_fields['steps'].setPlainText(test_case.steps or "")
        self.form_fields['expected_result'].setPlainText(test_case.expected_result or "")
        
        # 启用编辑按钮
        self.edit_btn.setEnabled(True)
        
        # 发送选择信号
        self.test_case_selected.emit(test_case)
    
    def _clear_detail(self):
        """清空详情显示"""
        self.current_test_case = None
        self.detail_title.setText("请选择测试用例")
        
        # 清空表单
        for widget in self.form_fields.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QTextEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
        
        # 禁用按钮
        self.edit_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        
        # 设置只读
        self._set_form_readonly(True)
    
    def _toggle_edit_mode(self):
        """切换编辑模式"""
        if self.edit_btn.text() == "编辑":
            self._set_form_readonly(False)
            self.edit_btn.setText("取消编辑")
            self.save_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
        else:
            self._cancel_changes()
    
    def _set_form_readonly(self, readonly: bool):
        """设置表单只读状态"""
        for field_name, widget in self.form_fields.items():
            if field_name == 'id':  # ID始终只读
                continue
            
            if isinstance(widget, (QLineEdit, QTextEdit)):
                widget.setReadOnly(readonly)
            elif isinstance(widget, QComboBox):
                widget.setEnabled(not readonly)
    
    def _on_field_changed(self):
        """字段变化处理"""
        if not self.current_test_case or self.form_fields['id'].isReadOnly():
            return
        
        # 标记为已修改
        self.save_btn.setEnabled(True)
    
    def _save_changes(self):
        """保存修改"""
        if not self.current_test_case:
            return
        
        try:
            # 创建修改后的测试用例
            modified_case = TestCase(
                id=self.current_test_case.id,
                title=self.form_fields['title'].text().strip(),
                module=self.form_fields['module'].text().strip(),
                function=self.form_fields['function'].text().strip(),
                type=self.form_fields['type'].currentData(),
                priority=self.form_fields['priority'].currentData(),
                preconditions=self.form_fields['preconditions'].toPlainText().strip(),
                steps=self.form_fields['steps'].toPlainText().strip(),
                expected_result=self.form_fields['expected_result'].toPlainText().strip()
            )
            
            # 验证必填字段
            if not modified_case.title:
                QMessageBox.warning(self, "验证失败", "测试用例标题不能为空")
                return
            
            # 保存修改
            self.modified_cases[modified_case.id] = modified_case
            
            # 更新原始数据
            for i, case in enumerate(self.test_cases):
                if case.id == modified_case.id:
                    self.test_cases[i] = modified_case
                    break
            
            # 更新当前测试用例
            self.current_test_case = modified_case
            
            # 退出编辑模式
            self._set_form_readonly(True)
            self.edit_btn.setText("编辑")
            self.save_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            
            # 更新树显示
            self._update_tree()
            
            # 发送修改信号
            self.test_case_modified.emit(modified_case)
            
            QMessageBox.information(self, "保存成功", "测试用例修改已保存")
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存测试用例时发生错误:\n{str(e)}")
    
    def _cancel_changes(self):
        """取消修改"""
        if self.current_test_case:
            self._show_test_case_detail(self.current_test_case)
        
        self._set_form_readonly(True)
        self.edit_btn.setText("编辑")
        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.tree_widget.itemAt(position)
        if not item:
            return
        
        test_case = item.data(0, Qt.ItemDataRole.UserRole)
        if not test_case:
            return
        
        menu = QMenu(self)
        
        # 编辑动作
        edit_action = QAction("编辑", self)
        edit_action.triggered.connect(lambda: self._edit_test_case(test_case))
        menu.addAction(edit_action)
        
        # 复制动作
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(lambda: self._copy_test_case(test_case))
        menu.addAction(copy_action)
        
        menu.addSeparator()
        
        # 导出动作
        export_action = QAction("导出此用例", self)
        export_action.triggered.connect(lambda: self._export_single_case(test_case))
        menu.addAction(export_action)
        
        menu.exec(self.tree_widget.mapToGlobal(position))
    
    def _edit_test_case(self, test_case: TestCase):
        """编辑测试用例"""
        # 选中对应项
        for i in range(self.tree_widget.topLevelItemCount()):
            self._select_case_in_tree(self.tree_widget.topLevelItem(i), test_case)
        
        # 进入编辑模式
        if self.current_test_case == test_case:
            self._toggle_edit_mode()
    
    def _select_case_in_tree(self, item: QTreeWidgetItem, target_case: TestCase) -> bool:
        """在树中选中指定测试用例"""
        case = item.data(0, Qt.ItemDataRole.UserRole)
        if case and case.id == target_case.id:
            self.tree_widget.setCurrentItem(item)
            return True
        
        for i in range(item.childCount()):
            if self._select_case_in_tree(item.child(i), target_case):
                return True
        
        return False
    
    def _copy_test_case(self, test_case: TestCase):
        """复制测试用例到剪贴板"""
        from PyQt6.QtWidgets import QApplication
        
        text = f"""测试用例: {test_case.title}
模块: {test_case.module}
功能点: {test_case.function}
类型: {test_case.type.value if test_case.type else ''}
优先级: {test_case.priority.value if test_case.priority else ''}

前置条件:
{test_case.preconditions or ''}

测试步骤:
{test_case.steps or ''}

预期结果:
{test_case.expected_result or ''}"""
        
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "复制成功", "测试用例已复制到剪贴板")
    
    def _export_single_case(self, test_case: TestCase):
        """导出单个测试用例"""
        self.test_cases_exported.emit([test_case])
    
    def clear(self):
        """清空组件"""
        self.test_cases.clear()
        self.modified_cases.clear()
        self.tree_widget.clear()
        self._clear_detail()
        self._update_count_label()
    
    def get_modified_cases(self) -> List[TestCase]:
        """获取已修改的测试用例"""
        return list(self.modified_cases.values())
    
    def has_unsaved_changes(self) -> bool:
        """是否有未保存的修改"""
        return len(self.modified_cases) > 0
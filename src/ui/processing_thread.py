#!/usr/bin/env python3
"""
处理线程，在后台执行文档解析和测试用例生成
"""

import os
import traceback
from typing import List, Optional, Dict, Any
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker

from ..parsers.document_processor import DocumentProcessor
from ..services.ocr.ocr_service import OCRService
from ..services.llm.llm_service import LLMService
from ..generators.test_case_generator import TestCaseGenerator
from ..generators.case_optimizer import CaseOptimizer
from ..models.data_models import TestCase, ParsedContent, StructuredInfo
from ..utils.config_helper import ConfigHelper


class ProcessingThread(QThread):
    """处理线程"""
    
    # 信号定义
    progress_updated = pyqtSignal(int, str, int, str)  # 步骤, 步骤名称, 步骤进度, 消息
    document_parsed = pyqtSignal(str)  # 解析的文档内容
    structured_info_extracted = pyqtSignal(object)  # 结构化信息
    test_cases_generated = pyqtSignal(list)  # 生成的测试用例
    processing_completed = pyqtSignal(str)  # 处理完成，包含报告
    error_occurred = pyqtSignal(str)  # 发生错误
    
    def __init__(self, file_paths: List[str], parent=None):
        """初始化处理线程"""
        super().__init__(parent)
        
        self.file_paths = file_paths
        self.config = ConfigHelper()
        
        # 线程控制
        self._stop_requested = False
        self._mutex = QMutex()
        
        # 处理结果
        self.parsed_content: Optional[ParsedContent] = None
        self.structured_info: Optional[StructuredInfo] = None
        self.test_cases: List[TestCase] = []
        self.processing_report = ""
        
        # 初始化服务
        self._init_services()
    
    def _init_services(self):
        """初始化服务组件"""
        try:
            self.document_processor = DocumentProcessor()
            self.ocr_service = OCRService()
            self.llm_service = LLMService()
            self.test_case_generator = TestCaseGenerator(self.llm_service)
            self.case_optimizer = CaseOptimizer(self.llm_service)
        except Exception as e:
            self.error_occurred.emit(f"初始化服务失败: {str(e)}")
    
    def run(self):
        """运行处理流程"""
        try:
            self._execute_processing_pipeline()
        except Exception as e:
            error_msg = f"处理过程中发生未预期的错误: {str(e)}"
            self.error_occurred.emit(error_msg)
    
    def _execute_processing_pipeline(self):
        """执行处理管道"""
        total_steps = 5
        
        try:
            # 步骤1: 文档解析
            if self._is_stop_requested():
                return
            
            self.progress_updated.emit(1, "解析文档文件", 0, "开始解析文档...")
            parsed_content = self._parse_documents()
            
            if not parsed_content:
                self.error_occurred.emit("文档解析失败，无法获取有效内容")
                return
            
            self.parsed_content = parsed_content
            self.document_parsed.emit(parsed_content.text)
            self.progress_updated.emit(1, "解析文档文件", 100, f"成功解析 {len(self.file_paths)} 个文件")
            
            # 步骤2: 结构化信息提取
            if self._is_stop_requested():
                return
            
            self.progress_updated.emit(2, "提取结构化信息", 0, "分析文档结构...")
            structured_info = self._extract_structured_info(parsed_content)
            
            if not structured_info:
                self.error_occurred.emit("结构化信息提取失败")
                return
            
            self.structured_info = structured_info
            self.structured_info_extracted.emit(structured_info)
            self.progress_updated.emit(2, "提取结构化信息", 100, f"提取了 {len(structured_info.modules)} 个模块")
            
            # 步骤3: 生成测试用例
            if self._is_stop_requested():
                return
            
            self.progress_updated.emit(3, "生成测试用例", 0, "基于AI生成测试用例...")
            test_cases = self._generate_test_cases(structured_info)
            
            if not test_cases:
                self.error_occurred.emit("测试用例生成失败")
                return
            
            self.progress_updated.emit(3, "生成测试用例", 100, f"生成了 {len(test_cases)} 个测试用例")
            
            # 步骤4: 优化测试用例
            if self._is_stop_requested():
                return
            
            self.progress_updated.emit(4, "优化测试用例", 0, "优化和去重测试用例...")
            optimized_cases = self._optimize_test_cases(test_cases)
            
            self.test_cases = optimized_cases
            self.test_cases_generated.emit(optimized_cases)
            self.progress_updated.emit(4, "优化测试用例", 100, f"优化后共 {len(optimized_cases)} 个测试用例")
            
            # 步骤5: 生成报告
            if self._is_stop_requested():
                return
            
            self.progress_updated.emit(5, "生成处理报告", 0, "生成详细报告...")
            report = self._generate_report()
            
            self.processing_report = report
            self.progress_updated.emit(5, "生成处理报告", 100, "报告生成完成")
            
            # 完成处理
            self.processing_completed.emit(report)
            
        except Exception as e:
            error_msg = f"处理管道执行失败: {str(e)}\\n{traceback.format_exc()}"
            self.error_occurred.emit(error_msg)
    
    def _parse_documents(self) -> Optional[ParsedContent]:
        """解析文档"""
        try:
            all_text = []
            all_images = []
            file_info = []
            
            for i, file_path in enumerate(self.file_paths):
                if self._is_stop_requested():
                    return None
                
                # 更新进度
                progress = int((i / len(self.file_paths)) * 100)
                self.progress_updated.emit(1, "解析文档文件", progress, f"正在处理: {Path(file_path).name}")
                
                # 解析单个文件
                try:
                    result = self.document_processor.process_file(file_path)
                    
                    if result.text:
                        all_text.append(result.text)
                    
                    if result.images:
                        all_images.extend(result.images)
                    
                    file_info.append({
                        'path': file_path,
                        'name': Path(file_path).name,
                        'size': Path(file_path).stat().st_size,
                        'text_length': len(result.text) if result.text else 0,
                        'image_count': len(result.images) if result.images else 0
                    })
                    
                except Exception as e:
                    self.progress_updated.emit(1, "解析文档文件", progress, f"文件 {Path(file_path).name} 解析失败: {str(e)}")
                    continue
            
            if not all_text and not all_images:
                return None
            
            # 合并所有文本
            combined_text = "\\n\\n".join(filter(None, all_text))
            
            # 对图片进行OCR识别
            if all_images:
                self.progress_updated.emit(1, "解析文档文件", 80, "正在进行OCR识别...")
                
                for image in all_images:
                    if self._is_stop_requested():
                        return None
                    
                    try:
                        ocr_text = self.ocr_service.extract_text(image)
                        if ocr_text:
                            combined_text += f"\\n\\n[OCR识别内容]\\n{ocr_text}"
                    except Exception as e:
                        self.progress_updated.emit(1, "解析文档文件", 80, f"OCR识别失败: {str(e)}")
                        continue
            
            return ParsedContent(
                text=combined_text,
                images=all_images,
                metadata={'files': file_info}
            )
            
        except Exception as e:
            raise Exception(f"文档解析失败: {str(e)}")
    
    def _extract_structured_info(self, parsed_content: ParsedContent) -> Optional[StructuredInfo]:
        """提取结构化信息"""
        try:
            # 使用测试用例生成器提取结构化信息
            return self.test_case_generator.extract_structured_info(parsed_content.text)
            
        except Exception as e:
            raise Exception(f"结构化信息提取失败: {str(e)}")
    
    def _generate_test_cases(self, structured_info: StructuredInfo) -> List[TestCase]:
        """生成测试用例"""
        try:
            all_test_cases = []
            total_functions = sum(len(module.functions) for module in structured_info.modules)
            processed_functions = 0
            
            for module in structured_info.modules:
                if self._is_stop_requested():
                    return []
                
                for function in module.functions:
                    if self._is_stop_requested():
                        return []
                    
                    # 更新进度
                    progress = int((processed_functions / total_functions) * 100)
                    self.progress_updated.emit(3, "生成测试用例", progress, f"正在处理: {module.name} - {function.name}")
                    
                    try:
                        # 为每个功能点生成测试用例
                        cases = self.test_case_generator.generate_test_cases_for_function(
                            module.name,
                            function
                        )
                        
                        if cases:
                            all_test_cases.extend(cases)
                        
                    except Exception as e:
                        self.progress_updated.emit(3, "生成测试用例", progress, f"功能 {function.name} 生成失败: {str(e)}")
                        continue
                    
                    processed_functions += 1
            
            return all_test_cases
            
        except Exception as e:
            raise Exception(f"测试用例生成失败: {str(e)}")
    
    def _optimize_test_cases(self, test_cases: List[TestCase]) -> List[TestCase]:
        """优化测试用例"""
        try:
            if not test_cases:
                return []
            
            # 去重
            self.progress_updated.emit(4, "优化测试用例", 25, "正在去除重复用例...")
            deduplicated_cases = self.case_optimizer.remove_duplicates(test_cases)
            
            if self._is_stop_requested():
                return []
            
            # 补充测试用例
            self.progress_updated.emit(4, "优化测试用例", 50, "正在补充测试用例...")
            enhanced_cases = self.case_optimizer.enhance_test_cases(deduplicated_cases)
            
            if self._is_stop_requested():
                return []
            
            # 优化测试用例
            self.progress_updated.emit(4, "优化测试用例", 75, "正在优化测试用例...")
            optimized_cases = self.case_optimizer.optimize_test_cases(enhanced_cases)
            
            return optimized_cases
            
        except Exception as e:
            raise Exception(f"测试用例优化失败: {str(e)}")
    
    def _generate_report(self) -> str:
        """生成处理报告"""
        try:
            report_lines = []
            report_lines.append("# 测试用例生成报告")
            report_lines.append("")
            
            # 基本信息
            report_lines.append("## 基本信息")
            report_lines.append(f"- 处理文件数量: {len(self.file_paths)}")
            
            if self.parsed_content and self.parsed_content.metadata:
                total_size = sum(f['size'] for f in self.parsed_content.metadata.get('files', []))
                report_lines.append(f"- 文件总大小: {total_size / 1024 / 1024:.2f} MB")
                report_lines.append(f"- 文档总字数: {len(self.parsed_content.text) if self.parsed_content.text else 0}")
            
            report_lines.append("")
            
            # 结构化信息
            if self.structured_info:
                report_lines.append("## 结构化信息")
                report_lines.append(f"- 识别模块数: {len(self.structured_info.modules)}")
                
                total_functions = sum(len(module.functions) for module in self.structured_info.modules)
                report_lines.append(f"- 识别功能点数: {total_functions}")
                
                report_lines.append("")
                report_lines.append("### 模块详情")
                for module in self.structured_info.modules:
                    report_lines.append(f"- **{module.name}**: {len(module.functions)} 个功能点")
                    for func in module.functions:
                        report_lines.append(f"  - {func.name}: {func.description}")
                
                report_lines.append("")
            
            # 测试用例统计
            if self.test_cases:
                report_lines.append("## 测试用例统计")
                report_lines.append(f"- 生成用例总数: {len(self.test_cases)}")
                
                # 按类型统计
                type_counts = {}
                priority_counts = {}
                module_counts = {}
                
                for case in self.test_cases:
                    # 类型统计
                    case_type = case.type.value if case.type else "未分类"
                    type_counts[case_type] = type_counts.get(case_type, 0) + 1
                    
                    # 优先级统计
                    priority = case.priority.value if case.priority else "未分类"
                    priority_counts[priority] = priority_counts.get(priority, 0) + 1
                    
                    # 模块统计
                    module = case.module or "未分类"
                    module_counts[module] = module_counts.get(module, 0) + 1
                
                report_lines.append("")
                report_lines.append("### 按类型分布")
                for case_type, count in type_counts.items():
                    percentage = (count / len(self.test_cases)) * 100
                    report_lines.append(f"- {case_type}: {count} 个 ({percentage:.1f}%)")
                
                report_lines.append("")
                report_lines.append("### 按优先级分布")
                for priority, count in priority_counts.items():
                    percentage = (count / len(self.test_cases)) * 100
                    report_lines.append(f"- {priority}: {count} 个 ({percentage:.1f}%)")
                
                report_lines.append("")
                report_lines.append("### 按模块分布")
                for module, count in module_counts.items():
                    percentage = (count / len(self.test_cases)) * 100
                    report_lines.append(f"- {module}: {count} 个 ({percentage:.1f}%)")
                
                report_lines.append("")
            
            # 处理文件详情
            if self.parsed_content and self.parsed_content.metadata:
                report_lines.append("## 处理文件详情")
                for file_info in self.parsed_content.metadata.get('files', []):
                    report_lines.append(f"- **{file_info['name']}**")
                    report_lines.append(f"  - 大小: {file_info['size'] / 1024:.1f} KB")
                    report_lines.append(f"  - 文本长度: {file_info['text_length']} 字符")
                    report_lines.append(f"  - 图片数量: {file_info['image_count']} 张")
                
                report_lines.append("")
            
            # 质量评估
            report_lines.append("## 质量评估")
            if self.test_cases:
                # 计算完整性
                complete_cases = sum(1 for case in self.test_cases 
                                   if case.title and case.steps and case.expected_result)
                completeness = (complete_cases / len(self.test_cases)) * 100
                report_lines.append(f"- 用例完整性: {completeness:.1f}% ({complete_cases}/{len(self.test_cases)})")
                
                # 计算覆盖度
                if self.structured_info:
                    total_functions = sum(len(module.functions) for module in self.structured_info.modules)
                    covered_functions = len(set(case.function for case in self.test_cases if case.function))
                    coverage = (covered_functions / total_functions) * 100 if total_functions > 0 else 0
                    report_lines.append(f"- 功能覆盖度: {coverage:.1f}% ({covered_functions}/{total_functions})")
            
            report_lines.append("")
            report_lines.append("---")
            report_lines.append(f"报告生成时间: {self._get_current_time()}")
            
            return "\\n".join(report_lines)
            
        except Exception as e:
            return f"报告生成失败: {str(e)}"
    
    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def stop(self):
        """停止处理"""
        with QMutexLocker(self._mutex):
            self._stop_requested = True
    
    def _is_stop_requested(self) -> bool:
        """检查是否请求停止"""
        with QMutexLocker(self._mutex):
            return self._stop_requested
    
    def get_results(self) -> Dict[str, Any]:
        """获取处理结果"""
        return {
            'parsed_content': self.parsed_content,
            'structured_info': self.structured_info,
            'test_cases': self.test_cases,
            'report': self.processing_report
        }
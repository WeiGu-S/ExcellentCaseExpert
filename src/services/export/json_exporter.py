"""
JSON格式导出器实现
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from ...interfaces.base_interfaces import IExporter, IFormatConverter
from ...models.data_models import TestCase, ExportResult, ExportConfig, ExportFormat
from ...utils.error_handler import ErrorHandler


class JSONExporter(IExporter):
    """JSON格式导出器"""
    
    def __init__(self, format_converter: IFormatConverter = None):
        """
        初始化JSON导出器
        
        Args:
            format_converter: 格式转换器，如果为None则使用内置转换器
        """
        self.format_converter = format_converter or JSONFormatConverter()
        self.error_handler = ErrorHandler()
    
    def export(self, cases: List[TestCase], output_path: str, config: ExportConfig = None) -> ExportResult:
        """
        导出测试用例为JSON格式
        
        Args:
            cases: 测试用例列表
            output_path: 输出文件路径
            config: 导出配置
            
        Returns:
            ExportResult: 导出结果
        """
        try:
            # 使用默认配置如果未提供
            if config is None:
                config = ExportConfig(
                    format=ExportFormat.JSON,
                    output_path=output_path,
                    indent_size=2,
                    include_metadata=True
                )
            
            # 确保输出目录存在
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 转换为JSON格式
            json_data = self.format_converter.convert_to_json(cases)
            
            # 添加元数据
            if config.include_metadata:
                json_data = self._add_metadata(json_data, cases)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    json_data, 
                    f, 
                    ensure_ascii=False, 
                    indent=config.indent_size,
                    separators=(',', ': ') if config.indent_size > 0 else (',', ':')
                )
            
            # 验证输出文件
            if not self.validate_output(output_path):
                raise ValueError("生成的JSON文件验证失败")
            
            # 获取文件大小
            file_size = os.path.getsize(output_path)
            
            return ExportResult(
                success=True,
                output_path=output_path,
                file_size=file_size,
                export_time=datetime.now(),
                error_message=None
            )
            
        except Exception as e:
            error_response = self.error_handler.handle_error(e, f"JSON导出: {output_path}")
            return ExportResult(
                success=False,
                output_path=output_path,
                file_size=0,
                export_time=datetime.now(),
                error_message=error_response.message
            )
    
    def validate_output(self, output_path: str) -> bool:
        """
        验证输出的JSON文件
        
        Args:
            output_path: 文件路径
            
        Returns:
            bool: 验证是否通过
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(output_path):
                return False
            
            # 检查文件是否为空
            if os.path.getsize(output_path) == 0:
                return False
            
            # 验证JSON格式
            with open(output_path, 'r', encoding='utf-8') as f:
                json.load(f)
            
            return True
            
        except (json.JSONDecodeError, IOError):
            return False
    
    def _add_metadata(self, json_data: Dict[str, Any], cases: List[TestCase]) -> Dict[str, Any]:
        """
        添加元数据到JSON数据
        
        Args:
            json_data: 原始JSON数据
            cases: 测试用例列表
            
        Returns:
            Dict[str, Any]: 包含元数据的JSON数据
        """
        metadata = {
            "export_time": datetime.now().isoformat(),
            "total_cases": len(cases),
            "modules": list(set(case.module for case in cases)),
            "priority_distribution": self._get_priority_distribution(cases),
            "generator_version": "1.0.0"
        }
        
        return {
            "metadata": metadata,
            "test_cases": json_data.get("test_cases", json_data)
        }
    
    def _get_priority_distribution(self, cases: List[TestCase]) -> Dict[str, int]:
        """
        获取优先级分布统计
        
        Args:
            cases: 测试用例列表
            
        Returns:
            Dict[str, int]: 优先级分布
        """
        distribution = {}
        for case in cases:
            priority = case.priority.value
            distribution[priority] = distribution.get(priority, 0) + 1
        return distribution


class JSONFormatConverter(IFormatConverter):
    """JSON格式转换器"""
    
    def convert_to_json(self, cases: List[TestCase]) -> Dict[str, Any]:
        """
        将测试用例转换为JSON格式
        
        Args:
            cases: 测试用例列表
            
        Returns:
            Dict[str, Any]: JSON格式数据
        """
        # 按模块分组
        modules_data = {}
        
        for case in cases:
            module_name = case.module
            if module_name not in modules_data:
                modules_data[module_name] = {
                    "module_name": module_name,
                    "functions": {}
                }
            
            function_name = case.function
            if function_name not in modules_data[module_name]["functions"]:
                modules_data[module_name]["functions"][function_name] = {
                    "function_name": function_name,
                    "test_cases": []
                }
            
            # 转换测试用例
            case_data = {
                "id": case.id,
                "title": case.title,
                "priority": case.priority.value,
                "steps": [
                    {
                        "step_number": step.step_number,
                        "description": step.description,
                        "input_data": step.input_data,
                        "expected_behavior": step.expected_behavior
                    }
                    for step in case.steps
                ],
                "expected_result": case.expected_result,
                "created_time": case.created_time.isoformat() if case.created_time else None
            }
            
            modules_data[module_name]["functions"][function_name]["test_cases"].append(case_data)
        
        # 转换为列表格式
        result = {
            "test_cases": {
                "modules": [
                    {
                        "module_name": module_name,
                        "functions": [
                            {
                                "function_name": func_name,
                                "test_cases": func_data["test_cases"]
                            }
                            for func_name, func_data in module_data["functions"].items()
                        ]
                    }
                    for module_name, module_data in modules_data.items()
                ]
            }
        }
        
        return result
    
    def convert_to_xmind(self, cases: List[TestCase]) -> Dict[str, Any]:
        """
        转换为XMind格式数据（为后续XMind导出器准备）
        
        Args:
            cases: 测试用例列表
            
        Returns:
            Dict[str, Any]: XMind格式数据
        """
        # 这里先返回基础结构，具体实现在XMind导出器中完成
        return {
            "root_topic": {
                "title": "测试用例",
                "children": []
            }
        }
"""
测试用例生成器实现，基于OCR识别信息生成测试用例
"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..interfaces.base_interfaces import ITestCaseGenerator
from ..models.data_models import (
    StructuredInfo, TestCase, TestStep, Module, Function, 
    Priority, ValidationResult, LLMResponse
)
from ..services.llm.llm_service import LLMService
from ..utils.error_handler import ErrorHandler


class TestCaseGenerator(ITestCaseGenerator):
    """测试用例生成器，基于OCR识别信息生成标准化测试用例"""
    
    def __init__(self, llm_service: LLMService):
        """
        初始化测试用例生成器
        
        Args:
            llm_service: 大模型API服务实例
        """
        self.llm_service = llm_service
        self.error_handler = ErrorHandler()
        
        # 测试用例模板
        self.case_template = {
            "id": "",
            "module": "",
            "function": "",
            "title": "",
            "steps": [],
            "expected_result": "",
            "priority": Priority.MEDIUM,
            "created_time": None
        }
        
        # 提示词模板
        self.prompt_templates = {
            "extract_structure": """
请分析以下PRD文档内容，提取出功能模块和功能点的结构化信息。

文档内容：
{content}

请按照以下JSON格式返回结果：
{{
    "modules": [
        {{
            "name": "模块名称",
            "description": "模块描述",
            "functions": [
                {{
                    "name": "功能点名称",
                    "description": "功能点描述",
                    "inputs": ["输入参数1", "输入参数2"],
                    "outputs": ["输出结果1", "输出结果2"],
                    "business_rules": ["业务规则1", "业务规则2"]
                }}
            ]
        }}
    ],
    "business_rules": ["全局业务规则1", "全局业务规则2"],
    "constraints": ["约束条件1", "约束条件2"]
}}

注意：
1. 请仔细分析文档内容，准确提取功能模块和功能点
2. 每个功能点都要包含输入、输出和业务规则
3. 返回的必须是有效的JSON格式
""",
            
            "generate_test_cases": """
请基于以下功能信息生成详细的测试用例。

模块名称：{module_name}
功能点名称：{function_name}
功能描述：{function_description}
输入参数：{inputs}
输出结果：{outputs}
业务规则：{business_rules}

请生成以下类型的测试用例：
1. 正常流程测试用例（至少2个）
2. 异常流程测试用例（至少2个）
3. 边界值测试用例（至少1个）

每个测试用例请按照以下JSON格式返回：
{{
    "test_cases": [
        {{
            "title": "测试用例标题",
            "priority": "high|medium|low|critical",
            "steps": [
                {{
                    "step_number": 1,
                    "description": "测试步骤描述",
                    "input_data": "输入数据（可选）",
                    "expected_behavior": "预期行为"
                }}
            ],
            "expected_result": "最终预期结果",
            "test_type": "正常流程|异常流程|边界值"
        }}
    ]
}}

注意：
1. 测试步骤要详细、可执行
2. 预期结果要明确、可验证
3. 优先级要合理分配
4. 返回的必须是有效的JSON格式
""",
            
            "optimize_test_cases": """
请优化以下测试用例，补充遗漏的测试场景，提高测试覆盖率。

现有测试用例：
{existing_cases}

功能信息：
模块：{module_name}
功能：{function_name}
描述：{function_description}

请分析现有测试用例，识别遗漏的测试场景，并生成补充的测试用例。
重点关注：
1. 数据验证测试
2. 权限控制测试
3. 并发操作测试
4. 性能边界测试
5. 集成接口测试

请按照相同的JSON格式返回补充的测试用例。
"""
        }
    
    def extract_structured_info(self, raw_text: str) -> StructuredInfo:
        """
        从原始文本中提取结构化信息
        
        Args:
            raw_text: 原始PRD文本
            
        Returns:
            结构化信息对象
        """
        try:
            # 使用大模型提取结构化信息
            prompt = self.prompt_templates["extract_structure"].format(content=raw_text)
            
            response = self.llm_service.call_api_with_retry(
                prompt=prompt,
                provider="openai",
                temperature=0.3,  # 较低的温度以获得更稳定的结果
                max_tokens=2000
            )
            
            if response.error_message:
                raise Exception(f"大模型调用失败: {response.error_message}")
            
            # 解析JSON响应
            try:
                structure_data = json.loads(response.content)
            except json.JSONDecodeError as e:
                # 尝试修复JSON格式
                cleaned_content = self._clean_json_response(response.content)
                structure_data = json.loads(cleaned_content)
            
            # 转换为结构化信息对象
            modules = []
            for module_data in structure_data.get("modules", []):
                functions = []
                for func_data in module_data.get("functions", []):
                    function = Function(
                        name=func_data.get("name", ""),
                        description=func_data.get("description", ""),
                        inputs=func_data.get("inputs", []),
                        outputs=func_data.get("outputs", []),
                        business_rules=func_data.get("business_rules", [])
                    )
                    functions.append(function)
                
                module = Module(
                    name=module_data.get("name", ""),
                    description=module_data.get("description", ""),
                    functions=functions
                )
                modules.append(module)
            
            # 计算提取覆盖率（简单的启发式方法）
            total_chars = len(raw_text)
            extracted_chars = sum(len(m.name) + len(m.description) for m in modules)
            coverage = min(1.0, extracted_chars / max(total_chars * 0.1, 1))
            
            return StructuredInfo(
                modules=modules,
                business_rules=structure_data.get("business_rules", []),
                constraints=structure_data.get("constraints", []),
                extraction_coverage=coverage
            )
            
        except Exception as e:
            error_response = self.error_handler.handle_error(e, "提取结构化信息")
            # 返回空的结构化信息
            return StructuredInfo(
                modules=[],
                business_rules=[],
                constraints=[],
                extraction_coverage=0.0
            )
    
    def generate_cases(self, structured_info: StructuredInfo) -> List[TestCase]:
        """
        基于结构化信息生成测试用例
        
        Args:
            structured_info: 结构化信息
            
        Returns:
            测试用例列表
        """
        all_test_cases = []
        case_id_counter = 1
        
        for module in structured_info.modules:
            for function in module.functions:
                try:
                    # 为每个功能点生成测试用例
                    function_cases = self._generate_function_test_cases(
                        module, function, case_id_counter
                    )
                    all_test_cases.extend(function_cases)
                    case_id_counter += len(function_cases)
                    
                except Exception as e:
                    print(f"为功能点 {function.name} 生成测试用例失败: {e}")
                    continue
        
        return all_test_cases
    
    def _generate_function_test_cases(self, module: Module, function: Function, 
                                    start_id: int) -> List[TestCase]:
        """
        为单个功能点生成测试用例
        
        Args:
            module: 模块信息
            function: 功能点信息
            start_id: 起始ID
            
        Returns:
            测试用例列表
        """
        # 准备提示词
        prompt = self.prompt_templates["generate_test_cases"].format(
            module_name=module.name,
            function_name=function.name,
            function_description=function.description,
            inputs=", ".join(function.inputs) if function.inputs else "无",
            outputs=", ".join(function.outputs) if function.outputs else "无",
            business_rules="; ".join(function.business_rules) if function.business_rules else "无"
        )
        
        # 调用大模型生成测试用例
        response = self.llm_service.call_api_with_retry(
            prompt=prompt,
            provider="openai",
            temperature=0.5,
            max_tokens=3000
        )
        
        if response.error_message:
            raise Exception(f"大模型调用失败: {response.error_message}")
        
        # 解析响应
        try:
            cases_data = json.loads(response.content)
        except json.JSONDecodeError:
            cleaned_content = self._clean_json_response(response.content)
            cases_data = json.loads(cleaned_content)
        
        # 转换为测试用例对象
        test_cases = []
        for i, case_data in enumerate(cases_data.get("test_cases", [])):
            # 创建测试步骤
            steps = []
            for step_data in case_data.get("steps", []):
                step = TestStep(
                    step_number=step_data.get("step_number", len(steps) + 1),
                    description=step_data.get("description", ""),
                    input_data=step_data.get("input_data"),
                    expected_behavior=step_data.get("expected_behavior", "")
                )
                steps.append(step)
            
            # 解析优先级
            priority_str = case_data.get("priority", "medium").lower()
            priority = self._parse_priority(priority_str)
            
            # 创建测试用例
            test_case = TestCase(
                id=f"TC_{start_id + i:03d}",
                module=module.name,
                function=function.name,
                title=case_data.get("title", f"{function.name}测试用例{i+1}"),
                steps=steps,
                expected_result=case_data.get("expected_result", ""),
                priority=priority,
                created_time=datetime.now()
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def optimize_cases(self, cases: List[TestCase]) -> List[TestCase]:
        """
        优化测试用例，补充遗漏的测试场景
        
        Args:
            cases: 现有测试用例列表
            
        Returns:
            优化后的测试用例列表
        """
        if not cases:
            return cases
        
        optimized_cases = cases.copy()
        
        # 按模块和功能分组
        grouped_cases = self._group_cases_by_function(cases)
        
        for (module_name, function_name), function_cases in grouped_cases.items():
            try:
                # 为每个功能生成补充的测试用例
                additional_cases = self._generate_additional_cases(
                    module_name, function_name, function_cases
                )
                optimized_cases.extend(additional_cases)
                
            except Exception as e:
                print(f"为功能 {function_name} 生成补充测试用例失败: {e}")
                continue
        
        return optimized_cases
    
    def _generate_additional_cases(self, module_name: str, function_name: str, 
                                 existing_cases: List[TestCase]) -> List[TestCase]:
        """
        生成补充的测试用例
        
        Args:
            module_name: 模块名称
            function_name: 功能名称
            existing_cases: 现有测试用例
            
        Returns:
            补充的测试用例列表
        """
        # 将现有测试用例转换为JSON格式
        existing_cases_json = []
        for case in existing_cases:
            case_dict = {
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
                "expected_result": case.expected_result
            }
            existing_cases_json.append(case_dict)
        
        # 准备优化提示词
        prompt = self.prompt_templates["optimize_test_cases"].format(
            existing_cases=json.dumps(existing_cases_json, ensure_ascii=False, indent=2),
            module_name=module_name,
            function_name=function_name,
            function_description=f"{module_name}模块的{function_name}功能"
        )
        
        # 调用大模型生成补充用例
        response = self.llm_service.call_api_with_retry(
            prompt=prompt,
            provider="openai",
            temperature=0.6,
            max_tokens=2500
        )
        
        if response.error_message:
            return []
        
        # 解析响应
        try:
            additional_data = json.loads(response.content)
        except json.JSONDecodeError:
            cleaned_content = self._clean_json_response(response.content)
            additional_data = json.loads(cleaned_content)
        
        # 转换为测试用例对象
        additional_cases = []
        start_id = max([int(case.id.split('_')[1]) for case in existing_cases]) + 1
        
        for i, case_data in enumerate(additional_data.get("test_cases", [])):
            steps = []
            for step_data in case_data.get("steps", []):
                step = TestStep(
                    step_number=step_data.get("step_number", len(steps) + 1),
                    description=step_data.get("description", ""),
                    input_data=step_data.get("input_data"),
                    expected_behavior=step_data.get("expected_behavior", "")
                )
                steps.append(step)
            
            priority = self._parse_priority(case_data.get("priority", "medium"))
            
            test_case = TestCase(
                id=f"TC_{start_id + i:03d}",
                module=module_name,
                function=function_name,
                title=case_data.get("title", f"{function_name}补充测试用例{i+1}"),
                steps=steps,
                expected_result=case_data.get("expected_result", ""),
                priority=priority,
                created_time=datetime.now()
            )
            additional_cases.append(test_case)
        
        return additional_cases
    
    def validate_cases(self, cases: List[TestCase]) -> ValidationResult:
        """
        验证测试用例的完整性和有效性
        
        Args:
            cases: 测试用例列表
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        for case in cases:
            # 检查必填字段
            if not case.id:
                errors.append(f"测试用例缺少ID")
            if not case.title:
                errors.append(f"测试用例 {case.id} 缺少标题")
            if not case.module:
                errors.append(f"测试用例 {case.id} 缺少模块信息")
            if not case.function:
                errors.append(f"测试用例 {case.id} 缺少功能信息")
            if not case.expected_result:
                errors.append(f"测试用例 {case.id} 缺少预期结果")
            
            # 检查测试步骤
            if not case.steps:
                errors.append(f"测试用例 {case.id} 缺少测试步骤")
            else:
                for step in case.steps:
                    if not step.description:
                        errors.append(f"测试用例 {case.id} 的步骤 {step.step_number} 缺少描述")
                    if not step.expected_behavior:
                        warnings.append(f"测试用例 {case.id} 的步骤 {step.step_number} 缺少预期行为")
            
            # 检查ID唯一性
            case_ids = [c.id for c in cases]
            if case_ids.count(case.id) > 1:
                errors.append(f"测试用例ID {case.id} 重复")
        
        # 检查覆盖率
        modules = set(case.module for case in cases if case.module)
        functions = set(case.function for case in cases if case.function)
        
        if len(modules) == 0:
            warnings.append("没有覆盖任何模块")
        if len(functions) == 0:
            warnings.append("没有覆盖任何功能点")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _clean_json_response(self, content: str) -> str:
        """
        清理大模型响应中的JSON格式问题
        
        Args:
            content: 原始响应内容
            
        Returns:
            清理后的JSON字符串
        """
        # 移除可能的markdown代码块标记
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        
        # 移除多余的空白字符
        content = content.strip()
        
        # 尝试找到JSON对象的开始和结束
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            content = content[start_idx:end_idx + 1]
        
        return content
    
    def _parse_priority(self, priority_str: str) -> Priority:
        """
        解析优先级字符串
        
        Args:
            priority_str: 优先级字符串
            
        Returns:
            优先级枚举值
        """
        priority_map = {
            "critical": Priority.CRITICAL,
            "high": Priority.HIGH,
            "medium": Priority.MEDIUM,
            "low": Priority.LOW
        }
        return priority_map.get(priority_str.lower(), Priority.MEDIUM)
    
    def _group_cases_by_function(self, cases: List[TestCase]) -> Dict[Tuple[str, str], List[TestCase]]:
        """
        按模块和功能分组测试用例
        
        Args:
            cases: 测试用例列表
            
        Returns:
            分组后的测试用例字典
        """
        grouped = {}
        for case in cases:
            key = (case.module, case.function)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(case)
        return grouped
    
    def get_generation_stats(self, cases: List[TestCase]) -> Dict[str, Any]:
        """
        获取测试用例生成统计信息
        
        Args:
            cases: 测试用例列表
            
        Returns:
            统计信息字典
        """
        if not cases:
            return {}
        
        # 按优先级统计
        priority_counts = {}
        for priority in Priority:
            priority_counts[priority.value] = sum(1 for case in cases if case.priority == priority)
        
        # 按模块统计
        module_counts = {}
        for case in cases:
            if case.module:
                module_counts[case.module] = module_counts.get(case.module, 0) + 1
        
        # 计算平均步骤数
        total_steps = sum(len(case.steps) for case in cases)
        avg_steps = total_steps / len(cases) if cases else 0
        
        return {
            "total_cases": len(cases),
            "priority_distribution": priority_counts,
            "module_distribution": module_counts,
            "average_steps_per_case": round(avg_steps, 2),
            "total_steps": total_steps,
            "modules_covered": len(module_counts),
            "functions_covered": len(set(case.function for case in cases if case.function))
        }
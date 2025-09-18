"""
测试用例优化器实现，自动优化和补充测试用例
"""

import re
from typing import List, Dict, Any, Tuple, Set
from datetime import datetime
from difflib import SequenceMatcher

from ..models.data_models import TestCase, TestStep, Priority, ValidationResult
from ..utils.constants import MIN_CASE_IMPROVEMENT, DUPLICATE_SIMILARITY_THRESHOLD
from ..utils.error_handler import ErrorHandler


class CaseOptimizer:
    """测试用例优化器，自动优化和补充测试用例，实现去重功能"""
    
    def __init__(self):
        """初始化用例优化器"""
        self.error_handler = ErrorHandler()
        self.improvement_target = MIN_CASE_IMPROVEMENT  # 30%改进目标
        self.similarity_threshold = DUPLICATE_SIMILARITY_THRESHOLD  # 80%相似度阈值
        
        # 优化规则配置
        self.optimization_rules = {
            "add_boundary_tests": True,      # 添加边界值测试
            "add_negative_tests": True,      # 添加负面测试
            "add_performance_tests": True,   # 添加性能测试
            "add_security_tests": True,      # 添加安全测试
            "merge_similar_cases": True,     # 合并相似用例
            "enhance_test_data": True,       # 增强测试数据
            "improve_assertions": True       # 改进断言
        }
        
        # 测试类型模板
        self.test_templates = {
            "boundary": {
                "min_value": "最小值边界测试",
                "max_value": "最大值边界测试",
                "empty_input": "空输入测试",
                "null_input": "空值输入测试"
            },
            "negative": {
                "invalid_format": "无效格式测试",
                "unauthorized_access": "未授权访问测试",
                "invalid_parameter": "无效参数测试",
                "missing_required": "缺少必填项测试"
            },
            "performance": {
                "load_test": "负载测试",
                "stress_test": "压力测试",
                "concurrent_test": "并发测试"
            },
            "security": {
                "sql_injection": "SQL注入测试",
                "xss_test": "XSS攻击测试",
                "csrf_test": "CSRF攻击测试",
                "privilege_escalation": "权限提升测试"
            }
        }
    
    def optimize_test_cases(self, cases: List[TestCase]) -> List[TestCase]:
        """
        优化测试用例集合
        
        Args:
            cases: 原始测试用例列表
            
        Returns:
            优化后的测试用例列表
        """
        if not cases:
            return cases
        
        try:
            optimized_cases = cases.copy()
            original_count = len(cases)
            
            # 1. 去重处理
            optimized_cases = self.remove_duplicates(optimized_cases)
            
            # 2. 补充边界值测试
            if self.optimization_rules["add_boundary_tests"]:
                boundary_cases = self._generate_boundary_tests(optimized_cases)
                optimized_cases.extend(boundary_cases)
            
            # 3. 补充负面测试
            if self.optimization_rules["add_negative_tests"]:
                negative_cases = self._generate_negative_tests(optimized_cases)
                optimized_cases.extend(negative_cases)
            
            # 4. 补充性能测试
            if self.optimization_rules["add_performance_tests"]:
                performance_cases = self._generate_performance_tests(optimized_cases)
                optimized_cases.extend(performance_cases)
            
            # 5. 补充安全测试
            if self.optimization_rules["add_security_tests"]:
                security_cases = self._generate_security_tests(optimized_cases)
                optimized_cases.extend(security_cases)
            
            # 6. 增强现有测试用例
            if self.optimization_rules["enhance_test_data"]:
                optimized_cases = self._enhance_test_data(optimized_cases)
            
            # 7. 改进断言
            if self.optimization_rules["improve_assertions"]:
                optimized_cases = self._improve_assertions(optimized_cases)
            
            # 8. 重新分配ID
            optimized_cases = self._reassign_case_ids(optimized_cases)
            
            # 验证改进目标
            improvement_ratio = (len(optimized_cases) - original_count) / original_count
            if improvement_ratio < self.improvement_target:
                print(f"警告: 优化改进率 {improvement_ratio:.2%} 低于目标 {self.improvement_target:.2%}")
            
            return optimized_cases
            
        except Exception as e:
            error_response = self.error_handler.handle_error(e, "优化测试用例")
            print(f"测试用例优化失败: {error_response.message}")
            return cases
    
    def remove_duplicates(self, cases: List[TestCase]) -> List[TestCase]:
        """
        移除重复的测试用例
        
        Args:
            cases: 测试用例列表
            
        Returns:
            去重后的测试用例列表
        """
        if not cases:
            return cases
        
        unique_cases = []
        duplicate_pairs = []
        
        for i, case1 in enumerate(cases):
            is_duplicate = False
            
            for j, case2 in enumerate(unique_cases):
                similarity = self.calculate_similarity(case1, case2)
                
                if similarity >= self.similarity_threshold:
                    is_duplicate = True
                    duplicate_pairs.append((case1.id, case2.id, similarity))
                    break
            
            if not is_duplicate:
                unique_cases.append(case1)
        
        # 记录重复用例信息
        if duplicate_pairs:
            print(f"发现 {len(duplicate_pairs)} 对重复用例:")
            for case1_id, case2_id, similarity in duplicate_pairs:
                print(f"  {case1_id} 与 {case2_id} 相似度: {similarity:.2%}")
        
        return unique_cases
    
    def calculate_similarity(self, case1: TestCase, case2: TestCase) -> float:
        """
        计算两个测试用例的相似度
        
        Args:
            case1: 测试用例1
            case2: 测试用例2
            
        Returns:
            相似度 (0.0-1.0)
        """
        # 权重配置
        weights = {
            "title": 0.3,
            "steps": 0.4,
            "expected_result": 0.2,
            "module_function": 0.1
        }
        
        similarities = {}
        
        # 1. 标题相似度
        similarities["title"] = SequenceMatcher(
            None, case1.title.lower(), case2.title.lower()
        ).ratio()
        
        # 2. 测试步骤相似度
        steps1_text = " ".join([step.description for step in case1.steps])
        steps2_text = " ".join([step.description for step in case2.steps])
        similarities["steps"] = SequenceMatcher(
            None, steps1_text.lower(), steps2_text.lower()
        ).ratio()
        
        # 3. 预期结果相似度
        similarities["expected_result"] = SequenceMatcher(
            None, case1.expected_result.lower(), case2.expected_result.lower()
        ).ratio()
        
        # 4. 模块功能相似度
        module_func1 = f"{case1.module}_{case1.function}".lower()
        module_func2 = f"{case2.module}_{case2.function}".lower()
        similarities["module_function"] = 1.0 if module_func1 == module_func2 else 0.0
        
        # 计算加权平均相似度
        total_similarity = sum(
            similarities[key] * weights[key] 
            for key in weights.keys()
        )
        
        return total_similarity
    
    def _generate_boundary_tests(self, cases: List[TestCase]) -> List[TestCase]:
        """
        生成边界值测试用例
        
        Args:
            cases: 现有测试用例
            
        Returns:
            边界值测试用例列表
        """
        boundary_cases = []
        
        # 按功能分组
        function_groups = self._group_by_function(cases)
        
        for (module, function), function_cases in function_groups.items():
            # 为每个功能生成边界值测试
            if self._needs_boundary_tests(function_cases):
                boundary_case = self._create_boundary_test_case(module, function)
                if boundary_case:
                    boundary_cases.append(boundary_case)
        
        return boundary_cases
    
    def _generate_negative_tests(self, cases: List[TestCase]) -> List[TestCase]:
        """
        生成负面测试用例
        
        Args:
            cases: 现有测试用例
            
        Returns:
            负面测试用例列表
        """
        negative_cases = []
        
        function_groups = self._group_by_function(cases)
        
        for (module, function), function_cases in function_groups.items():
            if self._needs_negative_tests(function_cases):
                negative_case = self._create_negative_test_case(module, function)
                if negative_case:
                    negative_cases.append(negative_case)
        
        return negative_cases
    
    def _generate_performance_tests(self, cases: List[TestCase]) -> List[TestCase]:
        """
        生成性能测试用例
        
        Args:
            cases: 现有测试用例
            
        Returns:
            性能测试用例列表
        """
        performance_cases = []
        
        function_groups = self._group_by_function(cases)
        
        for (module, function), function_cases in function_groups.items():
            if self._needs_performance_tests(function_cases):
                performance_case = self._create_performance_test_case(module, function)
                if performance_case:
                    performance_cases.append(performance_case)
        
        return performance_cases
    
    def _generate_security_tests(self, cases: List[TestCase]) -> List[TestCase]:
        """
        生成安全测试用例
        
        Args:
            cases: 现有测试用例
            
        Returns:
            安全测试用例列表
        """
        security_cases = []
        
        function_groups = self._group_by_function(cases)
        
        for (module, function), function_cases in function_groups.items():
            if self._needs_security_tests(function_cases, function):
                security_case = self._create_security_test_case(module, function)
                if security_case:
                    security_cases.append(security_case)
        
        return security_cases
    
    def _enhance_test_data(self, cases: List[TestCase]) -> List[TestCase]:
        """
        增强测试数据
        
        Args:
            cases: 测试用例列表
            
        Returns:
            增强后的测试用例列表
        """
        enhanced_cases = []
        
        for case in cases:
            enhanced_case = case
            
            # 增强测试步骤的输入数据
            enhanced_steps = []
            for step in case.steps:
                enhanced_step = TestStep(
                    step_number=step.step_number,
                    description=step.description,
                    input_data=self._enhance_input_data(step.input_data, case.function),
                    expected_behavior=step.expected_behavior
                )
                enhanced_steps.append(enhanced_step)
            
            enhanced_case.steps = enhanced_steps
            enhanced_cases.append(enhanced_case)
        
        return enhanced_cases
    
    def _improve_assertions(self, cases: List[TestCase]) -> List[TestCase]:
        """
        改进测试断言
        
        Args:
            cases: 测试用例列表
            
        Returns:
            改进后的测试用例列表
        """
        improved_cases = []
        
        for case in cases:
            improved_case = case
            
            # 改进预期结果的描述
            improved_case.expected_result = self._improve_expected_result(
                case.expected_result, case.function
            )
            
            # 改进测试步骤的预期行为
            improved_steps = []
            for step in case.steps:
                improved_step = TestStep(
                    step_number=step.step_number,
                    description=step.description,
                    input_data=step.input_data,
                    expected_behavior=self._improve_expected_behavior(
                        step.expected_behavior, case.function
                    )
                )
                improved_steps.append(improved_step)
            
            improved_case.steps = improved_steps
            improved_cases.append(improved_case)
        
        return improved_cases
    
    def _group_by_function(self, cases: List[TestCase]) -> Dict[Tuple[str, str], List[TestCase]]:
        """按模块和功能分组测试用例"""
        groups = {}
        for case in cases:
            key = (case.module, case.function)
            if key not in groups:
                groups[key] = []
            groups[key].append(case)
        return groups
    
    def _needs_boundary_tests(self, function_cases: List[TestCase]) -> bool:
        """判断是否需要边界值测试"""
        # 检查是否已有边界值测试
        for case in function_cases:
            if any(keyword in case.title.lower() for keyword in ["边界", "最大", "最小", "空"]):
                return False
        return True
    
    def _needs_negative_tests(self, function_cases: List[TestCase]) -> bool:
        """判断是否需要负面测试"""
        for case in function_cases:
            if any(keyword in case.title.lower() for keyword in ["异常", "错误", "失败", "无效"]):
                return False
        return True
    
    def _needs_performance_tests(self, function_cases: List[TestCase]) -> bool:
        """判断是否需要性能测试"""
        for case in function_cases:
            if any(keyword in case.title.lower() for keyword in ["性能", "负载", "压力", "并发"]):
                return False
        return True
    
    def _needs_security_tests(self, function_cases: List[TestCase], function_name: str) -> bool:
        """判断是否需要安全测试"""
        # 只为涉及用户输入或数据处理的功能添加安全测试
        security_keywords = ["登录", "注册", "输入", "查询", "搜索", "上传", "下载"]
        
        if not any(keyword in function_name for keyword in security_keywords):
            return False
        
        for case in function_cases:
            if any(keyword in case.title.lower() for keyword in ["安全", "注入", "攻击", "权限"]):
                return False
        return True
    
    def _create_boundary_test_case(self, module: str, function: str) -> TestCase:
        """创建边界值测试用例"""
        steps = [
            TestStep(1, "准备边界值测试数据", "最大值、最小值、空值", "数据准备完成"),
            TestStep(2, f"执行{function}功能", "边界值数据", "系统正确处理边界情况"),
            TestStep(3, "验证处理结果", None, "边界值处理符合预期")
        ]
        
        return TestCase(
            id="",  # 将在重新分配ID时设置
            module=module,
            function=function,
            title=f"{function}边界值测试",
            steps=steps,
            expected_result="系统能正确处理各种边界值情况，不出现异常",
            priority=Priority.HIGH,
            created_time=datetime.now()
        )
    
    def _create_negative_test_case(self, module: str, function: str) -> TestCase:
        """创建负面测试用例"""
        steps = [
            TestStep(1, "准备异常测试数据", "无效格式、非法参数", "异常数据准备完成"),
            TestStep(2, f"执行{function}功能", "异常数据", "系统检测到异常输入"),
            TestStep(3, "验证错误处理", None, "系统返回适当的错误信息")
        ]
        
        return TestCase(
            id="",
            module=module,
            function=function,
            title=f"{function}异常处理测试",
            steps=steps,
            expected_result="系统能正确识别和处理异常情况，返回友好的错误提示",
            priority=Priority.MEDIUM,
            created_time=datetime.now()
        )
    
    def _create_performance_test_case(self, module: str, function: str) -> TestCase:
        """创建性能测试用例"""
        steps = [
            TestStep(1, "准备性能测试环境", "大量测试数据", "测试环境准备完成"),
            TestStep(2, f"并发执行{function}功能", "100个并发请求", "系统处理并发请求"),
            TestStep(3, "监控系统性能指标", None, "记录响应时间和资源使用情况")
        ]
        
        return TestCase(
            id="",
            module=module,
            function=function,
            title=f"{function}性能测试",
            steps=steps,
            expected_result="系统在高负载下仍能正常工作，响应时间在可接受范围内",
            priority=Priority.MEDIUM,
            created_time=datetime.now()
        )
    
    def _create_security_test_case(self, module: str, function: str) -> TestCase:
        """创建安全测试用例"""
        steps = [
            TestStep(1, "准备安全测试数据", "SQL注入、XSS攻击代码", "恶意数据准备完成"),
            TestStep(2, f"尝试对{function}进行攻击", "恶意输入数据", "系统检测到攻击尝试"),
            TestStep(3, "验证安全防护效果", None, "系统成功阻止攻击")
        ]
        
        return TestCase(
            id="",
            module=module,
            function=function,
            title=f"{function}安全测试",
            steps=steps,
            expected_result="系统能有效防御常见的安全攻击，保护数据安全",
            priority=Priority.HIGH,
            created_time=datetime.now()
        )
    
    def _enhance_input_data(self, original_data: str, function_name: str) -> str:
        """增强输入数据"""
        if not original_data:
            return self._generate_sample_data(function_name)
        
        # 如果原始数据过于简单，进行增强
        if len(original_data) < 10:
            return f"{original_data} (增强: 包含特殊字符、边界值等)"
        
        return original_data
    
    def _improve_expected_result(self, original_result: str, function_name: str) -> str:
        """改进预期结果描述"""
        if not original_result:
            return f"{function_name}执行成功，返回预期结果"
        
        # 添加更具体的验证点
        if "成功" in original_result and "验证" not in original_result:
            return f"{original_result}，并验证数据完整性和状态一致性"
        
        return original_result
    
    def _improve_expected_behavior(self, original_behavior: str, function_name: str) -> str:
        """改进预期行为描述"""
        if not original_behavior:
            return "系统正确响应操作"
        
        # 添加更详细的行为描述
        if len(original_behavior) < 20:
            return f"{original_behavior}，界面状态更新，用户收到反馈"
        
        return original_behavior
    
    def _generate_sample_data(self, function_name: str) -> str:
        """为功能生成示例数据"""
        data_templates = {
            "登录": "用户名: testuser, 密码: Test123!",
            "注册": "邮箱: test@example.com, 密码: SecurePass123",
            "搜索": "关键词: 测试数据, 过滤条件: 时间范围",
            "上传": "文件: test.jpg (2MB), 格式: JPEG",
            "查询": "查询条件: ID=123, 状态=active"
        }
        
        for keyword, template in data_templates.items():
            if keyword in function_name:
                return template
        
        return "测试数据"
    
    def _reassign_case_ids(self, cases: List[TestCase]) -> List[TestCase]:
        """重新分配测试用例ID"""
        for i, case in enumerate(cases):
            case.id = f"TC_{i + 1:03d}"
        return cases
    
    def get_optimization_report(self, original_cases: List[TestCase], 
                              optimized_cases: List[TestCase]) -> Dict[str, Any]:
        """
        生成优化报告
        
        Args:
            original_cases: 原始测试用例
            optimized_cases: 优化后测试用例
            
        Returns:
            优化报告字典
        """
        original_count = len(original_cases)
        optimized_count = len(optimized_cases)
        improvement_ratio = (optimized_count - original_count) / original_count if original_count > 0 else 0
        
        # 统计新增用例类型
        new_cases = optimized_cases[original_count:]
        case_types = {
            "boundary": 0,
            "negative": 0,
            "performance": 0,
            "security": 0,
            "enhanced": 0
        }
        
        for case in new_cases:
            title_lower = case.title.lower()
            if "边界" in title_lower:
                case_types["boundary"] += 1
            elif "异常" in title_lower or "错误" in title_lower:
                case_types["negative"] += 1
            elif "性能" in title_lower or "并发" in title_lower:
                case_types["performance"] += 1
            elif "安全" in title_lower:
                case_types["security"] += 1
            else:
                case_types["enhanced"] += 1
        
        return {
            "original_count": original_count,
            "optimized_count": optimized_count,
            "added_count": optimized_count - original_count,
            "improvement_ratio": improvement_ratio,
            "target_achieved": improvement_ratio >= self.improvement_target,
            "new_case_types": case_types,
            "optimization_rules_applied": {
                rule: enabled for rule, enabled in self.optimization_rules.items()
            }
        }
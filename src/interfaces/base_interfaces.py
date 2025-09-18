"""
Base interfaces for the Test Case Generator application.
"""

from abc import ABC, abstractmethod
from typing import List

from ..models.data_models import (
    ParsedContent, StructuredInfo, TestCase, ExportResult,
    OCRResult, LLMResponse, ValidationResult, ExportFormat,
    ErrorResponse
)


class IUIController(ABC):
    """用户界面控制器接口"""
    
    @abstractmethod
    def handle_file_upload(self, file_path: str) -> bool:
        """处理文件上传"""
        pass
    
    @abstractmethod
    def display_parsed_content(self, content: ParsedContent) -> None:
        """显示解析内容"""
        pass
    
    @abstractmethod
    def show_generated_cases(self, cases: List[TestCase]) -> None:
        """显示生成的测试用例"""
        pass
    
    @abstractmethod
    def handle_export_request(self, format: ExportFormat, path: str) -> bool:
        """处理导出请求"""
        pass


class IPRDParser(ABC):
    """PRD解析器接口"""
    
    @abstractmethod
    def parse_document(self, file_path: str) -> ParsedContent:
        """解析文档"""
        pass
    
    @abstractmethod
    def extract_structured_info(self, raw_text: str) -> StructuredInfo:
        """提取结构化信息"""
        pass
    
    @abstractmethod
    def validate_extraction(self, info: StructuredInfo) -> ValidationResult:
        """验证提取结果"""
        pass


class IOCRService(ABC):
    """OCR识别服务接口"""
    
    @abstractmethod
    def recognize_text(self, image_path: str) -> OCRResult:
        """识别图片中的文字"""
        pass
    
    @abstractmethod
    def set_confidence_threshold(self, threshold: float) -> None:
        """设置置信度阈值"""
        pass


class ITestCaseGenerator(ABC):
    """测试用例生成器接口"""
    
    @abstractmethod
    def generate_cases(self, structured_info: StructuredInfo) -> List[TestCase]:
        """生成测试用例"""
        pass
    
    @abstractmethod
    def optimize_cases(self, cases: List[TestCase]) -> List[TestCase]:
        """优化测试用例"""
        pass
    
    @abstractmethod
    def validate_cases(self, cases: List[TestCase]) -> ValidationResult:
        """验证测试用例"""
        pass


class ILLMService(ABC):
    """大模型API服务接口"""
    
    @abstractmethod
    def call_api(self, prompt: str, model: str) -> LLMResponse:
        """调用大模型API"""
        pass
    
    @abstractmethod
    def set_retry_config(self, max_retries: int, interval: float) -> None:
        """设置重试配置"""
        pass


class IExporter(ABC):
    """导出器接口"""
    
    @abstractmethod
    def export(self, cases: List[TestCase], output_path: str) -> ExportResult:
        """导出测试用例"""
        pass
    
    @abstractmethod
    def validate_output(self, output_path: str) -> bool:
        """验证输出文件"""
        pass


class IFormatConverter(ABC):
    """格式转换器接口"""
    
    @abstractmethod
    def convert_to_json(self, cases: List[TestCase]) -> dict:
        """转换为JSON格式"""
        pass
    
    @abstractmethod
    def convert_to_xmind(self, cases: List[TestCase]) -> dict:
        """转换为XMind格式数据"""
        pass


class IConfigManager(ABC):
    """配置管理器接口"""
    
    @abstractmethod
    def save_api_key(self, service: str, key: str) -> bool:
        """保存API密钥"""
        pass
    
    @abstractmethod
    def get_api_key(self, service: str) -> str:
        """获取API密钥"""
        pass
    
    @abstractmethod
    def clear_all_keys(self) -> bool:
        """清除所有密钥"""
        pass



class IErrorHandler(ABC):
    """错误处理器接口"""
    
    @abstractmethod
    def handle_error(self, error: Exception, context: str) -> ErrorResponse:
        """处理错误"""
        pass
    
    @abstractmethod
    def attempt_recovery(self, error: Exception, context: str) -> ErrorResponse:
        """尝试错误恢复"""
        pass
"""
Core data models for the Test Case Generator application.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class Priority(Enum):
    """Test case priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestCaseType(Enum):
    """Test case types."""
    FUNCTIONAL = "功能测试"
    UI = "界面测试"
    PERFORMANCE = "性能测试"
    SECURITY = "安全测试"
    COMPATIBILITY = "兼容性测试"


class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    XMIND = "xmind"


class LLMProvider(Enum):
    """LLM provider types - 统一使用 OpenAI 兼容接口"""
    OPENAI = "openai"


@dataclass
class ParsedContent:
    """解析后的PRD内容"""
    text: str
    images: Optional[List] = None
    metadata: Optional[dict] = None


@dataclass
class StructuredInfo:
    """结构化信息"""
    modules: List['Module']
    business_rules: List[str]
    constraints: List[str]
    extraction_coverage: float


@dataclass
class Module:
    """功能模块"""
    name: str
    description: str
    functions: List['Function']


@dataclass
class Function:
    """功能点"""
    name: str
    description: str
    inputs: List[str]
    outputs: List[str]
    business_rules: List[str]


@dataclass
class TestStep:
    """测试步骤"""
    step_number: int
    description: str
    input_data: Optional[str]
    expected_behavior: str


@dataclass
class TestCase:
    """测试用例"""
    id: str
    title: str
    module: Optional[str] = None
    function: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    priority: Optional[Priority] = None
    type: Optional[TestCaseType] = None
    preconditions: Optional[str] = None
    created_time: Optional[datetime] = None
class ExportConfig:
    """导出配置"""
    format: ExportFormat
    output_path: str
    indent_size: int = 2
    include_metadata: bool = True


@dataclass
class OCRResult:
    """OCR识别结果"""
    text: str
    confidence: float
    processing_time: float
    error_message: Optional[str] = None


@dataclass
class LLMResponse:
    """大模型API响应"""
    content: str
    model: str
    tokens_used: int
    response_time: float
    error_message: Optional[str] = None


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


@dataclass
class ExportResult:
    """导出结果"""
    success: bool
    output_path: str
    file_size: int
    export_time: datetime
    error_message: Optional[str] = None


@dataclass
class ErrorResponse:
    """错误响应"""
    error_type: str
    message: str
    context: str
    recoverable: bool
    suggested_action: Optional[str] = None
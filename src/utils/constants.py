#!/usr/bin/env python3
"""
常量定义文件
"""

# 应用信息
APP_NAME = "测试用例生成器"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "基于AI的PRD文档测试用例生成工具"

# 窗口设置
MIN_WINDOW_WIDTH = 1280
MIN_WINDOW_HEIGHT = 720
DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 800

# 文件支持
SUPPORTED_FILE_TYPES = ['.png', '.jpg', '.jpeg', '.pdf', '.docx']
SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg']
SUPPORTED_DOCUMENT_FORMATS = ['.pdf', '.docx']
SUPPORTED_FORMATS = SUPPORTED_FILE_TYPES  # 别名
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_FILE_SIZE = MAX_FILE_SIZE_BYTES  # 别名
MAX_IMAGE_SIZE = MAX_FILE_SIZE_BYTES  # 图片大小限制

# 测试用例字段
TEST_CASE_FIELDS = [
    'id',
    'title', 
    'module',
    'function',
    'type',
    'priority',
    'preconditions',
    'steps',
    'expected_result'
]

# 处理步骤
PROCESSING_STEPS = [
    "解析文档文件",
    "提取结构化信息", 
    "生成测试用例",
    "优化测试用例",
    "生成处理报告"
]

# 主题配置
LIGHT_THEME = {
    'name': 'light',
    'background': '#ffffff',
    'foreground': '#000000',
    'accent': '#2196F3',
    'success': '#4CAF50',
    'warning': '#ff9800',
    'error': '#f44336'
}

DARK_THEME = {
    'name': 'dark',
    'background': '#2b2b2b',
    'foreground': '#ffffff',
    'accent': '#2196F3',
    'success': '#4CAF50',
    'warning': '#ff9800',
    'error': '#f44336'
}

# 默认配置
DEFAULT_CONFIG = {
    # LLM配置
    'openai_api_key': '',
    'openai_base_url': 'https://api.openai.com/v1',
    'openai_model': 'gpt-4o-mini',
    'openai_timeout': 60,
    'claude_api_key': '',
    'claude_base_url': 'https://api.anthropic.com',
    'claude_model': 'claude-3-5-sonnet-20241022',
    'claude_timeout': 60,
    'default_llm_provider': 'openai',
    
    # OCR配置
    'tesseract_path': '',
    'tesseract_lang': 'chi_sim+eng',
    'tesseract_config': '--oem 3 --psm 6',
    'enable_paddle_ocr': False,
    'paddle_lang': 'ch',
    'paddle_use_gpu': False,
    'ocr_retry_count': 3,
    'ocr_timeout': 30,
    'enable_image_enhance': True,
    
    # UI配置
    'theme': 'light',
    'font_size': 10,
    'window_width': DEFAULT_WINDOW_WIDTH,
    'window_height': DEFAULT_WINDOW_HEIGHT,
    'remember_window_state': True,
    'show_splash': True,
    'show_statusbar': True,
    'show_toolbar': True,
    
    # 高级配置
    'max_workers': 4,
    'memory_limit': 1024,
    'cache_size': 100,
    'log_level': 'INFO',
    'log_file_path': '',
    'log_retention_days': 30,
    'auto_save': True,
    'backup_config': True
}

# 错误消息
ERROR_MESSAGES = {
    'file_not_found': '文件不存在: {}',
    'file_too_large': '文件过大，超过 {}MB 限制: {}',
    'unsupported_format': '不支持的文件格式: {}',
    'ocr_failed': 'OCR识别失败: {}',
    'llm_api_error': 'LLM API调用失败: {}',
    'config_load_error': '配置加载失败: {}',
    'config_save_error': '配置保存失败: {}',
    'processing_error': '处理过程中发生错误: {}',
    'validation_error': '数据验证失败: {}'
}

# 成功消息
SUCCESS_MESSAGES = {
    'file_processed': '文件处理成功: {}',
    'test_cases_generated': '成功生成 {} 个测试用例',
    'config_saved': '配置保存成功',
    'export_completed': '导出完成: {}',
    'processing_completed': '处理完成'
}

# 状态消息
STATUS_MESSAGES = {
    'ready': '就绪',
    'processing': '处理中...',
    'completed': '完成',
    'error': '错误',
    'cancelled': '已取消'
}

# 导出格式
EXPORT_FORMATS = {
    'excel': {
        'name': 'Excel文件',
        'extension': '.xlsx',
        'filter': 'Excel文件 (*.xlsx)'
    },
    'csv': {
        'name': 'CSV文件',
        'extension': '.csv',
        'filter': 'CSV文件 (*.csv)'
    },
    'json': {
        'name': 'JSON文件',
        'extension': '.json',
        'filter': 'JSON文件 (*.json)'
    },
    'word': {
        'name': 'Word文档',
        'extension': '.docx',
        'filter': 'Word文档 (*.docx)'
    }
}

# 日志配置
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# 缓存配置
CACHE_DIR = '.cache'
TEMP_DIR = '.temp'
CONFIG_DIR = '.config'

# API配置
API_RETRY_COUNT = 3
API_RETRY_DELAY = 1.0
API_MAX_TOKENS = 4000
API_TEMPERATURE = 0.7

# 测试用例生成配置
MIN_TEST_CASES_PER_FUNCTION = 3
MAX_TEST_CASES_PER_FUNCTION = 10
SIMILARITY_THRESHOLD = 0.8
OPTIMIZATION_TARGET_INCREASE = 0.3
MIN_CASE_IMPROVEMENT = 0.3
DUPLICATE_SIMILARITY_THRESHOLD = 0.8

# OCR配置
OCR_CONFIDENCE_THRESHOLD = 0.6
OCR_MIN_COVERAGE = 0.8
OCR_MAX_RETRIES = 3
OCR_TIMEOUT_SECONDS = 30

# LLM配置
LLM_MAX_RETRIES = 3
LLM_TIMEOUT_SECONDS = 60
LLM_MAX_TOKENS = 4000
LLM_TEMPERATURE = 0.7
LLM_TIMEOUT = 60
LLM_RETRY_INTERVAL = 1.0

# 配置管理
DEFAULT_EXPORT_PATH = "./exports"
JSON_INDENT_OPTIONS = [2, 4]
CONFIG_FILE_ENCODING = "utf-8"
BACKUP_CONFIG_SUFFIX = ".backup"
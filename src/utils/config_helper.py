"""
配置辅助工具类
"""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..services.config.config_manager import ConfigManager

from ..models.data_models import LLMProvider


class ConfigHelper:
    """配置辅助工具类，提供全局配置访问"""
    
    _instance: Optional['ConfigHelper'] = None
    _config_manager: Optional['ConfigManager'] = None
    
    def __new__(cls) -> 'ConfigHelper':
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置辅助工具"""
        if self._config_manager is None:
            from ..services.config.config_manager import ConfigManager
            self._config_manager = ConfigManager()
    
    @property
    def config_manager(self) -> 'ConfigManager':
        """获取配置管理器实例"""
        return self._config_manager
    
    # UI配置快捷访问
    @property
    def window_width(self) -> int:
        """获取窗口宽度"""
        return self._config_manager.get_config('ui.window_width', 1280)
    
    @property
    def window_height(self) -> int:
        """获取窗口高度"""
        return self._config_manager.get_config('ui.window_height', 720)
    
    @property
    def theme(self) -> str:
        """获取主题"""
        return self._config_manager.get_config('ui.theme', 'light')
    
    @property
    def language(self) -> str:
        """获取语言设置"""
        return self._config_manager.get_config('ui.language', 'zh_CN')
    
    @property
    def auto_save(self) -> bool:
        """获取自动保存设置"""
        return self._config_manager.get_config('ui.auto_save', True)
    
    # OCR配置快捷访问
    @property
    def ocr_service(self) -> str:
        """获取OCR服务"""
        return self._config_manager.get_config('ocr.service', 'paddleocr')
    
    @property
    def ocr_confidence_threshold(self) -> float:
        """获取OCR置信度阈值"""
        return self._config_manager.get_config('ocr.confidence_threshold', 0.95)
    
    @property
    def ocr_min_coverage(self) -> float:
        """获取OCR最小覆盖率"""
        return self._config_manager.get_config('ocr.min_coverage', 0.90)
    
    @property
    def ocr_language(self) -> str:
        """获取OCR识别语言"""
        return self._config_manager.get_config('ocr.language', 'ch')
    
    # LLM配置快捷访问
    @property
    def llm_service(self) -> str:
        """获取默认LLM服务"""
        return self._config_manager.get_config('llm.default_service', 'openai')
    
    @property
    def llm_timeout(self) -> float:
        """获取LLM超时时间"""
        return self._config_manager.get_config('llm.timeout', 5.0)
    
    @property
    def llm_max_retries(self) -> int:
        """获取LLM最大重试次数"""
        return self._config_manager.get_config('llm.max_retries', 3)
    
    @property
    def llm_retry_interval(self) -> float:
        """获取LLM重试间隔"""
        return self._config_manager.get_config('llm.retry_interval', 2.0)
    
    @property
    def llm_temperature(self) -> float:
        """获取LLM温度参数"""
        return self._config_manager.get_config('llm.temperature', 0.7)
    
    @property
    def llm_max_tokens(self) -> int:
        """获取LLM最大令牌数"""
        return self._config_manager.get_config('llm.max_tokens', 2000)
    
    # 导出配置快捷访问
    @property
    def export_format(self) -> str:
        """获取默认导出格式"""
        return self._config_manager.get_config('export.default_format', 'json')
    
    @property
    def export_path(self) -> str:
        """获取默认导出路径"""
        return self._config_manager.get_config('export.default_path', './exports')
    
    @property
    def json_indent(self) -> int:
        """获取JSON缩进"""
        return self._config_manager.get_config('export.json_indent', 2)
    
    @property
    def auto_open_after_export(self) -> bool:
        """获取导出后自动打开设置"""
        return self._config_manager.get_config('export.auto_open_after_export', True)
    
    @property
    def remember_window_state(self) -> bool:
        """获取是否记住窗口状态"""
        return self._config_manager.get_config('ui.remember_window_state', True)
    
    # 统一的 LLM 配置属性（OpenAI 兼容）
    @property
    def openai_api_key(self) -> str:
        """获取 LLM API 密钥"""
        return self._config_manager.get_config('llm.api_key', '')
    
    @property
    def openai_base_url(self) -> str:
        """获取 LLM API 端点"""
        return self._config_manager.get_config('llm.api_endpoint', 'https://api.openai.com/v1/chat/completions')
    
    @property
    def openai_model(self) -> str:
        """获取 LLM 模型"""
        return self._config_manager.get_config('llm.model', 'gpt-4o-mini')
    
    @property
    def openai_timeout(self) -> int:
        """获取 LLM 超时时间"""
        return int(self._config_manager.get_config('llm.timeout', 60))
    
    # 为了兼容性保留 Claude 相关属性，但实际使用统一配置
    @property
    def claude_api_key(self) -> str:
        """获取 LLM API 密钥（兼容性）"""
        return self.openai_api_key
    
    @property
    def claude_base_url(self) -> str:
        """获取 LLM API 端点（兼容性）"""
        return self.openai_base_url
    
    @property
    def claude_model(self) -> str:
        """获取 LLM 模型（兼容性）"""
        return self.openai_model
    
    @property
    def claude_timeout(self) -> int:
        """获取 LLM 超时时间（兼容性）"""
        return self.openai_timeout
    
    @property
    def default_llm_provider(self) -> Optional[LLMProvider]:
        """获取默认LLM提供商"""
        return LLMProvider.OPENAI  # 统一使用 OpenAI 兼容接口
    
    # OCR配置属性
    @property
    def tesseract_path(self) -> str:
        """获取Tesseract路径"""
        return self._config_manager.get_config('ocr.tesseract_path', '')
    
    @property
    def tesseract_lang(self) -> str:
        """获取Tesseract语言"""
        return self._config_manager.get_config('ocr.tesseract_lang', 'chi_sim+eng')
    
    @property
    def tesseract_config(self) -> str:
        """获取Tesseract配置"""
        return self._config_manager.get_config('ocr.tesseract_config', '--oem 3 --psm 6')
    
    @property
    def enable_paddle_ocr(self) -> bool:
        """获取是否启用PaddleOCR"""
        return self._config_manager.get_config('ocr.enable_paddle', False)
    
    @property
    def paddle_lang(self) -> str:
        """获取PaddleOCR语言"""
        return self._config_manager.get_config('ocr.paddle_lang', 'ch')
    
    @property
    def paddle_use_gpu(self) -> bool:
        """获取PaddleOCR是否使用GPU"""
        return self._config_manager.get_config('ocr.paddle_use_gpu', False)
    
    @property
    def ocr_retry_count(self) -> int:
        """获取OCR重试次数"""
        return self._config_manager.get_config('ocr.retry_count', 3)
    
    @property
    def ocr_timeout(self) -> int:
        """获取OCR超时时间"""
        return self._config_manager.get_config('ocr.timeout', 30)
    
    @property
    def enable_image_enhance(self) -> bool:
        """获取是否启用图像增强"""
        return self._config_manager.get_config('ocr.enable_image_enhance', True)
    
    # UI配置属性
    @property
    def font_size(self) -> int:
        """获取字体大小"""
        return self._config_manager.get_config('ui.font_size', 10)
    
    @property
    def remember_window_state(self) -> bool:
        """获取是否记住窗口状态"""
        return self._config_manager.get_config('ui.remember_window_state', True)
    
    @property
    def show_splash(self) -> bool:
        """获取是否显示启动画面"""
        return self._config_manager.get_config('ui.show_splash', True)
    
    @property
    def show_statusbar(self) -> bool:
        """获取是否显示状态栏"""
        return self._config_manager.get_config('ui.show_statusbar', True)
    
    @property
    def show_toolbar(self) -> bool:
        """获取是否显示工具栏"""
        return self._config_manager.get_config('ui.show_toolbar', True)
    
    # 高级配置属性
    @property
    def max_workers(self) -> int:
        """获取最大工作线程数"""
        return self._config_manager.get_config('performance.max_workers', 4)
    
    @property
    def memory_limit(self) -> int:
        """获取内存限制（MB）"""
        return self._config_manager.get_config('performance.memory_limit', 1024)
    
    @property
    def cache_size(self) -> int:
        """获取缓存大小"""
        return self._config_manager.get_config('performance.cache_size', 100)
    
    @property
    def log_level(self) -> str:
        """获取日志级别"""
        return self._config_manager.get_config('logging.level', 'INFO')
    
    @property
    def log_file_path(self) -> str:
        """获取日志文件路径"""
        return self._config_manager.get_config('logging.file_path', '')
    
    @property
    def log_retention_days(self) -> int:
        """获取日志保留天数"""
        return self._config_manager.get_config('logging.retention_days', 30)
    
    @property
    def backup_config(self) -> bool:
        """获取是否备份配置"""
        return self._config_manager.get_config('ui.backup_config', True)
    
    # 性能配置快捷访问
    @property
    def max_file_size_mb(self) -> int:
        """获取最大文件大小（MB）"""
        return self._config_manager.get_config('performance.max_file_size_mb', 50)
    
    @property
    def max_image_size_mb(self) -> int:
        """获取最大图片大小（MB）"""
        return self._config_manager.get_config('performance.max_image_size_mb', 10)
    
    @property
    def batch_size(self) -> int:
        """获取批处理大小"""
        return self._config_manager.get_config('performance.batch_size', 10)
    
    @property
    def enable_cache(self) -> bool:
        """获取缓存启用状态"""
        return self._config_manager.get_config('performance.enable_cache', True)
    
    # API密钥管理（统一接口）
    def get_openai_api_key(self) -> str:
        """获取 LLM API 密钥"""
        return self._config_manager.get_config('llm.api_key', '')
    
    def get_claude_api_key(self) -> str:
        """获取 LLM API 密钥（兼容性）"""
        return self.get_openai_api_key()
    
    def get_custom_api_key(self, service: str) -> str:
        """获取 LLM API 密钥（兼容性）"""
        return self.get_openai_api_key()
    
    def set_api_key(self, service: str, key: str) -> bool:
        """设置 LLM API 密钥"""
        return self._config_manager.set_config('llm.api_key', key)
    
    # 新增的统一 LLM 配置方法
    def get_llm_api_key(self) -> str:
        """获取 LLM API 密钥"""
        return self._config_manager.get_config('llm.api_key', '')
    
    def get_llm_api_endpoint(self) -> str:
        """获取 LLM API 端点"""
        return self._config_manager.get_config('llm.api_endpoint', 'https://api.openai.com/v1/chat/completions')
    
    def get_llm_model(self) -> str:
        """获取 LLM 模型"""
        return self._config_manager.get_config('llm.model', 'gpt-4o-mini')
    
    def get_llm_presets(self) -> dict:
        """获取 LLM 预设配置"""
        return self._config_manager.get_config('llm.presets', {})
    
    def set_llm_config(self, api_endpoint: str = None, api_key: str = None, 
                      model: str = None, **kwargs) -> bool:
        """设置 LLM 配置"""
        success = True
        if api_endpoint is not None:
            success &= self._config_manager.set_config('llm.api_endpoint', api_endpoint)
        if api_key is not None:
            success &= self._config_manager.set_config('llm.api_key', api_key)
        if model is not None:
            success &= self._config_manager.set_config('llm.model', model)
        
        # 设置其他参数
        for key, value in kwargs.items():
            if key in ['timeout', 'temperature', 'max_tokens', 'max_retries', 'retry_interval']:
                success &= self._config_manager.set_config(f'llm.{key}', value)
        
        return success
    
    def apply_llm_preset(self, preset_name: str) -> bool:
        """应用 LLM 预设配置（仅设置端点，模型需用户手动输入）"""
        presets = self.get_llm_presets()
        if preset_name not in presets:
            return False
        
        preset = presets[preset_name]
        return self.set_llm_config(
            api_endpoint=preset.get('api_endpoint', '')
            # 不设置模型，由用户自行输入
        )
    
    # 配置更新方法
    def update_ui_config(self, **kwargs) -> bool:
        """更新UI配置"""
        success = True
        for key, value in kwargs.items():
            if not self._config_manager.set_config(f'ui.{key}', value):
                success = False
        return success
    
    def update_ocr_config(self, **kwargs) -> bool:
        """更新OCR配置"""
        success = True
        for key, value in kwargs.items():
            if not self._config_manager.set_config(f'ocr.{key}', value):
                success = False
        return success
    
    def update_llm_config(self, **kwargs) -> bool:
        """更新LLM配置"""
        success = True
        for key, value in kwargs.items():
            if not self._config_manager.set_config(f'llm.{key}', value):
                success = False
        return success
    
    def update_export_config(self, **kwargs) -> bool:
        """更新导出配置"""
        success = True
        for key, value in kwargs.items():
            if not self._config_manager.set_config(f'export.{key}', value):
                success = False
        return success
    
    def validate_all_config(self) -> dict:
        """验证所有配置"""
        return self._config_manager.validate_config()
    
    def reset_section(self, section: str) -> bool:
        """重置配置部分"""
        return self._config_manager.reset_to_default(section)
    
    def reset_all(self) -> bool:
        """重置所有配置"""
        return self._config_manager.reset_to_default()
    
    def reset_to_defaults(self) -> bool:
        """重置到默认配置（别名方法）"""
        return self.reset_all()


# 全局配置实例
config = ConfigHelper()
"""
配置辅助工具类
"""

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..services.config.config_manager import ConfigManager


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
    
    @property
    def openai_api_key(self) -> str:
        """获取OpenAI API密钥"""
        return self.get_openai_api_key()
    
    @property
    def claude_api_key(self) -> str:
        """获取Claude API密钥"""
        return self.get_claude_api_key()
    
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
    
    # API密钥管理
    def get_openai_api_key(self) -> str:
        """获取OpenAI API密钥"""
        return self._config_manager.get_api_key('openai')
    
    def get_claude_api_key(self) -> str:
        """获取Claude API密钥"""
        return self._config_manager.get_api_key('claude')
    
    def get_custom_api_key(self, service: str) -> str:
        """获取自定义服务API密钥"""
        return self._config_manager.get_api_key(service)
    
    def set_api_key(self, service: str, key: str) -> bool:
        """设置API密钥"""
        return self._config_manager.save_api_key(service, key)
    
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


# 全局配置实例
config = ConfigHelper()
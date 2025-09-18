"""
配置管理器实现
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...interfaces.base_interfaces import IConfigManager
from ...models.data_models import ErrorResponse
from ...utils.constants import DEFAULT_EXPORT_PATH, JSON_INDENT_OPTIONS


class ConfigManager(IConfigManager):
    """配置管理器实现"""
    
    def __init__(self):
        self.config_dir = Path.home()
        self.config_file = self.config_dir / 'config.json'
        self._config_cache: Dict[str, Any] = {}
        self._default_config = self._get_default_config()
        self._load_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'ui': {
                'window_width': 1280,
                'window_height': 720,
                'theme': 'light',
                'language': 'zh_CN',
                'remember_window_size': True,
                'auto_save': True
            },
            'ocr': {
                'service': 'paddleocr',  # paddleocr, tesseract
                'confidence_threshold': 0.95,
                'min_coverage': 0.90,
                'auto_correct': True,
                'language': 'ch'
            },
            'llm': {
                'default_service': 'custom',  # openai, claude, custom
                'timeout': 5.0,
                'max_retries': 3,
                'retry_interval': 2.0,
                'temperature': 0.7,
                'max_tokens': 2000,
                'providers': {
                    'openai': {
                        'api_endpoint': 'https://api.openai.com/v1/chat/completions',
                        'default_model': 'gpt-3.5-turbo',
                        'models': [
                            'gpt-3.5-turbo',
                            'gpt-3.5-turbo-16k',
                            'gpt-4',
                            'gpt-4-turbo-preview',
                            'gpt-4o'
                        ]
                    },
                    'claude': {
                        'api_endpoint': 'https://api.anthropic.com/v1/messages',
                        'default_model': 'claude-3-sonnet-20240229',
                        'models': [
                            'claude-3-haiku-20240307',
                            'claude-3-sonnet-20240229',
                            'claude-3-opus-20240229',
                            'claude-3-5-sonnet-20241022'
                        ]
                    },
                    'custom': {
                        'api_endpoint': 'https://api.smnet.studio/v1',
                        'default_model': 'deepseek-chat',
                        'models': []
                    }
                }
            },
            'export': {
                'default_format': 'json',  # json, xmind
                'default_path': DEFAULT_EXPORT_PATH,
                'json_indent': JSON_INDENT_OPTIONS[0],
                'auto_open_after_export': True,
                'include_metadata': True
            },
            'performance': {
                'max_file_size_mb': 50,
                'max_image_size_mb': 10,
                'batch_size': 10,
                'enable_cache': True
            }
        }
    
    def _load_config(self):
        """加载配置文件"""
        import copy
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并默认配置和加载的配置
                    self._config_cache = self._merge_config(copy.deepcopy(self._default_config), loaded_config)
            else:
                self._config_cache = copy.deepcopy(self._default_config)
                self._save_config()
        except Exception as e:
            # 配置文件损坏，使用默认配置
            print(f"配置文件加载失败，使用默认配置: {e}")
            self._config_cache = copy.deepcopy(self._default_config)
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """合并配置，确保所有默认键都存在"""
        import copy
        result = copy.deepcopy(default)
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = copy.deepcopy(value) if isinstance(value, (dict, list)) else value
        return result
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"配置文件保存失败: {e}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self._config_cache
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set_config(self, key: str, value: Any) -> bool:
        """设置配置项"""
        try:
            keys = key.split('.')
            config = self._config_cache
            
            # 导航到目标位置
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            self._save_config()
            return True
        except Exception as e:
            print(f"设置配置项失败: {e}")
            return False
    
    def delete_config(self, key: str) -> bool:
        """删除配置项"""
        try:
            keys = key.split('.')
            config = self._config_cache
            
            # 导航到父级
            for k in keys[:-1]:
                config = config[k]
            
            # 删除键
            if keys[-1] in config:
                del config[keys[-1]]
                self._save_config()
                return True
            return False
        except Exception as e:
            print(f"删除配置项失败: {e}")
            return False
    
    def reset_to_default(self, section: Optional[str] = None) -> bool:
        """重置配置到默认值"""
        try:
            if section:
                if section in self._default_config:
                    # 深拷贝默认配置的指定部分
                    import copy
                    self._config_cache[section] = copy.deepcopy(self._default_config[section])
            else:
                # 深拷贝整个默认配置
                import copy
                self._config_cache = copy.deepcopy(self._default_config)
            
            self._save_config()
            return True
        except Exception as e:
            print(f"重置配置失败: {e}")
            return False
    
    def validate_config(self) -> Dict[str, str]:
        """验证配置有效性"""
        errors = {}
        
        # 验证UI配置
        ui_config = self.get_config('ui', {})
        if ui_config.get('window_width', 0) < 800:
            errors['ui.window_width'] = '窗口宽度不能小于800像素'
        if ui_config.get('window_height', 0) < 600:
            errors['ui.window_height'] = '窗口高度不能小于600像素'
        
        # 验证OCR配置
        ocr_config = self.get_config('ocr', {})
        confidence = ocr_config.get('confidence_threshold', 0)
        if not (0.0 <= confidence <= 1.0):
            errors['ocr.confidence_threshold'] = '置信度阈值必须在0.0-1.0之间'
        
        # 验证LLM配置
        llm_config = self.get_config('llm', {})
        if llm_config.get('timeout', 0) <= 0:
            errors['llm.timeout'] = '超时时间必须大于0'
        if llm_config.get('max_retries', 0) < 0:
            errors['llm.max_retries'] = '最大重试次数不能为负数'
        
        # 验证导出配置
        export_config = self.get_config('export', {})
        json_indent = export_config.get('json_indent', 2)
        if json_indent not in JSON_INDENT_OPTIONS:
            errors['export.json_indent'] = f'JSON缩进必须是{JSON_INDENT_OPTIONS}中的一个'
        
        return errors
    
    def save_api_key(self, service: str, key: str) -> bool:
        """保存API密钥（明文存储）"""
        try:
            return self.set_config(f'api_keys.{service}', key)
        except Exception as e:
            print(f"保存API密钥失败: {e}")
            return False
    
    def get_api_key(self, service: str) -> str:
        """获取API密钥"""
        try:
            return self.get_config(f'api_keys.{service}', '')
        except Exception as e:
            print(f"获取API密钥失败: {e}")
            return ''
    
    def clear_all_keys(self) -> bool:
        """清除所有API密钥"""
        try:
            return self.delete_config('api_keys')
        except Exception as e:
            print(f"清除API密钥失败: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """获取所有配置（包含API密钥）"""
        return self._config_cache.copy()
    
    def export_config(self, file_path: str, include_api_keys: bool = True) -> bool:
        """导出配置到文件"""
        try:
            config = self._config_cache.copy()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, file_path: str) -> bool:
        """从文件导入配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 验证导入的配置
            temp_config = self._merge_config(self._default_config, imported_config)
            
            # 如果验证通过，应用配置
            self._config_cache = temp_config
            self._save_config()
            return True
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
    
    def add_llm_provider(self, provider_name: str, api_endpoint: str, 
                        default_model: str, models: List[str] = None) -> bool:
        """
        添加新的LLM提供商配置
        
        Args:
            provider_name: 提供商名称
            api_endpoint: API端点URL
            default_model: 默认模型
            models: 支持的模型列表
            
        Returns:
            是否成功
        """
        try:
            provider_config = {
                'api_endpoint': api_endpoint,
                'default_model': default_model,
                'models': models or [default_model]
            }
            return self.set_config(f'llm.providers.{provider_name}', provider_config)
        except Exception as e:
            print(f"添加LLM提供商失败: {e}")
            return False
    
    def update_llm_provider(self, provider_name: str, **kwargs) -> bool:
        """
        更新LLM提供商配置
        
        Args:
            provider_name: 提供商名称
            **kwargs: 要更新的配置项
            
        Returns:
            是否成功
        """
        try:
            current_config = self.get_config(f'llm.providers.{provider_name}', {})
            if not current_config:
                return False
            
            # 更新配置
            for key, value in kwargs.items():
                if key in ['api_endpoint', 'default_model', 'models']:
                    current_config[key] = value
            
            return self.set_config(f'llm.providers.{provider_name}', current_config)
        except Exception as e:
            print(f"更新LLM提供商失败: {e}")
            return False
    
    def remove_llm_provider(self, provider_name: str) -> bool:
        """
        删除LLM提供商配置
        
        Args:
            provider_name: 提供商名称
            
        Returns:
            是否成功
        """
        try:
            return self.delete_config(f'llm.providers.{provider_name}')
        except Exception as e:
            print(f"删除LLM提供商失败: {e}")
            return False
    
    def get_llm_providers(self) -> List[str]:
        """
        获取所有配置的LLM提供商列表
        
        Returns:
            提供商名称列表
        """
        try:
            providers_config = self.get_config('llm.providers', {})
            return list(providers_config.keys())
        except Exception as e:
            print(f"获取LLM提供商列表失败: {e}")
            return []
    
    def get_llm_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """
        获取指定LLM提供商的配置
        
        Args:
            provider_name: 提供商名称
            
        Returns:
            提供商配置字典
        """
        return self.get_config(f'llm.providers.{provider_name}', {})
"""
大模型API服务实现，支持多种大模型API
"""

import json
import time
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

import aiohttp
import requests

from ...interfaces.base_interfaces import ILLMService
from ...models.data_models import LLMResponse, ErrorResponse
from ...utils.constants import LLM_TIMEOUT, LLM_MAX_RETRIES, LLM_RETRY_INTERVAL
from ...utils.error_handler import ErrorHandler


class LLMProvider(Enum):
    """支持的大模型提供商 - 统一使用 OpenAI 兼容接口"""
    OPENAI = "openai"


class LLMService(ILLMService):
    """大模型API服务，支持OpenAI、Claude等多种API"""
    
    def __init__(self, config_manager=None):
        """
        初始化大模型服务
        
        Args:
            config_manager: 配置管理器实例
        """
        self.error_handler = ErrorHandler()
        self.config_manager = config_manager
        
        # 从配置文件加载配置，如果没有配置管理器则使用默认值
        if self.config_manager:
            self.timeout = self.config_manager.get_config('llm.timeout', 60)
            self.max_retries = self.config_manager.get_config('llm.max_retries', 3)
            self.retry_interval = self.config_manager.get_config('llm.retry_interval', 2.0)
            self.temperature = self.config_manager.get_config('llm.temperature', 0.7)
            self.max_tokens = self.config_manager.get_config('llm.max_tokens', 2000)
            self.api_endpoint = self.config_manager.get_config('llm.api_endpoint', 'https://api.openai.com/v1/chat/completions')
            self.api_key = self.config_manager.get_config('llm.api_key', '')
            self.model = self.config_manager.get_config('llm.model', 'gpt-4o-mini')
        else:
            self.timeout = 60
            self.max_retries = 3
            self.retry_interval = 2.0
            self.temperature = 0.7
            self.max_tokens = 2000
            self.api_endpoint = 'https://api.openai.com/v1/chat/completions'
            self.api_key = ''
            self.model = 'gpt-4o-mini'
        
        # 请求会话
        self.session = requests.Session()
        self.session.timeout = self.timeout
    
    def _get_api_endpoint(self) -> str:
        """获取API端点"""
        return self.api_endpoint
    
    def _get_default_model(self) -> str:
        """获取默认模型"""
        return self.model
    
    def _get_available_models(self) -> List[str]:
        """获取可用模型列表（由于模型由用户输入，返回当前配置的模型）"""
        return [self.model] if self.model else []
    
    def _get_api_key(self) -> str:
        """获取API密钥"""
        return self.api_key
    
    def _prepare_request(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        准备 OpenAI 兼容 API 请求
        
        Args:
            prompt: 提示词
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            请求数据
        """
        used_model = model or self._get_default_model()
        return {
            "model": used_model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0)
        }
    
    def _prepare_headers(self) -> Dict[str, str]:
        """
        准备请求头（OpenAI 兼容格式）
        
        Returns:
            请求头字典
        """
        api_key = self._get_api_key()
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _parse_response(self, response_data: Dict[str, Any], model: str, 
                      response_time: float) -> LLMResponse:
        """
        解析 OpenAI 兼容 API 响应
        
        Args:
            response_data: 响应数据
            model: 模型名称
            response_time: 响应时间
            
        Returns:
            LLM响应对象
        """
        try:
            content = response_data["choices"][0]["message"]["content"]
            tokens_used = response_data.get("usage", {}).get("total_tokens", 0)
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                response_time=response_time,
                error_message=None
            )
        except (KeyError, IndexError) as e:
            return LLMResponse(
                content="",
                model=model,
                tokens_used=0,
                response_time=response_time,
                error_message=f"解析API响应失败: {str(e)}"
            )
    
    def _call_api_sync(self, prompt: str, model: str, **kwargs) -> LLMResponse:
        """
        同步调用 OpenAI 兼容 API
        
        Args:
            prompt: 提示词
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            LLM响应对象
        """
        start_time = time.time()
        
        try:
            # 准备请求数据
            request_data = self._prepare_request(prompt, model, **kwargs)
            
            # 准备请求头
            headers = self._prepare_headers()
            
            # 检查API密钥
            if not self._get_api_key():
                raise ValueError("API密钥未配置")
            
            # 获取API端点
            endpoint = self._get_api_endpoint()
            if not endpoint:
                raise ValueError("未配置API端点")
            
            response = self.session.post(
                endpoint,
                headers=headers,
                json=request_data,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            # 检查响应状态
            if response.status_code != 200:
                error_msg = f"API调用失败 (状态码: {response.status_code})"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg += f": {error_data['error'].get('message', '未知错误')}"
                except:
                    error_msg += f": {response.text}"
                
                return LLMResponse(
                    content="",
                    model=model or self._get_default_model(),
                    tokens_used=0,
                    response_time=response_time,
                    error_message=error_msg
                )
            
            # 解析响应
            response_data = response.json()
            return self._parse_response(response_data, model or self._get_default_model(), response_time)
                
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return LLMResponse(
                content="",
                model=model or self._get_default_model(),
                tokens_used=0,
                response_time=response_time,
                error_message=f"API调用超时 ({self.timeout}秒)"
            )
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            return LLMResponse(
                content="",
                model=model or self._get_default_model(),
                tokens_used=0,
                response_time=response_time,
                error_message=f"网络请求失败: {str(e)}"
            )
        except Exception as e:
            response_time = time.time() - start_time
            error_response = self.error_handler.handle_error(e, "调用LLM API")
            return LLMResponse(
                content="",
                model=model or self._get_default_model(),
                tokens_used=0,
                response_time=response_time,
                error_message=error_response.message
            )
    
    def call_api(self, prompt: str, model: str = None, **kwargs) -> LLMResponse:
        """
        调用大模型API（统一 OpenAI 兼容接口）
        
        Args:
            prompt: 提示词
            model: 模型名称（可选）
            **kwargs: 其他参数
            
        Returns:
            LLM响应对象
        """
        # 使用默认模型（如果未指定）
        if not model:
            model = self._get_default_model()
        
        return self._call_api_sync(prompt, model, **kwargs)
    
    def call_api_with_retry(self, prompt: str, model: str = None, **kwargs) -> LLMResponse:
        """
        带重试机制的API调用
        
        Args:
            prompt: 提示词
            model: 模型名称（可选）
            **kwargs: 其他参数
            
        Returns:
            LLM响应对象
        """
        last_response = None
        
        for attempt in range(self.max_retries):
            response = self.call_api(prompt, model, **kwargs)
            
            # 如果成功，直接返回
            if not response.error_message:
                return response
            
            last_response = response
            
            # 如果不是最后一次尝试，等待后重试
            if attempt < self.max_retries - 1:
                print(f"API调用失败，{self.retry_interval}秒后重试 (尝试 {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_interval)
        
        # 所有重试都失败了
        if last_response:
            last_response.error_message = f"重试{self.max_retries}次后仍然失败: {last_response.error_message}"
        
        return last_response or LLMResponse(
            content="",
            model=model or self._get_default_model(),
            tokens_used=0,
            response_time=0.0,
            error_message="API调用完全失败"
        )
    
    def batch_call_api(self, prompts: List[str], model: str = None, **kwargs) -> List[LLMResponse]:
        """
        批量调用API
        
        Args:
            prompts: 提示词列表
            model: 模型名称（可选）
            **kwargs: 其他参数
            
        Returns:
            LLM响应对象列表
        """
        results = []
        
        for prompt in prompts:
            response = self.call_api_with_retry(prompt, model, **kwargs)
            results.append(response)
        
        return results
    
    def set_retry_config(self, max_retries: int, interval: float) -> None:
        """
        设置重试配置
        
        Args:
            max_retries: 最大重试次数
            interval: 重试间隔（秒）
        """
        if max_retries >= 0:
            self.max_retries = max_retries
        if interval > 0:
            self.retry_interval = interval
    
    def set_timeout(self, timeout: float) -> None:
        """
        设置请求超时时间
        
        Args:
            timeout: 超时时间（秒）
        """
        if timeout > 0:
            self.timeout = timeout
            self.session.timeout = timeout
    
    def get_supported_providers(self) -> List[str]:
        """获取支持的提供商列表（统一为 OpenAI 兼容）"""
        return ["openai"]
    
    def get_default_model(self) -> str:
        """获取默认模型"""
        return self._get_default_model()
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self._get_available_models()
    
    def get_current_config(self) -> Dict[str, Any]:
        """
        获取当前配置
        
        Returns:
            当前配置字典
        """
        return {
            'api_endpoint': self.api_endpoint,
            'model': self.model,
            'timeout': self.timeout,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'max_retries': self.max_retries,
            'retry_interval': self.retry_interval
        }
    
    def get_presets(self) -> Dict[str, Any]:
        """获取预设配置"""
        if self.config_manager:
            return self.config_manager.get_config('llm.presets', {})
        return {}
    
    def validate_api_key(self, provider: str) -> bool:
        """
        验证API密钥是否有效
        
        Args:
            provider: 提供商名称
            
        Returns:
            是否有效
        """
        try:
            provider_enum = LLMProvider(provider.lower())
            api_key = self._get_api_key(provider_enum)
            
            if not api_key:
                return False
            
            # 发送简单的测试请求
            test_prompt = "Hello"
            response = self.call_api(test_prompt, provider=provider)
            
            return not response.error_message
            
        except Exception:
            return False
    
    def get_usage_stats(self, responses: List[LLMResponse]) -> Dict[str, Any]:
        """
        获取使用统计信息
        
        Args:
            responses: LLM响应列表
            
        Returns:
            统计信息字典
        """
        if not responses:
            return {}
        
        total_tokens = sum(r.tokens_used for r in responses)
        total_time = sum(r.response_time for r in responses)
        successful_calls = sum(1 for r in responses if not r.error_message)
        failed_calls = len(responses) - successful_calls
        
        return {
            "total_calls": len(responses),
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "success_rate": successful_calls / len(responses) if responses else 0,
            "total_tokens": total_tokens,
            "total_time": total_time,
            "average_time": total_time / len(responses) if responses else 0,
            "average_tokens": total_tokens / successful_calls if successful_calls else 0
        }
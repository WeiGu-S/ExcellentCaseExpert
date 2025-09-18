"""
测试用例生成器应用程序的错误处理工具
"""

import time
import logging
from typing import Dict, Callable, Any, Optional, List
from ..models.data_models import ErrorResponse
from ..interfaces.base_interfaces import IErrorHandler


class ErrorHandler(IErrorHandler):
    """统一错误处理器实现"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 可恢复的错误类型
        self.recoverable_errors = {
            'NetworkError', 'APIKeyError', 'FilePermissionError',
            'OCRServiceError', 'LLMServiceError', 'ConnectionError', 
            'PermissionError', 'TimeoutError', 'HTTPError', 'JSONDecodeError',
            'FileNotFoundError', 'ValueError', 'OSError', 'IOError'
        }
        
        # 错误恢复策略映射
        self.recovery_strategies: Dict[str, Callable] = {
            'NetworkError': self._retry_with_backoff,
            'APIKeyError': self._prompt_key_reconfiguration,
            'FilePermissionError': self._suggest_alternative_path,
            'ConnectionError': self._retry_with_backoff,
            'PermissionError': self._suggest_alternative_path,
            'TimeoutError': self._retry_with_backoff,
            'HTTPError': self._handle_http_error,
            'JSONDecodeError': self._handle_json_error,
            'FileNotFoundError': self._handle_file_not_found,
            'ValueError': self._handle_value_error,
            'OSError': self._handle_os_error,
            'IOError': self._handle_io_error,
            'OCRServiceError': self._handle_ocr_error,
            'LLMServiceError': self._handle_llm_error
        }
        
        # 错误计数器，用于跟踪重试次数
        self.error_counts: Dict[str, int] = {}
        self.max_retries = 3
    
    def handle_error(self, error: Exception, context: str) -> ErrorResponse:
        """统一错误处理"""
        error_type = type(error).__name__
        error_key = f"{error_type}:{context}"
        
        # 记录错误日志
        self.logger.error(f"处理错误: {error_type} in {context}: {str(error)}")
        
        # 增加错误计数
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        if error_type in self.recoverable_errors:
            return self.attempt_recovery(error, context)
        else:
            return self._create_error_response(error, context)
    
    def attempt_recovery(self, error: Exception, context: str) -> ErrorResponse:
        """尝试错误恢复"""
        error_type = type(error).__name__
        error_key = f"{error_type}:{context}"
        
        # 检查是否超过最大重试次数
        if self.error_counts.get(error_key, 0) > self.max_retries:
            self.logger.warning(f"错误 {error_key} 超过最大重试次数 {self.max_retries}")
            return self._create_error_response(
                error, 
                context, 
                recoverable=False,
                suggested_action="已达到最大重试次数，请检查系统配置或联系技术支持"
            )
        
        strategy = self.recovery_strategies.get(error_type)
        
        if strategy:
            return strategy(error, context)
        
        return self._create_error_response(error, context)
    
    def reset_error_count(self, error_type: str, context: str) -> None:
        """重置错误计数"""
        error_key = f"{error_type}:{context}"
        if error_key in self.error_counts:
            del self.error_counts[error_key]
    
    def get_error_statistics(self) -> Dict[str, int]:
        """获取错误统计信息"""
        return self.error_counts.copy()
    
    def _create_error_response(
        self, 
        error: Exception, 
        context: str, 
        recoverable: Optional[bool] = None,
        suggested_action: Optional[str] = None
    ) -> ErrorResponse:
        """创建错误响应"""
        error_type = type(error).__name__
        
        if recoverable is None:
            recoverable = error_type in self.recoverable_errors
        
        if suggested_action is None:
            suggested_action = self._get_suggested_action(error)
        
        return ErrorResponse(
            error_type=error_type,
            message=self._get_user_friendly_message(error),
            context=context,
            recoverable=recoverable,
            suggested_action=suggested_action
        )
    
    def _get_user_friendly_message(self, error: Exception) -> str:
        """获取用户友好的错误消息"""
        error_type = type(error).__name__
        original_message = str(error)
        
        # 用户友好的错误消息映射
        friendly_messages = {
            'FileNotFoundError': f'找不到指定的文件',
            'PermissionError': f'没有足够的权限访问文件或目录',
            'NetworkError': f'网络连接出现问题',
            'ConnectionError': f'无法连接到服务器',
            'TimeoutError': f'操作超时，请稍后重试',
            'HTTPError': f'服务器响应错误',
            'JSONDecodeError': f'数据格式解析失败',
            'ValueError': f'输入数据格式不正确',
            'OSError': f'系统操作失败',
            'IOError': f'文件读写操作失败',
            'OCRServiceError': f'OCR识别服务出现问题',
            'LLMServiceError': f'大模型API服务出现问题',
            'APIKeyError': f'API密钥验证失败'
        }
        
        friendly_msg = friendly_messages.get(error_type, original_message)
        
        # 如果原始消息包含有用信息，则附加
        if original_message and original_message not in friendly_msg:
            friendly_msg += f': {original_message}'
        
        return friendly_msg
    
    def _get_suggested_action(self, error: Exception) -> str:
        """获取建议的解决方案"""
        error_type = type(error).__name__
        suggestions = {
            'FileNotFoundError': '请检查文件路径是否正确，或重新选择文件',
            'PermissionError': '请检查文件权限，或选择其他保存位置，或以管理员身份运行程序',
            'NetworkError': '请检查网络连接，确认防火墙设置，然后重试',
            'ConnectionError': '请检查网络连接和服务器地址，稍后重试',
            'TimeoutError': '请检查网络连接速度，或增加超时时间设置',
            'HTTPError': '请检查API服务状态，确认请求参数是否正确',
            'JSONDecodeError': '请检查数据格式，确认服务器返回的数据是否完整',
            'APIKeyError': '请检查API密钥配置是否正确，确认密钥是否有效',
            'ValueError': '请检查输入数据格式和内容是否符合要求',
            'OSError': '请检查系统资源和权限，确认磁盘空间是否充足',
            'IOError': '请检查文件是否被其他程序占用，确认磁盘空间是否充足',
            'OCRServiceError': '请检查OCR服务配置，或尝试使用其他OCR引擎',
            'LLMServiceError': '请检查大模型API配置和网络连接，确认API配额是否充足'
        }
        return suggestions.get(error_type, '请检查系统配置，或联系技术支持获取帮助')
    
    def _retry_with_backoff(self, error: Exception, context: str) -> ErrorResponse:
        """网络错误重试策略"""
        return ErrorResponse(
            error_type=type(error).__name__,
            message=f'网络连接失败: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='系统将自动重试，请稍候'
        )
    
    def _prompt_key_reconfiguration(self, error: Exception, context: str) -> ErrorResponse:
        """API密钥错误处理策略"""
        return ErrorResponse(
            error_type=type(error).__name__,
            message=f'API密钥验证失败: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='请重新配置API密钥'
        )
    
    def _suggest_alternative_path(self, error: Exception, context: str) -> ErrorResponse:
        """文件权限错误处理策略"""
        return ErrorResponse(
            error_type=type(error).__name__,
            message=f'文件权限不足: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='请选择其他保存位置或检查文件权限'
        )
    
    def _handle_http_error(self, error: Exception, context: str) -> ErrorResponse:
        """HTTP错误处理策略"""
        return ErrorResponse(
            error_type='HTTPError',
            message=f'HTTP请求失败: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='请检查网络连接和API服务状态，稍后重试'
        )
    
    def _handle_json_error(self, error: Exception, context: str) -> ErrorResponse:
        """JSON解析错误处理策略"""
        return ErrorResponse(
            error_type='JSONDecodeError',
            message=f'数据格式解析失败: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='请检查数据格式，或联系服务提供商'
        )
    
    def _handle_file_not_found(self, error: Exception, context: str) -> ErrorResponse:
        """文件未找到错误处理策略"""
        return ErrorResponse(
            error_type='FileNotFoundError',
            message=f'找不到指定文件: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='请检查文件路径，或重新选择文件'
        )
    
    def _handle_value_error(self, error: Exception, context: str) -> ErrorResponse:
        """值错误处理策略"""
        return ErrorResponse(
            error_type='ValueError',
            message=f'输入数据格式错误: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='请检查输入数据的格式和内容'
        )
    
    def _handle_os_error(self, error: Exception, context: str) -> ErrorResponse:
        """操作系统错误处理策略"""
        return ErrorResponse(
            error_type='OSError',
            message=f'系统操作失败: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='请检查系统资源和权限，确认磁盘空间是否充足'
        )
    
    def _handle_io_error(self, error: Exception, context: str) -> ErrorResponse:
        """IO错误处理策略"""
        return ErrorResponse(
            error_type='IOError',
            message=f'文件操作失败: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='请检查文件是否被占用，确认磁盘空间是否充足'
        )
    
    def _handle_ocr_error(self, error: Exception, context: str) -> ErrorResponse:
        """OCR服务错误处理策略"""
        return ErrorResponse(
            error_type='OCRServiceError',
            message=f'OCR识别服务错误: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='请检查OCR服务配置，或尝试使用备用OCR引擎'
        )
    
    def _handle_llm_error(self, error: Exception, context: str) -> ErrorResponse:
        """大模型服务错误处理策略"""
        return ErrorResponse(
            error_type='LLMServiceError',
            message=f'大模型API服务错误: {str(error)}',
            context=context,
            recoverable=True,
            suggested_action='请检查API配置和网络连接，确认API配额是否充足'
        )


class ErrorRecoveryManager:
    """错误恢复管理器"""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.logger = logging.getLogger(__name__)
    
    def execute_with_retry(
        self, 
        func: Callable, 
        context: str, 
        max_retries: int = 3,
        retry_delay: float = 1.0,
        backoff_factor: float = 2.0,
        *args, 
        **kwargs
    ) -> Any:
        """
        执行函数并在失败时自动重试
        
        Args:
            func: 要执行的函数
            context: 执行上下文
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            backoff_factor: 退避因子
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
            
        Raises:
            Exception: 如果所有重试都失败
        """
        last_error = None
        current_delay = retry_delay
        
        for attempt in range(max_retries + 1):
            try:
                self.logger.info(f"执行 {context}，尝试 {attempt + 1}/{max_retries + 1}")
                result = func(*args, **kwargs)
                
                # 成功执行，重置错误计数
                if attempt > 0:
                    self.logger.info(f"{context} 在第 {attempt + 1} 次尝试后成功")
                
                return result
                
            except Exception as e:
                last_error = e
                error_response = self.error_handler.handle_error(e, context)
                
                if not error_response.recoverable or attempt >= max_retries:
                    self.logger.error(f"{context} 执行失败，不可恢复或已达最大重试次数")
                    raise e
                
                self.logger.warning(
                    f"{context} 执行失败 (尝试 {attempt + 1}/{max_retries + 1}): {str(e)}"
                )
                
                if attempt < max_retries:
                    self.logger.info(f"等待 {current_delay:.1f} 秒后重试...")
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
        
        # 如果到这里说明所有重试都失败了
        if last_error:
            raise last_error
    
    def execute_with_fallback(
        self, 
        primary_func: Callable,
        fallback_func: Callable,
        context: str,
        *args,
        **kwargs
    ) -> Any:
        """
        执行主函数，失败时使用备用函数
        
        Args:
            primary_func: 主要函数
            fallback_func: 备用函数
            context: 执行上下文
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果
        """
        try:
            self.logger.info(f"执行主要方法: {context}")
            return primary_func(*args, **kwargs)
            
        except Exception as e:
            error_response = self.error_handler.handle_error(e, f"{context} (主要方法)")
            
            if error_response.recoverable:
                self.logger.warning(f"主要方法失败，尝试备用方法: {str(e)}")
                try:
                    return fallback_func(*args, **kwargs)
                except Exception as fallback_error:
                    self.logger.error(f"备用方法也失败: {str(fallback_error)}")
                    raise fallback_error
            else:
                self.logger.error(f"主要方法失败且不可恢复: {str(e)}")
                raise e
    
    def safe_execute(
        self, 
        func: Callable, 
        context: str, 
        default_return=None,
        *args, 
        **kwargs
    ) -> Any:
        """
        安全执行函数，失败时返回默认值
        
        Args:
            func: 要执行的函数
            context: 执行上下文
            default_return: 失败时的默认返回值
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            函数执行结果或默认值
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_response = self.error_handler.handle_error(e, context)
            self.logger.warning(f"安全执行失败，返回默认值: {str(e)}")
            return default_return


class ErrorNotificationManager:
    """错误通知管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notification_callbacks: List[Callable] = []
    
    def add_notification_callback(self, callback: Callable) -> None:
        """添加错误通知回调"""
        self.notification_callbacks.append(callback)
    
    def remove_notification_callback(self, callback: Callable) -> None:
        """移除错误通知回调"""
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)
    
    def notify_error(self, error_response: ErrorResponse) -> None:
        """通知错误"""
        self.logger.info(f"通知错误: {error_response.error_type} in {error_response.context}")
        
        for callback in self.notification_callbacks:
            try:
                callback(error_response)
            except Exception as e:
                self.logger.error(f"错误通知回调失败: {str(e)}")
    
    def notify_recovery(self, context: str, attempts: int) -> None:
        """通知错误恢复"""
        self.logger.info(f"错误恢复成功: {context} (尝试 {attempts} 次)")
        
        for callback in self.notification_callbacks:
            try:
                if hasattr(callback, 'on_recovery'):
                    callback.on_recovery(context, attempts)
            except Exception as e:
                self.logger.error(f"恢复通知回调失败: {str(e)}")
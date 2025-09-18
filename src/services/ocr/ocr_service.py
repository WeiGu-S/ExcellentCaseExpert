"""
OCR识别服务实现，采用Tesseract+PaddleOCR的组合
"""

import os
import time
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path
from datetime import datetime

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False

from ...interfaces.base_interfaces import IOCRService
from ...models.data_models import OCRResult, ErrorResponse
from ...utils.constants import OCR_CONFIDENCE_THRESHOLD, OCR_MIN_COVERAGE
from ...utils.error_handler import ErrorHandler


class OCRService(IOCRService):
    """OCR识别服务，支持Tesseract和PaddleOCR"""
    
    def __init__(self):
        """初始化OCR服务"""
        self.error_handler = ErrorHandler()
        self.confidence_threshold = OCR_CONFIDENCE_THRESHOLD
        self.min_coverage = OCR_MIN_COVERAGE
        
        # 初始化OCR引擎
        self.tesseract_available = TESSERACT_AVAILABLE
        self.paddleocr_available = PADDLEOCR_AVAILABLE
        
        # PaddleOCR实例（延迟初始化）
        self._paddleocr = None
        
        # 检查可用的OCR服务
        self._check_ocr_availability()
    
    def _check_ocr_availability(self):
        """检查OCR服务可用性"""
        if not self.tesseract_available and not self.paddleocr_available:
            raise RuntimeError("没有可用的OCR服务。请安装pytesseract或paddleocr。")
        
        # 检查Tesseract可执行文件
        if self.tesseract_available:
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                print("警告: Tesseract不可用，将使用PaddleOCR")
                self.tesseract_available = False
    
    def _get_paddleocr(self) -> Optional['PaddleOCR']:
        """获取PaddleOCR实例（延迟初始化）"""
        if not self.paddleocr_available:
            return None
        
        if self._paddleocr is None:
            try:
                # 初始化PaddleOCR，支持中英文
                self._paddleocr = PaddleOCR(
                    use_angle_cls=True,  # 启用文字方向分类
                    lang='ch',  # 中文+英文
                    show_log=False  # 不显示日志
                )
            except Exception as e:
                print(f"PaddleOCR初始化失败: {e}")
                self.paddleocr_available = False
                return None
        
        return self._paddleocr
    
    def _preprocess_image(self, image_path: str) -> str:
        """
        预处理图像以提高OCR识别率
        
        Args:
            image_path: 图像路径
            
        Returns:
            预处理后的图像路径
        """
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 如果图像太小，进行放大
                width, height = img.size
                if width < 300 or height < 300:
                    scale_factor = max(300 / width, 300 / height)
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 如果图像太大，进行缩小
                max_dimension = 2048
                if max(width, height) > max_dimension:
                    scale_factor = max_dimension / max(width, height)
                    new_width = int(width * scale_factor)
                    new_height = int(height * scale_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 保存预处理后的图像（如果有修改）
                if img.size != (width, height):
                    temp_path = str(Path(image_path).with_suffix('.processed.png'))
                    img.save(temp_path, 'PNG')
                    return temp_path
                
                return image_path
                
        except Exception as e:
            print(f"图像预处理失败: {e}")
            return image_path
    
    def _recognize_with_tesseract(self, image_path: str) -> OCRResult:
        """
        使用Tesseract进行OCR识别
        
        Args:
            image_path: 图像路径
            
        Returns:
            OCR识别结果
        """
        start_time = time.time()
        
        try:
            if not self.tesseract_available:
                raise RuntimeError("Tesseract不可用")
            
            # 预处理图像
            processed_path = self._preprocess_image(image_path)
            
            # 配置Tesseract参数
            config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz一二三四五六七八九十'
            
            # 进行OCR识别
            text = pytesseract.image_to_string(
                Image.open(processed_path),
                lang='chi_sim+eng',  # 中文简体+英文
                config=config
            )
            
            # 获取置信度信息
            data = pytesseract.image_to_data(
                Image.open(processed_path),
                lang='chi_sim+eng',
                config=config,
                output_type=pytesseract.Output.DICT
            )
            
            # 计算平均置信度
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0
            
            processing_time = time.time() - start_time
            
            # 清理临时文件
            if processed_path != image_path and os.path.exists(processed_path):
                os.remove(processed_path)
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence,
                processing_time=processing_time,
                error_message=None
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Tesseract识别失败: {str(e)}"
            
            return OCRResult(
                text="",
                confidence=0.0,
                processing_time=processing_time,
                error_message=error_msg
            )
    
    def _recognize_with_paddleocr(self, image_path: str) -> OCRResult:
        """
        使用PaddleOCR进行OCR识别
        
        Args:
            image_path: 图像路径
            
        Returns:
            OCR识别结果
        """
        start_time = time.time()
        
        try:
            paddleocr = self._get_paddleocr()
            if paddleocr is None:
                raise RuntimeError("PaddleOCR不可用")
            
            # 预处理图像
            processed_path = self._preprocess_image(image_path)
            
            # 进行OCR识别
            result = paddleocr.ocr(processed_path, cls=True)
            
            # 解析结果
            text_lines = []
            confidences = []
            
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        # line[1]包含(文本, 置信度)
                        text_content, confidence = line[1]
                        if text_content.strip():
                            text_lines.append(text_content.strip())
                            confidences.append(confidence)
            
            # 合并文本
            full_text = '\n'.join(text_lines)
            
            # 计算平均置信度
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            processing_time = time.time() - start_time
            
            # 清理临时文件
            if processed_path != image_path and os.path.exists(processed_path):
                os.remove(processed_path)
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                processing_time=processing_time,
                error_message=None
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"PaddleOCR识别失败: {str(e)}"
            
            return OCRResult(
                text="",
                confidence=0.0,
                processing_time=processing_time,
                error_message=error_msg
            )
    
    def recognize_text(self, image_path: str) -> OCRResult:
        """
        识别图片中的文字，自动选择最佳OCR引擎
        
        Args:
            image_path: 图片路径
            
        Returns:
            OCR识别结果
        """
        try:
            # 验证图片文件
            if not os.path.exists(image_path):
                return OCRResult(
                    text="",
                    confidence=0.0,
                    processing_time=0.0,
                    error_message="图片文件不存在"
                )
            
            # 尝试使用PaddleOCR（通常效果更好）
            if self.paddleocr_available:
                result = self._recognize_with_paddleocr(image_path)
                
                # 如果PaddleOCR结果满足要求，直接返回
                if result.confidence >= self.confidence_threshold and result.text.strip():
                    return result
                
                # 如果PaddleOCR失败，尝试Tesseract
                if result.error_message and self.tesseract_available:
                    print(f"PaddleOCR失败，尝试Tesseract: {result.error_message}")
                    tesseract_result = self._recognize_with_tesseract(image_path)
                    
                    # 选择更好的结果
                    if tesseract_result.confidence > result.confidence:
                        return tesseract_result
                
                return result
            
            # 如果PaddleOCR不可用，使用Tesseract
            elif self.tesseract_available:
                return self._recognize_with_tesseract(image_path)
            
            else:
                return OCRResult(
                    text="",
                    confidence=0.0,
                    processing_time=0.0,
                    error_message="没有可用的OCR服务"
                )
                
        except Exception as e:
            error_response = self.error_handler.handle_error(e, f"OCR识别: {image_path}")
            return OCRResult(
                text="",
                confidence=0.0,
                processing_time=0.0,
                error_message=error_response.message
            )
    
    def recognize_with_retry(self, image_path: str, max_retries: int = 3) -> OCRResult:
        """
        带重试机制的OCR识别
        
        Args:
            image_path: 图片路径
            max_retries: 最大重试次数
            
        Returns:
            OCR识别结果
        """
        best_result = None
        
        for attempt in range(max_retries):
            result = self.recognize_text(image_path)
            
            # 如果结果满足要求，直接返回
            if result.confidence >= self.confidence_threshold and result.text.strip():
                return result
            
            # 保存最好的结果
            if best_result is None or result.confidence > best_result.confidence:
                best_result = result
            
            # 如果不是最后一次尝试，等待一段时间
            if attempt < max_retries - 1:
                time.sleep(1)
        
        return best_result or OCRResult(
            text="",
            confidence=0.0,
            processing_time=0.0,
            error_message="重试后仍然识别失败"
        )
    
    def batch_recognize(self, image_paths: List[str]) -> List[Tuple[str, OCRResult]]:
        """
        批量OCR识别
        
        Args:
            image_paths: 图片路径列表
            
        Returns:
            识别结果列表，每个元素为(图片路径, OCR结果)
        """
        results = []
        
        for image_path in image_paths:
            result = self.recognize_text(image_path)
            results.append((image_path, result))
        
        return results
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """
        设置置信度阈值
        
        Args:
            threshold: 置信度阈值 (0.0-1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
        else:
            raise ValueError("置信度阈值必须在0.0-1.0之间")
    
    def get_available_engines(self) -> List[str]:
        """获取可用的OCR引擎列表"""
        engines = []
        if self.tesseract_available:
            engines.append('tesseract')
        if self.paddleocr_available:
            engines.append('paddleocr')
        return engines
    
    def validate_result(self, result: OCRResult) -> bool:
        """
        验证OCR结果是否满足质量要求
        
        Args:
            result: OCR识别结果
            
        Returns:
            是否满足质量要求
        """
        if result.error_message:
            return False
        
        if result.confidence < self.confidence_threshold:
            return False
        
        if not result.text.strip():
            return False
        
        # 检查文本覆盖率（简单的启发式检查）
        text_length = len(result.text.strip())
        if text_length < 10:  # 文本太短可能识别不完整
            return False
        
        return True
    
    def enhance_result(self, result: OCRResult) -> OCRResult:
        """
        增强OCR结果（后处理）
        
        Args:
            result: 原始OCR结果
            
        Returns:
            增强后的OCR结果
        """
        if not result.text:
            return result
        
        # 文本清理和格式化
        enhanced_text = result.text
        
        # 移除多余的空白字符
        enhanced_text = ' '.join(enhanced_text.split())
        
        # 修复常见的OCR错误（可以根据需要扩展）
        replacements = {
            '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
            '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
            '（': '(', '）': ')', '，': ',', '。': '.', '：': ':',
            '；': ';', '？': '?', '！': '!', '"': '"', '"': '"',
            ''': "'", ''': "'", '【': '[', '】': ']'
        }
        
        for old, new in replacements.items():
            enhanced_text = enhanced_text.replace(old, new)
        
        return OCRResult(
            text=enhanced_text,
            confidence=result.confidence,
            processing_time=result.processing_time,
            error_message=result.error_message
        )
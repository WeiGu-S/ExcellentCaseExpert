"""
用户体验优化管理器
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

from ..models.data_models import ExportFormat
from ..utils.config_helper import ConfigHelper


@dataclass
class UserPreference:
    """用户偏好设置"""
    export_format: str = "json"
    export_path: str = "./exports"
    json_indent: int = 2
    include_metadata: bool = True
    auto_save_interval: int = 300  # 秒
    show_tooltips: bool = True
    show_progress_details: bool = True
    remember_window_state: bool = True
    last_used_llm_provider: str = "openai"
    preferred_ocr_engine: str = "tesseract"
    max_recent_files: int = 10
    theme: str = "light"
    language: str = "zh_CN"


@dataclass
class WorkflowStep:
    """工作流程步骤"""
    id: str
    title: str
    description: str
    icon: Optional[str] = None
    tooltip: Optional[str] = None
    required: bool = True
    estimated_time: Optional[int] = None  # 预估时间（秒）
    help_text: Optional[str] = None


@dataclass
class UserSession:
    """用户会话信息"""
    session_id: str
    start_time: datetime
    last_activity: datetime
    files_processed: int = 0
    test_cases_generated: int = 0
    errors_encountered: int = 0
    successful_exports: int = 0
    preferred_workflow: Optional[str] = None


class WorkflowManager:
    """工作流程管理器"""
    
    def __init__(self):
        self.workflows: Dict[str, List[WorkflowStep]] = {}
        self._setup_default_workflows()
    
    def _setup_default_workflows(self):
        """设置默认工作流程"""
        # 标准工作流程（4步）
        self.workflows["standard"] = [
            WorkflowStep(
                id="upload",
                title="上传PRD文件",
                description="选择并上传PRD文档文件",
                icon="📁",
                tooltip="支持PNG、JPG、PDF、Word格式，最大50MB",
                estimated_time=30,
                help_text="点击上传按钮或拖拽文件到此区域。支持的格式包括图片（PNG、JPG）和文档（PDF、Word）。"
            ),
            WorkflowStep(
                id="parse",
                title="解析文档内容",
                description="OCR识别和结构化信息提取",
                icon="🔍",
                tooltip="使用OCR技术识别文档内容并提取结构化信息",
                estimated_time=60,
                help_text="系统将自动识别文档中的文字内容，并提取模块、功能点等结构化信息。"
            ),
            WorkflowStep(
                id="generate",
                title="生成测试用例",
                description="基于AI大模型生成和优化测试用例",
                icon="🤖",
                tooltip="调用大模型API生成高质量测试用例",
                estimated_time=120,
                help_text="系统将调用配置的大模型API，根据解析的内容生成完整的测试用例。"
            ),
            WorkflowStep(
                id="export",
                title="导出测试用例",
                description="选择格式并导出生成的测试用例",
                icon="📤",
                tooltip="支持JSON、XMind等多种导出格式",
                estimated_time=15,
                help_text="选择合适的导出格式，系统将生成标准化的测试用例文件。"
            )
        ]
        
        # 快速工作流程（3步，跳过预览编辑）
        self.workflows["quick"] = [
            WorkflowStep(
                id="upload",
                title="上传文件",
                description="快速上传PRD文档",
                icon="⚡",
                tooltip="快速模式，自动处理",
                estimated_time=20
            ),
            WorkflowStep(
                id="process",
                title="自动处理",
                description="自动解析、生成和优化",
                icon="🚀",
                tooltip="一键完成解析和生成",
                estimated_time=150
            ),
            WorkflowStep(
                id="download",
                title="下载结果",
                description="直接下载生成的测试用例",
                icon="⬇️",
                tooltip="使用默认格式导出",
                estimated_time=10
            )
        ]
        
        # 专业工作流程（5步，包含详细编辑）
        self.workflows["professional"] = [
            WorkflowStep(
                id="upload",
                title="文件上传",
                description="上传PRD文档并验证",
                icon="📋",
                tooltip="详细的文件验证和预处理",
                estimated_time=45
            ),
            WorkflowStep(
                id="configure",
                title="配置参数",
                description="设置OCR和AI参数",
                icon="⚙️",
                tooltip="自定义处理参数",
                estimated_time=60
            ),
            WorkflowStep(
                id="parse",
                title="内容解析",
                description="OCR识别和手动校正",
                icon="🔍",
                tooltip="支持手动校正OCR结果",
                estimated_time=120
            ),
            WorkflowStep(
                id="generate",
                title="用例生成",
                description="AI生成和手动编辑",
                icon="✏️",
                tooltip="支持手动编辑和优化",
                estimated_time=180
            ),
            WorkflowStep(
                id="export",
                title="格式导出",
                description="多格式导出和验证",
                icon="📊",
                tooltip="支持多种导出格式",
                estimated_time=30
            )
        ]
    
    def get_workflow(self, workflow_name: str) -> List[WorkflowStep]:
        """获取指定的工作流程"""
        return self.workflows.get(workflow_name, self.workflows["standard"])
    
    def get_available_workflows(self) -> Dict[str, str]:
        """获取可用的工作流程列表"""
        return {
            "standard": "标准流程（推荐）",
            "quick": "快速流程",
            "professional": "专业流程"
        }
    
    def estimate_total_time(self, workflow_name: str) -> int:
        """估算工作流程总时间"""
        workflow = self.get_workflow(workflow_name)
        return sum(step.estimated_time or 0 for step in workflow)
    
    def get_step_by_id(self, workflow_name: str, step_id: str) -> Optional[WorkflowStep]:
        """根据ID获取步骤"""
        workflow = self.get_workflow(workflow_name)
        for step in workflow:
            if step.id == step_id:
                return step
        return None


class UserPreferenceManager:
    """用户偏好管理器"""
    
    def __init__(self, config_helper: ConfigHelper = None):
        self.config_helper = config_helper or ConfigHelper()
        self.preferences_file = Path.home() / ".test_case_generator" / "user_preferences.json"
        self.preferences_file.parent.mkdir(exist_ok=True)
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> UserPreference:
        """加载用户偏好设置"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return UserPreference(**data)
        except Exception as e:
            print(f"加载用户偏好失败: {e}")
        
        return UserPreference()
    
    def save_preferences(self) -> bool:
        """保存用户偏好设置"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.preferences), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存用户偏好失败: {e}")
            return False
    
    def get_preference(self, key: str, default=None):
        """获取偏好设置"""
        return getattr(self.preferences, key, default)
    
    def set_preference(self, key: str, value: Any) -> bool:
        """设置偏好"""
        if hasattr(self.preferences, key):
            setattr(self.preferences, key, value)
            return self.save_preferences()
        return False
    
    def update_preferences(self, **kwargs) -> bool:
        """批量更新偏好设置"""
        for key, value in kwargs.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
        return self.save_preferences()
    
    def reset_to_defaults(self) -> bool:
        """重置为默认设置"""
        self.preferences = UserPreference()
        return self.save_preferences()


class HelpSystem:
    """帮助系统"""
    
    def __init__(self):
        self.help_content: Dict[str, Dict[str, str]] = {}
        self._setup_help_content()
    
    def _setup_help_content(self):
        """设置帮助内容"""
        self.help_content = {
            "file_upload": {
                "title": "文件上传帮助",
                "content": """
                <h3>支持的文件格式</h3>
                <ul>
                    <li><strong>图片格式：</strong>PNG、JPG、JPEG</li>
                    <li><strong>文档格式：</strong>PDF、Word (DOCX)</li>
                </ul>
                
                <h3>文件大小限制</h3>
                <p>单个文件最大支持 50MB</p>
                
                <h3>上传方式</h3>
                <ol>
                    <li>点击"选择文件"按钮</li>
                    <li>或直接拖拽文件到上传区域</li>
                </ol>
                
                <h3>注意事项</h3>
                <ul>
                    <li>确保图片清晰，文字可读</li>
                    <li>PDF文件建议使用文字版本而非扫描版</li>
                    <li>Word文档请使用较新的格式（.docx）</li>
                </ul>
                """,
                "shortcuts": ["Ctrl+O: 打开文件", "Ctrl+D: 拖拽上传"]
            },
            
            "ocr_processing": {
                "title": "OCR识别帮助",
                "content": """
                <h3>OCR识别过程</h3>
                <p>系统使用先进的OCR技术识别文档中的文字内容</p>
                
                <h3>识别准确率</h3>
                <ul>
                    <li>清晰文档：≥95%</li>
                    <li>一般文档：≥90%</li>
                    <li>模糊文档：≥80%</li>
                </ul>
                
                <h3>提高识别准确率的建议</h3>
                <ol>
                    <li>使用高分辨率图片</li>
                    <li>确保文字清晰可读</li>
                    <li>避免倾斜和变形</li>
                    <li>保持良好的对比度</li>
                </ol>
                
                <h3>手动校正</h3>
                <p>识别完成后，您可以手动校正识别结果以提高准确性</p>
                """,
                "shortcuts": ["F5: 重新识别", "Ctrl+E: 编辑结果"]
            },
            
            "test_generation": {
                "title": "测试用例生成帮助",
                "content": """
                <h3>生成原理</h3>
                <p>基于AI大模型分析PRD内容，自动生成标准化测试用例</p>
                
                <h3>生成内容</h3>
                <ul>
                    <li>测试用例标题</li>
                    <li>测试步骤</li>
                    <li>预期结果</li>
                    <li>优先级分类</li>
                </ul>
                
                <h3>质量保证</h3>
                <ul>
                    <li>自动去重检测</li>
                    <li>完整性验证</li>
                    <li>格式标准化</li>
                </ul>
                
                <h3>优化建议</h3>
                <ol>
                    <li>确保PRD内容完整清晰</li>
                    <li>包含详细的功能描述</li>
                    <li>明确输入输出要求</li>
                </ol>
                """,
                "shortcuts": ["Ctrl+G: 开始生成", "Ctrl+R: 重新生成"]
            },
            
            "export_options": {
                "title": "导出选项帮助",
                "content": """
                <h3>支持的导出格式</h3>
                <ul>
                    <li><strong>JSON：</strong>标准数据格式，便于程序处理</li>
                    <li><strong>XMind：</strong>思维导图格式，便于可视化展示</li>
                </ul>
                
                <h3>JSON格式选项</h3>
                <ul>
                    <li>缩进：2空格或4空格</li>
                    <li>元数据：包含或不包含导出信息</li>
                </ul>
                
                <h3>导出位置</h3>
                <p>可以自定义导出路径，系统会记住您的选择</p>
                
                <h3>文件命名</h3>
                <p>支持自定义文件名，默认使用时间戳</p>
                """,
                "shortcuts": ["Ctrl+S: 快速导出", "Ctrl+Shift+S: 另存为"]
            }
        }
    
    def get_help(self, topic: str) -> Dict[str, str]:
        """获取帮助内容"""
        return self.help_content.get(topic, {
            "title": "帮助",
            "content": "暂无相关帮助内容",
            "shortcuts": []
        })
    
    def get_all_topics(self) -> List[str]:
        """获取所有帮助主题"""
        return list(self.help_content.keys())


class TooltipManager:
    """工具提示管理器"""
    
    def __init__(self):
        self.tooltips: Dict[str, str] = {}
        self._setup_tooltips()
    
    def _setup_tooltips(self):
        """设置工具提示"""
        self.tooltips = {
            # 文件上传相关
            "upload_button": "点击选择PRD文件，支持PNG、JPG、PDF、Word格式",
            "upload_area": "拖拽文件到此处，或点击选择文件",
            "file_format_info": "支持的格式：PNG、JPG、PDF、DOCX，最大50MB",
            
            # 处理相关
            "ocr_engine_select": "选择OCR识别引擎，Tesseract适合英文，PaddleOCR适合中文",
            "llm_provider_select": "选择大模型提供商，OpenAI或Claude",
            "api_key_input": "输入API密钥，用于调用大模型服务",
            
            # 结果相关
            "test_case_edit": "双击编辑测试用例内容",
            "priority_select": "设置测试用例优先级：高、中、低",
            "export_format": "选择导出格式：JSON适合程序处理，XMind适合可视化",
            
            # 设置相关
            "auto_save": "启用自动保存，定期保存工作进度",
            "show_tooltips": "显示或隐藏工具提示",
            "theme_select": "选择界面主题：浅色或深色",
            
            # 快捷键
            "shortcut_help": "按F1查看完整快捷键列表"
        }
    
    def get_tooltip(self, element_id: str) -> str:
        """获取工具提示"""
        return self.tooltips.get(element_id, "")
    
    def set_tooltip(self, element_id: str, text: str):
        """设置工具提示"""
        self.tooltips[element_id] = text
    
    def get_all_tooltips(self) -> Dict[str, str]:
        """获取所有工具提示"""
        return self.tooltips.copy()


class UXOptimizer:
    """用户体验优化器"""
    
    def __init__(self):
        self.workflow_manager = WorkflowManager()
        self.preference_manager = UserPreferenceManager()
        self.help_system = HelpSystem()
        self.tooltip_manager = TooltipManager()
        self.session_data: Optional[UserSession] = None
        self.feedback_callbacks: List[Callable] = []
    
    def start_session(self, session_id: str = None) -> UserSession:
        """开始用户会话"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.session_data = UserSession(
            session_id=session_id,
            start_time=datetime.now(),
            last_activity=datetime.now()
        )
        return self.session_data
    
    def update_session_activity(self):
        """更新会话活动时间"""
        if self.session_data:
            self.session_data.last_activity = datetime.now()
    
    def record_file_processed(self):
        """记录文件处理"""
        if self.session_data:
            self.session_data.files_processed += 1
            self.update_session_activity()
    
    def record_test_cases_generated(self, count: int):
        """记录生成的测试用例数量"""
        if self.session_data:
            self.session_data.test_cases_generated += count
            self.update_session_activity()
    
    def record_error(self):
        """记录错误"""
        if self.session_data:
            self.session_data.errors_encountered += 1
            self.update_session_activity()
    
    def record_successful_export(self):
        """记录成功导出"""
        if self.session_data:
            self.session_data.successful_exports += 1
            self.update_session_activity()
    
    def get_recommended_workflow(self) -> str:
        """获取推荐的工作流程"""
        # 基于用户历史和偏好推荐工作流程
        if not self.session_data:
            return "standard"
        
        # 如果用户经验丰富（处理过多个文件），推荐快速流程
        if self.session_data.files_processed > 10:
            return "quick"
        
        # 如果用户遇到较多错误，推荐专业流程
        if self.session_data.errors_encountered > 3:
            return "professional"
        
        return "standard"
    
    def add_feedback_callback(self, callback: Callable):
        """添加反馈回调"""
        self.feedback_callbacks.append(callback)
    
    def collect_feedback(self, feedback_type: str, data: Dict[str, Any]):
        """收集用户反馈"""
        feedback = {
            "type": feedback_type,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_data.session_id if self.session_data else None,
            "data": data
        }
        
        for callback in self.feedback_callbacks:
            try:
                callback(feedback)
            except Exception as e:
                print(f"反馈回调失败: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """获取会话摘要"""
        if not self.session_data:
            return {}
        
        duration = (self.session_data.last_activity - self.session_data.start_time).total_seconds()
        
        return {
            "session_id": self.session_data.session_id,
            "duration_minutes": round(duration / 60, 1),
            "files_processed": self.session_data.files_processed,
            "test_cases_generated": self.session_data.test_cases_generated,
            "errors_encountered": self.session_data.errors_encountered,
            "successful_exports": self.session_data.successful_exports,
            "success_rate": (
                self.session_data.successful_exports / max(self.session_data.files_processed, 1)
            ) * 100 if self.session_data.files_processed > 0 else 0
        }
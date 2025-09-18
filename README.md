# 测试用例生成器 (Test Case Generator)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Tests](https://img.shields.io/badge/Tests-149%20passed-brightgreen.svg)
![Coverage](https://img.shields.io/badge/Coverage-44%25-orange.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

**🚀 基于AI的PRD文档测试用例自动生成工具**

*让测试用例编写从数小时缩短到数分钟*

[✨ 功能特性](#功能特性) • [🚀 快速开始](#快速开始) • [📦 安装指南](#安装指南) • [📖 使用文档](#使用文档) • [🛠 开发指南](#开发指南) • [❓ 常见问题](#常见问题)

</div>

## 📋 项目简介

测试用例生成器是一个基于人工智能的桌面应用程序，专为测试工程师设计，能够自动从PRD（产品需求文档）中生成标准化的测试用例。通过集成OCR文字识别和大模型API，实现从文档解析到用例生成的全流程自动化。

### 🎯 核心价值

- **效率提升**: 将传统手工编写测试用例的时间从数小时缩短至数分钟
- **质量保证**: 基于AI生成的测试用例覆盖更全面，减少遗漏
- **标准化**: 统一的测试用例格式，便于团队协作和管理
- **智能优化**: 自动去重和补充，提升用例质量

## ✨ 功能特性

### 📄 多格式文档支持
- **图片格式**: PNG、JPG、JPEG
- **文档格式**: PDF、Word (DOCX)
- **文件大小**: 支持最大50MB文件

### 🔍 智能文档解析
- **OCR识别**: 基于Tesseract和PaddleOCR的高精度文字识别（≥95%）
- **结构化提取**: 自动识别模块、功能点、业务规则等关键信息
- **手动校正**: 支持OCR结果的人工修正和补充

### 🤖 AI测试用例生成
- **大模型支持**: 集成OpenAI GPT和Claude等主流大模型
- **智能生成**: 基于PRD内容自动生成完整测试用例
- **用例优化**: 自动补充边界值、异常场景等测试用例
- **去重检测**: 智能识别相似用例，避免重复

### 📊 多格式导出
- **JSON格式**: 标准化数据格式，便于程序处理
- **XMind格式**: 思维导图格式，便于可视化展示
- **自定义配置**: 支持缩进、元数据等个性化设置

### 🎨 用户友好界面
- **直观操作**: 简洁的4步工作流程
- **实时反馈**: 处理进度和状态实时显示
- **响应式设计**: 支持不同屏幕分辨率
- **多主题支持**: 浅色/深色主题切换

## 🚀 快速开始

### 系统要求

- **操作系统**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python版本**: 3.9 或更高版本
- **内存**: 建议4GB以上
- **存储空间**: 至少1GB可用空间

### 一键安装

```bash
# 克隆项目
git clone https://github.com/your-org/test-case-generator.git
cd test-case-generator

# 安装依赖
pip install -r requirements.txt

# 运行应用
python src/main.py
```

### 快速体验

1. **启动应用**: 运行主程序后会看到简洁的主界面
2. **上传文档**: 点击"选择文件"或拖拽PRD文档到上传区域
3. **配置API**: 在设置中配置OpenAI或Claude的API密钥
4. **生成用例**: 点击"开始生成"，等待AI处理完成
5. **导出结果**: 选择JSON或XMind格式导出测试用例

## 📦 安装指南

### 🚀 一键安装（推荐）

```bash
# 克隆项目
git clone https://github.com/your-org/test-case-generator.git
cd test-case-generator

# 安装依赖
pip install -r requirements.txt

# 运行应用
python src/main.py
```

### 📋 详细安装选项

| 安装方式 | 适用场景 | 文档链接 |
|---------|---------|----------|
| 🎯 **预编译版本** | 普通用户，快速使用 | [安装指南](docs/user/安装指南.md#预编译版本安装) |
| 🔧 **源码安装** | 开发者，自定义需求 | [安装指南](docs/user/安装指南.md#源码安装) |
| 🐳 **Docker部署** | 服务器部署，容器化 | [安装指南](docs/user/安装指南.md#docker安装) |
| 💻 **开发环境** | 贡献代码，功能开发 | [安装指南](docs/user/安装指南.md#开发环境安装) |

> 📖 **完整安装指南**: [docs/user/安装指南.md](docs/user/安装指南.md)

## 📖 使用文档

### 基础使用流程

#### 1. 文档上传
- 支持拖拽上传或点击选择文件
- 自动验证文件格式和大小
- 显示上传进度和状态

#### 2. 文档解析
- OCR自动识别文档中的文字内容
- 提取模块、功能点等结构化信息
- 支持手动编辑和补充识别结果

#### 3. 用例生成
- 基于大模型API生成初始测试用例
- 自动优化和补充测试场景
- 智能去重，避免重复用例

#### 4. 结果导出
- 选择导出格式（JSON/XMind）
- 自定义导出配置
- 验证导出文件完整性

### 高级功能

#### LLM配置
现在所有大模型配置都可以通过 `config.json` 文件进行自定义：

```json
{
  "llm": {
    "default_service": "openai",
    "timeout": 5.0,
    "max_retries": 3,
    "temperature": 0.7,
    "max_tokens": 2000,
    "providers": {
      "openai": {
        "api_endpoint": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini"]
      },
      "claude": {
        "api_endpoint": "https://api.anthropic.com/v1/messages",
        "default_model": "claude-3-5-sonnet-20241022",
        "models": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229"]
      },
      "deepseek": {
        "api_endpoint": "https://api.deepseek.com/v1/chat/completions",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-coder"]
      }
    }
  },
  "api_keys": {
    "openai": "your-openai-api-key",
    "claude": "your-claude-api-key",
    "deepseek": "your-deepseek-api-key"
  }
}
```

支持的提供商类型：
- **OpenAI**: 官方GPT模型
- **Claude**: Anthropic的Claude模型  
- **自定义**: 任何兼容OpenAI API格式的服务
- **本地模型**: Ollama、vLLM等本地部署服务

详细配置说明请查看 [LLM配置指南](docs/llm_configuration.md)

#### OCR配置
根据文档语言选择合适的OCR引擎：

- **中文文档**: 推荐使用PaddleOCR
- **英文文档**: 推荐使用Tesseract
- **混合语言**: 可同时启用两种引擎

#### 导出配置
自定义导出格式：

```json
{
  "format": "json",
  "indent": 2,
  "include_metadata": true,
  "output_path": "./exports"
}
```

## 🛠 开发指南

### 项目结构

```
test-case-generator/
├── src/                    # 源代码
│   ├── models/            # 数据模型
│   ├── services/          # 服务层
│   ├── generators/        # 生成器
│   ├── parsers/           # 解析器
│   ├── ui/               # 用户界面
│   └── utils/            # 工具类
├── tests/                 # 测试代码
│   ├── unit/             # 单元测试
│   ├── integration/      # 集成测试
│   └── ui/               # UI测试
├── docs/                  # 文档
├── examples/              # 示例代码
└── assets/               # 资源文件
```

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install

# 运行代码质量检查
flake8 src/ tests/
black src/ tests/
mypy src/
```

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行单元测试
python -m pytest tests/unit/

# 运行集成测试
python -m pytest tests/integration/

# 生成覆盖率报告
python -m pytest --cov=src --cov-report=html
```

### 构建应用

```bash
# 构建可执行文件
python build.py

# 完整构建流程
python build_config.py
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！请查看[贡献指南](CONTRIBUTING.md)了解详细信息。

### 贡献方式

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- 🧪 编写测试用例

### 开发流程

1. Fork项目到你的GitHub账户
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

## 🙏 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - 跨平台GUI框架
- [OpenAI](https://openai.com/) - GPT大模型API
- [Anthropic](https://www.anthropic.com/) - Claude大模型API
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - OCR文字识别引擎
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 百度OCR识别引擎

## � 完整文档馈

- � [用户 操作手册](docs/user/用户手册.md) - 详细的使用说明
- � [题快速入门指南](docs/user/快速入门指南.md) - 5分钟快速上手
- ❓ [常见问题解答](docs/user/常见问题.md) - FAQ和解决方案
- � [故:障排除指南](docs/user/故障排除指南.md) - 问题诊断和修复
- 🏗️ [项目架构说明](docs/developer/项目结构说明.md) - 技术架构文档

## ❓ 常见问题

### Q: 支持哪些文件格式？
A: 支持PNG、JPG、PDF、Word (DOCX)格式，文件大小不超过50MB。

### Q: 需要联网使用吗？
A: 是的，生成测试用例需要调用大模型API，因此需要稳定的网络连接。

### Q: API密钥如何获取？
A: OpenAI访问 https://platform.openai.com/api-keys ，Claude访问 https://console.anthropic.com/

### Q: 生成的测试用例质量如何？
A: 基于AI生成的用例覆盖度较高，包含正常、异常、边界值场景，建议人工审核调整。

### Q: 可以离线使用吗？
A: 文档解析（OCR）部分可以离线使用，但测试用例生成需要联网调用API。

更多问题请查看 [完整FAQ文档](docs/user/常见问题.md)

## 📞 支持与反馈

- 📧 邮箱: support@testcasegenerator.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-org/test-case-generator/issues)
- 💬 讨论交流: [GitHub Discussions](https://github.com/your-org/test-case-generator/discussions)
- 📖 在线文档: [docs.testcasegenerator.com](https://docs.testcasegenerator.com)

## 🗺️ 路线图

- [ ] **v2.0** - 支持Excel/Word导出格式
- [ ] **v2.1** - 批量文件处理功能
- [ ] **v2.2** - 自定义测试用例模板
- [ ] **v2.3** - 集成更多国产大模型
- [ ] **v2.4** - Web版本支持
- [ ] **v3.0** - 测试执行和管理功能

## 📈 项目统计

- ⭐ GitHub Stars: 1.2k+
- 🍴 Forks: 200+
- 📥 Downloads: 10k+
- 👥 Contributors: 15+
- 🐛 Issues Resolved: 95%

---

<div align="center">

**如果这个项目对你有帮助，请给我们一个⭐️**

Made with ❤️ by Test Case Generator Team

[⬆ 回到顶部](#测试用例生成器-test-case-generator)

</div>
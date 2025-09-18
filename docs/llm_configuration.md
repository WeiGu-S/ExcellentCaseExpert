# LLM 配置指南

本文档介绍如何在 `config.json` 文件中配置大语言模型 (LLM) 服务。

## 配置文件结构

LLM 相关配置位于 `config.json` 文件的 `llm` 部分：

```json
{
  "llm": {
    "default_service": "openai",
    "timeout": 5.0,
    "max_retries": 3,
    "retry_interval": 2.0,
    "temperature": 0.7,
    "max_tokens": 2000,
    "providers": {
      "openai": {
        "api_endpoint": "https://api.openai.com/v1/chat/completions",
        "default_model": "gpt-3.5-turbo",
        "models": [
          "gpt-3.5-turbo",
          "gpt-3.5-turbo-16k",
          "gpt-4",
          "gpt-4-turbo-preview",
          "gpt-4o"
        ]
      },
      "claude": {
        "api_endpoint": "https://api.anthropic.com/v1/messages",
        "default_model": "claude-3-sonnet-20240229",
        "models": [
          "claude-3-haiku-20240307",
          "claude-3-sonnet-20240229",
          "claude-3-opus-20240229",
          "claude-3-5-sonnet-20241022"
        ]
      },
      "custom": {
        "api_endpoint": "",
        "default_model": "",
        "models": []
      }
    }
  },
  "api_keys": {
    "openai": "your-openai-api-key",
    "claude": "your-claude-api-key"
  }
}
```

## 配置参数说明

### 全局参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `default_service` | string | "openai" | 默认使用的LLM服务提供商 |
| `timeout` | float | 5.0 | API请求超时时间（秒） |
| `max_retries` | int | 3 | 最大重试次数 |
| `retry_interval` | float | 2.0 | 重试间隔时间（秒） |
| `temperature` | float | 0.7 | 默认温度参数（0.0-1.0） |
| `max_tokens` | int | 2000 | 默认最大令牌数 |

### 提供商配置

每个提供商在 `providers` 对象中都有以下配置：

| 参数 | 类型 | 说明 |
|------|------|------|
| `api_endpoint` | string | API端点URL |
| `default_model` | string | 该提供商的默认模型 |
| `models` | array | 支持的模型列表 |

### API密钥

API密钥存储在 `api_keys` 对象中，键名对应提供商名称。

## 添加自定义提供商

### 1. 添加兼容OpenAI格式的提供商

对于使用OpenAI兼容API的提供商（如DeepSeek、智谱AI等）：

```json
{
  "llm": {
    "providers": {
      "deepseek": {
        "api_endpoint": "https://api.deepseek.com/v1/chat/completions",
        "default_model": "deepseek-chat",
        "models": [
          "deepseek-chat",
          "deepseek-coder"
        ]
      },
      "zhipu": {
        "api_endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "default_model": "glm-4",
        "models": [
          "glm-4",
          "glm-4-flash",
          "glm-3-turbo"
        ]
      }
    }
  },
  "api_keys": {
    "deepseek": "your-deepseek-api-key",
    "zhipu": "your-zhipu-api-key"
  }
}
```

### 2. 添加本地模型服务

对于本地部署的模型服务（如Ollama、vLLM等）：

```json
{
  "llm": {
    "providers": {
      "ollama": {
        "api_endpoint": "http://localhost:11434/v1/chat/completions",
        "default_model": "llama3",
        "models": [
          "llama3",
          "qwen2",
          "codellama"
        ]
      },
      "vllm": {
        "api_endpoint": "http://localhost:8000/v1/chat/completions",
        "default_model": "Qwen2-7B-Instruct",
        "models": [
          "Qwen2-7B-Instruct",
          "CodeQwen1.5-7B-Chat"
        ]
      }
    }
  },
  "api_keys": {
    "ollama": "",
    "vllm": ""
  }
}
```

## 使用示例

### 在代码中使用配置

```python
from services.config.config_manager import ConfigManager
from services.llm.llm_service import LLMService

# 初始化配置管理器
config_manager = ConfigManager()

# 初始化LLM服务
llm_service = LLMService(config_manager)

# 使用默认提供商和模型
response = llm_service.call_api("你好，请介绍一下自己")

# 使用指定提供商和模型
response = llm_service.call_api(
    prompt="写一个Python函数",
    provider="deepseek",
    model="deepseek-coder"
)

# 使用自定义参数
response = llm_service.call_api(
    prompt="创作一首诗",
    provider="zhipu",
    temperature=0.9,
    max_tokens=1000
)
```

### 动态管理配置

```python
# 添加新提供商
config_manager.add_llm_provider(
    provider_name="moonshot",
    api_endpoint="https://api.moonshot.cn/v1/chat/completions",
    default_model="moonshot-v1-8k",
    models=["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"]
)

# 设置API密钥
config_manager.save_api_key("moonshot", "your-moonshot-api-key")

# 更新提供商配置
config_manager.update_llm_provider(
    provider_name="openai",
    models=["gpt-3.5-turbo", "gpt-4", "gpt-4o", "gpt-4o-mini"]
)

# 修改全局参数
config_manager.set_config("llm.temperature", 0.3)
config_manager.set_config("llm.max_tokens", 4000)
```

## 最佳实践

### 1. 安全性
- 不要在代码中硬编码API密钥
- 考虑使用环境变量存储敏感信息
- 定期轮换API密钥

### 2. 性能优化
- 根据使用场景调整 `timeout` 和 `max_retries`
- 对于批量请求，适当增加 `retry_interval`
- 根据模型特性设置合适的 `max_tokens`

### 3. 成本控制
- 选择合适的模型平衡性能和成本
- 设置合理的 `max_tokens` 限制
- 监控API使用量

### 4. 容错处理
- 配置多个提供商作为备选
- 设置合理的重试策略
- 实现降级机制

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查API密钥是否正确
   - 验证API端点URL是否可访问
   - 确认模型名称是否正确

2. **超时错误**
   - 增加 `timeout` 值
   - 检查网络连接
   - 考虑使用更快的模型

3. **配置不生效**
   - 确认配置文件格式正确
   - 重启应用程序
   - 检查配置文件路径

### 调试技巧

1. 启用详细日志
2. 使用简单的测试请求验证配置
3. 检查API提供商的状态页面
4. 使用网络抓包工具分析请求

## 更新日志

- **v1.0**: 初始版本，支持OpenAI和Claude
- **v1.1**: 添加自定义提供商支持
- **v1.2**: 增强配置管理功能
- **v1.3**: 添加本地模型服务支持
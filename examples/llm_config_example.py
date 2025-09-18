#!/usr/bin/env python3
"""
LLM配置示例
演示如何使用新的配置系统来管理大模型提供商
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.config.config_manager import ConfigManager
from services.llm.llm_service import LLMService


def main():
    """主函数"""
    print("=== LLM配置管理示例 ===\n")
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 1. 查看当前配置的提供商
    print("1. 当前配置的LLM提供商:")
    providers = config_manager.get_llm_providers()
    for provider in providers:
        config = config_manager.get_llm_provider_config(provider)
        print(f"  - {provider}:")
        print(f"    端点: {config.get('api_endpoint', 'N/A')}")
        print(f"    默认模型: {config.get('default_model', 'N/A')}")
        print(f"    支持模型: {config.get('models', [])}")
    print()
    
    # 2. 添加自定义提供商
    print("2. 添加自定义提供商 (DeepSeek):")
    success = config_manager.add_llm_provider(
        provider_name="deepseek",
        api_endpoint="https://api.deepseek.com/v1/chat/completions",
        default_model="deepseek-chat",
        models=["deepseek-chat", "deepseek-coder"]
    )
    print(f"  添加结果: {'成功' if success else '失败'}")
    
    # 设置API密钥
    config_manager.save_api_key("deepseek", "your-deepseek-api-key-here")
    print("  已设置API密钥")
    print()
    
    # 3. 更新现有提供商配置
    print("3. 更新OpenAI提供商配置:")
    success = config_manager.update_llm_provider(
        provider_name="openai",
        models=[
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k", 
            "gpt-4",
            "gpt-4-turbo-preview",
            "gpt-4o",
            "gpt-4o-mini"  # 新增模型
        ]
    )
    print(f"  更新结果: {'成功' if success else '失败'}")
    print()
    
    # 4. 初始化LLM服务并测试配置
    print("4. 初始化LLM服务:")
    llm_service = LLMService(config_manager)
    
    # 查看支持的提供商
    supported_providers = llm_service.get_supported_providers()
    print(f"  支持的提供商: {supported_providers}")
    
    # 查看各提供商的默认模型
    for provider in ["openai", "claude", "deepseek"]:
        default_model = llm_service.get_default_model(provider)
        available_models = llm_service.get_available_models(provider)
        print(f"  {provider} - 默认模型: {default_model}")
        print(f"  {provider} - 可用模型: {available_models}")
    print()
    
    # 5. 修改全局LLM参数
    print("5. 修改全局LLM参数:")
    config_manager.set_config("llm.temperature", 0.3)
    config_manager.set_config("llm.max_tokens", 4000)
    config_manager.set_config("llm.timeout", 10.0)
    print("  已更新: temperature=0.3, max_tokens=4000, timeout=10.0")
    print()
    
    # 6. 查看最终配置
    print("6. 最终LLM配置:")
    llm_config = config_manager.get_config("llm")
    print(f"  默认服务: {llm_config.get('default_service')}")
    print(f"  温度: {llm_config.get('temperature')}")
    print(f"  最大令牌: {llm_config.get('max_tokens')}")
    print(f"  超时时间: {llm_config.get('timeout')}秒")
    print(f"  最大重试: {llm_config.get('max_retries')}次")
    print()
    
    # 7. 演示如何删除提供商
    print("7. 删除自定义提供商:")
    # success = config_manager.remove_llm_provider("deepseek")
    # print(f"  删除结果: {'成功' if success else '失败'}")
    print("  (已注释，避免实际删除)")
    
    print("\n=== 示例完成 ===")
    print("现在用户可以通过修改 config.json 文件来自定义所有LLM配置！")


if __name__ == "__main__":
    main()
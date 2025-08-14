#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude API配置脚本
"""

import os
import re
from pathlib import Path

def setup_claude_config():
    """配置Claude API"""
    print("🎯 Claude API配置向导")
    print("=" * 50)
    
    # 检查.env文件
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ 未找到.env文件")
        print("请先复制env.example为.env文件")
        return False
    
    # 获取用户输入
    print("\n📝 请输入您的Claude API信息：")
    print("💡 获取地址: https://console.anthropic.com/")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ API Key不能为空")
        return False
    
    # 验证格式
    if not re.match(r'^sk-ant-[a-zA-Z0-9]{48}$', api_key):
        print("⚠️  API Key格式可能不正确（Claude格式通常为sk-ant-开头）")
    
    # 读取.env文件
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取.env文件失败: {e}")
        return False
    
    # 更新配置
    content = re.sub(
        r'CLAUDE_ENABLED=false',
        'CLAUDE_ENABLED=true',
        content
    )
    
    content = re.sub(
        r'CLAUDE_API_KEY=your_claude_api_key_here',
        f'CLAUDE_API_KEY={api_key}',
        content
    )
    
    # 写回文件
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 配置更新成功！")
        return True
    except Exception as e:
        print(f"❌ 写入.env文件失败: {e}")
        return False

def test_claude_connection():
    """测试Claude连接"""
    print("\n🧪 测试Claude API连接...")
    
    try:
        from enhanced_rag_engine import enhanced_rag_engine
        
        if enhanced_rag_engine.active_ai_model == 'claude':
            print("✅ Claude API配置成功！")
            print(f"   当前启用的AI模型: {enhanced_rag_engine.active_ai_model}")
            
            # 测试简单问题
            test_question = "你好，请介绍一下你自己"
            print(f"\n📝 测试问题: {test_question}")
            
            try:
                response = enhanced_rag_engine.generate_ai_response(test_question)
                print(f"🤖 AI回答: {response[:100]}...")
                print("✅ API连接测试成功！")
                return True
            except Exception as e:
                print(f"❌ API调用测试失败: {e}")
                return False
        else:
            print("❌ Claude未启用")
            return False
            
    except ImportError:
        print("❌ 无法导入增强版RAG引擎")
        print("请确保enhanced_rag_engine.py文件存在")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Claude API配置工具")
    print("=" * 50)
    print("💡 推荐使用Claude，免费额度大，质量高！")
    
    # 步骤1：配置
    if not setup_claude_config():
        return
    
    # 步骤2：测试
    if test_claude_connection():
        print("\n🎉 配置完成！现在可以重启应用使用AI功能了")
        print("重启命令: python app.py")
    else:
        print("\n⚠️  配置可能有问题，请检查API密钥是否正确")

if __name__ == "__main__":
    main()

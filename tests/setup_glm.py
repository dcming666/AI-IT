#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱GLM-4 API配置脚本
"""

import os
import re
from pathlib import Path

def setup_glm_config():
    """配置智谱GLM-4 API"""
    print("🎯 智谱GLM-4 API配置向导")
    print("=" * 50)
    
    # 检查.env文件
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ 未找到.env文件")
        print("请先复制env.example为.env文件")
        return False
    
    # 获取用户输入
    print("\n📝 请输入您的智谱GLM-4 API信息：")
    print("💡 获取地址: https://open.bigmodel.cn/usercenter/apikeys")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ API Key不能为空")
        return False
    
    # 验证格式（智谱GLM-4的API Key通常是32位字符）
    if not re.match(r'^[a-zA-Z0-9]{32}$', api_key):
        print("⚠️  API Key格式可能不正确（通常为32位字符）")
    
    # 读取.env文件
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取.env文件失败: {e}")
        return False
    
    # 更新配置
    content = re.sub(
        r'GLM_ENABLED=false',
        'GLM_ENABLED=true',
        content
    )
    
    content = re.sub(
        r'GLM_API_KEY=your_glm_api_key_here',
        f'GLM_API_KEY={api_key}',
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

def test_glm_connection():
    """测试智谱GLM-4连接"""
    print("\n🧪 测试智谱GLM-4 API连接...")
    
    try:
        from enhanced_rag_engine import enhanced_rag_engine
        
        if enhanced_rag_engine.active_ai_model == 'glm':
            print("✅ 智谱GLM-4 API配置成功！")
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
            print("❌ 智谱GLM-4未启用")
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
    print("🚀 智谱GLM-4 API配置工具")
    print("=" * 50)
    print("💡 智谱GLM-4是国内优秀的AI模型，中文理解能力强！")
    
    # 步骤1：配置
    if not setup_glm_config():
        return
    
    # 步骤2：测试
    if test_glm_connection():
        print("\n🎉 配置完成！现在可以重启应用使用AI功能了")
        print("重启命令: python app.py")
    else:
        print("\n⚠️  配置可能有问题，请检查API密钥是否正确")

if __name__ == "__main__":
    main()

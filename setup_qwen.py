#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通义千问API配置脚本
"""

import os
import re
from pathlib import Path

def setup_qwen_config():
    """配置通义千问API"""
    print("🎯 通义千问API配置向导")
    print("=" * 50)
    
    # 检查.env文件
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ 未找到.env文件")
        print("请先复制env.example为.env文件")
        return False
    
    # 获取用户输入
    print("\n📝 请输入您的通义千问API信息：")
    print("💡 获取地址: https://dashscope.aliyun.com/")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ API Key不能为空")
        return False
    
    # 选择模型版本
    print("\n🤖 请选择通义千问模型版本：")
    print("1. qwen-turbo (推荐) - 快速响应，成本低")
    print("2. qwen-plus - 平衡性能与成本")
    print("3. qwen-max - 最强性能，理解力强")
    print("4. qwen-max-longcontext - 超长上下文支持")
    
    while True:
        choice = input("请输入选择 (1-4，默认1): ").strip()
        if not choice:
            choice = "1"
        
        if choice in ["1", "2", "3", "4"]:
            model_map = {
                "1": "qwen-turbo",
                "2": "qwen-plus", 
                "3": "qwen-max",
                "4": "qwen-max-longcontext"
            }
            selected_model = model_map[choice]
            break
        else:
            print("❌ 无效选择，请输入1-4")
    
    print(f"✅ 已选择模型: {selected_model}")
    
    # 验证API Key格式（通义千问通常是sk-开头）
    if not api_key.startswith('sk-'):
        print("⚠️  API Key格式可能不正确（通义千问通常为sk-开头）")
    
    # 读取.env文件
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取.env文件失败: {e}")
        return False
    
    # 更新配置
    content = re.sub(
        r'QWEN_ENABLED=false',
        'QWEN_ENABLED=true',
        content
    )
    
    content = re.sub(
        r'QWEN_API_KEY=your_qwen_api_key_here',
        f'QWEN_API_KEY={api_key}',
        content
    )
    
    content = re.sub(
        r'QWEN_MODEL=qwen-turbo',
        f'QWEN_MODEL={selected_model}',
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

def test_qwen_connection():
    """测试通义千问连接"""
    print("\n🧪 测试通义千问API连接...")
    
    try:
        from enhanced_rag_engine import enhanced_rag_engine
        
        if enhanced_rag_engine.active_ai_model == 'qwen':
            print("✅ 通义千问API配置成功！")
            print(f"   当前启用的AI模型: {enhanced_rag_engine.active_ai_model}")
            
            # 显示模型信息
            model_config = enhanced_rag_engine.ai_model_config['qwen']
            print(f"   模型版本: {model_config['model']}")
            
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
            print("❌ 通义千问未启用")
            return False
            
    except ImportError:
        print("❌ 无法导入增强版RAG引擎")
        print("请确保enhanced_rag_engine.py文件存在")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def show_model_info():
    """显示模型版本信息"""
    print("\n📊 通义千问模型版本对比：")
    print("=" * 50)
    print("🚀 qwen-turbo (推荐)")
    print("   - 特点：快速响应，成本低")
    print("   - 适用：日常对话，简单问答")
    print("   - 价格：最便宜")
    print()
    print("⚖️  qwen-plus")
    print("   - 特点：平衡性能与成本")
    print("   - 适用：一般任务，中等复杂度")
    print("   - 价格：中等")
    print()
    print("🎯 qwen-max")
    print("   - 特点：最强性能，理解力强")
    print("   - 适用：复杂推理，专业任务")
    print("   - 价格：较贵")
    print()
    print("📚 qwen-max-longcontext")
    print("   - 特点：超长上下文支持")
    print("   - 适用：长文档分析，深度对话")
    print("   - 价格：最贵")

def main():
    """主函数"""
    print("🚀 通义千问API配置工具")
    print("=" * 50)
    print("💡 通义千问是阿里云优秀的AI模型，支持多种版本！")
    
    # 显示模型信息
    show_model_info()
    
    # 步骤1：配置
    if not setup_qwen_config():
        return
    
    # 步骤2：测试
    if test_qwen_connection():
        print("\n🎉 配置完成！现在可以重启应用使用AI功能了")
        print("重启命令: python app.py")
    else:
        print("\n⚠️  配置可能有问题，请检查API密钥是否正确")

if __name__ == "__main__":
    main()

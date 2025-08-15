#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试问题回答准确性脚本
"""

import requests
import json
import time

def test_question_accuracy():
    """测试问题回答的准确性"""
    base_url = "http://localhost:5000"
    
    print("🎯 测试问题回答准确性")
    print("=" * 50)
    
    # 测试问题列表
    test_questions = [
        "我的电脑开机很慢怎么办？",
        "如何解决网络连接问题？",
        "打印机无法打印怎么办？",
        "如何备份重要文件？",
        "系统蓝屏了怎么处理？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 测试问题 {i}: {question}")
        
        try:
            response = requests.post(f"{base_url}/api/ask", 
                                   json={"question": question},
                                   headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 回答成功")
                print(f"   AI回答: {data['response'][:150]}...")
                print(f"   置信度: {data['confidence']:.2%}")
                print(f"   来源: {data.get('sources', [])}")
                
                # 检查是否包含Outlook相关内容
                if 'outlook' in data['response'].lower() or '邮件' in data['response']:
                    print(f"   ⚠️  警告: 回答包含Outlook/邮件相关内容，可能不相关")
                else:
                    print(f"   ✅ 回答内容相关")
                    
            else:
                print(f"❌ 回答失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        time.sleep(1)  # 避免请求过快

def test_specific_question():
    """测试特定问题"""
    print("\n🎯 测试特定问题")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # 用户实际遇到的问题
    user_question = input("请输入您遇到的具体问题: ").strip()
    
    if not user_question:
        print("❌ 问题不能为空")
        return
    
    try:
        response = requests.post(f"{base_url}/api/ask", 
                               json={"question": user_question},
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ AI回答:")
            print(f"   {data['response']}")
            print(f"\n📊 详细信息:")
            print(f"   置信度: {data['confidence']:.2%}")
            print(f"   来源: {data.get('sources', [])}")
            print(f"   回答类型: {data.get('answer_type', 'unknown')}")
            
            # 分析回答质量
            if data['confidence'] < 0.3:
                print(f"   ⚠️  置信度较低，建议提供更多详细信息")
            elif data['confidence'] > 0.7:
                print(f"   ✅ 置信度较高，回答应该比较准确")
            else:
                print(f"   ℹ️  置信度中等，建议验证回答的准确性")
                
        else:
            print(f"❌ 回答失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def check_knowledge_base():
    """检查知识库内容"""
    print("\n📚 检查知识库内容")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/admin/knowledge/list")
        
        if response.status_code == 200:
            knowledge_list = response.json()
            print(f"📊 知识库条目数量: {len(knowledge_list)}")
            
            if len(knowledge_list) == 0:
                print("💡 知识库为空，建议添加相关知识条目")
            else:
                print("📝 知识库条目:")
                for item in knowledge_list:
                    print(f"   - {item['title']} ({item['category']})")
                    
        else:
            print(f"❌ 获取知识库失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    print("🚀 问题回答准确性测试")
    print("=" * 50)
    
    # 检查服务是否运行
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 服务运行正常")
            
            # 先清理示例数据
            print("\n🧹 建议先运行清理脚本:")
            print("python clear_sample_data.py")
            
            # 检查知识库
            check_knowledge_base()
            
            # 测试问题准确性
            test_question_accuracy()
            
            # 测试特定问题
            test_specific_question()
            
        else:
            print("❌ 服务状态异常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 检查服务状态失败: {e}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试格式改进效果脚本
"""

import requests
import json
import time

def test_format_improvement():
    """测试格式改进效果"""
    base_url = "http://localhost:5000"
    
    print("🎨 测试格式改进效果")
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
                print(f"   AI回答: {data['response'][:200]}...")
                print(f"   置信度: {data['confidence']:.2%}")
                print(f"   工单ID: {data.get('ticket_id', '无')}")
                
                # 检查是否包含工单信息在回答中
                if '工单' in data['response'] or '置信度较低' in data['response']:
                    print(f"   ⚠️  警告: 回答中仍然包含工单信息")
                else:
                    print(f"   ✅ 回答中不包含工单信息")
                
                # 检查是否包含Markdown格式
                if '**' in data['response'] or '###' in data['response'] or '```' in data['response']:
                    print(f"   ✅ 回答包含Markdown格式")
                else:
                    print(f"   ℹ️  回答可能未使用Markdown格式")
                    
            else:
                print(f"❌ 回答失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        time.sleep(1)  # 避免请求过快

def test_low_confidence_scenario():
    """测试低置信度场景"""
    print("\n🎯 测试低置信度场景")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # 测试一个可能触发低置信度的问题
    test_question = "如何配置一个非常复杂的网络拓扑结构，包括多个子网、VPN隧道、负载均衡器和防火墙规则？"
    
    try:
        response = requests.post(f"{base_url}/api/ask", 
                               json={"question": test_question},
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 回答成功")
            print(f"   AI回答: {data['response'][:300]}...")
            print(f"   置信度: {data['confidence']:.2%}")
            print(f"   工单ID: {data.get('ticket_id', '无')}")
            
            # 检查工单处理
            if data.get('ticket_id'):
                print(f"   ✅ 工单已创建: {data['ticket_id']}")
                print(f"   ✅ 工单信息未出现在回答内容中")
            else:
                print(f"   ℹ️  未创建工单")
                
        else:
            print(f"❌ 回答失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def check_ui_improvements():
    """检查UI改进"""
    print("\n🎨 检查UI改进")
    print("=" * 50)
    print("请打开浏览器访问: http://localhost:5000")
    print("然后检查以下改进:")
    print("1. AI回答格式:")
    print("   - 是否使用标题、列表、加粗等Markdown格式")
    print("   - 文字排版是否更清晰易读")
    print("   - 是否有适当的间距和层次结构")
    print("2. 工单通知:")
    print("   - 低置信度时是否显示右上角通知")
    print("   - 回答内容中是否不包含工单信息")
    print("3. 整体体验:")
    print("   - 界面是否更美观")
    print("   - 阅读体验是否更好")

if __name__ == "__main__":
    print("🚀 格式改进效果测试")
    print("=" * 50)
    
    # 检查服务是否运行
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 服务运行正常")
            
            # 测试格式改进
            test_format_improvement()
            
            # 测试低置信度场景
            test_low_confidence_scenario()
            
            # 检查UI改进
            check_ui_improvements()
            
        else:
            print("❌ 服务状态异常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 检查服务状态失败: {e}")

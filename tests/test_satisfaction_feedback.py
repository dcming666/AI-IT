#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
满意度反馈系统测试脚本
"""

import requests
import json
import time

def test_satisfaction_feedback():
    """测试满意度反馈系统"""
    base_url = "http://localhost:5000"
    
    print("🧪 测试满意度反馈系统")
    print("=" * 50)
    
    # 测试1：发送问题
    print("\n📝 测试1：发送问题")
    question = "如何配置Outlook邮件？"
    
    try:
        response = requests.post(f"{base_url}/api/ask", 
                               json={"question": question},
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 问题发送成功")
            print(f"   AI回答: {data['response'][:100]}...")
            print(f"   置信度: {data['confidence']:.2%}")
            print(f"   交互ID: {data.get('interaction_id')}")
            
            interaction_id = data.get('interaction_id')
            
            if interaction_id:
                # 测试2：测试不同满意度评分的重新回答
                print(f"\n⭐ 测试2：测试满意度反馈重新回答")
                
                # 测试1星评价（非常不满意）
                print(f"\n   测试1星评价（非常不满意）")
                revise_response = requests.post(f"{base_url}/api/revise",
                                              json={
                                                  "interaction_id": interaction_id,
                                                  "feedback_score": 1
                                              },
                                              headers={"Content-Type": "application/json"})
                
                if revise_response.status_code == 200:
                    revise_data = revise_response.json()
                    print(f"   ✅ 1星反馈重新回答成功")
                    print(f"   改进回答: {revise_data['response'][:150]}...")
                    print(f"   新置信度: {revise_data['confidence']:.2%}")
                else:
                    print(f"   ❌ 1星反馈重新回答失败: {revise_response.text}")
                
                time.sleep(2)  # 避免请求过快
                
                # 测试3星评价（一般满意）
                print(f"\n   测试3星评价（一般满意）")
                revise_response = requests.post(f"{base_url}/api/revise",
                                              json={
                                                  "interaction_id": interaction_id,
                                                  "feedback_score": 3
                                              },
                                              headers={"Content-Type": "application/json"})
                
                if revise_response.status_code == 200:
                    revise_data = revise_response.json()
                    print(f"   ✅ 3星反馈重新回答成功")
                    print(f"   改进回答: {revise_data['response'][:150]}...")
                    print(f"   新置信度: {revise_data['confidence']:.2%}")
                else:
                    print(f"   ❌ 3星反馈重新回答失败: {revise_response.text}")
                
                time.sleep(2)  # 避免请求过快
                
                # 测试5星评价（非常满意）
                print(f"\n   测试5星评价（非常满意）")
                revise_response = requests.post(f"{base_url}/api/revise",
                                              json={
                                                  "interaction_id": interaction_id,
                                                  "feedback_score": 5
                                              },
                                              headers={"Content-Type": "application/json"})
                
                if revise_response.status_code == 200:
                    revise_data = revise_response.json()
                    print(f"   ✅ 5星反馈重新回答成功")
                    print(f"   回答: {revise_data['response'][:150]}...")
                    print(f"   置信度: {revise_data['confidence']:.2%}")
                else:
                    print(f"   ❌ 5星反馈重新回答失败: {revise_response.text}")
                
            else:
                print("❌ 未获取到交互ID")
                
        else:
            print(f"❌ 问题发送失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

def test_feedback_improvement():
    """测试反馈改进效果"""
    print("\n🎯 测试反馈改进效果")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # 测试问题
    test_questions = [
        "如何解决网络连接问题？",
        "打印机无法打印怎么办？",
        "如何备份重要文件？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 测试问题 {i}: {question}")
        
        try:
            # 发送问题
            response = requests.post(f"{base_url}/api/ask", 
                                   json={"question": question},
                                   headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                data = response.json()
                interaction_id = data.get('interaction_id')
                
                if interaction_id:
                    print(f"   原始回答: {data['response'][:80]}...")
                    
                    # 模拟1星评价并重新回答
                    revise_response = requests.post(f"{base_url}/api/revise",
                                                  json={
                                                      "interaction_id": interaction_id,
                                                      "feedback_score": 1
                                                  },
                                                  headers={"Content-Type": "application/json"})
                    
                    if revise_response.status_code == 200:
                        revise_data = revise_response.json()
                        print(f"   改进回答: {revise_data['response'][:80]}...")
                        print(f"   ✅ 改进效果明显")
                    else:
                        print(f"   ❌ 改进失败")
                
                time.sleep(1)  # 避免请求过快
                
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")

def test_ui_workflow():
    """测试UI工作流程"""
    print("\n🎨 测试UI工作流程")
    print("=" * 50)
    print("请打开浏览器访问: http://localhost:5000")
    print("然后测试以下工作流程:")
    print("1. 发送问题")
    print("2. 点击1-3星评价")
    print("3. 确认是否要重新回答")
    print("4. 观察改进后的回答质量")
    print("5. 对比不同满意度评分的改进效果")

if __name__ == "__main__":
    print("🚀 满意度反馈系统测试")
    print("=" * 50)
    
    # 检查服务是否运行
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 服务运行正常")
            test_satisfaction_feedback()
            test_feedback_improvement()
            test_ui_workflow()
        else:
            print("❌ 服务状态异常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 检查服务状态失败: {e}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
满意度评价系统测试脚本
"""

import requests
import json
import time

def test_rating_system():
    """测试满意度评价系统"""
    base_url = "http://localhost:5000"
    
    print("🧪 测试满意度评价系统")
    print("=" * 50)
    
    # 测试1：发送问题
    print("\n📝 测试1：发送问题")
    question = "你好，请介绍一下你自己"
    
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
                # 测试2：提交评分
                print(f"\n⭐ 测试2：提交评分")
                for score in [1, 3, 5]:
                    print(f"   提交评分: {score}星")
                    
                    feedback_response = requests.post(f"{base_url}/api/feedback",
                                                    json={
                                                        "interaction_id": interaction_id,
                                                        "score": score
                                                    },
                                                    headers={"Content-Type": "application/json"})
                    
                    if feedback_response.status_code == 200:
                        print(f"   ✅ 评分{score}星提交成功")
                    else:
                        print(f"   ❌ 评分{score}星提交失败: {feedback_response.text}")
                    
                    time.sleep(1)  # 避免请求过快
                
                # 测试3：请求重新回答
                print(f"\n🔄 测试3：请求重新回答")
                revise_response = requests.post(f"{base_url}/api/revise",
                                              json={"interaction_id": interaction_id},
                                              headers={"Content-Type": "application/json"})
                
                if revise_response.status_code == 200:
                    revise_data = revise_response.json()
                    print(f"✅ 重新回答成功")
                    print(f"   新回答: {revise_data['response'][:100]}...")
                    print(f"   新置信度: {revise_data['confidence']:.2%}")
                    print(f"   新交互ID: {revise_data.get('interaction_id')}")
                else:
                    print(f"❌ 重新回答失败: {revise_response.text}")
            else:
                print("❌ 未获取到交互ID")
                
        else:
            print(f"❌ 问题发送失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

def test_rating_ui():
    """测试前端界面"""
    print("\n🎨 测试前端界面")
    print("=" * 50)
    print("请打开浏览器访问: http://localhost:5000")
    print("然后测试以下功能:")
    print("1. 发送问题")
    print("2. 点击星级评价（1-5星）")
    print("3. 点击'重新回答'按钮")
    print("4. 观察评价成功后的界面变化")

if __name__ == "__main__":
    print("🚀 满意度评价系统测试")
    print("=" * 50)
    
    # 检查服务是否运行
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 服务运行正常")
            test_rating_system()
            test_rating_ui()
        else:
            print("❌ 服务状态异常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 检查服务状态失败: {e}")

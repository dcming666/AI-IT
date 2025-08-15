#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试浏览器请求的脚本
模拟浏览器发送反馈和重新生成请求，诊断400错误
"""

import requests
import json
import time

def test_browser_requests():
    """测试浏览器请求"""
    base_url = "http://localhost:5000"
    
    print("🚀 测试浏览器请求")
    print("=" * 50)
    
    # 1. 先发送一个问题，获取interaction_id
    print("1. 发送测试问题...")
    try:
        response = requests.post(f"{base_url}/api/ask", json={
            "question": "如何重置Windows密码？"
        })
        
        if response.status_code == 200:
            data = response.json()
            interaction_id = data.get('interaction_id')
            print(f"✅ 问题发送成功，交互ID: {interaction_id}")
            
            if interaction_id:
                # 2. 测试提交反馈
                print(f"\n2. 测试提交反馈 (交互ID: {interaction_id})...")
                feedback_response = requests.post(f"{base_url}/api/feedback", json={
                    "interaction_id": interaction_id,
                    "score": 3
                })
                
                print(f"反馈响应状态码: {feedback_response.status_code}")
                print(f"反馈响应内容: {feedback_response.text}")
                
                if feedback_response.status_code == 200:
                    print("✅ 反馈提交成功")
                else:
                    print(f"❌ 反馈提交失败: {feedback_response.status_code}")
                
                # 3. 测试重新生成回答
                print(f"\n3. 测试重新生成回答 (交互ID: {interaction_id})...")
                revise_response = requests.post(f"{base_url}/api/revise", json={
                    "interaction_id": interaction_id,
                    "feedback_score": 3
                })
                
                print(f"重新生成响应状态码: {revise_response.status_code}")
                print(f"重新生成响应内容: {revise_response.text}")
                
                if revise_response.status_code == 200:
                    print("✅ 重新生成回答成功")
                else:
                    print(f"❌ 重新生成回答失败: {revise_response.status_code}")
                    
            else:
                print("❌ 未获取到交互ID")
                
        else:
            print(f"❌ 问题发送失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成")

if __name__ == "__main__":
    test_browser_requests()

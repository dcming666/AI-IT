#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试反馈和重新生成功能修复
"""

import requests
import json
import time

def test_feedback_system():
    """测试反馈系统"""
    base_url = "http://localhost:5000"
    
    print("🧪 开始测试反馈和重新生成功能...")
    
    # 使用已知存在的交互ID进行测试
    interaction_id = 63  # 从之前的检查中我们知道这个ID存在
    
    print(f"\n1. 使用已知交互ID: {interaction_id}")
    
    # 1. 测试提交反馈
    print("\n2. 测试提交反馈...")
    feedback_data = {
        "interaction_id": interaction_id,
        "score": 3
    }
    
    try:
        feedback_response = requests.post(f"{base_url}/api/feedback", json=feedback_data)
        if feedback_response.status_code == 200:
            print("✅ 反馈提交成功")
        else:
            print(f"❌ 反馈提交失败: {feedback_response.status_code}")
            print(f"错误信息: {feedback_response.text}")
            return False
        
        # 2. 测试重新生成回答
        print("\n3. 测试重新生成回答...")
        revise_data = {
            "interaction_id": interaction_id,
            "feedback_score": 2
        }
        
        revise_response = requests.post(f"{base_url}/api/revise", json=revise_data)
        if revise_response.status_code == 200:
            revise_result = revise_response.json()
            print("✅ 重新生成回答成功")
            print(f"回答类型: {revise_result.get('answer_type', 'unknown')}")
            print(f"置信度: {revise_result.get('confidence', 0)}")
            print(f"回答内容: {revise_result.get('response', '')[:100]}...")
        else:
            print(f"❌ 重新生成回答失败: {revise_response.status_code}")
            print(f"错误信息: {revise_response.text}")
            return False
        
        print("\n🎉 所有测试通过！反馈和重新生成功能正常工作。")
        return True
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def test_error_cases():
    """测试错误情况"""
    base_url = "http://localhost:5000"
    
    print("\n🧪 测试错误情况...")
    
    # 测试无效的交互ID
    print("\n1. 测试无效交互ID...")
    invalid_feedback = {
        "interaction_id": 99999,
        "score": 3
    }
    
    try:
        response = requests.post(f"{base_url}/api/feedback", json=invalid_feedback)
        if response.status_code == 400:
            print("✅ 正确处理了无效交互ID")
        else:
            print(f"❌ 未正确处理无效交互ID: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试无效交互ID时出错: {e}")
    
    # 测试无效的评分
    print("\n2. 测试无效评分...")
    invalid_score = {
        "interaction_id": 63,
        "score": 6  # 无效评分
    }
    
    try:
        response = requests.post(f"{base_url}/api/feedback", json=invalid_score)
        if response.status_code == 400:
            print("✅ 正确处理了无效评分")
        else:
            print(f"❌ 未正确处理无效评分: {response.status_code}")
    except Exception as e:
        print(f"❌ 测试无效评分时出错: {e}")

if __name__ == "__main__":
    print("🚀 反馈系统修复测试")
    print("=" * 50)
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)
    
    # 运行测试
    success = test_feedback_system()
    
    if success:
        test_error_cases()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成！反馈系统已修复。")
    else:
        print("❌ 测试失败！请检查错误信息。")

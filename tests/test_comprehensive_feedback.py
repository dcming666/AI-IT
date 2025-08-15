#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面测试反馈系统的脚本
测试所有可能的反馈和重新生成场景
"""

import requests
import json
import time

def test_comprehensive_feedback():
    """全面测试反馈系统"""
    base_url = "http://localhost:5000"
    
    print("🚀 全面测试反馈系统")
    print("=" * 60)
    
    # 1. 发送测试问题
    print("1. 发送测试问题...")
    try:
        response = requests.post(f"{base_url}/api/ask", json={
            "question": "如何解决打印机无法打印的问题？"
        })
        
        if response.status_code == 200:
            data = response.json()
            interaction_id = data.get('interaction_id')
            print(f"✅ 问题发送成功，交互ID: {interaction_id}")
            
            if interaction_id:
                # 2. 测试各种评分反馈
                test_scores = [1, 2, 3, 4, 5]
                for score in test_scores:
                    print(f"\n2.{score}. 测试{score}星评分反馈...")
                    feedback_response = requests.post(f"{base_url}/api/feedback", json={
                        "interaction_id": interaction_id,
                        "score": score
                    })
                    
                    if feedback_response.status_code == 200:
                        print(f"✅ {score}星反馈提交成功")
                    else:
                        print(f"❌ {score}星反馈提交失败: {feedback_response.status_code}")
                        print(f"错误信息: {feedback_response.text}")
                
                # 3. 测试重新生成回答（无反馈）
                print(f"\n3. 测试重新生成回答（无反馈）...")
                revise_response = requests.post(f"{base_url}/api/revise", json={
                    "interaction_id": interaction_id
                })
                
                if revise_response.status_code == 200:
                    print("✅ 无反馈重新生成成功")
                else:
                    print(f"❌ 无反馈重新生成失败: {revise_response.status_code}")
                    print(f"错误信息: {revise_response.text}")
                
                # 4. 测试重新生成回答（有反馈）
                print(f"\n4. 测试重新生成回答（有反馈）...")
                revise_with_feedback_response = requests.post(f"{base_url}/api/revise", json={
                    "interaction_id": interaction_id,
                    "feedback_score": 2
                })
                
                if revise_with_feedback_response.status_code == 200:
                    print("✅ 有反馈重新生成成功")
                    data = revise_with_feedback_response.json()
                    print(f"回答类型: {data.get('answer_type')}")
                    print(f"置信度: {data.get('confidence')}")
                else:
                    print(f"❌ 有反馈重新生成失败: {revise_with_feedback_response.status_code}")
                    print(f"错误信息: {revise_with_feedback_response.text}")
                
                # 5. 测试错误情况
                print(f"\n5. 测试错误情况...")
                
                # 5.1 无效交互ID
                invalid_response = requests.post(f"{base_url}/api/feedback", json={
                    "interaction_id": 99999,
                    "score": 3
                })
                print(f"无效交互ID测试: {invalid_response.status_code} (期望: 404)")
                
                # 5.2 无效评分
                invalid_score_response = requests.post(f"{base_url}/api/feedback", json={
                    "interaction_id": interaction_id,
                    "score": 6
                })
                print(f"无效评分测试: {invalid_score_response.status_code} (期望: 400)")
                
                # 5.3 缺少参数
                missing_param_response = requests.post(f"{base_url}/api/feedback", json={
                    "interaction_id": interaction_id
                })
                print(f"缺少参数测试: {missing_param_response.status_code} (期望: 400)")
                
            else:
                print("❌ 未获取到交互ID")
                
        else:
            print(f"❌ 问题发送失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("全面测试完成")

if __name__ == "__main__":
    test_comprehensive_feedback()

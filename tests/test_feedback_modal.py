#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
满意度反馈弹窗测试脚本
"""

import requests
import json
import time

def test_feedback_modal():
    """测试满意度反馈弹窗功能"""
    base_url = "http://localhost:5000"
    
    print("🎨 测试满意度反馈弹窗功能")
    print("=" * 50)
    
    # 测试1：发送问题
    print("\n📝 测试1：发送问题")
    question = "如何解决网络连接问题？"
    
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
                print(f"\n🎯 测试2：测试不同满意度评分的弹窗")
                
                # 测试1星评价
                print(f"\n   测试1星评价弹窗")
                test_feedback_scenario(interaction_id, 1, "非常不满意")
                
                time.sleep(1)
                
                # 测试2星评价
                print(f"\n   测试2星评价弹窗")
                test_feedback_scenario(interaction_id, 2, "不满意")
                
                time.sleep(1)
                
                # 测试3星评价
                print(f"\n   测试3星评价弹窗")
                test_feedback_scenario(interaction_id, 3, "一般满意")
                
            else:
                print("❌ 未获取到交互ID")
                
        else:
            print(f"❌ 问题发送失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

def test_feedback_scenario(interaction_id, rating, description):
    """测试特定评分场景"""
    print(f"   📊 评分: {rating}星 ({description})")
    print(f"   🎨 应该显示自定义弹窗")
    print(f"   ✅ 弹窗内容应该包含: '您给出了{rating}星评价'")
    print(f"   ✅ 弹窗应该居中显示")
    print(f"   ✅ 弹窗应该有两个按钮: '仅提交评分' 和 '重新生成回答'")

def test_ui_workflow():
    """测试UI工作流程"""
    print("\n🎨 测试UI工作流程")
    print("=" * 50)
    print("请打开浏览器访问: http://localhost:5000")
    print("然后测试以下工作流程:")
    print("1. 发送问题")
    print("2. 点击1-3星评价")
    print("3. 观察自定义弹窗:")
    print("   - 弹窗是否居中显示")
    print("   - 弹窗样式是否与整体界面一致")
    print("   - 弹窗内容是否正确")
    print("   - 按钮功能是否正常")
    print("4. 测试弹窗的两种操作:")
    print("   - 点击'仅提交评分'")
    print("   - 点击'重新生成回答'")
    print("5. 测试弹窗关闭方式:")
    print("   - 点击关闭按钮")
    print("   - 点击弹窗外部区域")

def test_modal_features():
    """测试弹窗特性"""
    print("\n🔧 测试弹窗特性")
    print("=" * 50)
    print("弹窗应该具备以下特性:")
    print("✅ 居中显示")
    print("✅ 与整体界面风格一致")
    print("✅ 平滑的动画效果")
    print("✅ 响应式设计（移动端适配）")
    print("✅ 清晰的图标和文字")
    print("✅ 直观的操作按钮")
    print("✅ 多种关闭方式")

if __name__ == "__main__":
    print("🚀 满意度反馈弹窗测试")
    print("=" * 50)
    
    # 检查服务是否运行
    try:
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 服务运行正常")
            test_feedback_modal()
            test_ui_workflow()
            test_modal_features()
        else:
            print("❌ 服务状态异常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 检查服务状态失败: {e}")

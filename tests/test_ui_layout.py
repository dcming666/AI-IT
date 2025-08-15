#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试UI布局改进效果脚本
"""
import requests
import json
import time

def test_ui_layout_improvements():
    base_url = "http://localhost:5000"
    print("🎨 测试UI布局改进效果")
    print("=" * 50)
    
    try:
        # 测试服务是否运行
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 服务运行正常")
            
            # 发送几个测试问题来验证布局
            test_questions = [
                "我的电脑开机很慢怎么办？",
                "如何解决网络连接问题？",
                "打印机无法打印怎么办？"
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
                        print(f"   回答长度: {len(data['response'])} 字符")
                        print(f"   置信度: {data['confidence']:.2%}")
                    else:
                        print(f"❌ 回答失败: {response.text}")
                except Exception as e:
                    print(f"❌ 测试失败: {e}")
                time.sleep(1)
            
            print("\n🎨 UI布局改进说明:")
            print("=" * 50)
            print("1. 顶部区域优化:")
            print("   - 头部高度从 20px padding 减少到 12px")
            print("   - Logo图标从 2.5rem 缩小到 2rem")
            print("   - 标题字体从 1.8rem 缩小到 1.5rem")
            print("   - 底部边距从 30px 减少到 15px")
            
            print("\n2. 聊天头部优化:")
            print("   - 内边距从 30px 减少到 15px 20px")
            print("   - 标题字体从 1.8rem 缩小到 1.4rem")
            print("   - 描述字体从 1.1rem 缩小到 0.9rem")
            
            print("\n3. 聊天消息区域优化:")
            print("   - 内边距从 30px 减少到 20px")
            print("   - 使用 flex: 1 自动填充剩余空间")
            print("   - 移除了固定的 max-height 限制")
            
            print("\n4. 底部输入区域优化:")
            print("   - 内边距从 30px 减少到 15px 20px")
            print("   - 输入框内边距从 20px 减少到 15px")
            print("   - 输入框圆角从 15px 减少到 12px")
            print("   - 操作区域上边距从 15px 减少到 10px")
            
            print("\n5. 整体布局优化:")
            print("   - 容器使用 100vh 高度和 flex 布局")
            print("   - 主内容区域使用 flex: 1 自动扩展")
            print("   - 聊天容器使用 flex 布局最大化消息区域")
            
            print("\n🎯 预期效果:")
            print("   - 顶部和底部区域更紧凑")
            print("   - 中间聊天区域占用更多空间")
            print("   - 整体界面更现代化")
            print("   - 用户体验更流畅")
            
            print("\n📱 请打开浏览器访问: http://localhost:5000")
            print("   观察以下改进:")
            print("   1. 头部是否更紧凑")
            print("   2. 聊天区域是否更大")
            print("   3. 底部输入区域是否更精简")
            print("   4. 整体布局是否更合理")
            
        else:
            print("❌ 服务状态异常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 检查服务状态失败: {e}")

def check_responsive_design():
    print("\n📱 响应式设计检查")
    print("=" * 50)
    print("请在不同屏幕尺寸下测试:")
    print("1. 桌面端 (1920x1080): 检查布局是否合理")
    print("2. 笔记本 (1366x768): 检查是否适配")
    print("3. 平板 (768x1024): 检查响应式效果")
    print("4. 手机 (375x667): 检查移动端适配")
    
    print("\n🎨 建议测试场景:")
    print("- 发送长问题，观察输入框自适应")
    print("- 接收长回答，观察消息区域滚动")
    print("- 快速发送多个问题，观察布局稳定性")
    print("- 调整浏览器窗口大小，观察响应式效果")

if __name__ == "__main__":
    print("🚀 UI布局改进效果测试")
    print("=" * 50)
    test_ui_layout_improvements()
    check_responsive_design()

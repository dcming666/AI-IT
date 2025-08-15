#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试界面美化效果
"""
import requests
import time
import json

def test_ui_beautification():
    """测试界面美化效果"""
    base_url = "http://localhost:5000"
    print("🎨 测试界面美化效果")
    print("=" * 50)
    
    try:
        # 1. 测试主页面加载
        print("1. 测试主页面加载...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 主页面加载成功")
            
            # 检查是否包含美化后的CSS类
            if 'backdrop-filter' in response.text or 'gradient' in response.text:
                print("✅ 检测到美化后的CSS样式")
            else:
                print("⚠️  未检测到美化后的CSS样式")
        else:
            print(f"❌ 主页面加载失败: {response.status_code}")
            return
        
        # 2. 测试CSS文件加载
        print("\n2. 测试CSS文件加载...")
        css_response = requests.get(f"{base_url}/static/css/style.css", timeout=5)
        if css_response.status_code == 200:
            css_content = css_response.text
            print("✅ CSS文件加载成功")
            
            # 检查美化特性
            features = {
                'backdrop-filter': 'backdrop-filter' in css_content,
                'gradient': 'linear-gradient' in css_content,
                'animation': '@keyframes' in css_content,
                'border-radius': 'border-radius: 25px' in css_content,
                'box-shadow': 'box-shadow' in css_content,
                'transition': 'transition' in css_content
            }
            
            print("📊 美化特性检测:")
            for feature, present in features.items():
                status = "✅" if present else "❌"
                print(f"   {status} {feature}")
            
            # 计算美化程度
            beauty_score = sum(features.values()) / len(features) * 100
            print(f"\n🎯 界面美化程度: {beauty_score:.1f}%")
            
        else:
            print(f"❌ CSS文件加载失败: {css_response.status_code}")
            return
        
        # 3. 测试JavaScript文件加载
        print("\n3. 测试JavaScript文件加载...")
        js_response = requests.get(f"{base_url}/static/js/app.js", timeout=5)
        if js_response.status_code == 200:
            print("✅ JavaScript文件加载成功")
        else:
            print(f"❌ JavaScript文件加载失败: {js_response.status_code}")
        
        # 4. 测试响应式设计
        print("\n4. 测试响应式设计...")
        if '@media' in css_content:
            media_queries = css_content.count('@media')
            print(f"✅ 检测到 {media_queries} 个媒体查询")
            
            if 'max-width: 768px' in css_content:
                print("✅ 移动端适配正常")
            if 'max-width: 480px' in css_content:
                print("✅ 小屏幕适配正常")
        else:
            print("❌ 未检测到响应式设计")
        
        # 5. 测试动画效果
        print("\n5. 测试动画效果...")
        if '@keyframes' in css_content:
            animations = ['fadeInUp', 'modalSlideIn', 'feedbackModalSlideIn', 'pulse', 'bounce']
            found_animations = [anim for anim in animations if anim in css_content]
            print(f"✅ 检测到 {len(found_animations)} 个动画: {', '.join(found_animations)}")
        else:
            print("❌ 未检测到动画效果")
        
        # 6. 测试现代化特性
        print("\n6. 测试现代化特性...")
        modern_features = {
            'backdrop-filter': 'backdrop-filter' in css_content,
            'gradient': 'linear-gradient' in css_content,
            'border-radius': 'border-radius: 25px' in css_content,
            'box-shadow': 'box-shadow: 0 8px 25px' in css_content,
            'transition': 'transition: all 0.3s ease' in css_content
        }
        
        print("📊 现代化特性检测:")
        for feature, present in modern_features.items():
            status = "✅" if present else "❌"
            print(f"   {status} {feature}")
        
        print("\n🎯 测试完成！")
        print("=" * 50)
        
        if beauty_score >= 80:
            print("🌟 界面美化效果优秀！")
        elif beauty_score >= 60:
            print("✨ 界面美化效果良好！")
        else:
            print("💡 界面美化效果有待提升")
        
        print(f"\n📱 请在浏览器中访问: {base_url}")
        print("🔍 检查以下美化效果:")
        print("   - 渐变背景和毛玻璃效果")
        print("   - 圆角设计和阴影效果")
        print("   - 平滑的动画过渡")
        print("   - 响应式布局适配")
        print("   - 现代化的按钮和输入框")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_ui_beautification()

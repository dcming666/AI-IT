#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试所有API功能脚本
"""
import requests
import json
import time

def test_all_apis():
    """测试所有API功能"""
    base_url = "http://localhost:5000"
    print("🔧 快速测试所有API功能")
    print("=" * 50)
    
    try:
        # 1. 测试健康检查
        print("1. 测试健康检查...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查通过")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return
        
        # 2. 测试管理统计
        print("\n2. 测试管理统计...")
        response = requests.get(f"{base_url}/admin/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 统计信息: {stats}")
        else:
            print(f"❌ 统计API失败: {response.status_code}")
            return
        
        # 3. 测试知识库列表
        print("\n3. 测试知识库列表...")
        response = requests.get(f"{base_url}/admin/knowledge/list?page=1&page_size=10", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 知识库列表: 共{data['total']}条，当前页{len(data['items'])}条")
        else:
            print(f"❌ 知识库列表API失败: {response.status_code}")
            return
        
        # 4. 测试分类列表
        print("\n4. 测试分类列表...")
        response = requests.get(f"{base_url}/admin/categories", timeout=5)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ 分类列表: {categories}")
        else:
            print(f"❌ 分类API失败: {response.status_code}")
            return
        
        # 5. 测试添加知识条目
        print("\n5. 测试添加知识条目...")
        test_data = {
            "title": f"API测试_{int(time.time())}",
            "category": "测试分类",
            "content": "这是一个通过API测试添加的知识条目。",
            "tags": "测试,API"
        }
        
        response = requests.post(
            f"{base_url}/admin/knowledge",
            json=test_data,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            knowledge_id = result.get('knowledge_id')
            print(f"✅ 添加成功，ID: {knowledge_id}")
            
            # 6. 测试获取单个知识条目
            print("\n6. 测试获取单个知识条目...")
            response = requests.get(f"{base_url}/admin/knowledge/{knowledge_id}", timeout=5)
            if response.status_code == 200:
                knowledge = response.json()
                print(f"✅ 获取成功: {knowledge['title']}")
            else:
                print(f"❌ 获取知识条目失败: {response.status_code}")
            
            # 7. 测试更新知识条目
            print("\n7. 测试更新知识条目...")
            update_data = {
                "title": f"更新后的标题_{int(time.time())}",
                "category": "更新分类",
                "content": "这是更新后的内容。",
                "tags": "更新,测试"
            }
            
            response = requests.put(
                f"{base_url}/admin/knowledge/{knowledge_id}",
                json=update_data,
                timeout=5
            )
            
            if response.status_code == 200:
                print("✅ 更新成功")
            else:
                print(f"❌ 更新失败: {response.status_code}")
            
            # 8. 测试删除知识条目
            print("\n8. 测试删除知识条目...")
            response = requests.delete(f"{base_url}/admin/knowledge/{knowledge_id}", timeout=5)
            if response.status_code == 200:
                print("✅ 删除成功")
            else:
                print(f"❌ 删除失败: {response.status_code}")
            
        else:
            print(f"❌ 添加失败: {response.status_code}")
            print(f"错误信息: {response.text}")
        
        print("\n🎯 所有API测试完成！")
        print("=" * 50)
        print("✅ 系统现在应该完全正常工作了")
        print("📱 请在浏览器中访问:")
        print(f"   - 主页面: {base_url}")
        print(f"   - 管理后台: {base_url}/admin")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_all_apis()

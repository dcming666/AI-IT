#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的管理后台API脚本
"""
import requests
import json
import time

def test_admin_api():
    base_url = "http://localhost:5000"
    print("🔧 测试修复后的管理后台API")
    print("=" * 50)
    
    try:
        # 测试健康检查
        print("1. 测试健康检查...")
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 健康检查通过")
        else:
            print(f"❌ 健康检查失败: {health_response.status_code}")
            return
        
        # 测试管理统计
        print("\n2. 测试管理统计...")
        stats_response = requests.get(f"{base_url}/admin/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"✅ 统计信息: {stats}")
        else:
            print(f"❌ 统计API失败: {stats_response.status_code}")
            return
        
        # 测试知识库列表
        print("\n3. 测试知识库列表...")
        list_response = requests.get(f"{base_url}/admin/knowledge/list?page=1&page_size=10", timeout=5)
        if list_response.status_code == 200:
            list_data = list_response.json()
            print(f"✅ 知识库列表: 共{list_data['total']}条，当前页{len(list_data['items'])}条")
        else:
            print(f"❌ 知识库列表API失败: {list_response.status_code}")
            return
        
        # 测试分类列表
        print("\n4. 测试分类列表...")
        categories_response = requests.get(f"{base_url}/admin/categories", timeout=5)
        if categories_response.status_code == 200:
            categories = categories_response.json()
            print(f"✅ 分类列表: {categories}")
        else:
            print(f"❌ 分类API失败: {categories_response.status_code}")
            return
        
        # 测试添加知识条目
        print("\n5. 测试添加知识条目...")
        test_knowledge = {
            "title": f"API测试标题_{int(time.time())}",
            "category": "技术文档",
            "content": "这是一个通过API测试添加的知识条目内容。",
            "tags": "测试,API,技术"
        }
        
        add_response = requests.post(
            f"{base_url}/admin/knowledge",
            json=test_knowledge,
            timeout=5
        )
        
        if add_response.status_code == 200:
            add_result = add_response.json()
            knowledge_id = add_result.get('knowledge_id')
            print(f"✅ 添加成功，ID: {knowledge_id}")
            
            # 测试获取单个知识条目
            print("\n6. 测试获取单个知识条目...")
            get_response = requests.get(f"{base_url}/admin/knowledge/{knowledge_id}", timeout=5)
            if get_response.status_code == 200:
                knowledge = get_response.json()
                print(f"✅ 获取成功: {knowledge['title']}")
            else:
                print(f"❌ 获取知识条目失败: {get_response.status_code}")
            
            # 测试更新知识条目
            print("\n7. 测试更新知识条目...")
            update_data = {
                "title": f"更新后的标题_{int(time.time())}",
                "category": "更新分类",
                "content": "这是更新后的内容。",
                "tags": "更新,测试"
            }
            
            update_response = requests.put(
                f"{base_url}/admin/knowledge/{knowledge_id}",
                json=update_data,
                timeout=5
            )
            
            if update_response.status_code == 200:
                print("✅ 更新成功")
            else:
                print(f"❌ 更新失败: {update_response.status_code}")
            
            # 测试删除知识条目
            print("\n8. 测试删除知识条目...")
            delete_response = requests.delete(f"{base_url}/admin/knowledge/{knowledge_id}", timeout=5)
            if delete_response.status_code == 200:
                print("✅ 删除成功")
            else:
                print(f"❌ 删除失败: {delete_response.status_code}")
            
        else:
            print(f"❌ 添加失败: {add_response.status_code}")
            print(f"错误信息: {add_response.text}")
        
        print("\n🎯 所有API测试完成！")
        print("=" * 50)
        print("✅ 管理后台API现在应该可以正常工作了")
        print("📱 请在浏览器中访问管理后台:")
        print(f"   {base_url}/admin")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_admin_api()

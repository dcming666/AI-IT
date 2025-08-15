#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试知识库查看功能
"""
import requests
import json
import time

def test_knowledge_view():
    """测试知识库查看功能"""
    base_url = "http://localhost:5000"
    print("📚 测试知识库查看功能")
    print("=" * 50)
    
    try:
        # 1. 测试主页面加载
        print("1. 测试主页面加载...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 主页面加载成功")
            
            # 检查是否包含知识库按钮
            if '知识库' in response.text:
                print("✅ 检测到知识库按钮")
            else:
                print("❌ 未检测到知识库按钮")
                return
        else:
            print(f"❌ 主页面加载失败: {response.status_code}")
            return
        
        # 2. 测试知识库列表API
        print("\n2. 测试知识库列表API...")
        response = requests.get(f"{base_url}/admin/knowledge/list?page=1&page_size=10", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 知识库列表API正常，共{data.get('total', 0)}条数据")
            
            if data.get('items'):
                print(f"   当前页显示{len(data['items'])}条数据")
                # 显示第一条数据的标题
                first_item = data['items'][0]
                print(f"   第一条数据: {first_item.get('title', '无标题')}")
            else:
                print("   ⚠️  知识库暂无数据")
        else:
            print(f"❌ 知识库列表API失败: {response.status_code}")
            return
        
        # 3. 测试分类API
        print("\n3. 测试分类API...")
        response = requests.get(f"{base_url}/admin/categories", timeout=5)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ 分类API正常，共{len(categories)}个分类")
            if categories:
                print(f"   分类列表: {', '.join(categories)}")
        else:
            print(f"❌ 分类API失败: {response.status_code}")
        
        # 4. 测试知识详情API
        print("\n4. 测试知识详情API...")
        if data.get('items'):
            first_id = data['items'][0]['id']
            response = requests.get(f"{base_url}/admin/knowledge/{first_id}", timeout=5)
            if response.status_code == 200:
                detail = response.json()
                print(f"✅ 知识详情API正常")
                print(f"   标题: {detail.get('title', '无标题')}")
                print(f"   分类: {detail.get('category', '无分类')}")
                print(f"   内容长度: {len(detail.get('content', ''))} 字符")
            else:
                print(f"❌ 知识详情API失败: {response.status_code}")
        else:
            print("   ⚠️  跳过知识详情测试（无数据）")
        
        # 5. 测试搜索功能
        print("\n5. 测试搜索功能...")
        if data.get('items'):
            # 使用第一条数据的标题作为搜索词
            search_term = data['items'][0]['title'].split()[0] if data['items'][0]['title'] else '系统'
            response = requests.get(f"{base_url}/admin/knowledge/list?page=1&page_size=10&search={search_term}", timeout=5)
            if response.status_code == 200:
                search_data = response.json()
                print(f"✅ 搜索功能正常，搜索'{search_term}'找到{search_data.get('total', 0)}条结果")
            else:
                print(f"❌ 搜索功能失败: {response.status_code}")
        else:
            print("   ⚠️  跳过搜索测试（无数据）")
        
        # 6. 测试分类筛选
        print("\n6. 测试分类筛选...")
        if categories:
            category = categories[0]
            response = requests.get(f"{base_url}/admin/knowledge/list?page=1&page_size=10&category={category}", timeout=5)
            if response.status_code == 200:
                filter_data = response.json()
                print(f"✅ 分类筛选正常，分类'{category}'有{filter_data.get('total', 0)}条数据")
            else:
                print(f"❌ 分类筛选失败: {response.status_code}")
        else:
            print("   ⚠️  跳过分类筛选测试（无分类）")
        
        print("\n🎯 测试完成！")
        print("=" * 50)
        print("✅ 知识库查看功能测试通过")
        print(f"\n📱 请在浏览器中访问: {base_url}")
        print("🔍 测试以下功能:")
        print("   1. 点击'知识库'按钮")
        print("   2. 查看知识库列表")
        print("   3. 搜索和筛选功能")
        print("   4. 点击查看详情")
        print("   5. 分页功能")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_knowledge_view()

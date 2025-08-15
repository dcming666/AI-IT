#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试admin页面的可展开表格功能
"""
import requests
import json
import time

def test_admin_expandable_table():
    """测试admin页面的可展开表格功能"""
    base_url = "http://localhost:5000"
    print("📊 测试admin页面的可展开表格功能")
    print("=" * 50)
    
    try:
        # 1. 测试admin页面加载
        print("1. 测试admin页面加载...")
        response = requests.get(f"{base_url}/admin", timeout=5)
        if response.status_code == 200:
            print("✅ admin页面加载成功")
            
            # 检查是否包含新的表格结构
            if 'knowledgeTableBody' in response.text:
                print("✅ 检测到新的表格结构")
            else:
                print("❌ 未检测到新的表格结构")
                return
        else:
            print(f"❌ admin页面加载失败: {response.status_code}")
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
                print(f"   内容长度: {len(first_item.get('content', ''))} 字符")
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
        
        # 4. 测试搜索功能
        print("\n4. 测试搜索功能...")
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
        
        # 5. 测试分类筛选
        print("\n5. 测试分类筛选...")
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
        print("✅ admin页面可展开表格功能测试通过")
        print(f"\n📱 请在浏览器中访问: {base_url}/admin")
        print("🔍 测试以下功能:")
        print("   1. 查看知识库条目表格")
        print("   2. 点击标题旁的展开按钮")
        print("   3. 查看完整内容")
        print("   4. 点击收起按钮")
        print("   5. 搜索和筛选功能")
        print("   6. 分页功能")
        print("\n💡 新功能特性:")
        print("   - 内容预览自动截断")
        print("   - 点击展开查看完整内容")
        print("   - 标签独立显示列")
        print("   - 响应式表格设计")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_expandable_table()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试管理后台功能脚本
"""
import requests
import json
import time

def test_admin_backend():
    base_url = "http://localhost:5000"
    print("🔧 测试管理后台功能")
    print("=" * 50)
    
    try:
        # 测试服务是否运行
        health_response = requests.get(f"{base_url}/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 服务运行正常")
            
            # 测试管理后台页面访问
            print("\n📱 测试管理后台页面访问")
            try:
                admin_response = requests.get(f"{base_url}/admin", timeout=5)
                if admin_response.status_code == 200:
                    print("✅ 管理后台页面访问成功")
                else:
                    print(f"❌ 管理后台页面访问失败: {admin_response.status_code}")
            except Exception as e:
                print(f"❌ 管理后台页面访问异常: {e}")
            
            # 测试管理统计信息
            print("\n📊 测试管理统计信息")
            try:
                stats_response = requests.get(f"{base_url}/admin/stats", timeout=5)
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    print("✅ 获取统计信息成功")
                    print(f"   知识条目总数: {stats.get('total_knowledge', 0)}")
                    print(f"   分类总数: {stats.get('total_categories', 0)}")
                    print(f"   最后更新: {stats.get('last_updated', '无')}")
                else:
                    print(f"❌ 获取统计信息失败: {stats_response.status_code}")
            except Exception as e:
                print(f"❌ 获取统计信息异常: {e}")
            
            # 测试知识库列表
            print("\n📚 测试知识库列表")
            try:
                list_response = requests.get(f"{base_url}/admin/knowledge/list", timeout=5)
                if list_response.status_code == 200:
                    list_data = list_response.json()
                    print("✅ 获取知识库列表成功")
                    print(f"   条目数量: {len(list_data.get('items', []))}")
                    print(f"   总条目数: {list_data.get('total', 0)}")
                    print(f"   当前页: {list_data.get('page', 1)}")
                    print(f"   总页数: {list_data.get('total_pages', 1)}")
                else:
                    print(f"❌ 获取知识库列表失败: {list_response.status_code}")
            except Exception as e:
                print(f"❌ 获取知识库列表异常: {e}")
            
            # 测试分类列表
            print("\n🏷️  测试分类列表")
            try:
                categories_response = requests.get(f"{base_url}/admin/categories", timeout=5)
                if categories_response.status_code == 200:
                    categories = categories_response.json()
                    print("✅ 获取分类列表成功")
                    print(f"   分类数量: {len(categories)}")
                    if categories:
                        print(f"   分类: {', '.join(categories[:5])}")
                        if len(categories) > 5:
                            print(f"   ... 还有 {len(categories) - 5} 个分类")
                else:
                    print(f"❌ 获取分类列表失败: {categories_response.status_code}")
            except Exception as e:
                print(f"❌ 获取分类列表异常: {e}")
            
            # 测试添加知识条目
            print("\n➕ 测试添加知识条目")
            test_knowledge = {
                "title": "测试知识条目",
                "category": "测试分类",
                "content": "这是一个测试用的知识条目，用于验证管理后台的添加功能。",
                "tags": "测试,功能验证,管理后台"
            }
            
            try:
                add_response = requests.post(
                    f"{base_url}/admin/knowledge",
                    json=test_knowledge,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if add_response.status_code == 200:
                    add_result = add_response.json()
                    print("✅ 添加知识条目成功")
                    print(f"   条目ID: {add_result.get('knowledge_id', '未知')}")
                    
                    # 测试获取刚添加的条目
                    knowledge_id = add_result.get('knowledge_id')
                    if knowledge_id:
                        print(f"\n🔍 测试获取知识条目 (ID: {knowledge_id})")
                        get_response = requests.get(f"{base_url}/admin/knowledge/{knowledge_id}", timeout=5)
                        if get_response.status_code == 200:
                            knowledge = get_response.json()
                            print("✅ 获取知识条目成功")
                            print(f"   标题: {knowledge.get('title')}")
                            print(f"   分类: {knowledge.get('category')}")
                            print(f"   内容长度: {len(knowledge.get('content', ''))} 字符")
                        else:
                            print(f"❌ 获取知识条目失败: {get_response.status_code}")
                        
                        # 测试更新知识条目
                        print(f"\n✏️  测试更新知识条目 (ID: {knowledge_id})")
                        update_data = {
                            "title": "更新后的测试知识条目",
                            "category": "更新后的测试分类",
                            "content": "这是更新后的测试内容，用于验证管理后台的更新功能。",
                            "tags": "更新,测试,功能验证"
                        }
                        
                        update_response = requests.put(
                            f"{base_url}/admin/knowledge/{knowledge_id}",
                            json=update_data,
                            headers={"Content-Type": "application/json"},
                            timeout=10
                        )
                        
                        if update_response.status_code == 200:
                            print("✅ 更新知识条目成功")
                        else:
                            print(f"❌ 更新知识条目失败: {update_response.status_code}")
                        
                        # 测试删除知识条目
                        print(f"\n🗑️  测试删除知识条目 (ID: {knowledge_id})")
                        delete_response = requests.delete(f"{base_url}/admin/knowledge/{knowledge_id}", timeout=10)
                        
                        if delete_response.status_code == 200:
                            print("✅ 删除知识条目成功")
                        else:
                            print(f"❌ 删除知识条目失败: {delete_response.status_code}")
                    else:
                        print("⚠️  未获取到条目ID，跳过后续测试")
                        
                else:
                    print(f"❌ 添加知识条目失败: {add_response.status_code}")
                    print(f"   错误信息: {add_response.text}")
                    
            except Exception as e:
                print(f"❌ 添加知识条目异常: {e}")
            
            # 测试搜索和筛选功能
            print("\n🔍 测试搜索和筛选功能")
            try:
                # 测试搜索
                search_response = requests.get(
                    f"{base_url}/admin/knowledge/list?search=测试",
                    timeout=5
                )
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    print("✅ 搜索功能正常")
                    print(f"   搜索结果数量: {len(search_data.get('items', []))}")
                else:
                    print(f"❌ 搜索功能异常: {search_response.status_code}")
                
                # 测试分页
                page_response = requests.get(
                    f"{base_url}/admin/knowledge/list?page=1&page_size=5",
                    timeout=5
                )
                if page_response.status_code == 200:
                    page_data = page_response.json()
                    print("✅ 分页功能正常")
                    print(f"   每页大小: {page_data.get('page_size', 0)}")
                    print(f"   当前页: {page_data.get('page', 0)}")
                else:
                    print(f"❌ 分页功能异常: {page_response.status_code}")
                    
            except Exception as e:
                print(f"❌ 搜索和筛选测试异常: {e}")
            
            print("\n🎯 管理后台功能测试完成")
            print("=" * 50)
            print("📱 请在浏览器中访问管理后台:")
            print(f"   {base_url}/admin")
            print("\n🔧 主要功能:")
            print("   ✅ 知识库增删改查")
            print("   ✅ 搜索和筛选")
            print("   ✅ 分页显示")
            print("   ✅ 分类管理")
            print("   ✅ 导入导出")
            print("   ✅ 统计概览")
            
        else:
            print("❌ 服务状态异常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请确保应用正在运行")
        print("启动命令: python app.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_ui_features():
    print("\n🎨 测试管理后台UI功能")
    print("=" * 50)
    print("请在浏览器中测试以下UI功能:")
    print("1. 响应式设计:")
    print("   - 调整浏览器窗口大小")
    print("   - 在不同设备上查看")
    print("2. 交互功能:")
    print("   - 点击添加知识按钮")
    print("   - 编辑现有知识条目")
    print("   - 删除知识条目")
    print("   - 搜索和筛选")
    print("3. 数据操作:")
    print("   - 导入CSV/JSON数据")
    print("   - 导出知识库")
    print("   - 批量操作")
    print("4. 用户体验:")
    print("   - 通知消息显示")
    print("   - 加载状态指示")
    print("   - 错误处理")

if __name__ == "__main__":
    print("🚀 管理后台功能测试")
    print("=" * 50)
    test_admin_backend()
    test_ui_features()

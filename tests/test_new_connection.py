#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的数据库连接池管理
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_utils import DatabaseManager
import time
import threading

def test_connection_pool():
    """测试连接池功能"""
    print("🔧 测试新的数据库连接池管理")
    print("=" * 50)
    
    try:
        # 创建数据库管理器
        db_manager = DatabaseManager()
        print("✅ 数据库管理器创建成功")
        
        # 测试基本查询
        print("\n1. 测试基本查询...")
        result = db_manager.execute_query("SELECT COUNT(*) FROM knowledge_base")
        print(f"✅ 知识库条目数量: {result[0][0]}")
        
        # 测试多次查询
        print("\n2. 测试多次查询...")
        for i in range(5):
            result = db_manager.execute_query("SELECT COUNT(*) FROM knowledge_base")
            print(f"   查询 {i+1}: {result[0][0]} 条")
            time.sleep(0.1)
        
        # 测试并发查询
        print("\n3. 测试并发查询...")
        def worker(worker_id):
            try:
                for i in range(3):
                    result = db_manager.execute_query("SELECT COUNT(*) FROM knowledge_base")
                    print(f"   工作线程 {worker_id} - 查询 {i+1}: {result[0][0]} 条")
                    time.sleep(0.1)
            except Exception as e:
                print(f"❌ 工作线程 {worker_id} 失败: {e}")
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i+1,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 测试知识库详情查询
        print("\n4. 测试知识库详情查询...")
        result = db_manager.get_knowledge_by_id(1)
        if result:
            print(f"✅ 获取知识条目成功: {result['title']}")
        else:
            print("⚠️  知识条目不存在")
        
        # 测试统计查询
        print("\n5. 测试统计查询...")
        stats = db_manager.get_admin_stats()
        print(f"✅ 统计信息: {stats}")
        
        print("\n🎯 所有测试通过！")
        print("新的连接池管理应该能解决连接断开问题")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection_pool()

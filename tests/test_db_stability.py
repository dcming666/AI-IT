#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库连接稳定性脚本
"""
import mysql.connector
import time
import threading

def test_single_connection():
    """测试单个连接的稳定性"""
    print("🔍 测试单个数据库连接稳定性...")
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            database='ai_it_support',
            connection_timeout=60,
            pool_reset_session=True
        )
        
        cursor = connection.cursor()
        
        # 执行多次查询测试稳定性
        for i in range(10):
            try:
                cursor.execute("SELECT COUNT(*) FROM knowledge_base")
                result = cursor.fetchone()
                print(f"✅ 查询 {i+1}: 知识库条目数量 = {result[0]}")
                time.sleep(0.5)  # 间隔0.5秒
            except Exception as e:
                print(f"❌ 查询 {i+1} 失败: {e}")
        
        cursor.close()
        connection.close()
        print("✅ 单个连接测试完成")
        
    except Exception as e:
        print(f"❌ 单个连接测试失败: {e}")

def test_multiple_connections():
    """测试多个并发连接的稳定性"""
    print("\n🔍 测试多个并发连接稳定性...")
    
    def worker(worker_id):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                port=3306,
                user='root',
                password='123456',
                database='ai_it_support',
                connection_timeout=60
            )
            
            cursor = connection.cursor()
            
            for i in range(5):
                try:
                    cursor.execute("SELECT COUNT(*) FROM knowledge_base")
                    result = cursor.fetchone()
                    print(f"✅ 工作线程 {worker_id} - 查询 {i+1}: {result[0]}")
                    time.sleep(0.2)
                except Exception as e:
                    print(f"❌ 工作线程 {worker_id} - 查询 {i+1} 失败: {e}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            print(f"❌ 工作线程 {worker_id} 连接失败: {e}")
    
    # 创建5个工作线程
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("✅ 多连接测试完成")

def test_connection_recovery():
    """测试连接恢复能力"""
    print("\n🔍 测试连接恢复能力...")
    
    try:
        # 创建连接
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            database='ai_it_support',
            connection_timeout=60
        )
        
        cursor = connection.cursor()
        
        # 测试连接
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        result = cursor.fetchone()
        print(f"✅ 初始连接成功: {result[0]}")
        
        # 模拟连接断开（通过执行一个会超时的查询）
        try:
            print("🔄 模拟连接断开...")
            cursor.execute("SELECT SLEEP(10)")  # 10秒超时
        except Exception as e:
            print(f"⚠️  连接超时: {e}")
        
        # 尝试重新连接
        try:
            if not connection.is_connected():
                print("🔄 连接已断开，尝试重新连接...")
                connection.ping(reconnect=True, attempts=3, delay=1)
                print("✅ 重新连接成功")
            else:
                print("✅ 连接仍然有效")
        except Exception as e:
            print(f"❌ 重新连接失败: {e}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ 连接恢复测试失败: {e}")

def main():
    """主函数"""
    print("🔧 数据库连接稳定性测试")
    print("=" * 50)
    
    # 测试单个连接
    test_single_connection()
    
    # 测试多连接
    test_multiple_connections()
    
    # 测试连接恢复
    test_connection_recovery()
    
    print("\n🎯 测试完成！")
    print("如果所有测试都通过，说明数据库连接稳定")
    print("如果有失败，请检查MySQL配置和网络连接")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彻底清理知识库示例数据脚本
"""

import mysql.connector
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

def clear_all_sample_data():
    """彻底清理知识库中的所有示例数据"""
    try:
        # 连接数据库
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '123456'),
            database=os.getenv('DB_NAME', 'ai_it_support')
        )
        
        cursor = connection.cursor()
        
        print("🧹 开始彻底清理知识库示例数据...")
        
        # 删除所有包含示例关键词的数据
        sample_keywords = [
            '网络连接问题排查',
            'Outlook邮件配置', 
            '打印机无法打印',
            '常见IT问题解决流程',
            '系统故障排查步骤'
        ]
        
        total_deleted = 0
        for keyword in sample_keywords:
            cursor.execute("DELETE FROM knowledge_base WHERE title LIKE %s", (f'%{keyword}%',))
            deleted_count = cursor.rowcount
            total_deleted += deleted_count
            if deleted_count > 0:
                print(f"✅ 已删除 {deleted_count} 条包含 '{keyword}' 的数据")
        
        # 删除重复数据（基于标题）
        cursor.execute("""
            DELETE k1 FROM knowledge_base k1
            INNER JOIN knowledge_base k2 
            WHERE k1.id > k2.id AND k1.title = k2.title
        """)
        duplicate_deleted = cursor.rowcount
        if duplicate_deleted > 0:
            print(f"✅ 已删除 {duplicate_deleted} 条重复数据")
            total_deleted += duplicate_deleted
        
        # 提交更改
        connection.commit()
        
        # 检查剩余数据
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        count = cursor.fetchone()[0]
        print(f"\n📊 知识库剩余条目: {count}")
        
        if count == 0:
            print("💡 知识库已完全清空，您可以添加自己的知识条目")
        else:
            cursor.execute("SELECT title, category FROM knowledge_base LIMIT 10")
            remaining = cursor.fetchall()
            print("📝 剩余条目:")
            for item in remaining:
                print(f"   - {item[0]} ({item[1]})")
            
            if count > 10:
                print(f"   ... 还有 {count - 10} 条数据")
        
        cursor.close()
        connection.close()
        
        print(f"\n✅ 清理完成！总共删除了 {total_deleted} 条数据")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")

if __name__ == "__main__":
    clear_all_sample_data()

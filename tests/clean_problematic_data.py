#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理有问题的知识库数据脚本
"""
import mysql.connector

def clean_problematic_data():
    try:
        # 连接数据库
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            database='ai_it_support'
        )
        cursor = connection.cursor()
        
        print("🔍 检查知识库数据...")
        
        # 查看当前数据
        cursor.execute("SELECT id, title, category, content FROM knowledge_base")
        rows = cursor.fetchall()
        
        print(f"📊 当前知识库条目数量: {len(rows)}")
        print("\n当前数据:")
        for row in rows:
            print(f"ID: {row[0]}, 标题: {row[1]}, 分类: {row[2]}")
            print(f"内容预览: {row[3][:50] if row[3] else '无内容'}...")
            print("-" * 50)
        
        # 清理有问题的数据
        print("\n🧹 清理有问题的数据...")
        
        # 删除标题或分类为"1"的条目
        cursor.execute("DELETE FROM knowledge_base WHERE title = '1' OR category = '1'")
        deleted_count1 = cursor.rowcount
        
        # 删除标题或分类包含乱码的条目
        cursor.execute("DELETE FROM knowledge_base WHERE title LIKE '%?%' OR category LIKE '%?%'")
        deleted_count2 = cursor.rowcount
        
        # 删除内容过短的条目
        cursor.execute("DELETE FROM knowledge_base WHERE LENGTH(content) < 10")
        deleted_count3 = cursor.rowcount
        
        connection.commit()
        
        print(f"✅ 清理完成:")
        print(f"   - 删除了 {deleted_count1} 个标题/分类为'1'的条目")
        print(f"   - 删除了 {deleted_count2} 个包含乱码的条目")
        print(f"   - 删除了 {deleted_count3} 个内容过短的条目")
        
        # 查看清理后的数据
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        remaining_count = cursor.fetchone()[0]
        print(f"\n📊 清理后知识库条目数量: {remaining_count}")
        
        if remaining_count > 0:
            cursor.execute("SELECT id, title, category FROM knowledge_base")
            remaining_rows = cursor.fetchall()
            print("\n剩余数据:")
            for row in remaining_rows:
                print(f"ID: {row[0]}, 标题: {row[1]}, 分类: {row[2]}")
        
        cursor.close()
        connection.close()
        
        print("\n🎯 建议:")
        print("1. 重新启动Flask应用: python app.py")
        print("2. 通过管理界面添加新的知识条目")
        print("3. 确保添加的数据格式正确")
        
    except Exception as e:
        print(f"❌ 清理数据失败: {e}")

if __name__ == "__main__":
    clean_problematic_data()

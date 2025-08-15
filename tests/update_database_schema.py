#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新数据库表结构脚本
"""
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def update_database_schema():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '123456'),
            database=os.getenv('DB_NAME', 'ai_it_support')
        )
        cursor = connection.cursor()
        
        print("🔧 开始更新数据库表结构...")
        
        # 检查并添加缺失的字段
        try:
            # 检查 knowledge_base 表是否有 updated_at 字段
            cursor.execute("SHOW COLUMNS FROM knowledge_base LIKE 'updated_at'")
            if not cursor.fetchone():
                print("➕ 添加 updated_at 字段到 knowledge_base 表...")
                cursor.execute("ALTER TABLE knowledge_base ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
                print("✅ updated_at 字段添加成功")
            else:
                print("ℹ️  updated_at 字段已存在")
            
            # 检查 knowledge_base 表是否有 tags 字段
            cursor.execute("SHOW COLUMNS FROM knowledge_base LIKE 'tags'")
            if not cursor.fetchone():
                print("➕ 添加 tags 字段到 knowledge_base 表...")
                cursor.execute("ALTER TABLE knowledge_base ADD COLUMN tags TEXT")
                print("✅ tags 字段添加成功")
            else:
                print("ℹ️  tags 字段已存在")
                
        except Exception as e:
            print(f"⚠️  更新字段时出现错误: {e}")
            print("尝试重新创建表...")
            
            # 删除旧表并重新创建
            cursor.execute("DROP TABLE IF EXISTS knowledge_base")
            print("🗑️  旧表已删除")
            
            # 重新创建知识库表
            knowledge_table = """
            CREATE TABLE knowledge_base (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                category VARCHAR(50),
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                use_count INT DEFAULT 0,
                FULLTEXT (title, content)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            cursor.execute(knowledge_table)
            print("✅ 知识库表重新创建成功")
        
        connection.commit()
        
        # 验证表结构
        print("\n🔍 验证表结构...")
        cursor.execute("DESCRIBE knowledge_base")
        columns = cursor.fetchall()
        
        print("📋 knowledge_base 表结构:")
        for column in columns:
            print(f"   - {column[0]}: {column[1]} {column[2]} {column[3]} {column[4]} {column[5]}")
        
        # 检查表是否为空
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        count = cursor.fetchone()[0]
        print(f"\n📊 知识库条目数量: {count}")
        
        cursor.close()
        connection.close()
        print("\n✅ 数据库表结构更新完成！")
        
    except Exception as e:
        print(f"❌ 更新数据库表结构失败: {e}")

if __name__ == "__main__":
    update_database_schema()

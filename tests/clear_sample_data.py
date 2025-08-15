#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理知识库示例数据脚本
"""

import mysql.connector
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

def clear_sample_data():
    """清理知识库中的示例数据"""
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
        
        print("🧹 开始清理知识库示例数据...")
        
        # 删除示例数据
        sample_titles = [
            '网络连接问题排查',
            'Outlook邮件配置', 
            '打印机无法打印'
        ]
        
        for title in sample_titles:
            cursor.execute("DELETE FROM knowledge_base WHERE title = %s", (title,))
            if cursor.rowcount > 0:
                print(f"✅ 已删除: {title}")
            else:
                print(f"ℹ️  未找到: {title}")
        
        # 提交更改
        connection.commit()
        
        # 检查剩余数据
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        count = cursor.fetchone()[0]
        print(f"\n📊 知识库剩余条目: {count}")
        
        if count == 0:
            print("💡 知识库已清空，您可以添加自己的知识条目")
        else:
            cursor.execute("SELECT title FROM knowledge_base LIMIT 5")
            remaining = cursor.fetchall()
            print("📝 剩余条目:")
            for item in remaining:
                print(f"   - {item[0]}")
        
        cursor.close()
        connection.close()
        
        print("\n✅ 清理完成！")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")

if __name__ == "__main__":
    clear_sample_data()

#!/usr/bin/env python3
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '123456'),
        database=os.getenv('DB_NAME', 'ai_it_support')
    )
    
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE knowledge_base")
    connection.commit()
    cursor.close()
    connection.close()
    
    print("✅ 知识库已完全清空")
    
except Exception as e:
    print(f"❌ 清空失败: {e}")

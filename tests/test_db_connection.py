#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库连接脚本
"""

import os
import sys
from dotenv import load_dotenv

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    
    # 加载环境变量
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ .env文件加载成功")
    else:
        print("❌ .env文件不存在，请先创建")
        return False
    
    # 获取数据库配置
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME', 'ai_it_support'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '123456')
    }
    
    print(f"📋 数据库配置:")
    print(f"   主机: {db_config['host']}")
    print(f"   端口: {db_config['port']}")
    print(f"   数据库: {db_config['database']}")
    print(f"   用户: {db_config['user']}")
    print(f"   密码: {'*' * len(db_config['password'])}")
    
    try:
        # 尝试导入MySQL连接器
        import mysql.connector
        print("✅ MySQL连接器导入成功")
        
        # 尝试连接数据库
        print("🔌 尝试连接数据库...")
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        if connection.is_connected():
            print("✅ 数据库连接成功！")
            
            # 检查数据库是否存在
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            
            if db_config['database'] in databases:
                print(f"✅ 数据库 '{db_config['database']}' 已存在")
                
                # 使用数据库
                cursor.execute(f"USE {db_config['database']}")
                print(f"✅ 已切换到数据库 '{db_config['database']}'")
                
                # 检查表是否存在
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                
                if tables:
                    print(f"✅ 发现 {len(tables)} 个表:")
                    for table in tables:
                        print(f"   - {table}")
                else:
                    print("⚠️  数据库中没有表")
                    
            else:
                print(f"⚠️  数据库 '{db_config['database']}' 不存在")
                print("   建议运行: python deploy.py 来自动创建")
            
            cursor.close()
            connection.close()
            print("✅ 数据库连接已关闭")
            return True
            
        else:
            print("❌ 数据库连接失败")
            return False
            
    except ImportError:
        print("❌ MySQL连接器未安装")
        print("   请运行: pip install mysql-connector-python")
        return False
        
    except mysql.connector.Error as err:
        print(f"❌ 数据库连接错误: {err}")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("   AI-IT 支持系统 - 数据库连接测试")
    print("=" * 50)
    print()
    
    success = test_database_connection()
    
    print()
    if success:
        print("🎉 数据库连接测试通过！")
        print("   现在可以运行: python deploy.py 来初始化系统")
    else:
        print("💥 数据库连接测试失败！")
        print("   请检查配置并重试")
    
    print("=" * 50)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的数据库连接测试脚本
"""

def test_mysql_connection():
    """测试MySQL连接"""
    print("🔍 测试MySQL数据库连接...")
    
    # 数据库配置
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '123456'
    }
    
    print(f"📋 数据库配置:")
    print(f"   主机: {db_config['host']}")
    print(f"   端口: {db_config['port']}")
    print(f"   用户: {db_config['user']}")
    print(f"   密码: {'*' * len(db_config['password'])}")
    
    try:
        # 尝试导入MySQL连接器
        import mysql.connector
        print("✅ MySQL连接器导入成功")
        
        # 尝试连接数据库
        print("🔌 尝试连接MySQL服务器...")
        connection = mysql.connector.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password']
        )
        
        if connection.is_connected():
            print("✅ MySQL连接成功！")
            
            # 检查数据库是否存在
            cursor = connection.cursor()
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            
            print(f"📊 发现 {len(databases)} 个数据库:")
            for db in databases:
                print(f"   - {db}")
            
            # 检查是否存在目标数据库
            target_db = 'ai_it_support'
            if target_db in databases:
                print(f"✅ 数据库 '{target_db}' 已存在")
                
                # 使用数据库
                cursor.execute(f"USE {target_db}")
                print(f"✅ 已切换到数据库 '{target_db}'")
                
                # 检查表是否存在
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                
                if tables:
                    print(f"✅ 发现 {len(tables)} 个表:")
                    for table in tables:
                        print(f"   - {table}")
                else:
                    print("⚠️  数据库中没有表")
                    print("   建议运行: python deploy.py 来自动创建")
                    
            else:
                print(f"⚠️  数据库 '{target_db}' 不存在")
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
        print(f"❌ MySQL连接错误: {err}")
        if "Can't connect to MySQL server" in str(err):
            print("💡 可能的原因:")
            print("   1. MySQL服务未启动")
            print("   2. MySQL未安装")
            print("   3. 端口被占用")
            print("   4. 防火墙阻止连接")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("   AI-IT 支持系统 - MySQL连接测试")
    print("=" * 50)
    print()
    
    success = test_mysql_connection()
    
    print()
    if success:
        print("🎉 MySQL连接测试通过！")
        print("   现在可以运行: python deploy.py 来初始化系统")
    else:
        print("💥 MySQL连接测试失败！")
        print("   请检查MySQL服务状态并重试")
    
    print("=" * 50)

if __name__ == "__main__":
    main()

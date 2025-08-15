#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加示例知识库数据脚本
"""
import mysql.connector

def add_sample_knowledge():
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
        
        print("📚 添加示例知识库数据...")
        
        # 示例知识库数据
        sample_data = [
            {
                'title': 'Windows系统常见问题解决',
                'category': '系统维护',
                'content': '''Windows系统常见问题及解决方案：

1. 系统运行缓慢
   - 清理临时文件
   - 关闭不必要的启动项
   - 运行磁盘清理工具

2. 蓝屏错误
   - 检查硬件驱动
   - 运行系统文件检查器
   - 更新系统补丁

3. 网络连接问题
   - 检查网络适配器
   - 重置网络设置
   - 运行网络故障排除工具''',
                'tags': 'Windows,系统,故障排除,维护'
            },
            {
                'title': '办公软件使用技巧',
                'category': '办公软件',
                'content': '''常用办公软件使用技巧：

1. Microsoft Office
   - Word文档格式设置
   - Excel数据处理技巧
   - PowerPoint演示制作

2. 文件管理
   - 文件命名规范
   - 文件夹组织结构
   - 文件备份策略

3. 协作工具
   - 共享文档设置
   - 版本控制管理
   - 在线协作平台使用''',
                'tags': 'Office,办公软件,技巧,协作'
            },
            {
                'title': '网络安全基础知识',
                'category': '网络安全',
                'content': '''网络安全基础知识：

1. 密码安全
   - 强密码设置原则
   - 定期更换密码
   - 多因素认证

2. 防病毒措施
   - 安装防病毒软件
   - 定期更新病毒库
   - 不打开可疑邮件附件

3. 数据保护
   - 重要文件加密
   - 定期数据备份
   - 敏感信息保护''',
                'tags': '网络安全,密码,防病毒,数据保护'
            },
            {
                'title': '打印机故障排除',
                'category': '硬件设备',
                'content': '''打印机常见故障排除：

1. 打印机无法连接
   - 检查USB连接线
   - 确认驱动程序安装
   - 重启打印机和电脑

2. 打印质量问题
   - 清洁打印头
   - 检查墨盒/碳粉
   - 调整打印设置

3. 卡纸问题
   - 安全取出卡纸
   - 检查纸张质量
   - 调整纸张设置''',
                'tags': '打印机,故障排除,硬件,维护'
            }
        ]
        
        # 插入数据
        for item in sample_data:
            query = """
            INSERT INTO knowledge_base (title, category, content, tags, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            cursor.execute(query, (item['title'], item['category'], item['content'], item['tags']))
            print(f"✅ 已添加: {item['title']}")
        
        connection.commit()
        
        # 查看添加后的数据
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        total_count = cursor.fetchone()[0]
        
        print(f"\n📊 知识库数据添加完成！")
        print(f"当前知识库条目数量: {total_count}")
        
        # 显示分类统计
        cursor.execute("SELECT category, COUNT(*) FROM knowledge_base GROUP BY category")
        categories = cursor.fetchall()
        
        print("\n📋 分类统计:")
        for category, count in categories:
            print(f"   - {category}: {count} 条")
        
        cursor.close()
        connection.close()
        
        print("\n🎯 下一步:")
        print("1. 重新启动Flask应用: python app.py")
        print("2. 访问管理后台: http://localhost:5000/admin")
        print("3. 查看和管理知识库数据")
        
    except Exception as e:
        print(f"❌ 添加示例数据失败: {e}")

if __name__ == "__main__":
    add_sample_knowledge()

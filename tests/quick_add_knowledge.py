#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速添加知识库条目脚本
"""

import os
from dotenv import load_dotenv
from db_utils import db_manager

def add_sample_knowledge():
    """添加示例知识库条目"""
    
    # 加载环境变量
    load_dotenv()
    
    # 示例知识库数据
    knowledge_items = [
        {
            "title": "打印机无法打印解决方案",
            "content": """
打印机无法打印的常见解决方法：

1. 检查电源和连接
   - 确认打印机电源已开启
   - 检查USB线或网络连接是否正常
   - 重启打印机

2. 检查驱动程序
   - 确认已安装正确的打印机驱动
   - 在设备管理器中检查打印机状态
   - 重新安装驱动程序

3. 检查打印队列
   - 打开"设备和打印机"
   - 右键点击打印机，选择"查看打印队列"
   - 清除所有待打印任务

4. 检查纸张和墨盒
   - 确认纸张充足且正确放置
   - 检查墨盒是否有墨水
   - 清洁打印头

5. 重启服务
   - 按Win+R，输入services.msc
   - 找到"Print Spooler"服务
   - 重启该服务
            """,
            "category": "硬件问题"
        },
        {
            "title": "网络连接故障排除",
            "content": """
网络连接问题的排查步骤：

1. 基础检查
   - 检查网线是否松动
   - 确认路由器/交换机电源正常
   - 查看网络适配器状态

2. 网络配置检查
   - 检查IP地址配置
   - 确认DNS服务器设置
   - 运行ipconfig /all查看详细信息

3. 网络诊断
   - 运行ping命令测试连通性
   - 使用tracert追踪路由
   - 检查防火墙设置

4. 重启设备
   - 重启网络适配器
   - 重启路由器/交换机
   - 重启计算机

5. 联系网络管理员
   - 如果以上步骤无效
   - 提供错误信息和诊断结果
            """,
            "category": "网络问题"
        },
        {
            "title": "软件安装失败处理",
            "content": """
软件安装失败的解决方法：

1. 权限检查
   - 以管理员身份运行安装程序
   - 检查用户账户控制设置
   - 确认有足够的磁盘空间

2. 系统要求检查
   - 确认操作系统版本兼容
   - 检查.NET Framework版本
   - 确认系统架构匹配（32位/64位）

3. 清理环境
   - 关闭杀毒软件
   - 清理临时文件
   - 卸载旧版本软件

4. 下载和安装
   - 从官方网站下载最新版本
   - 使用兼容模式安装
   - 检查安装日志文件

5. 系统修复
   - 运行系统文件检查器
   - 修复Windows更新
   - 重置系统设置
            """,
            "category": "软件安装"
        },
        {
            "title": "邮箱配置指南",
            "content": """
邮箱客户端配置步骤：

1. 获取邮箱信息
   - 邮箱地址和密码
   - 服务器地址（SMTP/POP3/IMAP）
   - 端口号和安全设置

2. Outlook配置
   - 打开Outlook
   - 文件 -> 添加账户
   - 输入邮箱地址和密码
   - 选择账户类型

3. 服务器设置
   - SMTP服务器：用于发送邮件
   - POP3/IMAP服务器：用于接收邮件
   - 启用SSL/TLS加密

4. 测试连接
   - 发送测试邮件
   - 检查接收是否正常
   - 确认同步设置

5. 常见问题
   - 检查网络连接
   - 确认服务器地址正确
   - 检查防火墙设置
            """,
            "category": "邮箱配置"
        },
        {
            "title": "系统性能优化",
            "content": """
Windows系统性能优化方法：

1. 启动项管理
   - 按Ctrl+Shift+Esc打开任务管理器
   - 选择"启动"标签
   - 禁用不必要的启动项

2. 磁盘清理
   - 运行磁盘清理工具
   - 删除临时文件和下载缓存
   - 清空回收站

3. 系统维护
   - 运行磁盘碎片整理
   - 检查磁盘错误
   - 更新系统补丁

4. 内存优化
   - 关闭不必要的程序
   - 增加虚拟内存
   - 使用内存优化工具

5. 定期维护
   - 每周清理临时文件
   - 每月检查系统更新
   - 定期备份重要数据
            """,
            "category": "系统优化"
        }
    ]
    
    print("🚀 开始添加知识库条目...")
    
    for i, item in enumerate(knowledge_items, 1):
        try:
            knowledge_id = db_manager.add_knowledge_item(
                title=item["title"],
                content=item["content"],
                category=item["category"]
            )
            print(f"✅ [{i}/{len(knowledge_items)}] 添加成功: {item['title']}")
        except Exception as e:
            print(f"❌ [{i}/{len(knowledge_items)}] 添加失败: {item['title']} - {e}")
    
    print(f"\n🎉 知识库添加完成！共添加 {len(knowledge_items)} 个条目")
    
    # 显示统计信息
    try:
        stats = db_manager.get_interaction_stats()
        print(f"📊 当前知识库条目数: {stats.get('knowledge_count', 0)}")
    except Exception as e:
        print(f"⚠️  无法获取统计信息: {e}")

if __name__ == "__main__":
    add_sample_knowledge()

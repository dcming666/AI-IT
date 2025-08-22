#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI-IT 智能客服系统数据库备份脚本
"""

import os
import sys
import subprocess
import datetime
from pathlib import Path

def backup_database():
    """备份数据库"""
    print("🗄️ 开始备份数据库...")
    
    # 创建备份目录
    backup_dir = Path("backup")
    backup_dir.mkdir(exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"ai_it_system_backup_{timestamp}.sql"
    
    try:
        # 从环境变量或配置文件读取数据库配置
        from config import Config
        
        # 构建mysqldump命令
        cmd = [
            "mysqldump",
            "-h", Config.DB_HOST,
            "-P", str(Config.DB_PORT),
            "-u", Config.DB_USER,
            f"--password={Config.DB_PASSWORD}",
            "--routines",
            "--triggers",
            "--single-transaction",
            "--add-drop-database",
            Config.DB_NAME
        ]
        
        # 执行备份
        with open(backup_file, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print(f"✅ 数据库备份成功: {backup_file}")
            
            # 显示备份文件大小
            file_size = backup_file.stat().st_size
            print(f"📊 备份文件大小: {file_size / 1024 / 1024:.2f} MB")
            
            return str(backup_file)
        else:
            print(f"❌ 数据库备份失败: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ 备份过程中出现错误: {e}")
        return None

def restore_database(backup_file):
    """恢复数据库"""
    print(f"🔄 开始恢复数据库: {backup_file}")
    
    try:
        from config import Config
        
        # 构建mysql命令
        cmd = [
            "mysql",
            "-h", Config.DB_HOST,
            "-P", str(Config.DB_PORT),
            "-u", Config.DB_USER,
            f"--password={Config.DB_PASSWORD}",
            Config.DB_NAME
        ]
        
        # 执行恢复
        with open(backup_file, 'r', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
        
        if result.returncode == 0:
            print("✅ 数据库恢复成功")
            return True
        else:
            print(f"❌ 数据库恢复失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 恢复过程中出现错误: {e}")
        return False

def list_backups():
    """列出所有备份文件"""
    backup_dir = Path("backup")
    if not backup_dir.exists():
        print("📁 备份目录不存在")
        return
    
    backup_files = list(backup_dir.glob("ai_it_system_backup_*.sql"))
    
    if not backup_files:
        print("📁 没有找到备份文件")
        return
    
    print("📋 备份文件列表:")
    for backup_file in sorted(backup_files, reverse=True):
        file_size = backup_file.stat().st_size
        file_time = datetime.datetime.fromtimestamp(backup_file.stat().st_mtime)
        print(f"  {backup_file.name}")
        print(f"    大小: {file_size / 1024 / 1024:.2f} MB")
        print(f"    时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python backup_database.py backup    # 备份数据库")
        print("  python backup_database.py restore <file>  # 恢复数据库")
        print("  python backup_database.py list      # 列出备份文件")
        return
    
    action = sys.argv[1]
    
    if action == "backup":
        backup_database()
    elif action == "restore":
        if len(sys.argv) < 3:
            print("❌ 请指定要恢复的备份文件")
            return
        backup_file = sys.argv[2]
        if not Path(backup_file).exists():
            print(f"❌ 备份文件不存在: {backup_file}")
            return
        restore_database(backup_file)
    elif action == "list":
        list_backups()
    else:
        print(f"❌ 未知操作: {action}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行器脚本
可以运行所有测试或特定类别的测试
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_test_file(test_file):
    """运行单个测试文件"""
    print(f"\n🔧 运行测试: {test_file}")
    print("=" * 60)
    
    try:
        # 切换到tests目录
        os.chdir(Path(__file__).parent)
        
        # 运行测试文件
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=60)
        
        if result.returncode == 0:
            print("✅ 测试通过")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ 测试失败")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print(result.stdout)
                
    except subprocess.TimeoutExpired:
        print("⏰ 测试超时")
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
    
    print("=" * 60)

def run_category_tests(category):
    """运行特定类别的测试"""
    category_tests = {
        'system': [
            'test_system.py',
            'test_admin_api_fixed.py',
            'test_admin_backend.py'
        ],
        'database': [
            'test_db_connection.py',
            'simple_db_test.py'
        ],
        'ui': [
            'test_rating_system.py',
            'test_feedback_modal.py',
            'test_satisfaction_feedback.py',
            'test_question_accuracy.py',
            'test_ui_layout.py',
            'test_format_improvement.py'
        ]
    }
    
    if category not in category_tests:
        print(f"❌ 未知的测试类别: {category}")
        print(f"可用的类别: {', '.join(category_tests.keys())}")
        return
    
    print(f"🚀 运行 {category} 类别测试...")
    for test_file in category_tests[category]:
        if os.path.exists(test_file):
            run_test_file(test_file)
        else:
            print(f"⚠️  测试文件不存在: {test_file}")

def run_all_tests():
    """运行所有测试"""
    print("🚀 运行所有测试...")
    
    # 获取所有测试文件
    test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.py')]
    test_files.extend([f for f in os.listdir('.') if 'test' in f and f.endswith('.py') and f not in test_files])
    
    # 按类别排序
    system_tests = [f for f in test_files if 'admin' in f or 'system' in f]
    database_tests = [f for f in test_files if 'db' in f or 'connection' in f]
    ui_tests = [f for f in test_files if f not in system_tests and f not in database_tests]
    
    print(f"📊 找到 {len(test_files)} 个测试文件")
    print(f"   - 系统测试: {len(system_tests)} 个")
    print(f"   - 数据库测试: {len(database_tests)} 个")
    print(f"   - 界面测试: {len(ui_tests)} 个")
    
    # 运行系统测试
    print("\n🔧 运行系统测试...")
    for test_file in system_tests:
        run_test_file(test_file)
    
    # 运行数据库测试
    print("\n🗄️ 运行数据库测试...")
    for test_file in database_tests:
        run_test_file(test_file)
    
    # 运行界面测试
    print("\n🎨 运行界面测试...")
    for test_file in ui_tests:
        run_test_file(test_file)

def show_help():
    """显示帮助信息"""
    print("""
🔧 AI-IT支持系统测试运行器

用法:
  python run_all_tests.py [选项]

选项:
  all             运行所有测试
  system          运行系统功能测试
  database        运行数据库测试
  ui              运行界面测试
  help            显示此帮助信息

示例:
  python run_all_tests.py all        # 运行所有测试
  python run_all_tests.py system     # 运行系统测试
  python run_all_tests.py database   # 运行数据库测试
  python run_all_tests.py ui         # 运行界面测试

注意:
  - 运行测试前请确保Flask应用正在运行
  - 确保数据库连接正常
  - 某些测试可能需要特定的环境配置
""")

def main():
    """主函数"""
    print("🔧 AI-IT支持系统测试运行器")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'help':
        show_help()
    elif command == 'all':
        run_all_tests()
    elif command in ['system', 'database', 'ui']:
        run_category_tests(command)
    else:
        print(f"❌ 未知命令: {command}")
        show_help()

if __name__ == "__main__":
    main()

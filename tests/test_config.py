#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置文件
包含测试环境的配置信息
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 测试配置
TEST_CONFIG = {
    # 测试服务器配置
    'TEST_SERVER': {
        'BASE_URL': 'http://localhost:5000',
        'TIMEOUT': 10,
        'RETRY_COUNT': 3
    },
    
    # 测试数据库配置
    'TEST_DATABASE': {
        'HOST': 'localhost',
        'PORT': 3306,
        'NAME': 'ai_it_support',
        'USER': 'root',
        'PASSWORD': '123456'
    },
    
    # 测试数据配置
    'TEST_DATA': {
        'SAMPLE_KNOWLEDGE': {
            'title': '测试知识条目',
            'category': '测试分类',
            'content': '这是一个用于测试的知识条目内容。',
            'tags': '测试,示例,知识库'
        },
        'SAMPLE_QUESTION': '这是一个测试问题，用于验证系统功能。',
        'SAMPLE_USER_ID': 'test_user_001',
        'SAMPLE_SESSION_ID': 'test_session_001'
    },
    
    # 测试超时配置
    'TIMEOUTS': {
        'API_CALL': 10,
        'DATABASE_QUERY': 5,
        'UI_RESPONSE': 3,
        'FILE_OPERATION': 2
    },
    
    # 测试重试配置
    'RETRY': {
        'MAX_ATTEMPTS': 3,
        'DELAY_BETWEEN_ATTEMPTS': 1
    }
}

# 测试环境检查
def check_test_environment():
    """检查测试环境是否准备就绪"""
    print("🔍 检查测试环境...")
    
    # 检查Flask应用是否运行
    try:
        import requests
        response = requests.get(f"{TEST_CONFIG['TEST_SERVER']['BASE_URL']}/api/health", 
                              timeout=TEST_CONFIG['TEST_SERVER']['TIMEOUT'])
        if response.status_code == 200:
            print("✅ Flask应用运行正常")
        else:
            print("❌ Flask应用状态异常")
            return False
    except Exception as e:
        print(f"❌ 无法连接到Flask应用: {e}")
        print("请确保运行: python app.py")
        return False
    
    # 检查数据库连接
    try:
        import mysql.connector
        connection = mysql.connector.connect(
            host=TEST_CONFIG['TEST_DATABASE']['HOST'],
            port=TEST_CONFIG['TEST_DATABASE']['PORT'],
            user=TEST_CONFIG['TEST_DATABASE']['USER'],
            password=TEST_CONFIG['TEST_DATABASE']['PASSWORD'],
            database=TEST_CONFIG['TEST_DATABASE']['NAME']
        )
        connection.close()
        print("✅ 数据库连接正常")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    # 检查必要的Python包
    required_packages = ['requests', 'mysql-connector-python', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少必要的Python包: {', '.join(missing_packages)}")
        print("请运行: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ 所有必要的Python包已安装")
    
    print("✅ 测试环境检查完成")
    return True

# 测试工具函数
def get_test_url(endpoint):
    """获取测试URL"""
    return f"{TEST_CONFIG['TEST_SERVER']['BASE_URL']}{endpoint}"

def get_test_timeout(timeout_type='API_CALL'):
    """获取测试超时时间"""
    return TEST_CONFIG['TIMEOUTS'].get(timeout_type, 10)

def get_test_data(data_type):
    """获取测试数据"""
    return TEST_CONFIG['TEST_DATA'].get(data_type, {})

def wait_with_timeout(seconds):
    """等待指定时间"""
    import time
    time.sleep(seconds)

# 测试日志配置
def setup_test_logging():
    """设置测试日志"""
    import logging
    
    # 创建logs目录
    logs_dir = PROJECT_ROOT / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # 配置测试日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'test.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

if __name__ == "__main__":
    # 运行环境检查
    check_test_environment()

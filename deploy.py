#!/usr/bin/env python3
"""
企业AI技术支持系统部署脚本
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        logger.error("需要Python 3.8或更高版本")
        return False
    logger.info(f"Python版本检查通过: {sys.version}")
    return True

def install_dependencies():
    """安装依赖包"""
    try:
        logger.info("正在安装依赖包...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        logger.info("依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"依赖包安装失败: {e}")
        return False

def create_env_file():
    """创建环境配置文件"""
    env_file = Path(".env")
    if env_file.exists():
        logger.info(".env文件已存在")
        return True
    
    try:
        # 复制示例文件
        example_file = Path("env.example")
        if example_file.exists():
            with open(example_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(".env文件创建成功，请根据实际情况修改配置")
            return True
        else:
            logger.warning("未找到env.example文件")
            return False
    except Exception as e:
        logger.error(f"创建.env文件失败: {e}")
        return False

def check_database_connection():
    """检查数据库连接"""
    try:
        from config import Config
        from db_utils import db_manager
        
        # 测试连接
        db_manager.connection.ping(reconnect=True)
        logger.info("数据库连接成功")
        return True
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        logger.info("请检查.env文件中的数据库配置")
        return False

def initialize_database():
    """初始化数据库"""
    try:
        from app import init_database
        logger.info("正在初始化数据库...")
        init_database()
        logger.info("数据库初始化完成")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False

def start_application():
    """启动应用"""
    try:
        logger.info("正在启动应用...")
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        logger.info("应用已停止")
    except subprocess.CalledProcessError as e:
        logger.error(f"应用启动失败: {e}")

def main():
    """主函数"""
    logger.info("开始部署企业AI技术支持系统...")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        logger.error("依赖安装失败，请检查网络连接和pip配置")
        sys.exit(1)
    
    # 创建环境配置文件
    if not create_env_file():
        logger.warning("环境配置文件创建失败，请手动创建")
    
    # 检查数据库连接
    if not check_database_connection():
        logger.error("数据库连接失败，请检查配置后重试")
        sys.exit(1)
    
    # 初始化数据库
    if not initialize_database():
        logger.error("数据库初始化失败")
        sys.exit(1)
    
    logger.info("部署完成！正在启动应用...")
    
    # 启动应用
    start_application()

if __name__ == "__main__":
    main()

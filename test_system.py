#!/usr/bin/env python3
"""
企业AI技术支持系统测试脚本
"""

import sys
import os
import logging
from unittest.mock import Mock, patch

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_config():
    """测试配置模块"""
    try:
        from config import Config
        logger.info("✓ 配置模块加载成功")
        
        # 检查关键配置项
        assert hasattr(Config, 'DB_HOST'), "缺少数据库主机配置"
        assert hasattr(Config, 'EMBEDDING_MODEL'), "缺少嵌入模型配置"
        assert hasattr(Config, 'CONFIDENCE_THRESHOLD'), "缺少置信度阈值配置"
        
        logger.info("✓ 配置项检查通过")
        return True
    except Exception as e:
        logger.error(f"✗ 配置模块测试失败: {e}")
        return False

def test_database_utils():
    """测试数据库工具模块"""
    try:
        from db_utils import DatabaseManager
        logger.info("✓ 数据库工具模块加载成功")
        
        # 测试类方法
        methods = ['connect', 'create_tables', 'add_interaction', 'search_knowledge']
        for method in methods:
            assert hasattr(DatabaseManager, method), f"缺少方法: {method}"
        
        logger.info("✓ 数据库工具方法检查通过")
        return True
    except Exception as e:
        logger.error(f"✗ 数据库工具模块测试失败: {e}")
        return False

def test_rag_engine():
    """测试RAG引擎模块"""
    try:
        from rag_engine import RAGEngine
        logger.info("✓ RAG引擎模块加载成功")
        
        # 测试类方法
        methods = ['generate_embedding', 'search_knowledge', 'generate_response']
        for method in methods:
            assert hasattr(RAGEngine, method), f"缺少方法: {method}"
        
        logger.info("✓ RAG引擎方法检查通过")
        return True
    except Exception as e:
        logger.error(f"✗ RAG引擎模块测试失败: {e}")
        return False

def test_flask_app():
    """测试Flask应用"""
    try:
        from app import app
        logger.info("✓ Flask应用加载成功")
        
        # 检查路由
        routes = ['/', '/api/ask', '/admin/knowledge', '/api/health']
        for route in routes:
            assert route in [str(rule) for rule in app.url_map.iter_rules()], f"缺少路由: {route}"
        
        logger.info("✓ Flask路由检查通过")
        return True
    except Exception as e:
        logger.error(f"✗ Flask应用测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    try:
        import flask
        import mysql.connector
        import numpy
        import sentence_transformers
        
        logger.info("✓ 核心依赖包导入成功")
        
        # 检查版本
        logger.info(f"  - Flask: {flask.__version__}")
        logger.info(f"  - NumPy: {numpy.__version__}")
        logger.info(f"  - Sentence Transformers: {sentence_transformers.__version__}")
        
        return True
    except ImportError as e:
        logger.error(f"✗ 依赖包导入失败: {e}")
        return False

def test_file_structure():
    """测试文件结构"""
    required_files = [
        'app.py',
        'config.py',
        'db_utils.py',
        'rag_engine.py',
        'requirements.txt',
        'README.md',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"✗ 缺少必要文件: {missing_files}")
        return False
    else:
        logger.info("✓ 文件结构检查通过")
        return True

def run_all_tests():
    """运行所有测试"""
    logger.info("开始系统测试...")
    
    tests = [
        ("文件结构", test_file_structure),
        ("依赖包", test_dependencies),
        ("配置模块", test_config),
        ("数据库工具", test_database_utils),
        ("RAG引擎", test_rag_engine),
        ("Flask应用", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- 测试 {test_name} ---")
        if test_func():
            passed += 1
            logger.info(f"✓ {test_name} 测试通过")
        else:
            logger.error(f"✗ {test_name} 测试失败")
    
    logger.info(f"\n=== 测试结果 ===")
    logger.info(f"通过: {passed}/{total}")
    logger.info(f"失败: {total - passed}/{total}")
    
    if passed == total:
        logger.info("🎉 所有测试通过！系统准备就绪。")
        return True
    else:
        logger.error("❌ 部分测试失败，请检查系统配置。")
        return False

def main():
    """主函数"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试过程中出现未预期的错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

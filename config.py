import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类 - 性能优化版"""
    
    # 数据库配置 - 优化连接池
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'ai_it_support')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # 数据库连接池优化配置
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', 10))  # 增加连接池大小
    DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', 30))  # 减少连接超时
    DB_CONNECTION_TIMEOUT = int(os.getenv('DB_CONNECTION_TIMEOUT', 10))  # 减少连接超时
    
    # AI模型配置 - 性能优化
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    OPENAI_ENABLED = os.getenv('OPENAI_ENABLED', 'false').lower() == 'true'
    OPENAI_TIMEOUT = int(os.getenv('OPENAI_TIMEOUT', 8))  # 大幅减少超时时间
    
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_API_BASE = os.getenv('CLAUDE_API_BASE', 'https://api.anthropic.com')
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
    CLAUDE_ENABLED = os.getenv('CLAUDE_ENABLED', 'false').lower() == 'true'
    CLAUDE_TIMEOUT = int(os.getenv('CLAUDE_TIMEOUT', 8))  # 大幅减少超时时间
    
    GLM_API_KEY = os.getenv('GLM_API_KEY')
    GLM_API_BASE = os.getenv('GLM_API_BASE', 'https://open.bigmodel.cn/api/paas/v4')
    GLM_MODEL = os.getenv('GLM_MODEL', 'glm-4')
    GLM_ENABLED = os.getenv('GLM_ENABLED', 'false').lower() == 'true'
    GLM_TIMEOUT = int(os.getenv('GLM_TIMEOUT', 8))  # 大幅减少超时时间
    
    QWEN_API_KEY = os.getenv('QWEN_API_KEY')
    QWEN_API_BASE = os.getenv('QWEN_API_BASE', 'https://dashscope.aliyuncs.com/api/v1')
    QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen-plus')
    QWEN_ENABLED = os.getenv('QWEN_ENABLED', 'false').lower() == 'true'
    QWEN_TIMEOUT = int(os.getenv('QWEN_TIMEOUT', 10))  # 减少超时时间
    
    # RAG引擎性能配置
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 500))  # 大幅减少token数量
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.3))  # 降低随机性
    TOP_K_SEARCH = int(os.getenv('TOP_K_SEARCH', 3))  # 减少搜索数量
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', 0.1))  # 降低相似度阈值
    
    # 缓存配置
    CACHE_SIZE = int(os.getenv('CACHE_SIZE', 1000))  # 增加缓存大小
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 缓存1小时
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # 性能监控配置
    ENABLE_PERFORMANCE_MONITORING = os.getenv('ENABLE_PERFORMANCE_MONITORING', 'true').lower() == 'true'
    PERFORMANCE_LOG_INTERVAL = int(os.getenv('PERFORMANCE_LOG_INTERVAL', 100))  # 每100次请求记录一次性能
    
    # 并发配置
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 10))  # 最大并发请求数
    
    # 超时配置
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 15))  # 请求总超时时间
    AI_RESPONSE_TIMEOUT = int(os.getenv('AI_RESPONSE_TIMEOUT', 8))  # AI响应超时时间
    
    # 重试配置
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 2))  # 最大重试次数
    RETRY_DELAY = float(os.getenv('RETRY_DELAY', 0.5))  # 重试延迟
    
    # Flask应用配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))  # 会话超时时间（秒）
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'AI-IT支持系统')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    @classmethod
    def get_ai_config(cls, model_name: str) -> dict:
        """获取指定AI模型的配置"""
        configs = {
            'openai': {
                'api_key': cls.OPENAI_API_KEY,
                'api_base': cls.OPENAI_API_BASE,
                'model': cls.OPENAI_MODEL,
                'enabled': cls.OPENAI_ENABLED,
                'timeout': cls.OPENAI_TIMEOUT
            },
            'claude': {
                'api_key': cls.CLAUDE_API_KEY,
                'api_base': cls.CLAUDE_API_BASE,
                'model': cls.CLAUDE_MODEL,
                'enabled': cls.CLAUDE_ENABLED,
                'timeout': cls.CLAUDE_TIMEOUT
            },
            'glm': {
                'api_key': cls.GLM_API_KEY,
                'api_base': cls.GLM_API_BASE,
                'model': cls.GLM_MODEL,
                'enabled': cls.GLM_ENABLED,
                'timeout': cls.GLM_TIMEOUT
            },
            'qwen': {
                'api_key': cls.QWEN_API_KEY,
                'api_base': cls.QWEN_API_BASE,
                'model': cls.QWEN_MODEL,
                'enabled': cls.QWEN_ENABLED,
                'timeout': cls.QWEN_TIMEOUT
            }
        }
        return configs.get(model_name, {})
    
    @classmethod
    def get_database_config(cls) -> dict:
        """获取数据库配置"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': True,
            'pool_name': 'ai_it_pool',
            'pool_size': cls.DB_POOL_SIZE,
            'pool_reset_session': True,
            'connection_timeout': cls.DB_CONNECTION_TIMEOUT,
            'get_warnings': True,
            'raise_on_warnings': False,
            'use_pure': False,  # 使用C扩展
            'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'
        }

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_NAME = os.getenv('DB_NAME', 'ai_support_db')
    DB_USER = os.getenv('DB_USER', 'ai_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_secure_password')
    
    # 应用配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_flask_secret_key')
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'XX科技有限公司')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # RAG参数
    TOP_K = int(os.getenv('TOP_K', 3))  # 检索知识条数
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.6))  # 转人工阈值
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    
    # 提示词模板
    PROMPT_TEMPLATE = """基于以下知识库信息，请回答用户的问题：

知识库信息：
{context}

用户问题：{question}

请提供清晰、准确的解决方案，如果信息不足，请说明需要更多信息。"""

    # 安全规则
    SENSITIVE_KEYWORDS = ["密码", "密钥", "管理员", "root", "admin", "password", "secret"]
    
    # 系统配置
    MAX_QUESTION_LENGTH = 500
    MAX_RESPONSE_LENGTH = 2000
    SESSION_TIMEOUT = 3600  # 1小时
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/ai-support.log')

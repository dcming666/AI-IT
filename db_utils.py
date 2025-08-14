import mysql.connector
from mysql.connector import Error
import numpy as np
import pickle
import logging
from datetime import datetime
from config import Config

# 配置日志
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            logger.info("数据库连接成功")
        except Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def create_tables(self):
        """创建必要的数据库表"""
        try:
            cursor = self.connection.cursor()
            
            # 创建交互日志表
            interactions_table = """
            CREATE TABLE IF NOT EXISTS interactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(40) NOT NULL,
                user_id VARCHAR(30) NOT NULL,
                question TEXT NOT NULL,
                ai_response TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence FLOAT DEFAULT 0.0,
                is_escalated BOOLEAN DEFAULT FALSE,
                ticket_id VARCHAR(20),
                feedback_score TINYINT,
                INDEX idx_timestamp (timestamp),
                INDEX idx_user (user_id),
                INDEX idx_session (session_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # 创建知识库表
            knowledge_table = """
            CREATE TABLE IF NOT EXISTS knowledge_base (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                category VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                use_count INT DEFAULT 0,
                FULLTEXT (title, content)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            # 创建工单表
            tickets_table = """
            CREATE TABLE IF NOT EXISTS tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticket_id VARCHAR(20) UNIQUE NOT NULL,
                session_id VARCHAR(40) NOT NULL,
                user_id VARCHAR(30) NOT NULL,
                question TEXT NOT NULL,
                status ENUM('pending', 'in_progress', 'resolved', 'closed') DEFAULT 'pending',
                assigned_to VARCHAR(30),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP NULL,
                priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
                INDEX idx_status (status),
                INDEX idx_user (user_id),
                INDEX idx_ticket_id (ticket_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(interactions_table)
            cursor.execute(knowledge_table)
            cursor.execute(tickets_table)
            
            self.connection.commit()
            logger.info("数据库表创建成功")
            
        except Error as e:
            logger.error(f"创建表失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def add_interaction(self, session_id, user_id, question, ai_response, confidence, is_escalated=False, ticket_id=None):
        """添加交互记录"""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO interactions (session_id, user_id, question, ai_response, confidence, is_escalated, ticket_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (session_id, user_id, question, ai_response, confidence, is_escalated, ticket_id))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            logger.error(f"添加交互记录失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def add_knowledge_item(self, title, content, category=None):
        """添加知识库条目"""
        try:
            cursor = self.connection.cursor()
            query = """
            INSERT INTO knowledge_base (title, content, category)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (title, content, category))
            knowledge_id = cursor.lastrowid
            self.connection.commit()
            
            # 生成并存储向量嵌入
            self.update_knowledge_embedding(knowledge_id, content)
            
            return knowledge_id
        except Error as e:
            logger.error(f"添加知识库条目失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def update_knowledge_embedding(self, knowledge_id, content):
        """更新知识库条目的向量嵌入"""
        try:
            from rag_engine import RAGEngine
            rag_engine = RAGEngine()
            embedding = rag_engine.generate_embedding(content)
            
            cursor = self.connection.cursor()
            query = "UPDATE knowledge_base SET embedding = %s WHERE id = %s"
            cursor.execute(query, (pickle.dumps(embedding), knowledge_id))
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"更新向量嵌入失败: {e}")
    
    def update_feedback(self, interaction_id, score):
        """更新交互记录的评分"""
        try:
            cursor = self.connection.cursor()
            query = "UPDATE interactions SET feedback_score = %s WHERE id = %s"
            cursor.execute(query, (score, interaction_id))
            self.connection.commit()
        except Error as e:
            logger.error(f"更新评分失败: {e}")
            raise
    
    def get_knowledge_list(self):
        """获取知识库列表"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT id, title, content, category, created_at FROM knowledge_base ORDER BY created_at DESC"
            cursor.execute(query)
            results = cursor.fetchall()
            
            knowledge_list = []
            for row in results:
                knowledge_list.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'category': row[3],
                    'created_at': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else ''
                })
            
            return knowledge_list
            
        except Error as e:
            logger.error(f"获取知识库列表失败: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def search_knowledge(self, query_embedding, top_k=3):
        """搜索相关知识库条目"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT id, title, content, embedding FROM knowledge_base"
            cursor.execute(query)
            results = cursor.fetchall()
            
            if not results:
                return []
            
            # 计算相似度
            similarities = []
            for row in results:
                knowledge_id, title, content, embedding_blob = row
                if embedding_blob:
                    stored_embedding = pickle.loads(embedding_blob)
                    similarity = self.calculate_cosine_similarity(query_embedding, stored_embedding)
                    similarities.append((knowledge_id, title, content, similarity))
            
            # 按相似度排序并返回top_k
            similarities.sort(key=lambda x: x[3], reverse=True)
            return similarities[:top_k]
            
        except Error as e:
            logger.error(f"搜索知识库失败: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def calculate_cosine_similarity(self, vec1, vec2):
        """计算两个向量的余弦相似度"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return 0.0
    
    def create_ticket(self, session_id, user_id, question):
        """创建工单"""
        try:
            cursor = self.connection.cursor()
            ticket_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            query = """
            INSERT INTO tickets (ticket_id, session_id, user_id, question)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (ticket_id, session_id, user_id, question))
            self.connection.commit()
            
            return ticket_id
        except Error as e:
            logger.error(f"创建工单失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def get_interaction_stats(self):
        """获取交互统计信息"""
        try:
            cursor = self.connection.cursor()
            
            # 总交互数
            cursor.execute("SELECT COUNT(*) FROM interactions")
            total_interactions = cursor.fetchone()[0]
            
            # 转人工数
            cursor.execute("SELECT COUNT(*) FROM interactions WHERE ticket_id IS NOT NULL")
            escalated_count = cursor.fetchone()[0]
            
            # 平均置信度
            cursor.execute("SELECT AVG(confidence) FROM interactions WHERE confidence > 0")
            avg_confidence = cursor.fetchone()[0] or 0.0
            
            # 知识库条目数
            cursor.execute("SELECT COUNT(*) FROM knowledge_base")
            knowledge_count = cursor.fetchone()[0]
            
            return {
                'total_interactions': total_interactions,
                'escalated_count': escalated_count,
                'avg_confidence': round(avg_confidence, 2),
                'knowledge_count': knowledge_count
            }
            
        except Error as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
        finally:
            if cursor:
                cursor.close()
    
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("数据库连接已关闭")

# 全局数据库管理器实例
db_manager = DatabaseManager()

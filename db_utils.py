import mysql.connector
from mysql.connector import Error, pooling
import numpy as np
import pickle
import logging
from datetime import datetime
from config import Config
import threading
import time

# 配置日志
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection_pool = None
        self._lock = threading.Lock()
        self.connect()
    
    def connect(self):
        """建立数据库连接池"""
        try:
            if self.connection_pool:
                try:
                    self.connection_pool.close()
                except:
                    pass
            
            # 使用连接池配置
            pool_config = {
                'host': Config.DB_HOST,
                'port': Config.DB_PORT,
                'database': Config.DB_NAME,
                'user': Config.DB_USER,
                'password': Config.DB_PASSWORD,
                'charset': 'utf8mb4',
                'collation': 'utf8mb4_unicode_ci',
                'autocommit': True,
                'pool_name': 'ai_it_pool',
                'pool_size': 5,
                'pool_reset_session': True,
                'connection_timeout': 60,
                'get_warnings': True,
                'raise_on_warnings': False,
                'use_pure': False,  # 使用C扩展
                'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'
            }
            
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**pool_config)
            logger.info("数据库连接池创建成功")
            
        except Error as e:
            logger.error(f"数据库连接池创建失败: {e}")
            raise
    
    def get_connection(self):
        """从连接池获取连接"""
        try:
            if not self.connection_pool:
                self.connect()
            
            connection = self.connection_pool.get_connection()
            
            # 测试连接是否有效
            try:
                connection.ping(reconnect=True, attempts=3, delay=0.5)
            except Exception as e:
                logger.warning(f"连接测试失败，关闭并重新获取: {e}")
                try:
                    connection.close()
                except:
                    pass
                connection = self.connection_pool.get_connection()
            
            return connection
            
        except Error as e:
            logger.error(f"获取数据库连接失败: {e}")
            # 尝试重新创建连接池
            try:
                self.connect()
                return self.connection_pool.get_connection()
            except:
                raise
    
    def execute_query(self, query, params=None, fetch=True, dictionary=False, max_retries=3):
        """执行数据库查询的统一方法"""
        connection = None
        cursor = None
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # 获取连接
                connection = self.get_connection()
                cursor = connection.cursor(dictionary=dictionary)
                
                # 执行查询
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    connection.commit()
                    return cursor.rowcount
                    
            except Error as e:
                retry_count += 1
                logger.error(f"数据库查询执行失败 (尝试 {retry_count}/{max_retries}): {e}")
                
                # 清理资源
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass
                if connection:
                    try:
                        connection.close()
                    except:
                        pass
                
                if retry_count >= max_retries:
                    raise
                else:
                    # 等待后重试
                    time.sleep(0.5)
                    continue
                    
            except Exception as e:
                logger.error(f"数据库查询执行出现未知错误: {e}")
                raise
            finally:
                # 清理资源
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass
                if connection:
                    try:
                        connection.close()
                    except:
                        pass
    
    def create_tables(self):
        """创建必要的数据库表"""
        try:
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
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
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
            
            self.execute_query(interactions_table, fetch=False)
            self.execute_query(knowledge_table, fetch=False)
            self.execute_query(tickets_table, fetch=False)
            
            logger.info("数据库表创建成功")
            
        except Exception as e:
            logger.error(f"创建数据库表失败: {e}")
            raise
    
    def add_interaction(self, session_id, user_id, question, ai_response, confidence, is_escalated=False, ticket_id=None):
        """添加交互记录"""
        connection = None
        cursor = None
        try:
            # 获取连接
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # 插入交互记录
            query = """
            INSERT INTO interactions (session_id, user_id, question, ai_response, confidence, is_escalated, ticket_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (session_id, user_id, question, ai_response, confidence, is_escalated, ticket_id)
            cursor.execute(query, params)
            
            # 获取插入的ID
            interaction_id = cursor.lastrowid
            
            # 提交事务
            connection.commit()
            
            return interaction_id
            
        except Error as e:
            logger.error(f"添加交互记录失败: {e}")
            if connection:
                try:
                    connection.rollback()
                except:
                    pass
            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if connection:
                try:
                    connection.close()
                except:
                    pass
    
    def update_knowledge_embedding(self, knowledge_id, content):
        """更新知识库条目的向量嵌入"""
        try:
            from enhanced_rag_engine import EnhancedRAGEngine
            rag_engine = EnhancedRAGEngine()
            embedding = rag_engine.generate_embedding(content)
            
            if embedding:
                query = "UPDATE knowledge_base SET embedding = %s WHERE id = %s"
                params = (pickle.dumps(embedding), knowledge_id)
                self.execute_query(query, params, fetch=False)
                logger.info(f"知识条目 {knowledge_id} 的向量嵌入更新成功")
            else:
                logger.warning(f"无法为知识条目 {knowledge_id} 生成向量嵌入")
                
        except Exception as e:
            logger.error(f"更新向量嵌入失败: {e}")
    
    def update_feedback(self, interaction_id, score):
        """更新交互记录的评分"""
        try:
            query = "UPDATE interactions SET feedback_score = %s WHERE id = %s"
            params = (score, interaction_id)
            self.execute_query(query, params, fetch=False)
        except Error as e:
            logger.error(f"更新评分失败: {e}")
            raise
    
    def get_knowledge_list(self):
        """获取知识库列表"""
        try:
            query = "SELECT id, title, content, category, created_at FROM knowledge_base ORDER BY created_at DESC"
            results = self.execute_query(query)
            
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
    
    def get_knowledge_count(self):
        """获取知识库条目数量"""
        try:
            query = "SELECT COUNT(*) FROM knowledge_base"
            count = self.execute_query(query)
            return count[0][0]
        except Exception as e:
            logger.error(f"获取知识库数量失败: {e}")
            return 0
    
    def get_interaction_by_id(self, interaction_id):
        """根据ID获取交互记录"""
        try:
            query = """
            SELECT id, session_id, user_id, question, ai_response, confidence, is_escalated, ticket_id, feedback_score, timestamp
            FROM interactions 
            WHERE id = %s
            """
            params = (interaction_id,)
            result = self.execute_query(query, params, dictionary=True)
            
            return result[0] if result else None
            
        except Error as e:
            logger.error(f"获取交互记录失败: {e}")
            return None
    
    def search_knowledge(self, query_embedding, top_k=3):
        """搜索相关知识库条目"""
        try:
            query = "SELECT id, title, content, embedding FROM knowledge_base"
            results = self.execute_query(query)
            
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
            ticket_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            query = """
            INSERT INTO tickets (ticket_id, session_id, user_id, question)
            VALUES (%s, %s, %s, %s)
            """
            params = (ticket_id, session_id, user_id, question)
            self.execute_query(query, params)
            
            return ticket_id
        except Error as e:
            logger.error(f"创建工单失败: {e}")
            raise
    
    def get_interaction_stats(self):
        """获取交互统计信息"""
        try:
            
            # 总交互数
            total_interactions = self.execute_query("SELECT COUNT(*) FROM interactions")
            total_interactions = total_interactions[0][0]
            
            # 转人工数
            escalated_count = self.execute_query("SELECT COUNT(*) FROM interactions WHERE ticket_id IS NOT NULL")
            escalated_count = escalated_count[0][0]
            
            # 平均置信度
            avg_confidence = self.execute_query("SELECT AVG(confidence) FROM interactions WHERE confidence > 0")
            avg_confidence = avg_confidence[0][0] if avg_confidence else 0.0
            
            # 知识库条目数
            knowledge_count = self.execute_query("SELECT COUNT(*) FROM knowledge_base")
            knowledge_count = knowledge_count[0][0]
            
            return {
                'total_interactions': total_interactions,
                'escalated_count': escalated_count,
                'avg_confidence': round(avg_confidence, 2),
                'knowledge_count': knowledge_count
            }
            
        except Error as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if self.connection_pool:
            try:
                self.connection_pool.closeall()
                logger.info("数据库连接池已关闭")
            except:
                pass

    # 管理后台相关方法
    
    def get_admin_stats(self):
        """获取管理后台统计信息"""
        try:
            
            # 知识条目总数
            total_knowledge = self.execute_query("SELECT COUNT(*) FROM knowledge_base")
            total_knowledge = total_knowledge[0][0]
            
            # 分类总数
            total_categories = self.execute_query("SELECT COUNT(DISTINCT category) FROM knowledge_base")
            total_categories = total_categories[0][0]
            
            # 最后更新时间
            last_updated = self.execute_query("SELECT MAX(updated_at) FROM knowledge_base")
            last_updated = last_updated[0][0]
            
            return {
                'total_knowledge': total_knowledge,
                'total_categories': total_categories,
                'last_updated': last_updated.strftime('%Y-%m-%d %H:%M:%S') if last_updated else '无'
            }
            
        except Error as e:
            logger.error(f"获取管理统计信息失败: {e}")
            return {}
    
    def get_knowledge_list_paginated(self, page=1, page_size=10, search='', category='', sort_by='updated'):
        """获取分页的知识库列表"""
        try:
            # 构建WHERE条件
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("(title LIKE %s OR content LIKE %s)")
                search_param = f"%{search}%"
                params.extend([search_param, search_param])
            
            if category:
                where_conditions.append("category = %s")
                params.append(category)
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # 构建ORDER BY
            order_by = "ORDER BY "
            if sort_by == 'title':
                order_by += "title ASC"
            elif sort_by == 'category':
                order_by += "category ASC, title ASC"
            else:  # updated
                order_by += "updated_at DESC, created_at DESC"
            
            # 获取总数
            count_query = f"SELECT COUNT(*) as count FROM knowledge_base{where_clause}"
            count_result = self.execute_query(count_query, params, dictionary=True)
            total = count_result[0]['count'] if count_result else 0
            
            # 计算分页
            offset = (page - 1) * page_size
            
            # 获取分页数据
            data_query = f"""
            SELECT id, title, category, content, tags, created_at, updated_at
            FROM knowledge_base{where_clause}
            {order_by}
            LIMIT %s OFFSET %s
            """
            data_params = params + [page_size, offset]
            items = self.execute_query(data_query, data_params, dictionary=True)
            
            return {
                'items': items,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
            
        except Error as e:
            logger.error(f"获取分页知识库列表失败: {e}")
            return {'items': [], 'total': 0, 'page': page, 'page_size': page_size, 'total_pages': 0}
    
    def add_knowledge(self, title, category, content, tags=''):
        """添加知识条目"""
        try:
            query = """
            INSERT INTO knowledge_base (title, category, content, tags, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            """
            params = (title, category, content, tags)
            self.execute_query(query, params, fetch=False)
            
            # 获取插入的ID
            result = self.execute_query("SELECT LAST_INSERT_ID() as id", dictionary=True)
            return result[0]['id'] if result else None
            
        except Error as e:
            logger.error(f"添加知识条目失败: {e}")
            raise
    
    def get_knowledge_by_id(self, knowledge_id):
        """根据ID获取知识条目"""
        try:
            query = "SELECT id, title, category, content, tags, created_at, updated_at FROM knowledge_base WHERE id = %s"
            params = (knowledge_id,)
            result = self.execute_query(query, params, dictionary=True)
            
            return result[0] if result else None
            
        except Error as e:
            logger.error(f"获取知识条目失败: {e}")
            return None
    
    def update_knowledge(self, knowledge_id, title, category, content, tags=''):
        """更新知识条目"""
        try:
            query = """
            UPDATE knowledge_base 
            SET title = %s, category = %s, content = %s, tags = %s, updated_at = NOW()
            WHERE id = %s
            """
            params = (title, category, content, tags, knowledge_id)
            row_count = self.execute_query(query, params, fetch=False)
            
            return row_count > 0
            
        except Error as e:
            logger.error(f"更新知识条目失败: {e}")
            raise
    
    def delete_knowledge(self, knowledge_id):
        """删除知识条目"""
        try:
            query = "DELETE FROM knowledge_base WHERE id = %s"
            params = (knowledge_id,)
            row_count = self.execute_query(query, params, fetch=False)
            
            return row_count > 0
            
        except Error as e:
            logger.error(f"删除知识条目失败: {e}")
            raise
    
    def import_knowledge_batch(self, knowledge_data):
        """批量导入知识库"""
        try:
            imported_count = 0
            
            for item in knowledge_data:
                title = item.get('title', '').strip()
                category = item.get('category', '').strip()
                content = item.get('content', '').strip()
                tags = item.get('tags', '').strip()
                
                if title and category and content:
                    query = """
                    INSERT INTO knowledge_base (title, category, content, tags, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                    """
                    params = (title, category, content, tags)
                    self.execute_query(query, params, fetch=False)
                    imported_count += 1
            
            return imported_count
            
        except Error as e:
            logger.error(f"批量导入知识库失败: {e}")
            raise
    
    def get_all_categories(self):
        """获取所有分类列表"""
        try:
            query = "SELECT DISTINCT category FROM knowledge_base ORDER BY category"
            results = self.execute_query(query)
            
            return [row[0] for row in results]
            
        except Error as e:
            logger.error(f"获取分类列表失败: {e}")
            return []

    def add_knowledge_item(self, title, content, category=None):
        """添加知识库条目"""
        try:
            query = """
            INSERT INTO knowledge_base (title, content, category)
            VALUES (%s, %s, %s)
            """
            params = (title, content, category)
            self.execute_query(query, params, fetch=False)
            
            # 获取插入的ID
            result = self.execute_query("SELECT LAST_INSERT_ID() as id", dictionary=True)
            knowledge_id = result[0]['id'] if result else None
            
            if knowledge_id:
                # 生成并存储向量嵌入
                self.update_knowledge_embedding(knowledge_id, content)
                logger.info(f"知识条目添加成功，ID: {knowledge_id}")
                return knowledge_id
            else:
                logger.error("无法获取新插入的知识条目ID")
                return None
                
        except Error as e:
            logger.error(f"添加知识库条目失败: {e}")
            raise

# 全局数据库管理器实例
db_manager = DatabaseManager()

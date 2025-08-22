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
            pool_config = Config.get_database_config()
            
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
            # 创建用户表
            users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(30) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_username (username)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
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
            
            self.execute_query(users_table, fetch=False)
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
            print(f"DEBUG: add_interaction开始，参数: session_id={session_id}, user_id={user_id}")
            
            # 获取连接
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # 插入交互记录
            query = """
            INSERT INTO interactions (session_id, user_id, question, ai_response, confidence, is_escalated, ticket_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (session_id, user_id, question, ai_response, confidence, is_escalated, ticket_id)
            print(f"DEBUG: 执行SQL: {query}")
            print(f"DEBUG: 参数: {params}")
            
            cursor.execute(query, params)
            
            # 获取插入的ID
            interaction_id = cursor.lastrowid
            print(f"DEBUG: 获取到lastrowid: {interaction_id}")
            
            # 提交事务
            connection.commit()
            print(f"DEBUG: 事务提交成功")
            
            return interaction_id
            
        except Error as e:
            print(f"DEBUG: 数据库错误: {e}")
            logger.error(f"添加交互记录失败: {e}")
            if connection:
                try:
                    connection.rollback()
                except:
                    pass
            raise
        except Exception as e:
            print(f"DEBUG: 其他错误: {e}")
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
    
    def update_consecutive_low_ratings(self, user_id, rating):
        """更新用户的连续低分计数"""
        try:
            if rating <= 3:  # 3星及以下为低分
                # 获取用户最近的交互记录
                query = """
                    SELECT consecutive_low_ratings 
                    FROM interactions 
                    WHERE user_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                result = self.execute_query(query, (user_id,))
                
                if result:
                    current_count = result[0][0] if result[0][0] else 0
                    new_count = current_count + 1
                else:
                    new_count = 1
                
                # 更新最新交互记录的连续低分计数
                update_query = """
                    UPDATE interactions 
                    SET consecutive_low_ratings = %s 
                    WHERE user_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                self.execute_query(update_query, (new_count, user_id), fetch=False)
                
                return new_count
            else:
                # 高分，重置连续低分计数
                reset_query = """
                    UPDATE interactions 
                    SET consecutive_low_ratings = 0 
                    WHERE user_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                """
                self.execute_query(reset_query, (user_id,), fetch=False)
                return 0
                
        except Exception as e:
            logger.error(f"更新连续低分计数失败: {e}")
            return 0
    
    def get_user_consecutive_low_ratings(self, user_id):
        """获取用户的连续低分次数"""
        try:
            query = """
                SELECT consecutive_low_ratings 
                FROM interactions 
                WHERE user_id = %s 
                ORDER BY timestamp DESC 
                LIMIT 1
            """
            result = self.execute_query(query, (user_id,))
            
            if result and result[0][0] is not None:
                return result[0][0]
            return 0
            
        except Exception as e:
            logger.error(f"获取连续低分计数失败: {e}")
            return 0
    
    def get_all_knowledge(self):
        """获取所有知识库内容"""
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
                    'created_at': row[4]
                })
            
            return knowledge_list
            
        except Error as e:
            logger.error(f"获取知识库列表失败: {e}")
            return []
    
    def search_knowledge_by_keyword(self, keyword):
        """根据关键词搜索知识库 - 只搜索标题，提高精准度"""
        try:
            # 只搜索标题，不搜索内容，确保更高的精准度
            query = """
            SELECT id, title, content, category, created_at 
            FROM knowledge_base 
            WHERE title LIKE %s
            ORDER BY created_at DESC
            """
            search_pattern = f'%{keyword}%'
            params = (search_pattern,)
            results = self.execute_query(query, params)
            
            knowledge_list = []
            for row in results:
                knowledge_list.append({
                    'id': row[0],
                    'title': row[1],
                    'content': row[2],
                    'category': row[3],
                    'created_at': row[4]
                })
            
            return knowledge_list
            
        except Error as e:
            logger.error(f"关键词搜索知识库失败: {e}")
            return []
    
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
                # 改进搜索逻辑：支持多个关键词搜索
                search_terms = search.strip().split()
                search_conditions = []
                search_params = []
                
                for term in search_terms:
                    if term.strip():  # 忽略空字符串
                        search_conditions.append("(title LIKE %s OR content LIKE %s OR tags LIKE %s)")
                        term_param = f"%{term.strip()}%"
                        search_params.extend([term_param, term_param, term_param])
                
                if search_conditions:
                    where_conditions.append(f"({' OR '.join(search_conditions)})")
                    params.extend(search_params)
            
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
            # 使用cursor来获取插入的ID
            connection = self.get_connection()
            cursor = connection.cursor()
            
            try:
                query = """
                INSERT INTO knowledge_base (title, category, content, tags, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                """
                params = (title, category, content, tags)
                cursor.execute(query, params)
                connection.commit()
                
                # 获取插入的ID
                knowledge_id = cursor.lastrowid
                
                # 自动生成向量嵌入
                if knowledge_id:
                    self._generate_embedding_for_knowledge(knowledge_id, content)
                
                # 自动提取和添加关键词
                if knowledge_id:
                    self._extract_and_add_keywords(knowledge_id, title, content)
                
                return knowledge_id
                
            finally:
                cursor.close()
                connection.close()
            
        except Error as e:
            logger.error(f"添加知识条目失败: {e}")
            raise
    
    def _generate_embedding_for_knowledge(self, knowledge_id, content):
        """为知识条目生成向量嵌入"""
        try:
            from enhanced_rag_engine import enhanced_rag_engine
            
            # 生成向量嵌入
            embedding = enhanced_rag_engine.generate_embedding(content)
            
            # 将向量嵌入存储到数据库
            import pickle
            embedding_blob = pickle.dumps(embedding)
            
            query = "UPDATE knowledge_base SET embedding = %s WHERE id = %s"
            params = (embedding_blob, knowledge_id)
            self.execute_query(query, params, fetch=False)
            
            logger.info(f"知识条目 {knowledge_id} 的向量嵌入生成成功")
            
        except Exception as e:
            logger.error(f"生成向量嵌入失败: {e}")
            # 不抛出异常，避免影响知识条目的添加
    
    def get_knowledge_by_id(self, knowledge_id):
        """根据ID获取知识条目"""
        try:
            query = "SELECT id, title, category, content, tags, embedding, created_at, updated_at FROM knowledge_base WHERE id = %s"
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
            
            # 重新生成向量嵌入
            if row_count > 0:
                self._generate_embedding_for_knowledge(knowledge_id, content)
                
                # 重新提取和添加关键词
                self._extract_and_add_keywords(knowledge_id, title, content)
            
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
                    # 使用add_knowledge方法，它会自动生成向量嵌入
                    knowledge_id = self.add_knowledge(title, category, content, tags)
                    if knowledge_id:
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

    def _extract_and_add_keywords(self, knowledge_id, title, content):
        """自动提取和添加关键词"""
        try:
            # 提取关键词
            extracted_keywords = self._extract_keywords_from_text(title + " " + content)
            
            if not extracted_keywords:
                return
            
            # 添加关键词到数据库并建立关联
            for keyword in extracted_keywords:
                self._add_keyword_to_knowledge(knowledge_id, keyword)
            
            logger.info(f"知识条目 {knowledge_id} 自动添加了 {len(extracted_keywords)} 个关键词: {extracted_keywords}")
            
        except Exception as e:
            logger.error(f"自动提取关键词失败: {e}")
            # 不抛出异常，避免影响知识条目的添加
    
    def _extract_keywords_from_text(self, text):
        """从文本中提取关键词"""
        try:
            # 获取所有关键词
            all_keywords = self.get_all_keywords()
            if not all_keywords:
                return []
            
            # 转换为小写进行匹配
            text_lower = text.lower()
            extracted_keywords = []
            
            # 检查每个关键词是否在文本中出现
            for keyword_info in all_keywords:
                keyword = keyword_info['keyword'].lower()
                if keyword in text_lower:
                    extracted_keywords.append(keyword_info['keyword'])
            
            # 限制关键词数量，避免过多
            return extracted_keywords[:10]
            
        except Exception as e:
            logger.error(f"提取关键词失败: {e}")
            return []
    
    def _add_keyword_to_knowledge(self, knowledge_id, keyword):
        """将关键词添加到知识条目"""
        try:
            # 首先检查关键词是否存在，不存在则创建
            keyword_id = self._get_or_create_keyword(keyword)
            if not keyword_id:
                return
            
            # 检查是否已经存在关联
            existing = self.execute_query(
                "SELECT id FROM knowledge_keywords WHERE knowledge_id = %s AND keyword_id = %s",
                (knowledge_id, keyword_id),
                dictionary=True
            )
            
            if existing:
                # 已存在关联，更新权重
                self.execute_query(
                    "UPDATE knowledge_keywords SET weight = weight + 0.1 WHERE knowledge_id = %s AND keyword_id = %s",
                    (knowledge_id, keyword_id),
                    fetch=False
                )
            else:
                # 创建新关联
                self.execute_query(
                    "INSERT INTO knowledge_keywords (knowledge_id, keyword_id, weight) VALUES (%s, %s, 1.0)",
                    (knowledge_id, keyword_id),
                    fetch=False
                )
            
            # 更新关键词频率
            self.execute_query(
                "UPDATE keywords SET frequency = frequency + 1 WHERE id = %s",
                (keyword_id,),
                fetch=False
            )
            
        except Exception as e:
            logger.error(f"添加关键词到知识条目失败: {e}")
    
    def _get_or_create_keyword(self, keyword):
        """获取或创建关键词"""
        try:
            # 检查关键词是否存在
            result = self.execute_query(
                "SELECT id FROM keywords WHERE keyword = %s",
                (keyword,),
                dictionary=True
            )
            
            if result:
                return result[0]['id']
            
            # 关键词不存在，创建新关键词
            self.execute_query(
                "INSERT INTO keywords (keyword, category) VALUES (%s, 'general')",
                (keyword,),
                fetch=False
            )
            
            # 获取新创建的关键词ID
            result = self.execute_query(
                "SELECT id FROM keywords WHERE keyword = %s",
                (keyword,),
                dictionary=True
            )
            
            return result[0]['id'] if result else None
            
        except Exception as e:
            logger.error(f"获取或创建关键词失败: {e}")
            return None
    
    def get_all_keywords(self):
        """获取所有关键词"""
        try:
            query = "SELECT id, keyword, category, frequency FROM keywords ORDER BY frequency DESC"
            return self.execute_query(query, dictionary=True)
        except Error as e:
            logger.error(f"获取关键词失败: {e}")
            return []
    
    def search_knowledge_by_keyword(self, keyword):
        """根据关键词搜索知识库 - 优化版本"""
        try:
            # 首先尝试关键词关联搜索
            query1 = """
            SELECT DISTINCT kb.id, kb.title, kb.content, kb.category, kb.tags
            FROM knowledge_base kb
            JOIN knowledge_keywords kk ON kb.id = kk.knowledge_id
            JOIN keywords k ON kk.keyword_id = k.id
            WHERE k.keyword LIKE %s AND kb.title LIKE %s
            ORDER BY kk.weight DESC, kb.created_at DESC
            """
            search_term = f"%{keyword}%"
            params1 = (search_term, search_term)
            results1 = self.execute_query(query1, params1, dictionary=True)
            
            if results1:
                return results1
            
            # 如果关键词关联搜索没有结果，尝试直接标题搜索
            query2 = """
            SELECT DISTINCT kb.id, kb.title, kb.content, kb.category, kb.tags
            FROM knowledge_base kb
            WHERE kb.title LIKE %s OR kb.content LIKE %s
            ORDER BY kb.created_at DESC
            """
            params2 = (search_term, search_term)
            results2 = self.execute_query(query2, params2, dictionary=True)
            
            return results2
            
        except Error as e:
            logger.error(f"关键词搜索失败: {e}")
            return []

    def find_interaction_by_content_and_time(self, question, timestamp, conversation_id=None):
        """根据问题内容和时间戳查找对应的交互记录"""
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            # 构建查询条件 - 使用更宽松的时间匹配
            query = """
                SELECT id, question, ai_response, confidence, feedback_score as rating, timestamp, user_id
                FROM interactions 
                WHERE question = %s 
                AND DATE(timestamp) = DATE(%s)
            """
            
            # 尝试多种时间格式解析
            timestamp_obj = None
            try:
                # 尝试解析ISO格式
                if 'T' in timestamp or 'Z' in timestamp:
                    timestamp_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    # 尝试解析GMT格式 (Thu, 21 Aug 2025 14:27:00 GMT)
                    timestamp_obj = datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S GMT')
            except ValueError as e:
                logger.warning(f"时间戳解析失败: {timestamp}, 错误: {e}")
                # 如果解析失败，使用当前时间作为备选
                timestamp_obj = datetime.now()
            
            params = [question, timestamp_obj]
            
            # 如果提供了对话ID，可以进一步过滤（如果有相关字段的话）
            if conversation_id:
                # 这里可以根据实际需要添加对话ID的过滤条件
                pass
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return result
            
        except Exception as e:
            print(f"查找交互记录失败: {e}")
            return None

    def get_interactions_list(self, page=1, page_size=10, search='', user_filter='', rating_filter='', sort_by='time'):
        """获取交互记录列表"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 构建查询条件
            where_conditions = []
            params = []
            
            if search:
                where_conditions.append("(i.question LIKE %s OR i.ai_response LIKE %s OR i.user_id LIKE %s)")
                params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
            
            if user_filter:
                where_conditions.append("i.user_id = %s")
                params.append(user_filter)
            
            if rating_filter:
                where_conditions.append("i.feedback_score = %s")
                params.append(int(rating_filter))
            
            where_clause = " WHERE " + " AND ".join(where_conditions) if where_conditions else ""
            
            # 构建排序
            order_clause = " ORDER BY "
            if sort_by == 'time':
                order_clause += "i.timestamp DESC"
            elif sort_by == 'rating':
                order_clause += "i.feedback_score DESC, i.timestamp DESC"
            elif sort_by == 'user':
                order_clause += "i.user_id, i.timestamp DESC"
            else:
                order_clause += "i.timestamp DESC"
            
            # 获取总数
            count_query = f"""
                SELECT COUNT(*) as total
                FROM interactions i
                {where_clause}
            """
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            
            # 计算分页
            offset = (page - 1) * page_size
            pages = (total + page_size - 1) // page_size
            
            # 获取数据
            query = f"""
                SELECT 
                    i.id,
                    i.question,
                    i.ai_response as answer,
                    i.feedback_score as rating,
                    i.timestamp as created_at,
                    i.user_id as username,
                    (SELECT COUNT(*) FROM revisions r WHERE r.interaction_id = i.id) as revision_count
                FROM interactions i
                {where_clause}
                {order_clause}
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, params + [page_size, offset])
            interactions = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                'interactions': interactions,
                'total': total,
                'page': page,
                'pages': pages
            }
            
        except Exception as e:
            logger.error(f"获取交互记录列表失败: {e}")
            raise

    def get_interaction_detail(self, interaction_id):
        """获取交互详情"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 获取交互基本信息
            query = """
                SELECT 
                    i.id,
                    i.question,
                    i.ai_response as answer,
                    i.feedback_score as rating,
                    i.timestamp as created_at,
                    i.user_id as username
                FROM interactions i
                WHERE i.id = %s
            """
            cursor.execute(query, [interaction_id])
            interaction = cursor.fetchone()
            
            if not interaction:
                cursor.close()
                conn.close()
                return None
            
            # 获取重新回答记录
            revision_query = """
                SELECT 
                    id,
                    feedback,
                    new_answer,
                    rating,
                    created_at
                FROM revisions
                WHERE interaction_id = %s
                ORDER BY created_at ASC
            """
            cursor.execute(revision_query, [interaction_id])
            revisions = cursor.fetchall()
            
            interaction['revisions'] = revisions
            interaction['revision_count'] = len(revisions)
            
            cursor.close()
            conn.close()
            
            return interaction
            
        except Exception as e:
            logger.error(f"获取交互详情失败: {e}")
            raise

    def table_exists(self, table_name):
        """检查表是否存在"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                AND table_name = %s
            """, [table_name])
            
            exists = cursor.fetchone()[0] > 0
            
            cursor.close()
            conn.close()
            
            return exists
            
        except Exception as e:
            logger.error(f"检查表 {table_name} 是否存在失败: {e}")
            return False

    def add_revision(self, interaction_id, feedback, new_answer, rating=None):
        """添加重新回答记录"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO revisions (interaction_id, feedback, new_answer, rating, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(query, [interaction_id, feedback, new_answer, rating])
            revision_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            return revision_id
        except Exception as e:
            logger.error(f"添加重新回答记录失败: {e}")
            raise

    # 权限管理相关方法
    def get_user_permissions(self, username):
        """获取用户权限"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM user_permissions WHERE username = %s"
            cursor.execute(query, [username])
            permissions = cursor.fetchone()
            cursor.close()
            conn.close()
            return permissions
        except Exception as e:
            logger.error(f"获取用户权限失败: {e}")
            return None

    def create_user_permissions(self, username, permissions_data, created_by=None):
        """创建用户权限"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO user_permissions 
                (username, can_access_admin, can_manage_permissions, can_view_interactions, can_export_data, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, [
                username,
                permissions_data.get('can_access_admin', False),
                permissions_data.get('can_manage_permissions', False),
                permissions_data.get('can_view_interactions', False),
                permissions_data.get('can_export_data', False),
                created_by
            ])
            permission_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            return permission_id
        except Exception as e:
            logger.error(f"创建用户权限失败: {e}")
            raise

    def update_user_permissions(self, username, permissions_data, updated_by=None):
        """更新用户权限"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = """
                UPDATE user_permissions 
                SET can_access_admin = %s, can_manage_permissions = %s, 
                    can_view_interactions = %s, can_export_data = %s, 
                    updated_by = %s, updated_at = NOW()
                WHERE username = %s
            """
            cursor.execute(query, [
                permissions_data.get('can_access_admin', False),
                permissions_data.get('can_manage_permissions', False),
                permissions_data.get('can_view_interactions', False),
                permissions_data.get('can_export_data', False),
                updated_by,
                username
            ])
            conn.commit()
            cursor.close()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"更新用户权限失败: {e}")
            raise

    def delete_user_permissions(self, username):
        """删除用户权限"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = "DELETE FROM user_permissions WHERE username = %s"
            cursor.execute(query, [username])
            conn.commit()
            cursor.close()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"删除用户权限失败: {e}")
            raise

    def get_all_permissions(self):
        """获取所有用户权限"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM user_permissions ORDER BY created_at DESC"
            cursor.execute(query)
            permissions = cursor.fetchall()
            cursor.close()
            conn.close()
            return permissions
        except Exception as e:
            logger.error(f"获取所有用户权限失败: {e}")
            return []

    def check_user_permission(self, username, permission_type):
        """检查用户是否有特定权限"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = f"SELECT {permission_type} FROM user_permissions WHERE username = %s"
            cursor.execute(query, [username])
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result[0] if result else False
        except Exception as e:
            logger.error(f"检查用户权限失败: {e}")
            return False

    def get_all_users_with_permissions(self):
        """获取所有用户及其权限状态"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # 获取所有用户
            query = """
                SELECT u.username, u.email, u.created_at,
                       CASE WHEN up.username IS NOT NULL THEN 1 ELSE 0 END as has_permissions
                FROM users u
                LEFT JOIN user_permissions up ON u.username = up.username
                ORDER BY u.created_at DESC
            """
            cursor.execute(query)
            users = cursor.fetchall()
            
            cursor.close()
            conn.close()
            return users
        except Exception as e:
            logger.error(f"获取所有用户失败: {e}")
            return []

    def get_users_list(self):
        """获取用户列表"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT DISTINCT user_id as username
                FROM interactions
                WHERE user_id IS NOT NULL AND user_id != ''
                ORDER BY user_id
            """
            cursor.execute(query)
            users = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return users
            
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            raise

# 全局数据库管理器实例
db_manager = DatabaseManager()

# 添加用户管理功能
def create_user(self, username, password):
    """创建新用户"""
    try:
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        params = (username, password)
        
        self.execute_query(query, params)
        return True
        
    except Error as e:
        logger.error(f"创建用户失败: {e}")
        return False

def get_user_by_username(self, username):
    """根据用户名获取用户信息"""
    try:
        query = "SELECT id, username, password FROM users WHERE username = %s"
        params = (username,)
        
        result = self.execute_query(query, params, dictionary=True)
        return result[0] if result else None
        
    except Error as e:
        logger.error(f"获取用户信息失败: {e}")
        return None

def check_user_exists(self, username):
    """检查用户是否存在"""
    try:
        query = "SELECT COUNT(*) as count FROM users WHERE username = %s"
        params = (username,)
        
        result = self.execute_query(query, params, dictionary=True)
        return result[0]['count'] > 0 if result else False
        
    except Error as e:
        logger.error(f"检查用户是否存在失败: {e}")
        return False

# 将用户管理方法添加到DatabaseManager类
DatabaseManager.create_user = create_user
DatabaseManager.get_user_by_username = get_user_by_username
DatabaseManager.check_user_exists = check_user_exists

# 添加对话记忆相关方法
def create_conversation(self, user_id, session_id=None, topic=None):
    """创建新的对话会话"""
    try:
        conversation_id = f"conv_{int(time.time())}_{user_id}"
        query = """
            INSERT INTO conversations (conversation_id, user_id, session_id, topic, start_time, last_activity)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
        """
        params = (conversation_id, user_id, session_id, topic)
        
        self.execute_query(query, params)
        return conversation_id
        
    except Exception as e:
        logger.error(f"创建对话会话失败: {e}")
        return None

def get_active_conversation(self, user_id, session_id=None):
    """获取用户的活跃对话会话"""
    try:
        query = """
            SELECT * FROM conversations 
            WHERE user_id = %s AND status = 'active'
            ORDER BY last_activity DESC 
            LIMIT 1
        """
        params = (user_id,)
        
        result = self.execute_query(query, params, dictionary=True)
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"获取活跃对话会话失败: {e}")
        return None

def add_conversation_message(self, conversation_id, user_id, message_type, content, context_tokens=None, relevance_score=0.0, parent_message_id=None):
    """添加对话消息"""
    try:
        query = """
            INSERT INTO conversation_messages 
            (conversation_id, user_id, message_type, content, context_tokens, relevance_score, parent_message_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (conversation_id, user_id, message_type, content, context_tokens, relevance_score, parent_message_id)
        
        message_id = self.execute_query(query, params)
        
        # 更新会话的最后活跃时间
        self.update_conversation_activity(conversation_id)
        
        return message_id
        
    except Exception as e:
        logger.error(f"添加对话消息失败: {e}")
        return None

def update_conversation_activity(self, conversation_id):
    """更新会话的最后活跃时间"""
    try:
        query = """
            UPDATE conversations 
            SET last_activity = NOW() 
            WHERE conversation_id = %s
        """
        params = (conversation_id,)
        
        self.execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"更新会话活跃时间失败: {e}")
        return False

def close_conversation(self, conversation_id):
    """关闭对话会话"""
    try:
        query = """
            UPDATE conversations 
            SET status = 'closed', last_activity = NOW() 
            WHERE conversation_id = %s
        """
        params = (conversation_id,)
        
        self.execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"关闭对话会话失败: {e}")
        return False

def get_user_conversation_history(self, user_id, limit=20):
    """获取用户的对话历史"""
    try:
        query = """
            SELECT c.*, 
                   COUNT(cm.id) as message_count,
                   MAX(cm.timestamp) as last_message_time
            FROM conversations c
            LEFT JOIN conversation_messages cm ON c.conversation_id = cm.conversation_id
            WHERE c.user_id = %s
            GROUP BY c.id
            ORDER BY c.last_activity DESC
            LIMIT %s
        """
        params = (user_id, limit)
        
        result = self.execute_query(query, params, dictionary=True)
        return result if result else []
        
    except Exception as e:
        logger.error(f"获取用户对话历史失败: {e}")
        return []

def detect_conversation_topic(self, messages):
    """检测对话主题"""
    try:
        if not messages:
            return "一般咨询"
        
        # 简单的主题检测逻辑
        content = " ".join([msg['content'] for msg in messages])
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['鼠标', '键盘', '打印机', '显示器']):
            return "硬件问题"
        elif any(word in content_lower for word in ['软件', '安装', '卸载', '程序']):
            return "软件问题"
        elif any(word in content_lower for word in ['网络', 'wifi', '连接', '上网']):
            return "网络问题"
        elif any(word in content_lower for word in ['密码', '登录', '账户', '权限']):
            return "账户管理"
        elif any(word in content_lower for word in ['病毒', '安全', '杀毒', '防护']):
            return "安全问题"
        else:
            return "一般咨询"
            
    except Exception as e:
        logger.error(f"检测对话主题失败: {e}")
        return "一般咨询"

def get_or_create_user_preferences(self, user_id):
    """获取或创建用户对话偏好"""
    try:
        # 先尝试获取现有偏好
        query = "SELECT * FROM user_conversation_preferences WHERE user_id = %s"
        params = (user_id,)
        
        result = self.execute_query(query, params, dictionary=True)
        
        if result:
            return result[0]
        else:
            # 创建默认偏好
            query = """
                INSERT INTO user_conversation_preferences 
                (user_id, preferred_context_length, memory_enabled, auto_topic_detection)
                VALUES (%s, 5, TRUE, TRUE)
            """
            params = (user_id,)
            
            self.execute_query(query, params)
            
            # 返回创建的偏好
            return {
                'user_id': user_id,
                'preferred_context_length': 5,
                'memory_enabled': True,
                'auto_topic_detection': True
            }
            
    except Exception as e:
        logger.error(f"获取或创建用户偏好失败: {e}")
        return None

def update_conversation_topic(self, conversation_id, topic):
    """更新对话主题"""
    try:
        query = """
            UPDATE conversations 
            SET topic = %s
            WHERE conversation_id = %s
        """
        params = (topic, conversation_id)
        
        self.execute_query(query, params, fetch=False)
        logger.info(f"对话主题更新成功: {conversation_id} -> {topic}")
        return True
        
    except Exception as e:
        logger.error(f"更新对话主题失败: {e}")
        return False

def get_conversation_context(self, conversation_id, limit=5):
    """获取对话上下文（最近的消息）"""
    try:
        query = """
            SELECT * FROM conversation_messages 
            WHERE conversation_id = %s 
            ORDER BY timestamp ASC 
            LIMIT %s
        """
        params = (conversation_id, limit)
        
        result = self.execute_query(query, params, dictionary=True)
        # 直接返回，因为已经按时间正序排列
        return result if result else []
        
    except Exception as e:
        logger.error(f"获取对话上下文失败: {e}")
        return []

def update_conversation_activity(self, conversation_id):
    """更新会话的最后活跃时间"""
    try:
        query = """
            UPDATE conversations 
            SET last_activity = NOW() 
            WHERE conversation_id = %s
        """
        params = (conversation_id,)
        
        self.execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"更新会话活跃时间失败: {e}")
        return False

def close_conversation(self, conversation_id):
    """关闭对话会话"""
    try:
        query = """
            UPDATE conversations 
            SET status = 'closed', last_activity = NOW() 
            WHERE conversation_id = %s
        """
        params = (conversation_id,)
        
        self.execute_query(query, params)
        return True
        
    except Exception as e:
        logger.error(f"关闭对话会话失败: {e}")
        return False

def get_user_conversation_history(self, user_id, limit=20):
    """获取用户的对话历史"""
    try:
        query = """
            SELECT c.*, 
                   COUNT(cm.id) as message_count,
                   MAX(cm.timestamp) as last_message_time
            FROM conversations c
            LEFT JOIN conversation_messages cm ON c.conversation_id = cm.conversation_id
            WHERE c.user_id = %s
            GROUP BY c.id
            ORDER BY c.last_activity DESC
            LIMIT %s
        """
        params = (user_id, limit)
        
        result = self.execute_query(query, params, dictionary=True)
        return result if result else []
        
    except Exception as e:
        logger.error(f"获取用户对话历史失败: {e}")
        return []

def detect_conversation_topic(self, messages):
    """检测对话主题"""
    try:
        if not messages:
            return "一般咨询"
        
        # 简单的主题检测逻辑
        content = " ".join([msg['content'] for msg in messages])
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['鼠标', '键盘', '打印机', '显示器']):
            return "硬件问题"
        elif any(word in content_lower for word in ['软件', '安装', '卸载', '程序']):
            return "软件问题"
        elif any(word in content_lower for word in ['网络', 'wifi', '连接', '上网']):
            return "网络问题"
        elif any(word in content_lower for word in ['密码', '登录', '账户', '权限']):
            return "账户管理"
        elif any(word in content_lower for word in ['病毒', '安全', '杀毒', '防护']):
            return "安全问题"
        else:
            return "一般咨询"
            
    except Exception as e:
        logger.error(f"检测对话主题失败: {e}")
        return "一般咨询"

def get_or_create_user_preferences(self, user_id):
    """获取或创建用户对话偏好"""
    try:
        # 先尝试获取现有偏好
        query = "SELECT * FROM user_conversation_preferences WHERE user_id = %s"
        params = (user_id,)
        
        result = self.execute_query(query, params, dictionary=True)
        
        if result:
            return result[0]
        else:
            # 创建默认偏好
            query = """
                INSERT INTO user_conversation_preferences 
                (user_id, preferred_context_length, memory_enabled, auto_topic_detection)
                VALUES (%s, 5, TRUE, TRUE)
            """
            params = (user_id,)
            
            self.execute_query(query, params)
            
            # 返回创建的偏好
            return {
                'user_id': user_id,
                'preferred_context_length': 5,
                'memory_enabled': True,
                'auto_topic_detection': True
            }
            
    except Exception as e:
        logger.error(f"获取或创建用户偏好失败: {e}")
        return None

def update_conversation_topic(self, conversation_id, topic):
    """更新对话主题"""
    try:
        query = """
            UPDATE conversations 
            SET topic = %s
            WHERE conversation_id = %s
        """
        params = (topic, conversation_id)
        
        self.execute_query(query, params, fetch=False)
        logger.info(f"对话主题更新成功: {conversation_id} -> {topic}")
        return True
        
    except Exception as e:
        logger.error(f"更新对话主题失败: {e}")
        return False

def delete_conversation(self, conversation_id):
    """删除对话及其所有消息"""
    try:
        # 首先删除对话中的所有消息
        query_messages = "DELETE FROM conversation_messages WHERE conversation_id = %s"
        self.execute_query(query_messages, (conversation_id,), fetch=False)
        
        # 然后删除对话本身
        query_conversation = "DELETE FROM conversations WHERE conversation_id = %s"
        self.execute_query(query_conversation, (conversation_id,), fetch=False)
        
        logger.info(f"对话 {conversation_id} 及其消息已删除")
        return True
        
    except Exception as e:
        logger.error(f"删除对话失败: {e}")
        return False

def get_conversation_by_id(self, conversation_id):
    """根据ID获取对话信息"""
    try:
        query = """
            SELECT conversation_id, user_id, topic, status, start_time, last_activity
            FROM conversations
            WHERE conversation_id = %s
        """
        params = (conversation_id,)
        
        result = self.execute_query(query, params, dictionary=True)
        return result[0] if result else None
        
    except Exception as e:
        logger.error(f"获取对话信息失败: {e}")
        return None

# 将对话记忆方法添加到DatabaseManager类
DatabaseManager.create_conversation = create_conversation
DatabaseManager.get_active_conversation = get_active_conversation
DatabaseManager.add_conversation_message = add_conversation_message
DatabaseManager.get_conversation_context = get_conversation_context
DatabaseManager.update_conversation_activity = update_conversation_activity
DatabaseManager.close_conversation = close_conversation
DatabaseManager.get_user_conversation_history = get_user_conversation_history
DatabaseManager.detect_conversation_topic = detect_conversation_topic
DatabaseManager.get_or_create_user_preferences = get_or_create_user_preferences
DatabaseManager.update_conversation_topic = update_conversation_topic
DatabaseManager.delete_conversation = delete_conversation
DatabaseManager.get_conversation_by_id = get_conversation_by_id

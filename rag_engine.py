import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from config import Config
from db_utils import db_manager

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        """初始化RAG引擎"""
        try:
            self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
            logger.info(f"RAG引擎初始化成功，使用模型: {Config.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"RAG引擎初始化失败: {e}")
            raise
    
    def generate_embedding(self, text):
        """生成文本的向量嵌入"""
        try:
            if not text or not text.strip():
                return np.zeros(384)  # 默认向量维度
            
            # 生成嵌入向量
            embedding = self.model.encode([text])[0]
            return embedding
        except Exception as e:
            logger.error(f"生成文本嵌入失败: {e}")
            return np.zeros(384)
    
    def search_knowledge(self, question, top_k=None):
        """搜索相关知识库条目"""
        if top_k is None:
            top_k = Config.TOP_K
        
        try:
            # 生成问题的向量嵌入
            question_embedding = self.generate_embedding(question)
            
            # 在知识库中搜索相似内容
            search_results = db_manager.search_knowledge(question_embedding, top_k)
            
            return search_results
        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            return []
    
    def generate_response(self, question, search_results):
        """基于搜索结果生成回答"""
        try:
            if not search_results:
                return {
                    'response': '抱歉，我在知识库中没有找到相关信息。建议您联系技术支持或提交工单。',
                    'confidence': 0.0,
                    'sources': []
                }
            
            # 构建上下文信息
            context = self._build_context(search_results)
            
            # 生成回答（这里使用简单的模板方法，实际项目中可以集成更高级的LLM）
            response = self._generate_simple_response(question, context)
            
            # 计算置信度
            confidence = self._calculate_confidence(search_results)
            
            # 提取来源信息
            sources = [result[1] for result in search_results]
            
            return {
                'response': response,
                'confidence': confidence,
                'sources': sources
            }
            
        except Exception as e:
            logger.error(f"生成回答失败: {e}")
            return {
                'response': '抱歉，生成回答时出现错误，请稍后重试。',
                'confidence': 0.0,
                'sources': []
            }
    
    def _build_context(self, search_results):
        """构建上下文信息"""
        context_parts = []
        for i, (knowledge_id, title, content, similarity) in enumerate(search_results, 1):
            context_parts.append(f"{i}. {title}\n{content[:200]}...")
        
        return "\n\n".join(context_parts)
    
    def _generate_simple_response(self, question, context):
        """生成简单回答（模板方法）"""
        # 这里使用配置的提示词模板
        response = Config.PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        
        # 简化回答，移除提示词部分
        if "基于以下知识库信息" in response:
            # 提取实际回答部分
            lines = response.split('\n')
            answer_lines = []
            capture = False
            
            for line in lines:
                if "用户问题：" in line:
                    break
                if capture:
                    answer_lines.append(line)
                if "请提供清晰、准确的解决方案" in line:
                    capture = True
            
            if answer_lines:
                response = '\n'.join(answer_lines).strip()
        
        return response
    
    def _calculate_confidence(self, search_results):
        """计算回答的置信度"""
        if not search_results:
            return 0.0
        
        # 基于相似度计算置信度
        similarities = [result[3] for result in search_results]
        max_similarity = max(similarities)
        
        # 如果最高相似度很高，置信度也高
        if max_similarity > 0.8:
            confidence = 0.9
        elif max_similarity > 0.6:
            confidence = 0.7
        elif max_similarity > 0.4:
            confidence = 0.5
        else:
            confidence = 0.3
        
        # 考虑搜索结果数量
        if len(search_results) >= 2:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def should_escalate(self, confidence):
        """判断是否需要转人工"""
        return confidence < Config.CONFIDENCE_THRESHOLD
    
    def process_question(self, question, session_id, user_id):
        """处理用户问题的完整流程"""
        try:
            # 1. 搜索知识库
            search_results = self.search_knowledge(question)
            
            # 2. 生成回答
            response_data = self.generate_response(question, search_results)
            
            # 3. 判断是否需要转人工
            should_escalate = self.should_escalate(response_data['confidence'])
            ticket_id = None
            
            if should_escalate:
                # 创建工单
                ticket_id = db_manager.create_ticket(session_id, user_id, question)
                response_data['response'] += f"\n\n由于置信度较低({response_data['confidence']:.2f})，已为您创建工单 {ticket_id}，技术人员将尽快联系您。"
            
            # 4. 记录交互
            db_manager.add_interaction(
                session_id=session_id,
                user_id=user_id,
                question=question,
                ai_response=response_data['response'],
                confidence=response_data['confidence'],
                is_escalated=should_escalate,
                ticket_id=ticket_id
            )
            
            # 5. 返回结果
            return {
                'response': response_data['response'],
                'confidence': response_data['confidence'],
                'sources': response_data['sources'],
                'ticket_id': ticket_id,
                'escalated': should_escalate
            }
            
        except Exception as e:
            logger.error(f"处理问题失败: {e}")
            return {
                'response': '抱歉，处理您的问题时出现错误，请稍后重试或联系技术支持。',
                'confidence': 0.0,
                'sources': [],
                'ticket_id': None,
                'escalated': False
            }

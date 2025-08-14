#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版RAG引擎 - 集成AI大模型API
"""

import os
import logging
import requests
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class EnhancedRAGEngine:
    def __init__(self):
        """初始化增强版RAG引擎"""
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # AI模型配置
        self.ai_model_config = {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'api_base': os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1'),
                'model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                'enabled': os.getenv('OPENAI_ENABLED', 'false').lower() == 'true'
            },
            'claude': {
                'api_key': os.getenv('CLAUDE_API_KEY'),
                'api_base': os.getenv('CLAUDE_API_BASE', 'https://api.anthropic.com'),
                'model': os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
                'enabled': os.getenv('CLAUDE_ENABLED', 'false').lower() == 'true'
            },
            'glm': {
                'api_key': os.getenv('GLM_API_KEY'),
                'api_base': 'https://open.bigmodel.cn/api/paas/v4',
                'model': os.getenv('GLM_MODEL', 'glm-4'),
                'enabled': os.getenv('GLM_ENABLED', 'false').lower() == 'true'
            },
            'qwen': {
                'api_key': os.getenv('QWEN_API_KEY'),
                'api_base': 'https://dashscope.aliyuncs.com/api/v1',  # 强制使用正确域名
                'model': os.getenv('QWEN_MODEL', 'qwen-plus'),
                'enabled': os.getenv('QWEN_ENABLED', 'false').lower() == 'true'
            }
        }
        
        # 选择启用的AI模型
        self.active_ai_model = self._get_active_ai_model()
        if self.active_ai_model:
            logger.info(f"AI大模型已启用: {self.active_ai_model}")
        else:
            logger.info("AI大模型未启用，将使用基础RAG模式")
    
    def _get_active_ai_model(self) -> str:
        """获取启用的AI模型"""
        for model_name, config in self.ai_model_config.items():
            if config['enabled'] and config.get('api_key'):
                return model_name
        return None
    
    def generate_embedding(self, text: str) -> List[float]:
        """生成文本向量嵌入"""
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"生成向量嵌入失败: {e}")
            return []
    
    def search_knowledge(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索相关知识库条目"""
        try:
            from db_utils import db_manager
            
            # 生成问题向量
            question_embedding = self.generate_embedding(question)
            if not question_embedding:
                return []
            
            # 搜索知识库
            search_results = db_manager.search_knowledge(question_embedding, top_k)
            
            # 格式化结果
            formatted_results = []
            for result in search_results:
                knowledge_id, title, content, similarity = result
                formatted_results.append({
                    'id': knowledge_id,
                    'title': title,
                    'content': content,
                    'similarity': float(similarity)
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            return []
    
    def generate_ai_response(self, question: str, context: str = "") -> str:
        """使用AI大模型生成回答"""
        try:
            if not self.active_ai_model:
                return "AI大模型未启用"
            
            if self.active_ai_model == 'openai':
                return self._call_openai_api(question, context)
            elif self.active_ai_model == 'claude':
                return self._call_claude_api(question, context)
            elif self.active_ai_model == 'glm':
                return self._call_glm_api(question, context)
            elif self.active_ai_model == 'qwen':
                return self._call_qwen_api(question, context)
            else:
                return "不支持的AI模型"
                
        except Exception as e:
            logger.error(f"AI模型调用失败: {e}")
            return f"AI模型调用失败: {str(e)}"
    
    def _call_openai_api(self, question: str, context: str = "") -> str:
        """调用OpenAI API"""
        try:
            config = self.ai_model_config['openai']
            
            # 构建提示词
            if context:
                prompt = f"""基于以下知识库信息回答用户问题：

知识库信息：
{context}

用户问题：{question}

请提供准确、有用的回答。如果知识库信息不足，请说明需要更多信息。"""
            else:
                prompt = f"用户问题：{question}\n\n请提供准确、有用的IT技术支持回答。"
            
            # 调用API
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的IT技术支持助手，请用中文回答用户问题。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 1000,
                'temperature': 0.7
            }
            
            response = requests.post(
                f"{config['api_base']}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"OpenAI API调用失败: {response.status_code} - {response.text}")
                return f"OpenAI API调用失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"OpenAI API调用异常: {e}")
            return f"OpenAI API调用异常: {str(e)}"
    
    def _call_claude_api(self, question: str, context: str = "") -> str:
        """调用Claude API"""
        try:
            config = self.ai_model_config['claude']
            
            # 构建提示词
            if context:
                prompt = f"""基于以下知识库信息回答用户问题：

知识库信息：
{context}

用户问题：{question}

请提供准确、有用的回答。如果知识库信息不足，请说明需要更多信息。"""
            else:
                prompt = f"用户问题：{question}\n\n请提供准确、有用的IT技术支持回答。"
            
            # 调用API
            headers = {
                'x-api-key': config['api_key'],
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'max_tokens': 1000,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            }
            
            response = requests.post(
                f"{config['api_base']}/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text'].strip()
            else:
                logger.error(f"Claude API调用失败: {response.status_code} - {response.text}")
                return f"Claude API调用失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Claude API调用异常: {e}")
            return f"Claude API调用异常: {str(e)}"
    
    def _call_glm_api(self, question: str, context: str = "") -> str:
        """调用GLM API"""
        try:
            config = self.ai_model_config['glm']
            
            # 构建提示词
            if context:
                prompt = f"""基于以下知识库信息回答用户问题：

知识库信息：
{context}

用户问题：{question}

请提供准确、有用的回答。如果知识库信息不足，请说明需要更多信息。"""
            else:
                prompt = f"用户问题：{question}\n\n请提供准确、有用的IT技术支持回答。"
            
            # 调用API
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'input': {
                    'messages': [
                        {'role': 'user', 'content': prompt}
                    ]
                },
                'parameters': {
                    'max_tokens': 1000,
                    'temperature': 0.7
                }
            }
            
            response = requests.post(
                f"{config['api_base']}/api/paas/v4/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['output']['text'].strip()
            else:
                logger.error(f"GLM API调用失败: {response.status_code} - {response.text}")
                return f"GLM API调用失败: {response.status_code}"
                
        except Exception as e:
            logger.error(f"GLM API调用异常: {e}")
            return f"GLM API调用异常: {str(e)}"
    
    def _call_qwen_api(self, question: str, context: str = "") -> str:
        """调用通义千问API"""
        try:
            config = self.ai_model_config['qwen']
            
            # 构建提示词
            if context:
                prompt = f"""基于以下知识库信息回答用户问题：

知识库信息：
{context}

用户问题：{question}

请提供准确、有用的回答。如果知识库信息不足，请说明需要更多信息。"""
            else:
                prompt = f"用户问题：{question}\n\n请提供准确、有用的IT技术支持回答。"
            
            # 根据模型版本调整参数
            model_params = self._get_qwen_model_params(config['model'])
            
            # 调用API
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'input': {
                    'messages': [
                        {'role': 'system', 'content': '你是一个专业的IT技术支持助手，请用中文回答用户问题。'},
                        {'role': 'user', 'content': prompt}
                    ]
                },
                'parameters': model_params
            }
            
            # 使用正确的通义千问API端点
            api_url = f"{config['api_base']}/services/aigc/text-generation/generation"
            logger.info(f"调用通义千问API: {api_url}")
            logger.info(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"通义千问API成功返回: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                # 修复返回格式解析逻辑
                if 'output' in result and 'choices' in result['output'] and len(result['output']['choices']) > 0:
                    return result['output']['choices'][0]['message']['content'].strip()
                elif 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                elif 'output' in result and 'text' in result['output']:
                    return result['output']['text'].strip()
                else:
                    logger.error(f"通义千问API返回格式异常: {result}")
                    return "通义千问API返回格式异常"
            else:
                logger.error(f"通义千问API调用失败: {response.status_code}")
                logger.error(f"响应头: {dict(response.headers)}")
                logger.error(f"响应内容: {response.text}")
                return f"通义千问API调用失败: {response.status_code} - {response.text}"
                
        except Exception as e:
            logger.error(f"通义千问API调用异常: {e}")
            return f"通义千问API调用异常: {str(e)}"
    
    def _get_qwen_model_params(self, model: str) -> dict:
        """根据通义千问模型版本获取合适的参数"""
        # 通义千问API的标准参数格式
        base_params = {
            'temperature': 0.7,
            'top_p': 0.9,
            'result_format': 'message'
        }
        
        if model == 'qwen-turbo':
            # 快速版本，适合日常对话
            return {
                **base_params,
                'max_tokens': 1500
            }
        elif model == 'qwen-plus':
            # 平衡版本，适合一般任务
            return {
                **base_params,
                'max_tokens': 2000
            }
        elif model == 'qwen-max':
            # 最强版本，适合复杂任务
            return {
                **base_params,
                'max_tokens': 3000,
                'temperature': 0.6  # 稍微保守一些
            }
        elif model == 'qwen-max-longcontext':
            # 长上下文版本，适合深度分析
            return {
                **base_params,
                'max_tokens': 6000,
                'temperature': 0.5  # 更保守，确保准确性
            }
        else:
            # 默认参数
            return {
                **base_params,
                'max_tokens': 2000
            }
    
    def process_question(self, question: str, session_id: str, user_id: str = "anonymous") -> Dict[str, Any]:
        """处理用户问题 - 增强版"""
        try:
            # 1. 搜索知识库
            knowledge_results = self.search_knowledge(question)
            
            # 2. 构建上下文
            context = self._build_context(knowledge_results)
            
            # 3. 计算置信度
            confidence = self._calculate_confidence(knowledge_results)
            
            # 4. 生成回答
            if confidence >= 0.7:
                # 高置信度：使用AI模型生成回答
                if self.active_ai_model:
                    answer = self.generate_ai_response(question, context)
                    answer_type = "ai_generated"
                else:
                    answer = self._generate_simple_response(question, context)
                    answer_type = "knowledge_based"
            else:
                # 低置信度：使用AI模型尝试回答
                if self.active_ai_model:
                    answer = self.generate_ai_response(question, context)
                    answer_type = "ai_generated_low_confidence"
                else:
                    answer = self._generate_simple_response(question, context)
                    answer_type = "knowledge_based_low_confidence"
            
            # 5. 记录交互
            try:
                from db_utils import db_manager
                db_manager.add_interaction(
                    session_id=session_id,
                    user_id=user_id,
                    question=question,
                    ai_response=answer,
                    confidence=confidence,
                    is_escalated=(confidence < 0.7)
                )
            except Exception as e:
                logger.error(f"记录交互失败: {e}")
            
            # 检查是否需要创建工单
            ticket_id = None
            escalated = False
            if confidence < 0.7:
                escalated = True
                try:
                    from db_utils import db_manager
                    ticket_id = db_manager.create_ticket(session_id, user_id, question)
                    answer += f"\n\n由于置信度较低({confidence:.2%})，已为您创建工单 {ticket_id}，技术人员将尽快联系您。"
                except Exception as e:
                    logger.error(f"创建工单失败: {e}")
                    answer += f"\n\n由于置信度较低({confidence:.2%})，建议联系技术支持获取帮助。"
            
            return {
                'answer': answer,
                'confidence': confidence,
                'sources': [item['title'] for item in knowledge_results],
                'answer_type': answer_type,
                'knowledge_count': len(knowledge_results),
                'ticket_id': ticket_id,
                'escalated': escalated
            }
            
        except Exception as e:
            logger.error(f"处理问题失败: {e}")
            return {
                'answer': f"抱歉，处理您的问题时出现错误：{str(e)}",
                'confidence': 0.0,
                'sources': [],
                'answer_type': 'error',
                'knowledge_count': 0
            }
    
    def _build_context(self, knowledge_results: List[Dict[str, Any]]) -> str:
        """构建知识库上下文"""
        if not knowledge_results:
            return ""
        
        context_parts = []
        for i, result in enumerate(knowledge_results, 1):
            context_parts.append(f"{i}. {result['title']}\n{result['content']}")
        
        return "\n\n".join(context_parts)
    
    def _calculate_confidence(self, knowledge_results: List[Dict[str, Any]]) -> float:
        """计算置信度"""
        if not knowledge_results:
            return 0.0
        
        # 基于相似度和结果数量计算置信度
        max_similarity = max(result['similarity'] for result in knowledge_results)
        result_count_factor = min(len(knowledge_results) / 3.0, 1.0)  # 最多3个结果
        
        confidence = (max_similarity * 0.7 + result_count_factor * 0.3)
        return min(confidence, 1.0)
    
    def _generate_simple_response(self, question: str, context: str) -> str:
        """生成简单回答（备用方案）"""
        if not context:
            return "抱歉，我在知识库中没有找到相关信息。请尝试重新描述您的问题，或联系技术支持获取帮助。"
        
        return f"""基于以下知识库信息回答您的问题：

{context}

如果您需要更详细的帮助，请提供更多具体信息。"""

# 全局增强版RAG引擎实例
enhanced_rag_engine = EnhancedRAGEngine()

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
                logger.warning("无法生成问题向量嵌入")
                return []
            
            # 搜索知识库
            search_results = db_manager.search_knowledge(question_embedding, top_k)
            
            if not search_results:
                logger.info("知识库中没有找到相关内容")
                return []
            
            # 格式化结果
            formatted_results = []
            for result in search_results:
                if len(result) >= 4:
                    knowledge_id, title, content, similarity = result
                    formatted_results.append({
                        'id': knowledge_id,
                        'title': title,
                        'content': content,
                        'similarity': float(similarity)
                    })
                else:
                    logger.warning(f"搜索结果格式不正确: {result}")
            
            logger.info(f"找到 {len(formatted_results)} 条相关知识库条目")
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
                        {'role': 'system', 'content': '你是一个专业的IT技术支持助手。请使用Markdown格式进行排版，例如使用标题、列表、加粗等，使回答更清晰易读。请用中文回答用户问题。'},
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
    
    def process_question(self, question, session_id=None, user_id=None, feedback_score=None):
        """处理用户问题，实现知识库优先的智能回复策略"""
        try:
            # 如果有满意度反馈，优先使用改进的回复策略
            if feedback_score is not None and feedback_score <= 3:
                logger.info(f"检测到低满意度反馈({feedback_score}星)，使用改进回复策略")
                return self._generate_improved_response_with_context(question, feedback_score)
            
            # 1. 首先在知识库中搜索相关答案
            knowledge_results = self.search_knowledge(question)
            knowledge_answer = None
            knowledge_sources = []
            
            if knowledge_results and len(knowledge_results) > 0:
                # 计算知识库答案的置信度
                knowledge_confidence = max(result['similarity'] for result in knowledge_results)
                
                # 如果知识库答案置信度足够高（>0.7），直接使用知识库答案
                if knowledge_confidence > 0.7:
                    best_knowledge = max(knowledge_results, key=lambda x: x['similarity'])
                    knowledge_answer = best_knowledge['content']
                    knowledge_sources = [best_knowledge['title']]
                    logger.info(f"使用知识库答案，置信度: {knowledge_confidence:.2f}")
                else:
                    # 置信度不够高，记录知识库信息供AI参考
                    knowledge_sources = [result['title'] for result in knowledge_results[:3]]
                    logger.info(f"知识库置信度不够高，供AI参考，置信度: {knowledge_confidence:.2f}")
            
            # 2. 根据情况决定回复策略
            if knowledge_answer and knowledge_confidence > 0.8:
                # 策略1：知识库答案非常准确，直接返回
                response = {
                    'answer': knowledge_answer,
                    'confidence': knowledge_confidence,
                    'sources': knowledge_sources,
                    'answer_type': 'knowledge_base',
                    'ai_answer': None,
                    'ticket_id': None,
                    'escalated': False
                }
                logger.info("使用纯知识库答案回复")
                
            elif knowledge_answer and knowledge_confidence > 0.6:
                # 策略2：知识库答案较好，但可能需要AI补充
                ai_answer = self._generate_ai_answer(question, knowledge_sources)
                response = {
                    'answer': f"**知识库答案：**\n{knowledge_answer}\n\n**AI补充说明：**\n{ai_answer}",
                    'confidence': knowledge_confidence,
                    'sources': knowledge_sources,
                    'answer_type': 'hybrid',
                    'ai_answer': ai_answer,
                    'ticket_id': None,
                    'escalated': False
                }
                logger.info("使用知识库+AI混合答案回复")
                
            else:
                # 策略3：知识库没有合适答案，使用AI生成
                ai_answer = self._generate_ai_answer(question, knowledge_sources)
                ai_confidence = self._calculate_ai_confidence(ai_answer, question)
                
                response = {
                    'answer': ai_answer,
                    'confidence': ai_confidence,
                    'sources': knowledge_sources if knowledge_sources else [],
                    'answer_type': 'ai_only',
                    'ai_answer': ai_answer,
                    'ticket_id': None,
                    'escalated': False
                }
                logger.info("使用纯AI答案回复")
            
            # 3. 检查是否需要转人工
            if response['confidence'] < 0.3:
                response['escalated'] = True
                response['ticket_id'] = self._create_ticket(question, session_id, user_id)
                logger.info(f"置信度过低，转人工处理，工单ID: {response['ticket_id']}")
            
            return response
            
        except Exception as e:
            logger.error(f"处理问题失败: {e}")
            # 发生错误时，尝试使用AI生成答案
            try:
                ai_answer = self._generate_ai_answer(question, [])
                return {
                    'answer': f"抱歉，处理您的问题时遇到了一些问题。以下是AI生成的答案：\n\n{ai_answer}",
                    'confidence': 0.1,
                    'sources': [],
                    'answer_type': 'error_fallback',
                    'ai_answer': ai_answer,
                    'ticket_id': None,
                    'escalated': False
                }
            except Exception as ai_error:
                logger.error(f"AI备用方案也失败: {ai_error}")
                return {
                    'answer': "抱歉，系统暂时无法处理您的问题。已为您创建工单，技术人员将尽快联系您。",
                    'confidence': 0.0,
                    'sources': [],
                    'answer_type': 'error',
                    'ai_answer': None,
                    'ticket_id': self._create_ticket(question, session_id, user_id),
                    'escalated': True
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
        
        # 提高相似度阈值，减少不相关匹配
        if max_similarity < 0.3:  # 如果最高相似度低于30%，认为不相关
            return 0.0
        
        confidence = (max_similarity * 0.8 + result_count_factor * 0.2)  # 更重视相似度
        return min(confidence, 1.0)
    
    def _generate_simple_response(self, question: str, context: str) -> str:
        """生成简单回答（备用方案）"""
        if not context:
            return "抱歉，我在知识库中没有找到相关信息。请尝试重新描述您的问题，或联系技术支持获取帮助。"
        
        return f"""基于以下知识库信息回答您的问题：

{context}

如果您需要更详细的帮助，请提供更多具体信息。"""
    
    def _generate_improved_response_with_context(self, question: str, feedback_score: int) -> Dict[str, Any]:
        """根据用户反馈生成改进的回答（带上下文）"""
        try:
            # 搜索相关知识库
            knowledge_results = self.search_knowledge(question)
            context = ""
            knowledge_sources = []
            
            if knowledge_results:
                context = "\n".join([result['content'] for result in knowledge_results[:3]])
                knowledge_sources = [result['title'] for result in knowledge_results[:3]]
            
            # 生成改进的回答
            improved_answer = self._generate_improved_response(question, context, feedback_score)
            
            return {
                'answer': improved_answer,
                'confidence': 0.8,  # 改进回答的置信度
                'sources': knowledge_sources,
                'answer_type': 'improved',
                'ai_answer': improved_answer,
                'ticket_id': None,
                'escalated': False
            }
            
        except Exception as e:
            logger.error(f"生成改进回答失败: {e}")
            return {
                'answer': "抱歉，生成改进回答时遇到问题。请稍后重试。",
                'confidence': 0.1,
                'sources': [],
                'answer_type': 'error',
                'ai_answer': None,
                'ticket_id': None,
                'escalated': False
            }
    
    def _generate_improved_response(self, question: str, context: str, feedback_score: int) -> str:
        """根据用户反馈生成改进的回答"""
        try:
            if not self.active_ai_model:
                return self._generate_simple_improved_response(question, context, feedback_score)
            
            # 根据反馈分数构建不同的改进提示词
            if feedback_score == 1:
                improvement_prompt = "用户对之前的回答非常不满意。请重新思考这个问题，提供更详细、更准确、更有帮助的回答。"
            elif feedback_score == 2:
                improvement_prompt = "用户对之前的回答不满意。请提供更清晰、更实用的解决方案。"
            elif feedback_score == 3:
                improvement_prompt = "用户对之前的回答一般满意。请尝试提供更完整、更有针对性的回答。"
            else:
                improvement_prompt = "请重新思考这个问题，提供更好的回答。"
            
            # 构建改进的提示词
            if context:
                prompt = f"""基于以下知识库信息回答用户问题：

知识库信息：
{context}

用户问题：{question}

{improvement_prompt}

请提供更准确、更详细、更有用的回答。如果知识库信息不足，请说明需要更多信息，并尝试提供一般性的解决方案。"""
            else:
                prompt = f"""用户问题：{question}

{improvement_prompt}

请提供准确、有用的IT技术支持回答。如果信息不足，请说明需要更多具体信息。"""
            
            # 调用AI模型生成改进回答
            if self.active_ai_model == 'qwen':
                return self._call_qwen_api_with_improvement(prompt)
            elif self.active_ai_model == 'openai':
                return self._call_openai_api_with_improvement(prompt)
            elif self.active_ai_model == 'claude':
                return self._call_claude_api_with_improvement(prompt)
            elif self.active_ai_model == 'glm':
                return self._call_glm_api_with_improvement(prompt)
            else:
                return self._generate_simple_improved_response(question, context, feedback_score)
                
        except Exception as e:
            logger.error(f"生成改进回答失败: {e}")
            return self._generate_simple_improved_response(question, context, feedback_score)
    
    def _generate_simple_improved_response(self, question: str, context: str, feedback_score: int) -> str:
        """生成简单的改进回答（备用方案）"""
        if feedback_score <= 2:
            return f"""我理解您对之前的回答不满意。让我重新为您分析这个问题：

{context if context else "基于我的知识库"}

针对您的问题"{question}"，我建议：

1. 请提供更多具体信息，比如：
   - 您使用的具体软件版本
   - 错误信息的具体内容
   - 您已经尝试过的解决方案

2. 如果问题仍然存在，建议：
   - 联系技术支持获取专业帮助
   - 查看相关官方文档
   - 在技术论坛寻求帮助

我会继续改进我的回答质量，感谢您的反馈！"""
        else:
            return f"""感谢您的反馈！让我为您提供更详细的解答：

{context if context else "基于我的知识库"}

针对您的问题"{question}"，这里是更完整的解决方案：

1. 详细步骤说明
2. 可能遇到的问题及解决方法
3. 预防措施

如果您需要更具体的帮助，请提供更多详细信息。"""
    
    def _call_qwen_api_with_improvement(self, prompt: str) -> str:
        """调用通义千问API生成改进回答"""
        try:
            config = self.ai_model_config['qwen']
            
            # 使用更保守的参数来生成更准确的回答
            model_params = {
                'temperature': 0.3,  # 降低随机性，提高准确性
                'top_p': 0.8,
                'result_format': 'message',
                'max_tokens': 2500  # 增加长度以提供更详细回答
            }
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'input': {
                    'messages': [
                        {'role': 'system', 'content': '你是一个专业的IT技术支持助手。用户对之前的回答不满意，请提供更准确、更详细、更有帮助的回答。'},
                        {'role': 'user', 'content': prompt}
                    ]
                },
                'parameters': model_params
            }
            
            api_url = f"{config['api_base']}/services/aigc/text-generation/generation"
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'output' in result and 'choices' in result['output'] and len(result['output']['choices']) > 0:
                    return result['output']['choices'][0]['message']['content'].strip()
                else:
                    return "抱歉，生成改进回答时出现技术问题。"
            else:
                return f"抱歉，生成改进回答失败，请稍后重试。"
                
        except Exception as e:
            logger.error(f"通义千问改进回答生成失败: {e}")
            return "抱歉，生成改进回答时出现错误。"
    
    def _call_openai_api_with_improvement(self, prompt: str) -> str:
        """调用OpenAI API生成改进回答"""
        try:
            config = self.ai_model_config['openai']
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的IT技术支持助手。用户对之前的回答不满意，请提供更准确、更详细、更有帮助的回答。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 2000,
                'temperature': 0.3
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
                return "抱歉，生成改进回答失败，请稍后重试。"
                
        except Exception as e:
            logger.error(f"OpenAI改进回答生成失败: {e}")
            return "抱歉，生成改进回答时出现错误。"
    
    def _call_claude_api_with_improvement(self, prompt: str) -> str:
        """调用Claude API生成改进回答"""
        try:
            config = self.ai_model_config['claude']
            
            headers = {
                'x-api-key': config['api_key'],
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'max_tokens': 2000,
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
                return "抱歉，生成改进回答失败，请稍后重试。"
                
        except Exception as e:
            logger.error(f"Claude改进回答生成失败: {e}")
            return "抱歉，生成改进回答时出现错误。"
    
    def _call_glm_api_with_improvement(self, prompt: str) -> str:
        """调用GLM API生成改进回答"""
        try:
            config = self.ai_model_config['glm']
            
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
                    'max_tokens': 2000,
                    'temperature': 0.3
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
                return "抱歉，生成改进回答失败，请稍后重试。"
                
        except Exception as e:
            logger.error(f"GLM改进回答生成失败: {e}")
            return "抱歉，生成改进回答时出现错误。"

    def _generate_ai_answer(self, question, knowledge_sources):
        """生成AI答案"""
        try:
            if not self.active_ai_model:
                return "抱歉，AI模型暂时不可用。"
            
            # 构建上下文提示
            context = ""
            if knowledge_sources:
                context = f"参考知识库内容：{', '.join(knowledge_sources)}\n\n"
            
            # 根据不同的AI模型生成答案
            if self.active_ai_model == "qwen":
                return self._call_qwen_api(question, context)
            elif self.active_ai_model == "openai":
                return self._call_openai_api(question, context)
            elif self.active_ai_model == "claude":
                return self._call_claude_api(question, context)
            elif self.active_ai_model == "glm":
                return self._call_glm_api(question, context)
            elif self.active_ai_model == "wenxin":
                return self._call_wenxin_api(question, context)
            else:
                return self._call_qwen_api(question, context)  # 默认使用通义千问
                
        except Exception as e:
            logger.error(f"生成AI答案失败: {e}")
            return "抱歉，AI生成答案时出现错误。"
    
    def _calculate_ai_confidence(self, ai_answer, question):
        """计算AI答案的置信度"""
        try:
            # 简单的置信度计算：基于答案长度和相关性
            if not ai_answer or len(ai_answer.strip()) < 10:
                return 0.1
            
            # 基础置信度
            base_confidence = 0.5
            
            # 根据答案长度调整
            if len(ai_answer) > 100:
                base_confidence += 0.2
            elif len(ai_answer) > 50:
                base_confidence += 0.1
            
            # 根据是否包含关键词调整
            question_keywords = set(question.lower().split())
            answer_keywords = set(ai_answer.lower().split())
            keyword_overlap = len(question_keywords.intersection(answer_keywords))
            if keyword_overlap > 0:
                base_confidence += min(0.2, keyword_overlap * 0.05)
            
            return min(0.9, base_confidence)
            
        except Exception as e:
            logger.error(f"计算AI置信度失败: {e}")
            return 0.3
    
    def _create_ticket(self, question, session_id, user_id):
        """创建工单"""
        try:
            from db_utils import db_manager
            ticket_id = db_manager.create_ticket(session_id, user_id, question)
            return ticket_id
        except Exception as e:
            logger.error(f"创建工单失败: {e}")
            return None

# 全局增强版RAG引擎实例
enhanced_rag_engine = EnhancedRAGEngine()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版RAG引擎 - 集成AI大模型API (性能优化版)
"""

import os
import logging
import requests
import json
import time
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from functools import lru_cache

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class EnhancedRAGEngine:
    def __init__(self):
        """初始化增强版RAG引擎"""
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # 初始化数据库管理器
        try:
            from db_utils import DatabaseManager
            self.db_manager = DatabaseManager()
        except Exception as e:
            logger.warning(f"无法初始化数据库管理器: {e}")
            self.db_manager = None
        
        # AI模型配置 - 大幅优化超时时间和参数
        self.ai_model_config = {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'api_base': os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1'),
                'model': os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                'enabled': os.getenv('OPENAI_ENABLED', 'false').lower() == 'true',
                'timeout': 8  # 大幅减少超时时间到8秒
            },
            'claude': {
                'api_key': os.getenv('CLAUDE_API_KEY'),
                'api_base': os.getenv('CLAUDE_API_BASE', 'https://api.anthropic.com'),
                'model': os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
                'enabled': os.getenv('CLAUDE_ENABLED', 'false').lower() == 'true',
                'timeout': 8
            },
            'glm': {
                'api_key': os.getenv('GLM_API_KEY'),
                'api_base': 'https://open.bigmodel.cn/api/paas/v4',
                'model': os.getenv('GLM_MODEL', 'glm-4'),
                'enabled': os.getenv('GLM_ENABLED', 'false').lower() == 'true',
                'timeout': 8
            },
            'qwen': {
                'api_key': os.getenv('QWEN_API_KEY'),
                'api_base': 'https://dashscope.aliyuncs.com/api/v1',
                'model': os.getenv('QWEN_MODEL', 'qwen-plus'),
                'enabled': os.getenv('QWEN_ENABLED', 'false').lower() == 'true',
                'timeout': 10  # 减少超时时间到10秒
            }
        }
        
        # 选择启用的AI模型
        self.active_ai_model = self._get_active_ai_model()
        if self.active_ai_model:
            logger.info(f"AI大模型已启用: {self.active_ai_model}")
        else:
            logger.info("AI大模型未启用，将使用基础RAG模式")
        
        # 性能优化：预加载常用问题的向量
        self._preload_common_embeddings()
    
    def _preload_common_embeddings(self):
        """预加载常用问题的向量嵌入"""
        common_questions = [
            "鼠标失灵怎么办",
            "打印机故障",
            "网络连接问题",
            "密码设置",
            "软件安装",
            "系统故障",
            "数据备份",
            "病毒防护"
        ]
        
        for question in common_questions:
            self._get_cached_embedding(question)
        
        logger.info(f"预加载了 {len(common_questions)} 个常用问题的向量嵌入")
    
    @lru_cache(maxsize=1000)
    def _get_cached_embedding(self, text: str) -> List[float]:
        """获取缓存的向量嵌入"""
        return self.embedding_model.encode(text).tolist()
    
    def generate_embedding(self, text: str) -> List[float]:
        """生成向量嵌入（公共方法）"""
        return self._get_cached_embedding(text)
    
    def _extract_keywords(self, question: str) -> List[str]:
        """从问题中提取关键词 - 完全自动化的精准版本"""
        logger.info(f"开始提取关键词，问题: '{question}'")
        keywords = []
        question_lower = question.lower()
        logger.info(f"问题转小写: '{question_lower}'")
        
        # 首先检查是否是问候语 - 使用完整匹配，避免误识别
        greeting_keywords = ['你好', '您好', 'hi', 'hello', '早上好', '下午好', '晚上好', '在吗', '在么']
        logger.info(f"检查问候语关键词: {greeting_keywords}")
        for greeting_keyword in greeting_keywords:
            logger.info(f"比较: '{greeting_keyword}' == '{question_lower}' -> {greeting_keyword == question_lower}")
            if greeting_keyword == question_lower:  # 完全匹配，不是包含关系
                logger.info(f"识别到问候语: {greeting_keyword}")
                return ['greeting']  # 返回特殊标识，表示这是问候语
        
        logger.info("未识别到问候语，继续检查身份询问")
        
        # 检查是否是身份询问类问题 - 使用完整匹配
        identity_keywords = ['你是谁', '你是什么', '你的名字', '你叫什么', '你是什么人', '你是什么助手', '你是什么系统']
        for identity_keyword in identity_keywords:
            if identity_keyword == question_lower:  # 完全匹配，不是包含关系
                logger.info(f"识别到身份询问问题: {identity_keyword}")
                return ['identity']  # 返回特殊标识，表示这是身份询问
        
        logger.info("未识别到身份询问，开始问题类型检测")
        
        # 如果不是问候语或身份询问，才进行问题类型检测
        # 动态问题类型映射表 - 支持自动扩展
        problem_type_mapping = {
            # 硬件设备问题
            '打印机': ['打印机', 'printer', '打印', '打印不了', '打印故障', '打印问题', '打印设备'],
            '鼠标': ['鼠标', 'mouse', '鼠标失灵', '鼠标不动', '鼠标故障', '鼠标问题', '鼠标设备'],
            '键盘': ['键盘', 'keyboard', '键盘失灵', '键盘故障', '键盘问题', '键盘设备'],
            '显示器': ['显示器', 'monitor', '屏幕', '显示器故障', '屏幕问题', '显示设备'],
            '网络': ['网络', 'network', 'wifi', '网络连接', '网络故障', '网络问题', '网络设备'],
            '蓝牙': ['蓝牙', 'bluetooth', '蓝牙连接', '蓝牙故障', '蓝牙问题'],
            
            # 系统问题
            '系统重置': ['重装', '重置', '重装电脑', '重置电脑', '系统重置', '重装系统', 'reset', '重装windows', '重置windows', '系统重装'],
            '蓝屏': ['蓝屏', '蓝屏死机', '蓝屏错误', '系统蓝屏', '蓝屏问题'],
            '死机': ['死机', '卡死', '系统死机', '电脑死机', '死机问题'],
            '卡顿': ['卡顿', '慢', '系统慢', '电脑慢', '卡', '卡顿问题', '性能问题'],
            
            # 安全认证问题
            '密码': ['密码', 'password', '修改密码', '更改密码', '重置密码', '忘记密码', '密码问题'],
            '登录': ['登录', 'login', '无法登录', '登录失败', '登录问题', '登入'],
            '账户': ['账户', 'account', '账户问题', '账号', '账号问题'],
            
            # 软件问题
            '软件': ['软件', '软件安装', '软件卸载', '软件问题', '程序', '应用程序'],
            'outlook': ['outlook', '邮件', '邮箱', '邮件客户端', '邮件软件'],
            'office': ['office', 'word', 'excel', 'powerpoint', '办公软件'],
            '驱动': ['驱动', '驱动程序', '驱动安装', '驱动问题', '驱动更新'],
            '系统更新': ['系统更新', 'windows更新', '更新问题', '补丁', '系统补丁'],
            
            # 数据问题
            '数据': ['数据', '数据备份', '数据恢复', '文件', '文件丢失', '数据问题'],
            '病毒': ['病毒', '杀毒', '病毒防护', '安全软件', '恶意软件', '木马'],
            
            # 连接问题
            '连接': ['连接', '连接问题', '连接失败', '无法连接', '连接故障'],
            'USB': ['usb', 'usb连接', 'usb设备', 'usb问题'],
            
            # 性能问题
            '性能': ['性能', '性能问题', '速度慢', '运行慢', '响应慢'],
            '内存': ['内存', '内存不足', '内存问题', 'ram'],
            '硬盘': ['硬盘', '硬盘问题', '存储', '存储问题', '磁盘'],
            
            # 音频视频问题
            '音频': ['音频', '声音', '声音问题', '音频问题', '麦克风', '扬声器'],
            '视频': ['视频', '视频问题', '摄像头', '摄像头问题', '视频通话'],
            
            # 电源问题
            '电源': ['电源', '电源问题', '电池', '电池问题', '充电', '充电问题'],
            '开机': ['开机', '开机问题', '启动', '启动问题', '无法开机'],
            '关机': ['关机', '关机问题', '无法关机', '自动关机']
        }
        
        # 优先级排序的问题类型 - 系统级问题优先级最高
        priority_order = [
            # 系统级问题（最高优先级）
            '系统重置', '蓝屏', '死机', '开机', '关机',
            
            # 硬件设备问题
            '打印机', '鼠标', '键盘', '显示器', '网络', '蓝牙', 'USB',
            
            # 安全认证问题
            '密码', '登录', '账户',
            
            # 软件问题
            'outlook', 'office', '软件', '驱动', '系统更新',
            
            # 数据和安全问题
            '数据', '病毒',
            
            # 连接问题
            '连接',
            
            # 性能问题
            '性能', '内存', '硬盘', '卡顿',
            
            # 多媒体问题
            '音频', '视频',
            
            # 电源问题
            '电源'
        ]
        
        # 按优先级顺序检查问题类型
        for problem_type in priority_order:
            if problem_type in problem_type_mapping:
                for keyword in problem_type_mapping[problem_type]:
                    if keyword in question_lower:
                        logger.info(f"识别到问题类型: {problem_type} (关键词: {keyword})")
                        keywords.append(problem_type)  # 使用问题类型作为关键词
                        break  # 找到一个匹配就跳出内层循环，避免重复添加
        
        # 如果没有找到明确的问题类型，尝试通用关键词
        generic_keywords = ['电脑', '系统', '问题', '故障', '错误', '设备']
        for keyword in generic_keywords:
            if keyword in question_lower:
                logger.info(f"识别到通用关键词: {keyword}")
                keywords.append(keyword)
                break
        
        logger.info(f"最终提取的关键词: {keywords}")
        return keywords[:1]  # 只返回1个关键词，确保最高精准度
    
    def search_knowledge(self, question: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """搜索知识库 - 完全自动化的精准搜索策略"""
        try:
            from db_utils import db_manager
            
            # 第一步：精确问题类型识别
            keywords = self._extract_keywords(question)
            if keywords:
                logger.info(f"识别到问题类型: {keywords}")
                
                # 第二步：基于问题类型的精准搜索
                primary_keyword = keywords[0]  # 只使用第一个（最重要的）关键词
                logger.info(f"使用主要关键词进行搜索: {primary_keyword}")
                
                # 使用严格的关键词搜索
                keyword_results = self._strict_keyword_search(primary_keyword, question)
                
                if keyword_results:
                    logger.info(f"精准关键词搜索找到 {len(keyword_results)} 条相关结果")
                    return keyword_results[:top_k]
                else:
                    logger.info("精准关键词搜索无结果，尝试扩展搜索")
                    
                    # 第三步：扩展搜索（如果精准搜索无结果）
                    expanded_results = self._expanded_search(primary_keyword, question)
                    if expanded_results:
                        logger.info(f"扩展搜索找到 {len(expanded_results)} 条相关结果")
                        return expanded_results[:top_k]
            
            # 第四步：向量搜索作为最后手段（提高阈值）
            logger.info("使用向量搜索作为最后手段")
            return self._vector_search(question, top_k)
            
        except Exception as e:
            logger.error(f"搜索知识库失败: {e}")
            return []

    def search_knowledge_strict(self, question: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """严格的知识库搜索 - 专门用于知识库模式，确保高精度"""
        try:
            from db_utils import db_manager
            
            # 第一步：精确问题类型识别
            keywords = self._extract_keywords(question)
            if not keywords:
                logger.info("未识别到问题类型，返回空结果")
                return []
            
            logger.info(f"识别到问题类型: {keywords}")
            
            # 第二步：只使用严格的关键词搜索
            primary_keyword = keywords[0]
            logger.info(f"使用主要关键词进行严格搜索: {primary_keyword}")
            
            # 使用更严格的关键词搜索
            keyword_results = self._strict_keyword_search_strict(primary_keyword, question)
            
            if keyword_results:
                logger.info(f"严格关键词搜索找到 {len(keyword_results)} 条相关结果")
                return keyword_results[:top_k]
            else:
                logger.info("严格关键词搜索无结果，知识库模式不进行扩展搜索")
                return []
            
        except Exception as e:
            logger.error(f"严格知识库搜索失败: {e}")
            return []

    def _strict_keyword_search(self, keyword: str, question: str) -> List[Dict[str, Any]]:
        """严格关键词搜索 - 专门用于知识库模式"""
        try:
            if not self.db_manager:
                logger.warning("数据库管理器不可用")
                return []
            
            # 构建严格的搜索条件
            search_terms = self._get_search_terms_for_problem_type(keyword)
            
            # 执行严格搜索
            all_results = []
            for term in search_terms:
                try:
                    results = self.db_manager.search_knowledge_by_keyword(term)
                    for result in results:
                        # 检查是否已存在
                        if not any(r['id'] == result['id'] for r in all_results):
                            # 更严格的相关性检查
                            if self._is_strictly_relevant(result, keyword, question):
                                relevance_score = self._calculate_strict_relevance(result, keyword, question)
                                if relevance_score > 0.7:  # 进一步提高阈值到0.7，确保更高精准度
                                    all_results.append({
                                        'id': result['id'],
                                        'title': result['title'],
                                        'content': result['content'],
                                        'similarity': relevance_score
                                    })
                except Exception as e:
                    logger.warning(f"搜索关键词 '{term}' 失败: {e}")
                    continue
            
            # 按相关性排序
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            return all_results
            
        except Exception as e:
            logger.error(f"严格关键词搜索失败: {e}")
            return []

    def _strict_keyword_search_strict(self, keyword: str, question: str) -> List[Dict[str, Any]]:
        """更严格的关键词搜索 - 专门用于知识库模式"""
        try:
            if not self.db_manager:
                logger.warning("数据库管理器不可用")
                return []
            
            # 构建严格的搜索条件
            search_terms = self._get_search_terms_for_problem_type(keyword)
            
            # 执行严格搜索
            all_results = []
            for term in search_terms:
                try:
                    results = self.db_manager.search_knowledge_by_keyword(term)
                    for result in results:
                        # 检查是否已存在
                        if not any(r['id'] == result['id'] for r in all_results):
                            # 更严格的相关性检查
                            if self._is_strictly_relevant_strict(result, keyword, question):
                                relevance_score = self._calculate_strict_relevance_strict(result, keyword, question)
                                if relevance_score >= 0.6:  # 降低阈值到0.6，确保能找到相关结果
                                    all_results.append({
                                        'id': result['id'],
                                        'title': result['title'],
                                        'content': result['content'],
                                        'similarity': relevance_score
                                    })
                except Exception as e:
                    logger.warning(f"搜索关键词 '{term}' 失败: {e}")
                    continue
            
            # 按相关性排序
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            return all_results
            
        except Exception as e:
            logger.error(f"严格关键词搜索失败: {e}")
            return []

    def _get_search_terms_for_problem_type(self, problem_type: str) -> List[str]:
        """根据问题类型获取搜索词汇"""
        search_terms_mapping = {
            '系统重置': ['重置', '重装', 'reset', 'windows重置', '系统重置', '重装电脑', '重置电脑'],
            '打印机': ['打印机', 'printer', '打印故障', '打印问题'],
            '鼠标': ['鼠标', 'mouse', '鼠标故障', '鼠标问题'],
            '键盘': ['键盘', 'keyboard', '键盘故障', '键盘问题'],
            '显示器': ['显示器', 'monitor', '屏幕', '显示器故障', '屏幕问题'],
            '网络': ['网络', 'network', '网络故障', '网络问题', 'wifi'],
            '蓝牙': ['蓝牙', 'bluetooth', '蓝牙故障', '蓝牙问题'],
            '密码': ['密码', 'password', '修改密码', '密码问题'],
            '登录': ['登录', 'login', '登录问题', '登入'],
            '账户': ['账户', 'account', '账户问题', '账号'],
            '软件': ['软件', '软件安装', '软件问题', '程序'],
            'outlook': ['outlook', '邮件', '邮箱', '邮件客户端'],
            'office': ['office', 'word', 'excel', 'powerpoint', '办公软件'],
            '驱动': ['驱动', '驱动程序', '驱动问题'],
            '系统更新': ['系统更新', 'windows更新', '更新问题'],
            '数据': ['数据', '数据备份', '数据问题', '文件'],
            '病毒': ['病毒', '杀毒', '病毒防护', '安全软件'],
            '连接': ['连接', '连接问题', '连接故障'],
            'USB': ['usb', 'usb连接', 'usb问题'],
            '性能': ['性能', '性能问题', '速度慢'],
            '内存': ['内存', '内存不足', '内存问题'],
            '硬盘': ['硬盘', '硬盘问题', '存储问题'],
            '音频': ['音频', '声音', '声音问题', '麦克风'],
            '视频': ['视频', '视频问题', '摄像头'],
            '电源': ['电源', '电源问题', '电池'],
            '开机': ['开机', '开机问题', '启动'],
            '关机': ['关机', '关机问题'],
            '蓝屏': ['蓝屏', '蓝屏死机', '蓝屏错误'],
            '死机': ['死机', '卡死', '系统死机'],
            '卡顿': ['卡顿', '慢', '系统慢', '卡顿问题']
        }
        
        return search_terms_mapping.get(problem_type, [problem_type])
    
    def _is_strictly_relevant(self, result: Dict[str, Any], keyword: str, question: str) -> bool:
        """检查结果是否严格相关 - 更严格的检查"""
        title_lower = result['title'].lower()
        content_lower = result['content'].lower()
        question_lower = question.lower()
        
        # 标题必须包含关键词或相关词汇
        search_terms = self._get_search_terms_for_problem_type(keyword)
        
        # 检查标题是否包含任何相关搜索词汇
        title_relevant = any(term in title_lower for term in search_terms)
        
        if not title_relevant:
            return False
        
        # 进一步检查问题类型匹配
        if keyword == '系统重置':
            return any(term in title_lower for term in ['重置', '重装', 'reset', 'windows'])
        elif keyword == '打印机':
            return any(term in title_lower for term in ['打印机', 'printer', '打印'])
        elif keyword == '鼠标':
            return any(term in title_lower for term in ['鼠标', 'mouse'])
        elif keyword == '键盘':
            return any(term in title_lower for term in ['键盘', 'keyboard'])
        elif keyword == '网络':
            return any(term in title_lower for term in ['网络', 'network', 'wifi'])
        elif keyword == '密码':
            return any(term in title_lower for term in ['密码', 'password'])
        elif keyword == '登录':
            return any(term in title_lower for term in ['登录', 'login'])
        elif keyword == '蓝屏':
            return '蓝屏' in title_lower
        elif keyword == '死机':
            return '死机' in title_lower
        elif keyword == '卡顿':
            return any(term in title_lower for term in ['卡顿', '慢'])
        elif keyword == '病毒':
            return any(term in title_lower for term in ['病毒', '杀毒', '安全'])
        elif keyword == '数据':
            return any(term in title_lower for term in ['数据', '文件', '备份'])
        elif keyword == '软件':
            return any(term in title_lower for term in ['软件', '程序', '应用'])
        elif keyword == 'outlook':
            return any(term in title_lower for term in ['outlook', '邮件', '邮箱'])
        elif keyword == 'office':
            return any(term in title_lower for term in ['office', 'word', 'excel', 'powerpoint', '办公'])
        elif keyword == '驱动':
            return any(term in title_lower for term in ['驱动', '驱动程序'])
        elif keyword == '音频':
            return any(term in title_lower for term in ['音频', '声音', '麦克风'])
        elif keyword == '视频':
            return any(term in title_lower for term in ['视频', '摄像头'])
        elif keyword == '电源':
            return any(term in title_lower for term in ['电源', '电池', '充电'])
        elif keyword == '开机':
            return any(term in title_lower for term in ['开机', '启动'])
        elif keyword == '关机':
            return any(term in title_lower for term in ['关机'])
        elif keyword == 'USB':
            return 'usb' in title_lower
        elif keyword == '蓝牙':
            return any(term in title_lower for term in ['蓝牙', 'bluetooth'])
        elif keyword == '显示器':
            return any(term in title_lower for term in ['显示器', '屏幕', 'monitor'])
        elif keyword == '内存':
            return any(term in title_lower for term in ['内存', 'ram'])
        elif keyword == '硬盘':
            return any(term in title_lower for term in ['硬盘', '存储', '磁盘'])
        elif keyword == '性能':
            return any(term in title_lower for term in ['性能', '速度'])
        elif keyword == '连接':
            return any(term in title_lower for term in ['连接', '连接问题'])
        elif keyword == '系统更新':
            return any(term in title_lower for term in ['更新', '补丁', '系统更新'])
        elif keyword == '账户':
            return any(term in title_lower for term in ['账户', '账号', 'account'])
        
        return True
    
    def _is_strictly_relevant_strict(self, result: Dict[str, Any], keyword: str, question: str) -> bool:
        """更严格的相关性检查 - 专门用于知识库模式"""
        try:
            title = result['title'].lower()
            content = result['content'].lower()
            question_lower = question.lower()
            
            # 检查标题是否包含关键词
            if keyword.lower() not in title:
                return False
            
            # 简化检查：只要标题包含关键词就认为相关
            return True
            
        except Exception as e:
            logger.error(f"严格相关性检查失败: {e}")
            return False
    
    def _calculate_strict_relevance(self, result: Dict[str, Any], keyword: str, question: str) -> float:
        """计算严格的相关性分数 - 更严格的评分"""
        title_lower = result['title'].lower()
        content_lower = result['content'].lower()
        question_lower = question.lower()
        
        score = 0.0
        
        # 标题匹配权重最高
        search_terms = self._get_search_terms_for_problem_type(keyword)
        title_match_count = sum(1 for term in search_terms if term in title_lower)
        
        if title_match_count > 0:
            score += 0.8  # 标题匹配给高分
        
        # 问题词汇匹配
        question_words = set(question_lower.split())
        title_words = set(title_lower.split())
        overlap = len(question_words.intersection(title_words))
        if overlap > 0:
            score += min(0.2, overlap * 0.1)
        
        return min(1.0, score)
    
    def _calculate_strict_relevance_strict(self, result: Dict[str, Any], keyword: str, question: str) -> float:
        """更严格的相关性评分 - 专门用于知识库模式"""
        try:
            title = result['title'].lower()
            content = result['content'].lower()
            question_lower = question.lower()
            
            score = 0.0
            
            # 标题匹配权重最高
            if keyword.lower() in title:
                score += 0.6
            
            # 问题词汇在标题中的匹配
            question_words = question_lower.split()
            relevant_words = [word for word in question_words if len(word) > 2]
            
            title_match_count = sum(1 for word in relevant_words if word in title)
            if title_match_count > 0:
                score += min(0.3, title_match_count * 0.1)
            
            # 问题词汇在内容中的匹配
            content_match_count = sum(1 for word in relevant_words if word in content)
            if content_match_count > 0:
                score += min(0.1, content_match_count * 0.02)
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"严格相关性评分失败: {e}")
            return 0.0
    
    def _expanded_search(self, keyword: str, question: str) -> List[Dict[str, Any]]:
        """扩展搜索 - 当严格搜索无结果时使用"""
        try:
            from db_utils import db_manager
            
            # 使用向量搜索作为扩展搜索
            return self._vector_search(question, 3)
            
        except Exception as e:
            logger.error(f"扩展搜索失败: {e}")
            return []
    
    def _vector_search(self, question: str, top_k: int) -> List[Dict[str, Any]]:
        """向量搜索 - 更严格的阈值"""
        try:
            from db_utils import db_manager
            
            question_embedding = self._get_cached_embedding(question)
            all_knowledge = db_manager.get_all_knowledge()
            
            if not all_knowledge:
                return []
            
            similarities = []
            for knowledge_item in all_knowledge:
                knowledge_id = knowledge_item['id']
                title = knowledge_item['title']
                content = knowledge_item['content']
                
                # 计算相似度
                title_embedding = self._get_cached_embedding(title)
                title_similarity = self._cosine_similarity(question_embedding, title_embedding)
                
                content_embedding = self._get_cached_embedding(content)
                content_similarity = self._cosine_similarity(question_embedding, content_embedding)
                
                # 标题权重更高
                final_similarity = title_similarity * 0.8 + content_similarity * 0.2
                
                # 大幅提高向量搜索阈值，确保高相关性
                if final_similarity > 0.7:  # 从0.4提高到0.7
                    similarities.append({
                        'id': knowledge_id,
                        'title': title,
                        'content': content,
                        'similarity': float(final_similarity)
                    })
            
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"向量搜索失败: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        try:
            import numpy as np
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.error(f"计算余弦相似度失败: {e}")
            return 0.0
    
    def _calculate_relevance_score(self, question: str, title: str, content: str, keywords: List[str]) -> float:
        """计算相关性分数 - 更严格的评分"""
        try:
            score = 0.0
            
            # 标题匹配权重最高
            title_score = 0.0
            for keyword in keywords:
                if keyword in title:
                    title_score += 0.6  # 标题匹配给更高分
                    break
            
            # 内容匹配权重次之
            content_score = 0.0
            keyword_count = 0
            for keyword in keywords:
                if keyword in content:
                    keyword_count += 1
            
            if keyword_count > 0:
                content_score = min(0.2, keyword_count * 0.1)  # 最多0.2分
            
            # 问题词汇匹配
            question_words = set(question.split())
            title_words = set(title.split())
            content_words = set(content.split())
            
            # 计算词汇重叠度
            title_overlap = len(question_words.intersection(title_words)) / max(len(question_words), 1)
            content_overlap = len(question_words.intersection(content_words)) / max(len(question_words), 1)
            
            overlap_score = title_overlap * 0.15 + content_overlap * 0.05
            
            # 总分
            score = title_score + content_score + overlap_score
            
            # 确保分数在合理范围内
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"计算相关性分数失败: {e}")
            return 0.0
    
    def generate_ai_response(self, question: str, context: str = "") -> str:
        """使用AI大模型生成回答 - 大幅优化超时时间"""
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
        """调用OpenAI API - 大幅优化超时和参数"""
        try:
            config = self.ai_model_config['openai']
            
            # 构建简化的提示词，减少token数量
            if context:
                prompt = f"基于知识库信息回答：{context}\n\n问题：{question}\n\n请用中文简洁回答，使用Markdown格式。"
            else:
                prompt = f"问题：{question}\n\n请提供简洁的IT技术支持回答，使用Markdown格式。"
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是IT技术支持助手，请用中文简洁回答。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 500,  # 大幅减少token数量
                'temperature': 0.3,  # 降低随机性
                'timeout': config['timeout']
            }
            
            response = requests.post(
                f"{config['api_base']}/chat/completions",
                headers=headers,
                json=data,
                timeout=config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"OpenAI API调用失败: {response.status_code}")
                return f"OpenAI API调用失败: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("OpenAI API调用超时")
            return "AI响应超时，请稍后重试"
        except Exception as e:
            logger.error(f"OpenAI API调用异常: {e}")
            return f"OpenAI API调用异常: {str(e)}"
    
    def _call_claude_api(self, question: str, context: str = "") -> str:
        """调用Claude API - 大幅优化超时和参数"""
        try:
            config = self.ai_model_config['claude']
            
            if context:
                prompt = f"基于知识库信息回答：{context}\n\n问题：{question}\n\n请用中文简洁回答。"
            else:
                prompt = f"问题：{question}\n\n请提供简洁的IT技术支持回答。"
            
            headers = {
                'x-api-key': config['api_key'],
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'max_tokens': 500,  # 大幅减少token数量
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            }
            
            response = requests.post(
                f"{config['api_base']}/v1/messages",
                headers=headers,
                json=data,
                timeout=config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text'].strip()
            else:
                logger.error(f"Claude API调用失败: {response.status_code}")
                return f"Claude API调用失败: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Claude API调用超时")
            return "AI响应超时，请稍后重试"
        except Exception as e:
            logger.error(f"Claude API调用异常: {e}")
            return f"Claude API调用异常: {str(e)}"
    
    def _call_glm_api(self, question: str, context: str = "") -> str:
        """调用GLM API - 大幅优化超时和参数"""
        try:
            config = self.ai_model_config['glm']
            
            if context:
                prompt = f"基于知识库信息回答：{context}\n\n问题：{question}\n\n请用中文简洁回答。"
            else:
                prompt = f"问题：{question}\n\n请提供简洁的IT技术支持回答。"
            
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
                    'max_tokens': 500,  # 大幅减少token数量
                    'temperature': 0.3
                }
            }
            
            response = requests.post(
                f"{config['api_base']}/api/paas/v4/chat/completions",
                headers=headers,
                json=data,
                timeout=config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['output']['text'].strip()
            else:
                logger.error(f"GLM API调用失败: {response.status_code}")
                return f"GLM API调用失败: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("GLM API调用超时")
            return "AI响应超时，请稍后重试"
        except Exception as e:
            logger.error(f"GLM API调用异常: {e}")
            return f"GLM API调用异常: {str(e)}"
    
    def _call_qwen_api(self, question: str, context: str = "") -> str:
        """调用通义千问API - 大幅优化超时和参数"""
        try:
            config = self.ai_model_config['qwen']
            
            # 构建简化的提示词
            if context:
                prompt = f"基于知识库信息回答：{context}\n\n问题：{question}\n\n请用中文简洁回答，使用Markdown格式。"
            else:
                prompt = f"问题：{question}\n\n请提供简洁的IT技术支持回答，使用Markdown格式。"
            
            # 使用更快的模型参数
            model_params = {
                'temperature': 0.3,  # 降低随机性
                'top_p': 0.8,
                'result_format': 'message',
                'max_tokens': 500  # 大幅减少token数量
            }
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'input': {
                    'messages': [
                        {'role': 'system', 'content': '你是IT技术支持助手，请用中文简洁回答。'},
                        {'role': 'user', 'content': prompt}
                    ]
                },
                'parameters': model_params
            }
            
            api_url = f"{config['api_base']}/services/aigc/text-generation/generation"
            
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                
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
                return f"通义千问API调用失败: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("通义千问API调用超时")
            return "AI响应超时，请稍后重试"
        except Exception as e:
            logger.error(f"通义千问API调用异常: {e}")
            return f"通义千问API调用异常: {str(e)}"
    
    def _get_qwen_model_params(self, model: str) -> dict:
        """根据通义千问模型版本获取合适的参数 - 大幅优化性能"""
        base_params = {
            'temperature': 0.3,  # 降低随机性
            'top_p': 0.8,
            'result_format': 'message'
        }
        
        if model == 'qwen-turbo':
            return {
                **base_params,
                'max_tokens': 500  # 大幅减少token数量
            }
        elif model == 'qwen-plus':
            return {
                **base_params,
                'max_tokens': 500
            }
        elif model == 'qwen-max':
            return {
                **base_params,
                'max_tokens': 500
            }
        else:
            return {
                **base_params,
                'max_tokens': 500
            }
    
    def _get_active_ai_model(self) -> str:
        """获取启用的AI模型"""
        for model_name, config in self.ai_model_config.items():
            if config['enabled'] and config['api_key']:
                return model_name
        return None
    
    def process_question(self, question: str, answer_mode: str = 'hybrid', session_id: str = None, user_id: str = 'anonymous') -> Dict[str, Any]:
        """处理用户问题 - 优化响应策略"""
        try:
            start_time = time.time()
            logger.info(f"开始处理问题: {question}, 模式: {answer_mode}")
            
            # 首先检查是否是问候语 - 使用原始问题，不包含上下文
            keywords = self._extract_keywords(question)
            logger.info(f"提取的关键词: {keywords}")
            
            if keywords and keywords[0] == 'greeting':
                # 问候语，返回友好的回应
                logger.info("检测到问候语，返回问候回应")
                greeting_answer = """您好！很高兴为您服务！

我是AI-IT支持系统的智能助手，专门帮助解决各种IT技术问题。

请告诉我您遇到的具体IT问题，比如：
• 鼠标、键盘、打印机等硬件故障
• 软件安装、系统更新等问题
• 网络连接、密码设置等常见问题
• 或者其他任何IT相关的困扰

我会尽力为您提供专业的解决方案！"""
                
                response_time = time.time() - start_time
                logger.info(f"问候语回答完成，耗时: {response_time:.2f}秒")
                
                return {
                    'answer': greeting_answer,
                    'confidence': 1.0,
                    'sources': [],
                    'answer_type': '问候回应',
                    'ai_answer': None,
                    'ticket_id': None,
                    'escalated': False,
                    'response_time': response_time
                }
            
            # 检查是否是身份询问问题
            if keywords and keywords[0] == 'identity':
                # 身份询问问题，直接返回身份介绍
                logger.info("检测到身份询问问题，返回身份介绍")
                identity_answer = """我是AI-IT支持系统的智能助手，专门为您提供IT技术支持服务。

我可以帮助您解决以下问题：
• 硬件设备故障（鼠标、键盘、打印机、显示器等）
• 软件安装和使用问题
• 系统故障和性能优化
• 网络连接和安全问题
• 密码和账户管理
• 数据备份和恢复

请描述您遇到的具体IT问题，我将为您提供专业的解决方案。"""
                
                response_time = time.time() - start_time
                logger.info(f"身份询问回答完成，耗时: {response_time:.2f}秒")
                
                return {
                    'answer': identity_answer,
                    'confidence': 1.0,
                    'sources': [],
                    'answer_type': '身份介绍',
                    'ai_answer': None,
                    'ticket_id': None,
                    'escalated': False,
                    'response_time': response_time
                }
            
            logger.info(f"不是问候语或身份询问，继续处理问题类型: {keywords}")
            
            # 如果不是问候语或身份询问，则进行知识库搜索
            # 重新提取关键词（排除问候语和身份询问）
            knowledge_results = []
            
            # 只搜索标题，不使用向量相似度
            if self.db_manager and keywords:
                for keyword in keywords:
                    if keyword not in ['greeting', 'identity']:  # 跳过特殊关键词
                        try:
                            results = self.db_manager.search_knowledge_by_keyword(keyword)
                            knowledge_results.extend(results)
                        except Exception as e:
                            logger.warning(f"搜索知识库失败: {e}")
                            continue
            else:
                logger.warning("数据库管理器不可用或没有有效关键词")
            
            # 去重
            seen_ids = set()
            unique_results = []
            for result in knowledge_results:
                if result['id'] not in seen_ids:
                    seen_ids.add(result['id'])
                    unique_results.append(result)
            
            knowledge_results = unique_results[:5]  # 限制结果数量
            knowledge_confidence = self._calculate_confidence(knowledge_results)
            
            logger.info(f"知识库搜索结果: {len(knowledge_results)} 条，置信度: {knowledge_confidence}")
            
            # 根据答案模式决定回答策略
            if answer_mode == 'knowledge_base' or answer_mode == 'knowledge_only':
                # 纯知识库模式 - 只搜索标题，如果标题中没有找到就提示没有
                if knowledge_results and knowledge_confidence > 0.5:
                    # 只返回知识库内容，不进行任何AI补充
                    knowledge_content = "\n\n".join([result['content'] for result in knowledge_results])
                    answer = f"基于知识库信息：\n\n{knowledge_content}"
                    answer_type = '知识库'
                else:
                    # 标题中没有找到相关内容
                    answer = "抱歉，在知识库标题中没有找到相关信息。建议您尝试使用混合模式，让AI为您提供帮助。"
                    answer_type = '无结果'
                
                response_time = time.time() - start_time
                logger.info(f"知识库模式回答完成，耗时: {response_time:.2f}秒")
                
                return {
                    'answer': answer,
                    'confidence': knowledge_confidence,
                    'sources': [result['title'] for result in knowledge_results],
                    'answer_type': answer_type,
                    'ai_answer': None,
                    'ticket_id': None,
                    'escalated': False,
                    'response_time': response_time
                }
            
            elif answer_mode == 'ai_only':
                # 纯AI模式
                ai_answer = self.generate_ai_response(question)
                ai_confidence = self._calculate_ai_confidence(ai_answer, question)
                
                response_time = time.time() - start_time
                logger.info(f"AI模式回答完成，耗时: {response_time:.2f}秒")
                
                return {
                    'answer': ai_answer,
                    'confidence': ai_confidence,
                    'sources': [],
                    'answer_type': 'AI回答',
                    'ai_answer': ai_answer,
                    'ticket_id': None,
                    'escalated': False,
                    'response_time': response_time
                }
            
            else:  # hybrid模式
                # 混合模式：优先使用知识库，AI补充
                if knowledge_results and knowledge_confidence > 0.05:  # 降低阈值
                    # 有相关知识，生成混合回答
                    knowledge_context = "\n".join([result['content'] for result in knowledge_results])
                    ai_answer = self.generate_ai_response(question, knowledge_context)
                    
                    # 组合知识库和AI回答
                    combined_answer = f"""基于知识库信息：

{knowledge_context}

AI补充建议：

{ai_answer}"""
                    
                    response_time = time.time() - start_time
                    logger.info(f"混合模式回答完成，耗时: {response_time:.2f}秒")
                    
                    return {
                        'answer': combined_answer,
                        'confidence': max(knowledge_confidence, 0.6),
                        'sources': [result['title'] for result in knowledge_results],
                        'answer_type': '知识库+AI',
                        'ai_answer': ai_answer,
                        'ticket_id': None,
                        'escalated': False,
                        'response_time': response_time
                    }
                else:
                    # 标题中没有找到相关知识，直接使用AI回答
                    ai_answer = self.generate_ai_response(question)
                    ai_confidence = self._calculate_ai_confidence(ai_answer, question)
                    
                    # 在AI回答前添加提示
                    answer_with_hint = f"""未在知识库标题中找到相关信息，以下是AI的建议：

{ai_answer}"""
                    
                    response_time = time.time() - start_time
                    logger.info(f"混合模式AI回答完成，耗时: {response_time:.2f}秒")
                    
                    return {
                        'answer': answer_with_hint,
                        'confidence': ai_confidence,
                        'sources': [],
                        'answer_type': 'AI回答',
                        'ai_answer': ai_answer,
                        'ticket_id': None,
                        'escalated': False,
                        'response_time': response_time
                    }
                    
        except Exception as e:
            logger.error(f"处理问题失败: {e}")
            response_time = time.time() - start_time
            return {
                'answer': f"抱歉，处理您的问题时遇到错误: {str(e)}",
                'confidence': 0.0,
                'sources': [],
                'answer_type': '错误',
                'ai_answer': None,
                'ticket_id': None,
                'escalated': False,
                'response_time': response_time
            }
    
    def _generate_knowledge_response(self, question: str, knowledge_results: List[Dict[str, Any]]) -> str:
        """生成知识库回答"""
        try:
            if not knowledge_results:
                return "抱歉，在知识库中没有找到相关信息。"
            
            # 组合所有相关知识
            combined_content = "\n\n".join([
                f"**{result['title']}**\n{result['content']}"
                for result in knowledge_results
            ])
            
            return f"""基于知识库信息回答您的问题：

{combined_content}

如果您需要更详细的帮助，请提供更多具体信息。"""
            
        except Exception as e:
            logger.error(f"生成知识库回答失败: {e}")
            return "抱歉，生成知识库回答时遇到问题。"
    
    def _calculate_confidence(self, knowledge_results):
        """计算置信度"""
        if not knowledge_results:
            return 0.0
        
        # 基于结果数量计算置信度（标题搜索模式）
        result_count_factor = min(len(knowledge_results) / 3.0, 1.0)
        
        # 标题搜索模式下，只要有结果就给予一定置信度
        if len(knowledge_results) > 0:
            confidence = (0.7 + result_count_factor * 0.3)  # 基础置信度0.7，最高1.0
            return min(confidence, 1.0)
        
        return 0.0
    
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
            # 搜索相关知识库 - 只搜索标题
            keywords = self._extract_keywords(question)
            knowledge_results = []
            
            # 只搜索标题，不使用向量相似度
            if self.db_manager:
                for keyword in keywords:
                    if keyword != 'identity':  # 跳过身份关键词
                        try:
                            results = self.db_manager.search_knowledge_by_keyword(keyword)
                            knowledge_results.extend(results)
                        except Exception as e:
                            logger.warning(f"搜索知识库失败: {e}")
                            continue
            else:
                logger.warning("数据库管理器不可用，无法搜索知识库")
            
            # 去重
            seen_ids = set()
            unique_results = []
            for result in knowledge_results:
                if result['id'] not in seen_ids:
                    seen_ids.add(result['id'])
                    unique_results.append(result)
            
            knowledge_results = unique_results[:5]  # 限制结果数量
            context = ""
            knowledge_sources = []
            
            if knowledge_results:
                context = "\n".join([result['content'] for result in knowledge_results])
                knowledge_sources = [result['title'] for result in knowledge_results]
            
            # 生成改进的回答
            improved_answer = self._generate_improved_response(question, context, feedback_score)
            
            return {
                'answer': improved_answer,
                'confidence': 0.8,
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
            
            # 构建简化的改进提示词
            if context:
                prompt = f"知识库信息：{context}\n\n问题：{question}\n\n{improvement_prompt}\n\n请提供更准确、更详细、更有用的回答。"
            else:
                prompt = f"问题：{question}\n\n{improvement_prompt}\n\n请提供准确、有用的IT技术支持回答。"
            
            # 根据不同的AI模型生成改进回答
            if self.active_ai_model == 'openai':
                return self._call_openai_api_with_improvement(prompt)
            elif self.active_ai_model == 'claude':
                return self._call_claude_api_with_improvement(prompt)
            elif self.active_ai_model == 'glm':
                return self._call_glm_api_with_improvement(prompt)
            elif self.active_ai_model == 'qwen':
                return self._call_qwen_api_with_improvement(prompt)
            else:
                return self._generate_simple_improved_response(question, context, feedback_score)
                
        except Exception as e:
            logger.error(f"生成改进回答失败: {e}")
            return self._generate_simple_improved_response(question, context, feedback_score)
    
    def _generate_simple_improved_response(self, question: str, context: str, feedback_score: int) -> str:
        """生成简单的改进回答（备用方案）"""
        if feedback_score <= 2:
            return f"""抱歉之前的回答没有帮助到您。让我重新分析您的问题：

{question}

基于知识库信息：
{context if context else '暂无相关知识库信息'}

请尝试以下步骤：
1. 重新描述您遇到的具体问题
2. 提供错误信息或截图（如果有）
3. 说明您使用的设备和软件版本

这样我可以为您提供更准确的帮助。"""
        else:
            return f"""感谢您的反馈！基于知识库信息，为您提供补充说明：

{context if context else '暂无相关知识库信息'}

如果您还有其他问题，请随时告诉我。"""
    
    def _call_openai_api_with_improvement(self, prompt: str) -> str:
        """调用OpenAI API生成改进回答 - 大幅优化参数"""
        try:
            config = self.ai_model_config['openai']
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'messages': [
                    {'role': 'system', 'content': '你是IT技术支持助手。用户对之前的回答不满意，请提供更准确、更详细、更有帮助的回答。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 600,  # 减少token数量
                'temperature': 0.3
            }
            
            response = requests.post(
                f"{config['api_base']}/chat/completions",
                headers=headers,
                json=data,
                timeout=config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                return "抱歉，生成改进回答失败，请稍后重试。"
                
        except requests.exceptions.Timeout:
            return "抱歉，生成改进回答超时，请稍后重试。"
        except Exception as e:
            logger.error(f"OpenAI改进回答生成失败: {e}")
            return "抱歉，生成改进回答时出现错误。"
    
    def _call_claude_api_with_improvement(self, prompt: str) -> str:
        """调用Claude API生成改进回答 - 大幅优化参数"""
        try:
            config = self.ai_model_config['claude']
            
            headers = {
                'x-api-key': config['api_key'],
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'max_tokens': 600,  # 减少token数量
                'messages': [
                    {'role': 'user', 'content': prompt}
                ]
            }
            
            response = requests.post(
                f"{config['api_base']}/v1/messages",
                headers=headers,
                json=data,
                timeout=config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text'].strip()
            else:
                return "抱歉，生成改进回答失败，请稍后重试。"
                
        except requests.exceptions.Timeout:
            return "抱歉，生成改进回答超时，请稍后重试。"
        except Exception as e:
            logger.error(f"Claude改进回答生成失败: {e}")
            return "抱歉，生成改进回答时出现错误。"
    
    def _call_glm_api_with_improvement(self, prompt: str) -> str:
        """调用GLM API生成改进回答 - 大幅优化参数"""
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
                    'max_tokens': 500,  # 减少token数量
                    'temperature': 0.3
                }
            }
            
            response = requests.post(
                f"{config['api_base']}/api/paas/v4/chat/completions",
                headers=headers,
                json=data,
                timeout=config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['output']['text'].strip()
            else:
                return "抱歉，生成改进回答失败，请稍后重试。"
                
        except requests.exceptions.Timeout:
            return "抱歉，生成改进回答超时，请稍后重试。"
        except Exception as e:
            logger.error(f"GLM改进回答生成失败: {e}")
            return "抱歉，生成改进回答时出现错误。"
    
    def _call_qwen_api_with_improvement(self, prompt: str) -> str:
        """调用通义千问API生成改进回答 - 大幅优化参数"""
        try:
            config = self.ai_model_config['qwen']
            
            headers = {
                'Authorization': f'Bearer {config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': config['model'],
                'input': {
                    'messages': [
                        {'role': 'system', 'content': '你是IT技术支持助手。用户对之前的回答不满意，请提供更准确、更详细、更有帮助的回答。'},
                        {'role': 'user', 'content': prompt}
                    ]
                },
                'parameters': {
                    'temperature': 0.3,
                    'top_p': 0.8,
                    'result_format': 'message',
                    'max_tokens': 500  # 减少token数量
                }
            }
            
            api_url = f"{config['api_base']}/services/aigc/text-generation/generation"
            
            response = requests.post(
                api_url,
                headers=headers,
                json=data,
                timeout=config['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'output' in result and 'choices' in result['output'] and len(result['output']['choices']) > 0:
                    return result['output']['choices'][0]['message']['content'].strip()
                elif 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                elif 'output' in result and 'text' in result['output']:
                    return result['output']['text'].strip()
                else:
                    return "抱歉，生成改进回答失败，请稍后重试。"
            else:
                return "抱歉，生成改进回答失败，请稍后重试。"
                
        except requests.exceptions.Timeout:
            return "抱歉，生成改进回答超时，请稍后重试。"
        except Exception as e:
            logger.error(f"通义千问改进回答生成失败: {e}")
            return "抱歉，生成改进回答时出现错误。"
    
    def _generate_ai_answer(self, question, knowledge_sources):
        """生成AI答案 - 大幅优化提示词长度"""
        try:
            if not self.active_ai_model:
                return "抱歉，AI模型暂时不可用。"
            
            # 构建简化的上下文提示
            context = ""
            if knowledge_sources:
                context = f"参考知识库：{', '.join(knowledge_sources[:2])}\n\n"  # 只取前2个来源
            
            # 根据不同的AI模型生成答案
            if self.active_ai_model == "qwen":
                return self._call_qwen_api(question, context)
            elif self.active_ai_model == "openai":
                return self._call_openai_api(question, context)
            elif self.active_ai_model == "claude":
                return self._call_claude_api(question, context)
            elif self.active_ai_model == "glm":
                return self._call_glm_api(question, context)
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

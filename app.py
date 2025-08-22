import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import uuid
from functools import wraps
from config import Config
from db_utils import db_manager
from enhanced_rag_engine import enhanced_rag_engine
import csv
import io
from datetime import datetime

# 配置Flask应用
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
# app.config['SESSION_TYPE'] = 'filesystem'  # 移除这行，使用默认session配置
app.config['PERMANENT_SESSION_LIFETIME'] = Config.SESSION_TIMEOUT

# 启用CORS
CORS(app)

# 配置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 使用增强版RAG引擎（已初始化）

# 权限检查装饰器
def require_permission(permission_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return jsonify({'success': False, 'message': '请先登录'}), 401
            
            # 检查用户是否有指定权限
            has_permission = db_manager.check_user_permission(session['username'], permission_type)
            if not has_permission:
                return jsonify({'success': False, 'message': '权限不足'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 管理后台权限检查装饰器
def require_admin_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_page'))
        
        # 检查用户是否有管理后台访问权限
        has_permission = db_manager.check_user_permission(session['username'], 'can_access_admin')
        if not has_permission:
            return render_template('error.html', message='您没有访问管理后台的权限，请联系管理员'), 403
        
        return f(*args, **kwargs)
    return decorated_function

# 登录验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    """主页面"""
    return render_template('index.html', company_name=Config.COMPANY_NAME)

@app.route('/admin')
@require_admin_access
def admin_dashboard():
    """管理后台主页面"""
    return render_template('admin.html', company_name=Config.COMPANY_NAME)

@app.route('/knowledge')
@login_required
def knowledge_detail():
    """知识详情页面"""
    return render_template('knowledge_detail.html', company_name=Config.COMPANY_NAME)

@app.route('/conversations')
@login_required
def conversations_page():
    """对话历史页面"""
    return render_template('conversations.html', company_name=Config.COMPANY_NAME)

@app.route('/login')
def login_page():
    """登录页面"""
    # 如果已经登录，重定向到主页
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html', company_name=Config.COMPANY_NAME)

@app.route('/register')
def register_page():
    """注册页面"""
    # 如果已经登录，重定向到主页
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('register.html', company_name=Config.COMPANY_NAME)

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """处理用户问题（集成对话记忆功能）"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        answer_mode = data.get('answer_mode', 'hybrid')  # 获取回答模式
        
        if not question:
            return jsonify({'success': False, 'error': '问题不能为空'})
        
        # 获取当前用户ID
        user_id = session.get('username', 'anonymous')
        
        # 获取或创建活跃对话会话
        logger.info(f"用户 {user_id} 开始提问，检查对话状态")
        active_conversation = db_manager.get_active_conversation(user_id)
        if not active_conversation:
            # 创建新的对话会话
            logger.info(f"用户 {user_id} 没有活跃对话，创建新对话")
            conversation_id = db_manager.create_conversation(user_id, topic="新对话")
            active_conversation = {'conversation_id': conversation_id}
            logger.info(f"为用户 {user_id} 创建新对话: {conversation_id}")
        else:
            conversation_id = active_conversation['conversation_id']
            logger.info(f"用户 {user_id} 使用现有对话: {conversation_id}")
        
        # 检查是否是对话中的第一个问题，如果是则更新主题
        context_messages = db_manager.get_conversation_context(conversation_id, limit=5)
        if not context_messages:
            # 这是对话中的第一个问题，提取前五个字作为主题
            topic = question[:5] if len(question) >= 5 else question
            try:
                db_manager.update_conversation_topic(conversation_id, topic)
                logger.info(f"更新对话主题为: {topic}")
            except Exception as e:
                logger.warning(f"更新对话主题失败: {e}")
        else:
            logger.info(f"对话 {conversation_id} 已有 {len(context_messages)} 条消息，不是第一个问题")
        
        # 获取对话上下文（最近的消息）
        context_messages = db_manager.get_conversation_context(conversation_id, limit=5)
        
        # 构建上下文增强的问题
        enhanced_question = question
        if context_messages:
            # 如果有上下文，将最近的问题和回答作为上下文
            context_text = ""
            for msg in context_messages[-3:]:  # 只取最近3条消息
                if msg['message_type'] == 'user_question':
                    context_text += f"用户之前问过: {msg['content']}\n"
                elif msg['message_type'] == 'ai_response':
                    context_text += f"AI之前回答过: {msg['content']}\n"
            
            if context_text:
                enhanced_question = f"上下文信息:\n{context_text}\n\n当前问题: {question}"
        
        # 使用增强版RAG引擎处理问题（包含上下文）
        # 注意：问候语检测应该使用原始问题，而不是增强问题
        response = enhanced_rag_engine.process_question(
            question=question,  # 使用原始问题进行问候语检测
            session_id=conversation_id,
            user_id=user_id,
            answer_mode=answer_mode
        )
        
        # 记录用户问题到对话历史
        db_manager.add_conversation_message(
            conversation_id=conversation_id,
            user_id=user_id,
            message_type='user_question',
            content=question,
            context_tokens=enhanced_question,
            relevance_score=1.0
        )
        
        # 记录AI回答到对话历史
        db_manager.add_conversation_message(
            conversation_id=conversation_id,
            user_id=user_id,
            message_type='ai_response',
            content=response['answer'],
            context_tokens=question,  # 关联到用户问题
            relevance_score=response['confidence']
        )
        
        # 检测并更新对话主题
        if len(context_messages) >= 2:  # 至少有2条消息才开始检测主题
            all_messages = context_messages + [
                {'content': question, 'message_type': 'user_question'},
                {'content': response['answer'], 'message_type': 'ai_response'}
            ]
            topic = db_manager.detect_conversation_topic(all_messages)
            # 这里可以更新会话主题，但为了性能考虑，暂时不更新
        
        # 同时记录到原有的交互记录表（保持向后兼容）
        session_id = str(uuid.uuid4())
        print(f"DEBUG: 准备创建交互记录，session_id={session_id}, user_id={user_id}")
        
        try:
            interaction_id = db_manager.add_interaction(
                session_id=session_id,
                user_id=user_id,
                question=question,
                ai_response=response['answer'],
                confidence=response['confidence'],
                is_escalated=response['escalated'],
                ticket_id=response['ticket_id']
            )
            print(f"DEBUG: 交互记录创建成功，interaction_id={interaction_id}")
        except Exception as e:
            print(f"DEBUG: 交互记录创建失败: {e}")
            interaction_id = None
        
        print(f"DEBUG: 最终返回的interaction_id={interaction_id}")
        
        return jsonify({
            'success': True,
            'answer': response['answer'],
            'confidence': response['confidence'],
            'sources': response['sources'],
            'answer_type': response['answer_type'],
            'ticket_id': response['ticket_id'],
            'escalated': response['escalated'],
            'interaction_id': interaction_id,
            'conversation_id': conversation_id,  # 返回对话ID
            'has_context': len(context_messages) > 0  # 是否有上下文
        })
        
    except Exception as e:
        logger.error(f"处理问题失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/interactions/find', methods=['POST'])
def find_interaction():
    """根据问题内容和时间戳查找对应的交互记录"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        timestamp = data.get('timestamp', '')
        conversation_id = data.get('conversation_id', '')
        
        if not question or not timestamp:
            return jsonify({'success': False, 'error': '问题内容和时间戳不能为空'})
        
        # 查找对应的交互记录
        interaction = db_manager.find_interaction_by_content_and_time(question, timestamp, conversation_id)
        
        if interaction:
            return jsonify({
                'success': True,
                'interaction_id': interaction['id'],
                'question': interaction['question'],
                'ai_response': interaction['ai_response'],
                'confidence': interaction['confidence'],
                'rating': interaction.get('rating'),
                'timestamp': interaction['timestamp']
            })
        else:
            return jsonify({'success': False, 'error': '未找到对应的交互记录'})
            
    except Exception as e:
        logger.error(f"查找交互记录失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'error': '用户名和密码不能为空'})
        
        # 检查用户是否已存在
        if db_manager.check_user_exists(username):
            return jsonify({'success': False, 'error': '用户名已存在'})
        
        # 创建新用户
        if db_manager.create_user(username, password):
            return jsonify({'success': True, 'message': '注册成功'})
        else:
            return jsonify({'success': False, 'error': '注册失败，请稍后重试'})
            
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'error': '用户名和密码不能为空'})
        
        # 获取用户信息
        user = db_manager.get_user_by_username(username)
        
        if user and user['password'] == password:
            # 登录成功，设置session
            session['user_id'] = user['id']
            session['username'] = user['username']
            session.permanent = True
            
            # 登录成功后自动创建新对话
            try:
                logger.info(f"用户 {username} 登录成功，开始处理对话管理")
                
                # 关闭之前的活跃对话（如果有的话）
                active_conversation = db_manager.get_active_conversation(username)
                if active_conversation:
                    logger.info(f"发现用户 {username} 的活跃对话: {active_conversation['conversation_id']}")
                    close_result = db_manager.close_conversation(active_conversation['conversation_id'])
                    if close_result:
                        logger.info(f"成功关闭用户 {username} 的旧对话: {active_conversation['conversation_id']}")
                    else:
                        logger.warning(f"关闭用户 {username} 的旧对话失败: {active_conversation['conversation_id']}")
                else:
                    logger.info(f"用户 {username} 没有活跃对话")
                
                # 创建新对话，主题暂时设为"新对话"
                new_conversation_id = db_manager.create_conversation(username, topic="新对话")
                
                if new_conversation_id:
                    logger.info(f"用户 {username} 登录成功，自动创建新对话: {new_conversation_id}")
                    
                    # 验证新对话是否真的创建成功
                    verify_conversation = db_manager.get_active_conversation(username)
                    if verify_conversation:
                        logger.info(f"验证成功：新对话 {new_conversation_id} 已创建并设为活跃状态")
                    else:
                        logger.error(f"验证失败：新对话 {new_conversation_id} 创建后无法获取")
                else:
                    logger.warning(f"用户 {username} 登录成功，但创建新对话失败")
                    
            except Exception as e:
                logger.error(f"用户 {username} 登录后创建新对话失败: {e}")
                # 不影响登录流程，只记录错误
            
            return jsonify({'success': True, 'message': '登录成功'})
        else:
            return jsonify({'success': False, 'error': '用户名或密码错误'})
            
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/logout', methods=['POST'])
def logout():
    """用户退出"""
    try:
        # 清除session
        session.clear()
        return jsonify({'success': True, 'message': '退出成功'})
        
    except Exception as e:
        logger.error(f"用户退出失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check-login')
def check_login():
    """检查登录状态"""
    try:
        if 'user_id' in session and 'username' in session:
            username = session['username']
            
            # 检查是否需要强制创建新对话（通过URL参数控制）
            force_new = request.args.get('force_new', 'false').lower() == 'true'
            
            if force_new:
                try:
                    logger.info(f"用户 {username} 请求强制创建新对话")
                    active_conversation = db_manager.get_active_conversation(username)
                    
                    if active_conversation:
                        # 关闭旧对话
                        logger.info(f"关闭用户 {username} 的旧对话: {active_conversation['conversation_id']}")
                        db_manager.close_conversation(active_conversation['conversation_id'])
                    
                    # 创建新对话
                    logger.info(f"为用户 {username} 创建新对话")
                    new_conversation_id = db_manager.create_conversation(username, topic="新对话")
                    if new_conversation_id:
                        logger.info(f"成功为用户 {username} 创建新对话: {new_conversation_id}")
                        return jsonify({
                            'logged_in': True,
                            'user_id': session['user_id'],
                            'username': session['username'],
                            'new_conversation_id': new_conversation_id
                        })
                    else:
                        logger.warning(f"为用户 {username} 创建新对话失败")
                        
                except Exception as e:
                    logger.error(f"强制创建新对话失败: {e}")
            
            return jsonify({
                'logged_in': True,
                'user_id': session['user_id'],
                'username': session['username']
            })
        else:
            return jsonify({'logged_in': False})
            
    except Exception as e:
        logger.error(f"检查登录状态失败: {e}")
        return jsonify({'logged_in': False})

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """提交用户反馈"""
    try:
        data = request.get_json()
        interaction_id = data.get('interaction_id')
        rating = data.get('rating')  # 改为rating以匹配前端
        username = session.get('username', 'anonymous')
        
        if not interaction_id or rating not in [1, 2, 3, 4, 5]:
            return jsonify({'error': '参数错误'}), 400
        
        # 确保interaction_id是整数
        try:
            interaction_id = int(interaction_id)
        except (ValueError, TypeError):
            return jsonify({'error': '交互ID格式错误'}), 400
        
        # 更新交互记录的评分
        db_manager.update_feedback(interaction_id, rating)
        
        # 更新连续低分计数
        consecutive_count = db_manager.update_consecutive_low_ratings(username, rating)
        
        return jsonify({
            'success': True, 
            'message': '反馈提交成功',
            'consecutiveCount': consecutive_count
        })
        
    except Exception as e:
        logger.error(f"提交反馈失败: {e}")
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500

@app.route('/api/revise', methods=['POST'])
def revise_answer():
    """重新生成回答（支持满意度反馈）"""
    try:
        data = request.get_json()
        interaction_id = data.get('interaction_id')
        feedback_score = data.get('feedback_score')  # 新增：获取满意度评分
        
        if not interaction_id:
            return jsonify({'error': '参数错误'}), 400
        
        # 确保interaction_id是整数
        try:
            interaction_id = int(interaction_id)
        except (ValueError, TypeError):
            return jsonify({'error': '交互ID格式错误'}), 400
        
        # 获取原始交互记录
        original_interaction = db_manager.get_interaction_by_id(interaction_id)
        if not original_interaction:
            return jsonify({'error': '交互记录不存在'}), 404
        
        # 如果有满意度评分，先更新到数据库
        if feedback_score is not None:
            db_manager.update_feedback(interaction_id, feedback_score)
        
        # 重新处理问题，传入满意度反馈
        result = enhanced_rag_engine.process_question(
            question=original_interaction['question'],
            answer_mode='hybrid',  # 默认使用混合模式
            session_id=original_interaction['session_id'],
            user_id=original_interaction['user_id']
        )
        
        # 保存重新回答记录
        feedback_text = data.get('feedback', '用户要求重新回答')  # 获取用户反馈文本
        db_manager.add_revision(
            interaction_id=interaction_id,
            feedback=feedback_text,
            new_answer=result['answer'],
            rating=feedback_score
        )
        
        return jsonify({
            'success': True,
            'new_answer': result['answer'],
            'confidence': result['confidence'],
            'sources': result['sources'],
            'ticket_id': result.get('ticket_id'),
            'escalated': result.get('escalated', False),
            'interaction_id': interaction_id,  # 使用原始的interaction_id
            'answer_type': result.get('answer_type', 'ai_only')
        })
        
    except Exception as e:
        logger.error(f"重新生成回答失败: {e}")
        return jsonify({'error': '服务器内部错误'}), 500

# 管理后台API路由
@app.route('/admin/stats')
@login_required
def admin_stats():
    """获取管理后台统计信息"""
    try:
        stats = db_manager.get_admin_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取管理统计信息失败: {e}")
        return jsonify({'error': '获取统计信息失败'}), 500

@app.route('/admin/knowledge/list')
@login_required
def admin_knowledge_list():
    """获取分页知识库列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        sort_by = request.args.get('sort_by', 'updated')
        
        result = db_manager.get_knowledge_list_paginated(
            page, page_size, search, category, sort_by
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}")
        return jsonify({'error': '获取知识库列表失败'}), 500

@app.route('/admin/knowledge', methods=['POST'])
@login_required
def admin_add_knowledge():
    """添加知识条目"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        category = data.get('category', '').strip()
        content = data.get('content', '').strip()
        tags = data.get('tags', '').strip()
        
        if not title or not category or not content:
            return jsonify({'error': '标题、分类和内容不能为空'}), 400
        
        if len(title) > 200:
            return jsonify({'error': '标题长度不能超过200字符'}), 400
        
        if len(content) > 10000:
            return jsonify({'error': '内容长度不能超过10000字符'}), 400
        
        # 添加知识条目
        knowledge_id = db_manager.add_knowledge(title, category, content, tags)
        
        return jsonify({
            'message': '知识条目添加成功',
            'knowledge_id': knowledge_id
        })
        
    except Exception as e:
        logger.error(f"添加知识条目失败: {e}")
        return jsonify({'error': '添加知识条目失败'}), 500

@app.route('/admin/knowledge/<int:knowledge_id>', methods=['GET'])
@login_required
def admin_get_knowledge(knowledge_id):
    """获取单个知识条目"""
    try:
        knowledge = db_manager.get_knowledge_by_id(knowledge_id)
        if not knowledge:
            return jsonify({'error': '知识条目不存在'}), 404
        
        # 移除embedding字段，避免JSON序列化错误
        if 'embedding' in knowledge:
            del knowledge['embedding']
        
        return jsonify(knowledge)
        
    except Exception as e:
        logger.error(f"获取知识条目失败: {e}")
        return jsonify({'error': '获取知识条目失败'}), 500

@app.route('/admin/knowledge/<int:knowledge_id>', methods=['PUT'])
@login_required
def admin_update_knowledge(knowledge_id):
    """更新知识条目"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        category = data.get('category', '').strip()
        content = data.get('content', '').strip()
        tags = data.get('tags', '').strip()
        
        # 参数验证
        if not title or not category or not content:
            return jsonify({'error': '标题、分类和内容不能为空'}), 400
        
        if len(title) > 200:
            return jsonify({'error': '标题长度不能超过200字符'}), 400
        
        if len(content) > 10000:
            return jsonify({'error': '内容长度不能超过10000字符'}), 400
        
        # 检查知识条目是否存在
        existing = db_manager.get_knowledge_by_id(knowledge_id)
        if not existing:
            return jsonify({'error': '知识条目不存在'}), 404
        
        # 更新知识条目
        db_manager.update_knowledge(knowledge_id, title, category, content, tags)
        
        return jsonify({'message': '知识条目更新成功'})
        
    except Exception as e:
        logger.error(f"更新知识条目失败: {e}")
        return jsonify({'error': '更新知识条目失败'}), 500

@app.route('/admin/knowledge/<int:knowledge_id>', methods=['DELETE'])
@login_required
def admin_delete_knowledge(knowledge_id):
    """删除知识条目"""
    try:
        # 检查知识条目是否存在
        existing = db_manager.get_knowledge_by_id(knowledge_id)
        if not existing:
            return jsonify({'error': '知识条目不存在'}), 404
        
        # 删除知识条目
        db_manager.delete_knowledge(knowledge_id)
        
        return jsonify({'message': '知识条目删除成功'})
        
    except Exception as e:
        logger.error(f"删除知识条目失败: {e}")
        return jsonify({'error': '删除知识条目失败'}), 500

@app.route('/admin/knowledge/import', methods=['POST'])
@login_required
def admin_import_knowledge():
    """批量导入知识库"""
    try:
        data = request.get_json()
        import_data = data.get('data', [])
        
        if not isinstance(import_data, list) or len(import_data) == 0:
            return jsonify({'error': '导入数据格式不正确'}), 400
        
        # 批量导入知识条目
        imported_count = db_manager.import_knowledge_batch(import_data)
        
        return jsonify({
            'message': f'成功导入 {imported_count} 条知识条目',
            'imported_count': imported_count
        })
        
    except Exception as e:
        logger.error(f"批量导入知识库失败: {e}")
        return jsonify({'error': '批量导入失败'}), 500

@app.route('/admin/categories')
@login_required
def admin_categories():
    """获取所有分类列表"""
    try:
        categories = db_manager.get_all_categories()
        return jsonify(categories)
    except Exception as e:
        logger.error(f"获取分类列表失败: {e}")
        return jsonify({'error': '获取分类列表失败'}), 500

@app.route('/admin/interactions')
@require_admin_access
@require_permission('can_view_interactions')
def admin_interactions():
    """用户交互查询页面"""
    return render_template('interactions.html', company_name=Config.COMPANY_NAME)

@app.route('/admin/interactions/list')
@login_required
def admin_interactions_list():
    """获取交互记录列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        search = request.args.get('search', '')
        user_filter = request.args.get('user', '')
        rating_filter = request.args.get('rating', '')
        sort_by = request.args.get('sort_by', 'time')
        
        # 获取交互记录
        result = db_manager.get_interactions_list(
            page=page,
            page_size=page_size,
            search=search,
            user_filter=user_filter,
            rating_filter=rating_filter,
            sort_by=sort_by
        )
        
        return jsonify({
            'success': True,
            'interactions': result['interactions'],
            'total': result['total'],
            'page': page,
            'pages': result['pages']
        })
        
    except Exception as e:
        logger.error(f"获取交互记录失败: {e}")
        return jsonify({'success': False, 'message': '获取交互记录失败'}), 500

@app.route('/admin/interactions/<int:interaction_id>')
@login_required
def admin_interaction_detail(interaction_id):
    """获取交互详情"""
    try:
        interaction = db_manager.get_interaction_detail(interaction_id)
        if interaction:
            return jsonify({
                'success': True,
                'interaction': interaction
            })
        else:
            return jsonify({'success': False, 'message': '交互记录不存在'}), 404
            
    except Exception as e:
        logger.error(f"获取交互详情失败: {e}")
        return jsonify({'success': False, 'message': '获取交互详情失败'}), 500

@app.route('/admin/users')
@login_required
def admin_users():
    """获取用户列表"""
    try:
        users = db_manager.get_users_list()
        return jsonify({
            'success': True,
            'users': users
        })
        
    except Exception as e:
        logger.error(f"获取用户列表失败: {e}")
        return jsonify({'success': False, 'message': '获取用户列表失败'}), 500

@app.route('/admin/interactions/export')
@require_admin_access
@require_permission('can_export_data')
def admin_interactions_export():
    """导出交互记录"""
    try:
        search = request.args.get('search', '')
        user_filter = request.args.get('user', '')
        rating_filter = request.args.get('rating', '')
        sort_by = request.args.get('sort_by', 'time')
        
        # 获取所有符合条件的交互记录
        result = db_manager.get_interactions_list(
            page=1,
            page_size=10000,  # 导出所有记录
            search=search,
            user_filter=user_filter,
            rating_filter=rating_filter,
            sort_by=sort_by
        )
        
        # 生成CSV文件
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow(['时间', '用户', '问题', '回答', '评分', '重新回答次数', '重新回答详情'])
        
        # 写入数据
        for interaction in result['interactions']:
            revisions_text = ''
            if interaction.get('revisions'):
                for i, revision in enumerate(interaction['revisions'], 1):
                    revisions_text += f"第{i}次: {revision['feedback']} -> {revision['new_answer']}; "
            
            writer.writerow([
                interaction['created_at'],
                interaction.get('username', '未知用户'),
                interaction['question'],
                interaction['answer'],
                interaction.get('rating', '未评分'),
                interaction.get('revision_count', 0),
                revisions_text
            ])
        
        output.seek(0)
        
        # 创建响应
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=interactions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
        
        return response
        
    except Exception as e:
        logger.error(f"导出交互记录失败: {e}")
        return jsonify({'success': False, 'message': '导出失败'}), 500

@app.route('/api/health')
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        db_manager.connection.ping(reconnect=True)
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500

# 权限管理相关路由
@app.route('/admin/permissions')
@require_admin_access
@require_permission('can_manage_permissions')
def permissions_page():
    """权限管理页面"""
    return render_template('permissions.html', company_name=Config.COMPANY_NAME)

@app.route('/admin/permissions/list')
@require_admin_access
@require_permission('can_manage_permissions')
def get_permissions_list():
    """获取权限列表"""
    try:
        permissions = db_manager.get_all_permissions()
        return jsonify({
            'success': True,
            'permissions': permissions
        })
    except Exception as e:
        logger.error(f"获取权限列表失败: {e}")
        return jsonify({'success': False, 'message': '获取权限列表失败'}), 500

@app.route('/admin/permissions/create', methods=['POST'])
@require_admin_access
@require_permission('can_manage_permissions')
def create_permission():
    """创建用户权限"""
    try:
        data = request.get_json()
        username = data.get('username')
        permissions_data = data.get('permissions', {})
        
        if not username:
            return jsonify({'success': False, 'message': '用户名不能为空'}), 400
        
        # 检查用户是否存在
        user = db_manager.get_user_by_username(username)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 400
        
        # 检查权限是否已存在
        existing_permission = db_manager.get_user_permissions(username)
        if existing_permission:
            return jsonify({'success': False, 'message': '用户权限已存在'}), 400
        
        # 创建权限
        db_manager.create_user_permissions(username, permissions_data, session.get('username'))
        
        return jsonify({'success': True, 'message': '权限创建成功'})
        
    except Exception as e:
        logger.error(f"创建权限失败: {e}")
        return jsonify({'success': False, 'message': '创建权限失败'}), 500

@app.route('/admin/permissions/update', methods=['PUT'])
@require_admin_access
@require_permission('can_manage_permissions')
def update_permission():
    """更新用户权限"""
    try:
        data = request.get_json()
        username = data.get('username')
        permissions_data = data.get('permissions', {})
        
        if not username:
            return jsonify({'success': False, 'message': '用户名不能为空'}), 400
        
        # 检查权限是否存在
        existing_permission = db_manager.get_user_permissions(username)
        if not existing_permission:
            return jsonify({'success': False, 'message': '用户权限不存在'}), 400
        
        # 更新权限
        success = db_manager.update_user_permissions(username, permissions_data, session.get('username'))
        
        if success:
            return jsonify({'success': True, 'message': '权限更新成功'})
        else:
            return jsonify({'success': False, 'message': '权限更新失败'}), 500
        
    except Exception as e:
        logger.error(f"更新权限失败: {e}")
        return jsonify({'success': False, 'message': '更新权限失败'}), 500

@app.route('/admin/permissions/delete', methods=['DELETE'])
@require_admin_access
@require_permission('can_manage_permissions')
def delete_permission():
    """删除用户权限"""
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({'success': False, 'message': '用户名不能为空'}), 400
        
        # 删除权限
        success = db_manager.delete_user_permissions(username)
        
        if success:
            return jsonify({'success': True, 'message': '权限删除成功'})
        else:
            return jsonify({'success': False, 'message': '权限删除失败'}), 500
        
    except Exception as e:
        logger.error(f"删除权限失败: {e}")
        return jsonify({'success': False, 'message': '删除权限失败'}), 500

@app.route('/admin/users/all')
@require_admin_access
@require_permission('can_manage_permissions')
def get_all_users():
    """获取所有用户列表"""
    try:
        users = db_manager.get_all_users_with_permissions()
        return jsonify({
            'success': True,
            'users': users
        })
    except Exception as e:
        logger.error(f"获取所有用户失败: {e}")
        return jsonify({'success': False, 'message': '获取用户列表失败'}), 500

@app.route('/admin/users/create', methods=['POST'])
@require_admin_access
@require_permission('can_manage_permissions')
def create_user():
    """创建新用户"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        permissions = data.get('permissions', {})
        
        # 验证输入
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        if len(password) < 3:
            return jsonify({'success': False, 'message': '密码长度至少3位'}), 400
        
        # 检查用户是否已存在
        if db_manager.check_user_exists(username):
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        # 创建用户
        success = db_manager.create_user(username, password)
        if not success:
            return jsonify({'success': False, 'message': '创建用户失败'}), 500
        
        # 如果有权限设置，创建权限记录
        if any(permissions.values()):
            try:
                db_manager.create_user_permissions(username, permissions, created_by=session.get('username'))
            except Exception as e:
                logger.warning(f"创建用户权限失败: {e}")
                # 权限创建失败不影响用户创建
        
        return jsonify({
            'success': True,
            'message': '用户创建成功'
        })
        
    except Exception as e:
        logger.error(f"创建用户失败: {e}")
        return jsonify({'success': False, 'message': '创建用户失败'}), 500

# 对话记忆相关API端点
@app.route('/api/conversations/history')
@login_required
def get_conversation_history():
    """获取用户的对话历史"""
    try:
        user_id = session.get('username')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取用户对话历史
        conversations = db_manager.get_user_conversation_history(user_id, limit=20)
        
        return jsonify({
            'success': True,
            'conversations': conversations
        })
        
    except Exception as e:
        logger.error(f"获取对话历史失败: {e}")
        return jsonify({'success': False, 'message': '获取对话历史失败'}), 500

@app.route('/api/conversations/<conversation_id>/messages')
@login_required
def get_conversation_messages(conversation_id):
    """获取特定对话的消息详情"""
    try:
        user_id = session.get('username')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取对话消息
        messages = db_manager.get_conversation_context(conversation_id, limit=50)
        
        # 检查用户是否有权限访问此对话
        if messages and messages[0]['user_id'] != user_id:
            return jsonify({'success': False, 'message': '无权访问此对话'}), 403
        
        return jsonify({
            'success': True,
            'messages': messages
        })
        
    except Exception as e:
        logger.error(f"获取对话消息失败: {e}")
        return jsonify({'success': False, 'message': '获取对话消息失败'}), 500

@app.route('/api/conversations/current')
@login_required
def get_current_conversation():
    """获取当前活跃的对话会话"""
    try:
        user_id = session.get('username')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取当前活跃对话
        active_conversation = db_manager.get_active_conversation(user_id)
        
        if active_conversation:
            # 获取对话消息
            messages = db_manager.get_conversation_context(active_conversation['conversation_id'], limit=10)
            active_conversation['messages'] = messages
            active_conversation['message_count'] = len(messages)
        
        return jsonify({
            'success': True,
            'conversation': active_conversation
        })
        
    except Exception as e:
        logger.error(f"获取当前对话失败: {e}")
        return jsonify({'success': False, 'message': '获取当前对话失败'}), 500

@app.route('/api/conversations/close', methods=['POST'])
@login_required
def close_current_conversation():
    """关闭当前对话会话"""
    try:
        user_id = session.get('username')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        # 获取当前活跃对话
        active_conversation = db_manager.get_active_conversation(user_id)
        
        if not active_conversation:
            return jsonify({'success': False, 'message': '没有活跃的对话会话'}), 404
        
        # 关闭对话
        success = db_manager.close_conversation(active_conversation['conversation_id'])
        
        if success:
            return jsonify({'success': True, 'message': '对话会话已关闭'})
        else:
            return jsonify({'success': False, 'message': '关闭对话会话失败'}), 500
        
    except Exception as e:
        logger.error(f"关闭对话会话失败: {e}")
        return jsonify({'success': False, 'message': '关闭对话会话失败'}), 500

@app.route('/api/conversations/new', methods=['POST'])
@login_required
def start_new_conversation():
    """开始新的对话会话"""
    try:
        user_id = session.get('username')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.get_json()
        topic = data.get('topic', '新对话')
        
        # 关闭当前活跃对话（如果有）
        active_conversation = db_manager.get_active_conversation(user_id)
        if active_conversation:
            db_manager.close_conversation(active_conversation['conversation_id'])
        
        # 创建新对话
        conversation_id = db_manager.create_conversation(user_id, topic=topic)
        
        if conversation_id:
            return jsonify({
                'success': True,
                'message': '新对话会话已创建',
                'conversation_id': conversation_id
            })
        else:
            return jsonify({'success': False, 'message': '创建新对话会话失败'}), 500
        
    except Exception as e:
        logger.error(f"创建新对话会话失败: {e}")
        return jsonify({'success': False, 'message': '创建新对话会话失败'}), 500

@app.route('/api/conversations/delete', methods=['POST'])
@login_required
def delete_conversation():
    """删除指定的对话会话"""
    try:
        user_id = session.get('username')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            return jsonify({'success': False, 'message': '对话ID不能为空'}), 400
        
        # 验证对话是否属于当前用户
        conversation = db_manager.get_conversation_by_id(conversation_id)
        if not conversation or conversation['user_id'] != user_id:
            return jsonify({'success': False, 'message': '对话不存在或无权限删除'}), 403
        
        # 删除对话及其所有消息
        success = db_manager.delete_conversation(conversation_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '对话已删除'
            })
        else:
            return jsonify({'success': False, 'message': '删除对话失败'}), 500
        
    except Exception as e:
        logger.error(f"删除对话失败: {e}")
        return jsonify({'success': False, 'message': '删除对话失败'}), 500

@app.route('/api/conversations/force-new', methods=['POST'])
@login_required
def force_new_conversation():
    """强制创建新对话会话"""
    try:
        user_id = session.get('username')
        if not user_id:
            return jsonify({'success': False, 'message': '请先登录'}), 401
        
        data = request.get_json()
        topic = data.get('topic', '新对话')
        
        # 强制关闭当前活跃对话（如果有）
        active_conversation = db_manager.get_active_conversation(user_id)
        if active_conversation:
            logger.info(f"强制关闭用户 {user_id} 的旧对话: {active_conversation['conversation_id']}")
            db_manager.close_conversation(active_conversation['conversation_id'])
        
        # 强制创建新对话
        logger.info(f"为用户 {user_id} 强制创建新对话")
        conversation_id = db_manager.create_conversation(user_id, topic=topic)
        
        if conversation_id:
            logger.info(f"成功为用户 {user_id} 创建新对话: {conversation_id}")
            return jsonify({
                'success': True,
                'message': '新对话已创建',
                'conversation_id': conversation_id
            })
        else:
            logger.warning(f"为用户 {user_id} 创建新对话失败")
            return jsonify({'success': False, 'message': '创建新对话失败'}), 500
        
    except Exception as e:
        logger.error(f"强制创建新对话失败: {e}")
        return jsonify({'success': False, 'message': '创建新对话失败'}), 500

def init_database():
    """初始化数据库"""
    try:
        db_manager.create_tables()
        logger.info("数据库初始化成功")
        
        # 不再自动添加任何示例数据，让用户自己添加
        knowledge_count = db_manager.get_knowledge_count()
        logger.info(f"知识库当前有 {knowledge_count} 个条目")
        logger.info("请通过管理界面添加您需要的知识条目")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

if __name__ == '__main__':
    try:
        # 初始化数据库
        init_database()
        
        # 启动应用
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=Config.DEBUG
        )
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        exit(1)

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import uuid
import logging
from datetime import datetime
from config import Config
from db_utils import db_manager
from enhanced_rag_engine import enhanced_rag_engine

# 配置Flask应用
app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
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

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html', company_name=Config.COMPANY_NAME)

@app.route('/admin')
def admin_dashboard():
    """管理后台主页面"""
    return render_template('admin.html', company_name=Config.COMPANY_NAME)

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """处理用户问题，实现知识库优先的智能回复"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        
        # 生成会话ID和用户ID
        session_id = str(uuid.uuid4())
        user_id = "anonymous"  # 可以根据需要修改为实际的用户ID
        
        # 使用增强版RAG引擎处理问题
        result = enhanced_rag_engine.process_question(question, session_id, user_id)
        
        # 记录交互到数据库
        interaction_id = None
        try:
            interaction_id = db_manager.add_interaction(
                session_id=session_id,
                user_id=user_id,
                question=question,
                ai_response=result['answer'],
                confidence=result['confidence'],
                is_escalated=result['escalated'],
                ticket_id=result['ticket_id']
            )
        except Exception as e:
            logger.error(f"记录交互失败: {e}")
        
        # 构建响应
        response_data = {
            'response': result['answer'],
            'confidence': result['confidence'],
            'sources': result['sources'],
            'answer_type': result['answer_type'],
            'ticket_id': result['ticket_id'],
            'escalated': result['escalated'],
            'interaction_id': interaction_id
        }
        
        # 如果有工单，显示通知信息
        if result['ticket_id']:
            response_data['notification'] = f"由于置信度较低，已为您创建工单 {result['ticket_id']}，技术人员将尽快联系您。"
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"处理问题失败: {e}")
        return jsonify({'error': '处理问题失败，请稍后重试'}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """提交用户反馈"""
    try:
        data = request.get_json()
        interaction_id = data.get('interaction_id')
        score = data.get('score')
        
        if not interaction_id or score not in [1, 2, 3, 4, 5]:
            return jsonify({'error': '参数错误'}), 400
        
        # 更新交互记录的评分
        db_manager.update_feedback(interaction_id, score)
        
        return jsonify({'message': '反馈提交成功'})
        
    except Exception as e:
        logger.error(f"提交反馈失败: {e}")
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/api/revise', methods=['POST'])
def revise_answer():
    """重新生成回答（支持满意度反馈）"""
    try:
        data = request.get_json()
        interaction_id = data.get('interaction_id')
        feedback_score = data.get('feedback_score')  # 新增：获取满意度评分
        
        if not interaction_id:
            return jsonify({'error': '参数错误'}), 400
        
        # 获取原始交互记录
        original_interaction = db_manager.get_interaction_by_id(interaction_id)
        if not original_interaction:
            return jsonify({'error': '交互记录不存在'}), 404
        
        # 如果有满意度评分，先更新到数据库
        if feedback_score is not None:
            db_manager.update_feedback(interaction_id, feedback_score)
        
        # 重新处理问题，传入满意度反馈
        result = enhanced_rag_engine.process_question(
            original_interaction['question'], 
            original_interaction['session_id'], 
            original_interaction['user_id'],
            feedback_score  # 传入满意度评分
        )
        
        return jsonify({
            'response': result['answer'],
            'confidence': result['confidence'],
            'sources': result['sources'],
            'ticket_id': result.get('ticket_id'),
            'escalated': result.get('escalated', False),
            'interaction_id': result.get('interaction_id'),
            'answer_type': result.get('answer_type', 'ai_only')
        })
        
    except Exception as e:
        logger.error(f"重新生成回答失败: {e}")
        return jsonify({'error': '服务器内部错误'}), 500

# 管理后台API路由
@app.route('/admin/stats')
def admin_stats():
    """获取管理后台统计信息"""
    try:
        stats = db_manager.get_admin_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取管理统计信息失败: {e}")
        return jsonify({'error': '获取统计信息失败'}), 500

@app.route('/admin/knowledge/list')
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
def admin_get_knowledge(knowledge_id):
    """获取单个知识条目"""
    try:
        knowledge = db_manager.get_knowledge_by_id(knowledge_id)
        if not knowledge:
            return jsonify({'error': '知识条目不存在'}), 404
        
        return jsonify(knowledge)
        
    except Exception as e:
        logger.error(f"获取知识条目失败: {e}")
        return jsonify({'error': '获取知识条目失败'}), 500

@app.route('/admin/knowledge/<int:knowledge_id>', methods=['PUT'])
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
def admin_categories():
    """获取所有分类列表"""
    try:
        categories = db_manager.get_all_categories()
        return jsonify(categories)
    except Exception as e:
        logger.error(f"获取分类列表失败: {e}")
        return jsonify({'error': '获取分类列表失败'}), 500

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

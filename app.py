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

@app.route('/api/ask', methods=['POST'])
def ask_question():
    """处理用户问题"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': '问题不能为空'}), 400
        
        if len(question) > Config.MAX_QUESTION_LENGTH:
            return jsonify({'error': f'问题长度不能超过{Config.MAX_QUESTION_LENGTH}字符'}), 400
        
        # 获取或创建会话ID
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        # 获取用户ID（这里简化处理，实际项目中应该从认证系统获取）
        user_id = session.get('user_id', 'anonymous')
        
        # 使用增强版RAG引擎处理问题
        result = enhanced_rag_engine.process_question(question, session['session_id'], user_id)
        
        return jsonify({
            'response': result['answer'],
            'confidence': result['confidence'],
            'sources': result['sources'],
            'ticket_id': result.get('ticket_id'),
            'escalated': result.get('escalated', False)
        })
        
    except Exception as e:
        logger.error(f"处理问题失败: {e}")
        return jsonify({'error': '服务器内部错误'}), 500

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

@app.route('/admin/knowledge', methods=['GET', 'POST'])
def manage_knowledge():
    """知识库管理页面"""
    if request.method == 'GET':
        return render_template('admin_knowledge.html', company_name=Config.COMPANY_NAME)
    
    # POST请求：添加知识条目
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category = data.get('category', '').strip()
        
        if not title or not content:
            return jsonify({'error': '标题和内容不能为空'}), 400
        
        # 添加知识条目
        knowledge_id = db_manager.add_knowledge_item(title, content, category)
        
        return jsonify({
            'message': '知识条目添加成功',
            'knowledge_id': knowledge_id
        })
        
    except Exception as e:
        logger.error(f"添加知识条目失败: {e}")
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/admin/stats')
def get_stats():
    """获取系统统计信息"""
    try:
        stats = db_manager.get_interaction_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return jsonify({'error': '服务器内部错误'}), 500

@app.route('/admin/knowledge/list')
def list_knowledge():
    """获取知识库列表"""
    try:
        knowledge_list = db_manager.get_knowledge_list()
        return jsonify(knowledge_list)
    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}")
        return jsonify({'error': '服务器内部错误'}), 500

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
        
        # 添加一些示例知识条目
        sample_knowledge = [
            {
                'title': '网络连接问题排查',
                'content': '1. 检查网线连接是否正常\n2. 确认网络适配器已启用\n3. 运行网络诊断工具\n4. 重启网络设备',
                'category': '网络'
            },
            {
                'title': 'Outlook邮件配置',
                'content': '1. 打开Outlook\n2. 添加新账户\n3. 输入邮箱地址和密码\n4. 选择IMAP或POP3协议\n5. 配置服务器设置',
                'category': '软件'
            },
            {
                'title': '打印机无法打印',
                'content': '1. 检查打印机电源和连接\n2. 确认打印机驱动已安装\n3. 检查打印队列\n4. 重启打印服务',
                'category': '硬件'
            }
        ]
        
        for item in sample_knowledge:
            db_manager.add_knowledge_item(item['title'], item['content'], item['category'])
        
        logger.info("示例知识条目添加成功")
        
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

// 全局变量
let currentInteractionId = null;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    // 绑定字符计数
    const questionInput = document.getElementById('questionInput');
    const charCount = document.getElementById('charCount');
    
    questionInput.addEventListener('input', function() {
        const length = this.value.length;
        charCount.textContent = `${length}/500`;
        
        // 字符数接近限制时的视觉提示
        if (length > 450) {
            charCount.style.color = '#dc3545';
        } else if (length > 400) {
            charCount.style.color = '#ffc107';
        } else {
            charCount.style.color = '#6c757d';
        }
    });
    
    // 绑定回车键发送
    questionInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuestion();
        }
    });
    
    // 绑定知识表单提交
    const knowledgeForm = document.getElementById('knowledgeForm');
    knowledgeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        addKnowledgeItem();
    });
}

// 发送问题
async function sendQuestion() {
    const questionInput = document.getElementById('questionInput');
    const sendBtn = document.getElementById('sendBtn');
    const question = questionInput.value.trim();
    
    if (!question) {
        showNotification('请输入您的问题', 'warning');
        return;
    }
    
    // 禁用发送按钮
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发送中...';
    
    try {
        // 添加用户消息到聊天界面
        addUserMessage(question);
        
        // 清空输入框
        questionInput.value = '';
        document.getElementById('charCount').textContent = '0/500';
        
        // 调用API
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 添加AI回复
            addAIMessage(data.response, data.confidence, data.sources, data.ticket_id, data.escalated);
        } else {
            throw new Error(data.error || '请求失败');
        }
        
    } catch (error) {
        console.error('发送问题失败:', error);
        addAIMessage('抱歉，处理您的问题时出现错误，请稍后重试。', 0, [], null, false);
        showNotification('发送失败，请重试', 'error');
    } finally {
        // 恢复发送按钮
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 发送';
    }
}

// 添加用户消息
function addUserMessage(question) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    
    const currentTime = new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-user"></i>
        </div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(question)}</div>
            <div class="message-time">${currentTime}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// 添加AI消息
function addAIMessage(response, confidence, sources, ticketId, escalated) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';
    
    const currentTime = new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    // 构建消息内容
    let messageContent = escapeHtml(response);
    
    // 添加置信度信息
    if (confidence > 0) {
        messageContent += `<div class="confidence-info">置信度: ${(confidence * 100).toFixed(1)}%</div>`;
    }
    
    // 添加来源信息
    if (sources && sources.length > 0) {
        messageContent += `<div class="sources-info">参考来源: ${sources.join(', ')}</div>`;
    }
    
    // 添加工单信息
    if (ticketId) {
        messageContent += `<div class="ticket-info">工单号: ${ticketId}</div>`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-text">${messageContent}</div>
            <div class="message-time">${currentTime}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// 滚动到底部
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 显示统计信息
async function showStats() {
    const modal = document.getElementById('statsModal');
    modal.style.display = 'block';
    
    try {
        const response = await fetch('/admin/stats');
        const stats = await response.json();
        
        if (response.ok) {
            document.getElementById('totalInteractions').textContent = stats.total_interactions || 0;
            document.getElementById('escalatedCount').textContent = stats.escalated_count || 0;
            document.getElementById('avgConfidence').textContent = (stats.avg_confidence || 0) + '%';
            document.getElementById('knowledgeCount').textContent = stats.knowledge_count || 0;
        } else {
            throw new Error(stats.error || '获取统计信息失败');
        }
    } catch (error) {
        console.error('获取统计信息失败:', error);
        showNotification('获取统计信息失败', 'error');
    }
}

// 显示管理界面
function showAdmin() {
    const modal = document.getElementById('adminModal');
    modal.style.display = 'block';
    
    // 默认显示添加知识标签页
    switchTab('add');
}

// 关闭模态框
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.style.display = 'none';
}

// 切换标签页
function switchTab(tabName) {
    // 隐藏所有标签页内容
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));
    
    // 移除所有标签页按钮的active状态
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => btn.classList.remove('active'));
    
    // 显示选中的标签页
    document.getElementById(tabName + 'Tab').classList.add('active');
    
    // 激活对应的按钮
    event.target.classList.add('active');
    
    // 如果是知识列表标签页，加载数据
    if (tabName === 'list') {
        loadKnowledgeList();
    }
}

// 添加知识条目
async function addKnowledgeItem() {
    const title = document.getElementById('title').value.trim();
    const category = document.getElementById('category').value.trim();
    const content = document.getElementById('content').value.trim();
    
    if (!title || !content) {
        showNotification('请填写标题和内容', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/admin/knowledge', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, category, content })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('知识条目添加成功', 'success');
            // 清空表单
            document.getElementById('knowledgeForm').reset();
            // 刷新知识列表
            if (document.getElementById('listTab').classList.contains('active')) {
                loadKnowledgeList();
            }
        } else {
            throw new Error(data.error || '添加失败');
        }
        
    } catch (error) {
        console.error('添加知识条目失败:', error);
        showNotification('添加失败，请重试', 'error');
    }
}

// 加载知识列表
async function loadKnowledgeList() {
    const knowledgeList = document.getElementById('knowledgeList');
    
    try {
        const response = await fetch('/admin/knowledge/list');
        const data = await response.json();
        
        if (response.ok) {
            if (data.length === 0) {
                knowledgeList.innerHTML = '<p class="no-data">暂无知识条目</p>';
                return;
            }
            
            knowledgeList.innerHTML = data.map(item => `
                <div class="knowledge-item">
                    <h4>${escapeHtml(item.title)}</h4>
                    ${item.category ? `<span class="category">${escapeHtml(item.category)}</span>` : ''}
                    <div class="content">${escapeHtml(item.content.substring(0, 200))}${item.content.length > 200 ? '...' : ''}</div>
                </div>
            `).join('');
        } else {
            throw new Error(data.error || '获取知识列表失败');
        }
        
    } catch (error) {
        console.error('获取知识列表失败:', error);
        knowledgeList.innerHTML = '<p class="error">加载失败，请重试</p>';
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => notification.classList.add('show'), 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 获取通知图标
function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-circle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 点击模态框外部关闭
window.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// 添加通知样式
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        padding: 15px 20px;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        z-index: 10000;
        max-width: 300px;
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .notification-success {
        border-left: 4px solid #28a745;
    }
    
    .notification-error {
        border-left: 4px solid #dc3545;
    }
    
    .notification-warning {
        border-left: 4px solid #ffc107;
    }
    
    .notification-info {
        border-left: 4px solid #17a2b8;
    }
    
    .notification i {
        font-size: 1.2rem;
    }
    
    .notification-success i {
        color: #28a745;
    }
    
    .notification-error i {
        color: #dc3545;
    }
    
    .notification-warning i {
        color: #ffc107;
    }
    
    .notification-info i {
        color: #17a2b8;
    }
    
    .confidence-info,
    .sources-info,
    .ticket-info {
        margin-top: 10px;
        padding: 8px 12px;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 8px;
        font-size: 0.9rem;
        color: #667eea;
    }
    
    .ticket-info {
        background: rgba(220, 53, 69, 0.1);
        color: #dc3545;
    }
    
    .no-data,
    .error {
        text-align: center;
        padding: 40px;
        color: #6c757d;
    }
    
    .error {
        color: #dc3545;
    }
`;

// 注入通知样式
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);

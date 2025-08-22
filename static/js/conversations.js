// 对话历史页面JavaScript
let currentConversationId = null;
let conversations = [];
let filteredConversations = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadConversations();
    setupEventListeners();
});

// 设置事件监听器
function setupEventListeners() {
    // 搜索框输入事件
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterConversations(this.value);
        });
    }
}

// 加载对话列表
async function loadConversations() {
    try {
        const response = await fetch('/api/conversations/history');
        const data = await response.json();
        
        if (data.success) {
            conversations = data.conversations;
            filteredConversations = [...conversations];
            displayConversations();
            
            // 如果有活跃对话，自动选择第一个
            if (conversations.length > 0) {
                const activeConversation = conversations.find(c => c.status === 'active');
                if (activeConversation) {
                    selectConversation(activeConversation.conversation_id);
                }
            }
        } else {
            showNotification('加载对话列表失败: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('加载对话列表失败:', error);
        showNotification('加载对话列表失败，请检查网络连接', 'error');
    }
}

// 显示对话列表
function displayConversations() {
    const container = document.getElementById('conversationList');
    if (!container) return;
    
    if (filteredConversations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-comments"></i>
                <h3>暂无对话</h3>
                <p>开始您的第一个对话吧！</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = filteredConversations.map(conv => `
        <div class="conversation-item ${conv.conversation_id === currentConversationId ? 'active' : ''}" 
             onclick="selectConversation('${conv.conversation_id}')">
            <div class="conversation-header">
                <div class="conversation-topic">${conv.topic || '未命名对话'}</div>
                <div class="conversation-status status-${conv.status}">
                    ${conv.status === 'active' ? '活跃' : '已结束'}
                </div>
            </div>
            <div class="conversation-meta">
                <div>消息数: ${conv.message_count || 0}</div>
                <div>开始时间: ${formatTime(conv.start_time)}</div>
                <div>最后活跃: ${formatTime(conv.last_activity)}</div>
            </div>
            <div class="conversation-actions">
                <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); continueConversation('${conv.conversation_id}')">
                    <i class="fas fa-reply"></i> 继续对话
                </button>
                <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); viewConversation('${conv.conversation_id}')">
                    <i class="fas fa-eye"></i> 查看
                </button>
                ${conv.status === 'active' ? `
                    <button class="btn btn-sm btn-warning" onclick="event.stopPropagation(); closeConversation('${conv.conversation_id}')">
                        <i class="fas fa-times"></i> 结束
                    </button>
                ` : ''}
                <button class="btn btn-sm btn-danger" onclick="event.stopPropagation(); deleteConversation('${conv.conversation_id}')">
                    <i class="fas fa-trash"></i> 删除
                </button>
            </div>
        </div>
    `).join('');
}

// 过滤对话
function filterConversations(searchTerm) {
    if (!searchTerm.trim()) {
        filteredConversations = [...conversations];
    } else {
        const term = searchTerm.toLowerCase();
        filteredConversations = conversations.filter(conv => 
            conv.topic && conv.topic.toLowerCase().includes(term) ||
            conv.conversation_id.toLowerCase().includes(term)
        );
    }
    displayConversations();
}

// 选择对话
async function selectConversation(conversationId) {
    currentConversationId = conversationId;
    
    // 更新UI状态
    displayConversations();
    
    // 加载对话详情
    await loadConversationDetail(conversationId);
}

// 加载对话详情
async function loadConversationDetail(conversationId) {
    try {
        const response = await fetch(`/api/conversations/${conversationId}/messages`);
        const data = await response.json();
        
        if (data.success) {
            displayConversationDetail(data.messages, conversationId);
        } else {
            showNotification('加载对话详情失败: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('加载对话详情失败:', error);
        showNotification('加载对话详情失败，请检查网络连接', 'error');
    }
}

// 显示对话详情
function displayConversationDetail(messages, conversationId) {
    const container = document.getElementById('conversationDetail');
    if (!container) return;
    
    if (messages.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-comment-slash"></i>
                <h3>暂无消息</h3>
                <p>这个对话还没有任何消息</p>
            </div>
        `;
        return;
    }
    
    // 获取对话信息
    const conversation = conversations.find(c => c.conversation_id === conversationId);
    
    container.innerHTML = `
        <div class="conversation-header">
            <h3>${conversation?.topic || '未命名对话'}</h3>
            <div class="conversation-status status-${conversation?.status || 'closed'}">
                ${conversation?.status === 'active' ? '活跃' : '已结束'}
            </div>
        </div>
        
        <div class="messages-container">
            ${messages.map(msg => `
                <div class="message ${msg.message_type === 'user_question' ? 'user-message' : 'ai-message'}">
                    <div class="message-avatar">
                        ${msg.message_type === 'user_question' ? 'U' : 'AI'}
                    </div>
                    <div class="message-content">
                        <div class="message-bubble">
                            ${formatMessageContent(msg.content)}
                        </div>
                        <div class="message-time">
                            ${formatTime(msg.timestamp)}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div class="conversation-controls">
            <button class="btn btn-primary" onclick="continueConversation('${conversationId}')">
                <i class="fas fa-reply"></i> 继续对话
            </button>
            ${conversation?.status === 'active' ? `
                <button class="btn btn-danger" onclick="closeConversation('${conversationId}')">
                    <i class="fas fa-times"></i> 结束对话
                </button>
            ` : ''}
            <button class="btn btn-secondary" onclick="window.location.href='/'">
                <i class="fas fa-arrow-left"></i> 返回主页
            </button>
        </div>
    `;
}

// 格式化消息内容
function formatMessageContent(content) {
    // 简单的换行处理
    return content.replace(/\n/g, '<br>');
}

// 格式化时间
function formatTime(timeString) {
    if (!timeString) return '未知时间';
    
    const date = new Date(timeString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // 1分钟内
        return '刚刚';
    } else if (diff < 3600000) { // 1小时内
        return `${Math.floor(diff / 60000)}分钟前`;
    } else if (diff < 86400000) { // 1天内
        return `${Math.floor(diff / 3600000)}小时前`;
    } else {
        return date.toLocaleDateString('zh-CN');
    }
}

// 关闭对话
async function closeConversation(conversationId) {
    if (!confirm('确定要结束这个对话吗？')) return;
    
    try {
        const response = await fetch('/api/conversations/close', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ conversation_id: conversationId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('对话已结束', 'success');
            // 重新加载对话列表
            await loadConversations();
            
            // 如果关闭的是当前选中的对话，清空详情
            if (conversationId === currentConversationId) {
                currentConversationId = null;
                document.getElementById('conversationDetail').innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-comments"></i>
                        <h3>选择对话</h3>
                        <p>从左侧选择一个对话来查看详细信息</p>
                    </div>
                `;
            }
        } else {
            showNotification('结束对话失败: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('结束对话失败:', error);
        showNotification('结束对话失败，请检查网络连接', 'error');
    }
}

// 继续对话
function continueConversation(conversationId) {
    // 跳转到主页，并传递对话ID
    window.location.href = `/?conversation_id=${conversationId}`;
}

// 查看对话
function viewConversation(conversationId) {
    selectConversation(conversationId);
}

// 开始新对话
function startNewConversation() {
    document.getElementById('newConversationModal').style.display = 'block';
}

// 关闭新对话模态框
function closeNewConversationModal() {
    document.getElementById('newConversationModal').style.display = 'none';
    document.getElementById('conversationTopic').value = '';
}

// 确认开始新对话
async function confirmNewConversation() {
    const topic = document.getElementById('conversationTopic').value.trim();
    
    try {
        const response = await fetch('/api/conversations/new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ topic: topic || '新对话' })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('新对话已创建', 'success');
            closeNewConversationModal();
            
            // 重新加载对话列表
            await loadConversations();
            
            // 自动选择新创建的对话
            if (data.conversation_id) {
                selectConversation(data.conversation_id);
            }
        } else {
            showNotification('创建新对话失败: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('创建新对话失败:', error);
        showNotification('创建新对话失败，请检查网络连接', 'error');
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    
    // 添加样式
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        max-width: 400px;
        animation: slideIn 0.3s ease;
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 自动移除
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        margin-left: 10px;
    }
    
    .notification-close:hover {
        opacity: 0.8;
    }
`;
document.head.appendChild(style);

// 删除对话
async function deleteConversation(conversationId) {
    if (!confirm('确定要删除这个对话吗？删除后将无法恢复。')) {
        return;
    }
    
    try {
        const response = await fetch('/api/conversations/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ conversation_id: conversationId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('对话已删除', 'success');
            
            // 重新加载对话列表
            await loadConversations();
            
            // 如果删除的是当前选中的对话，清除选择
            if (currentConversationId === conversationId) {
                currentConversationId = null;
                const detailContainer = document.getElementById('conversationDetail');
                if (detailContainer) {
                    detailContainer.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-comments"></i>
                            <h3>选择对话</h3>
                            <p>从左侧选择一个对话来查看详情</p>
                        </div>
                    `;
                }
            }
        } else {
            showNotification('删除对话失败: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('删除对话失败:', error);
        showNotification('删除对话失败，请检查网络连接', 'error');
    }
}

// 强制创建新对话
async function forceNewConversation() {
    try {
        const response = await fetch('/api/conversations/force-new', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic: '新对话' })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('新对话已创建', 'success');
            
            // 重新加载对话列表
            await loadConversations();
            
            // 自动选择新创建的对话
            if (data.conversation_id) {
                selectConversation(data.conversation_id);
            }
        } else {
            showNotification('创建新对话失败: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('强制创建新对话失败:', error);
        showNotification('创建新对话失败，请检查网络连接', 'error');
    }
}

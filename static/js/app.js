// 全局变量
let currentInteractionId = null;
let currentFeedbackData = null; // 存储当前反馈数据

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
            addAIMessage(data.response, data.confidence, data.sources, data.ticket_id, data.escalated, data.interaction_id, data.answer_type);
        } else {
            throw new Error(data.error || '请求失败');
        }
        
    } catch (error) {
        console.error('发送问题失败:', error);
        addAIMessage('抱歉，处理您的问题时出现错误，请稍后重试。', 0, [], null, false, null, 'ai_only');
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
function addAIMessage(response, confidence, sources, ticketId, escalated, interactionId, answerType) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';
    
    const currentTime = new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    // 使用Markdown渲染回答内容
    let messageContent = marked.parse(response);
    
    // 根据答案类型添加不同的标识
    let sourceInfo = '';
    if (answerType === 'knowledge_base') {
        sourceInfo = `<div class="source-info knowledge-source">
            <i class="fas fa-database"></i> 答案来源：知识库
        </div>`;
    } else if (answerType === 'hybrid') {
        sourceInfo = `<div class="source-info hybrid-source">
            <i class="fas fa-database"></i> 知识库 + <i class="fas fa-robot"></i> AI补充
        </div>`;
    } else if (answerType === 'ai_only') {
        sourceInfo = `<div class="source-info ai-source">
            <i class="fas fa-robot"></i> AI生成答案
        </div>`;
    } else if (answerType === 'improved') {
        sourceInfo = `<div class="source-info hybrid-source">
            <i class="fas fa-star"></i> 根据反馈改进的答案
        </div>`;
    }
    
    // 添加置信度信息
    if (confidence > 0) {
        messageContent += `<div class="confidence-info">置信度: ${(confidence * 100).toFixed(1)}%</div>`;
    }
    
    // 添加来源信息
    if (sources && sources.length > 0) {
        messageContent += `<div class="sources-info">
            <i class="fas fa-book"></i> 参考来源: ${sources.join(', ')}
        </div>`;
    }
    
    // 如果有工单ID，显示单独的通知
    if (ticketId) {
        showNotification(`由于置信度较低，已为您创建工单 ${ticketId}，技术人员将尽快联系您。`, 'info', 8000);
    }
    
    // 添加满意度评价
    const ratingHtml = `
        <div class="rating-container">
            <div class="rating-label">这个回答对您有帮助吗？</div>
            <div class="rating-stars" data-interaction-id="${interactionId}">
                <i class="fas fa-star" data-rating="1" title="非常不满意"></i>
                <i class="fas fa-star" data-rating="2" title="不满意"></i>
                <i class="fas fa-star" data-rating="3" title="一般"></i>
                <i class="fas fa-star" data-rating="4" title="满意"></i>
                <i class="fas fa-star" data-rating="5" title="非常满意"></i>
            </div>
            <div class="rating-actions">
                <button class="btn btn-sm btn-outline" onclick="requestRevision('${interactionId}')">
                    <i class="fas fa-redo"></i> 重新回答
                </button>
            </div>
        </div>
    `;
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            ${sourceInfo}
            <div class="message-text">${messageContent}</div>
            <div class="message-time">${currentTime}</div>
            ${ratingHtml}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // 绑定星级评价事件
    bindRatingEvents(messageDiv, interactionId);
    
    scrollToBottom();
}

// 滚动到底部
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 绑定星级评价事件
function bindRatingEvents(messageDiv, interactionId) {
    const stars = messageDiv.querySelectorAll('.rating-stars i');
    const ratingContainer = messageDiv.querySelector('.rating-container');
    
    stars.forEach(star => {
        star.addEventListener('click', function() {
            const rating = parseInt(this.getAttribute('data-rating'));
            
            // 如果是3星及以下，显示自定义弹窗
            if (rating <= 3) {
                showFeedbackModal(interactionId, rating, messageDiv);
            } else {
                // 4-5星，只提交评分
                submitRating(interactionId, rating, messageDiv);
            }
        });
        
        star.addEventListener('mouseenter', function() {
            const rating = parseInt(this.getAttribute('data-rating'));
            highlightStars(stars, rating);
        });
    });
    
    const ratingStars = messageDiv.querySelector('.rating-stars');
    ratingStars.addEventListener('mouseleave', function() {
        resetStars(stars);
    });
}

// 高亮星级
function highlightStars(stars, rating) {
    stars.forEach((star, index) => {
        if (index < rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

// 重置星级
function resetStars(stars) {
    stars.forEach(star => {
        star.classList.remove('active');
    });
}

// 提交评分
async function submitRating(interactionId, rating, messageDiv) {
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                interaction_id: interactionId,
                score: rating
            })
        });
        
        if (response.ok) {
            // 显示评分成功
            const ratingContainer = messageDiv.querySelector('.rating-container');
            if (ratingContainer) {
                ratingContainer.innerHTML = `
                    <div class="rating-success">
                        <i class="fas fa-check-circle"></i>
                        感谢您的评价！
                    </div>
                `;
            }
            
            showNotification('评分提交成功', 'success');
        } else {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || '评分提交失败');
        }
    } catch (error) {
        console.error('提交评分失败:', error);
        showNotification('评分提交失败，请重试', 'error');
    }
}

// 请求重新回答
async function requestRevision(interactionId) {
    try {
        const response = await fetch('/api/revise', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                interaction_id: interactionId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 添加新的AI回复
            addAIMessage(data.response, data.confidence, data.sources, data.ticket_id, data.escalated, data.interaction_id, data.answer_type);
            showNotification('正在重新生成回答...', 'info');
        } else {
            throw new Error(data.error || '重新回答失败');
        }
    } catch (error) {
        console.error('请求重新回答失败:', error);
        showNotification('重新回答失败，请重试', 'error');
    }
}

// 根据满意度评分重新回答
async function requestRevisionWithFeedback(interactionId, feedbackScore) {
    try {
        const response = await fetch('/api/revise', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                interaction_id: interactionId,
                feedback_score: feedbackScore
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 添加新的AI回复
            addAIMessage(data.response, data.confidence, data.sources, data.ticket_id, data.escalated, data.interaction_id, data.answer_type);
            
            // 根据满意度评分显示不同的提示
            if (feedbackScore <= 3) {
                showNotification('正在根据您的反馈改进回答...', 'info');
            } else {
                showNotification('正在重新生成回答...', 'info');
            }
        } else {
            throw new Error(data.error || '重新回答失败');
        }
    } catch (error) {
        console.error('请求重新回答失败:', error);
        showNotification('重新回答失败，请重试', 'error');
    }
}

// 显示满意度反馈弹窗
function showFeedbackModal(interactionId, rating, messageDiv) {
    // 存储当前反馈数据
    currentFeedbackData = {
        interactionId: interactionId,
        rating: rating,
        messageDiv: messageDiv
    };
    
    // 更新弹窗内容
    const feedbackRatingElement = document.getElementById('feedbackRating');
    const feedbackMessageElement = document.getElementById('feedbackMessage');
    
    if (feedbackRatingElement && feedbackMessageElement) {
        feedbackRatingElement.textContent = rating;
        
        // 根据评分调整消息内容
        let message = '';
        if (rating === 1) {
            message = '您给出了1星评价，表示对回答非常不满意。';
        } else if (rating === 2) {
            message = '您给出了2星评价，表示对回答不满意。';
        } else {
            message = '您给出了3星评价，表示对回答一般满意。';
        }
        
        feedbackMessageElement.innerHTML = message + '<br>是否希望我根据您的反馈重新生成一个更好的回答？';
        
        // 显示弹窗
        document.getElementById('feedbackModal').style.display = 'block';
    } else {
        console.error('反馈模态框元素未找到');
        // 如果模态框元素不存在，直接提交评分
        submitRating(interactionId, rating, messageDiv);
    }
}

// 关闭满意度反馈弹窗
function closeFeedbackModal() {
    document.getElementById('feedbackModal').style.display = 'none';
    currentFeedbackData = null;
}

// 确认反馈重新回答
function confirmFeedbackRevision() {
    if (currentFeedbackData) {
        const { interactionId, rating, messageDiv } = currentFeedbackData;
        
        // 先提交评分
        submitRating(interactionId, rating, messageDiv);
        
        // 延迟一下再重新回答，确保评分已保存
        setTimeout(() => {
            requestRevisionWithFeedback(interactionId, rating);
        }, 500);
        
        // 关闭弹窗
        closeFeedbackModal();
    }
}

// 显示统计信息
function showStats() {
    fetch('/admin/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalInteractions').textContent = data.total_interactions || 0;
            document.getElementById('escalatedCount').textContent = data.escalated_count || 0;
            document.getElementById('avgConfidence').textContent = (data.avg_confidence || 0) + '%';
            document.getElementById('knowledgeCount').textContent = data.knowledge_count || 0;
            document.getElementById('statsModal').style.display = 'block';
        })
        .catch(error => {
            console.error('获取统计信息失败:', error);
            alert('获取统计信息失败');
        });
}

// 显示知识库
function showKnowledgeBase() {
    document.getElementById('knowledgeModal').style.display = 'block';
    loadKnowledgeList();
    loadCategories();
}

// 加载知识库列表
function loadKnowledgeList(page = 1, search = '', category = '') {
    const params = new URLSearchParams({
        page: page,
        page_size: 10,
        search: search,
        category: category,
        sort_by: 'updated'
    });
    
    fetch(`/admin/knowledge/list?${params}`)
        .then(response => response.json())
        .then(data => {
            renderKnowledgeList(data.items);
            updatePagination(data.page, data.total_pages);
            currentPage = data.page;
            currentSearch = search;
            currentCategory = category;
        })
        .catch(error => {
            console.error('加载知识库失败:', error);
            document.getElementById('knowledgeList').innerHTML = '<p class="error-message">加载知识库失败</p>';
        });
}

// 渲染知识库列表
function renderKnowledgeList(items) {
    const container = document.getElementById('knowledgeList');
    
    if (!items || items.length === 0) {
        container.innerHTML = '<p class="no-data">暂无知识库数据</p>';
        return;
    }
    
    const html = items.map(item => `
        <div class="knowledge-item" onclick="showKnowledgeDetail(${item.id})">
            <div class="item-header">
                <h4 class="item-title">${escapeHtml(item.title)}</h4>
                <span class="category-badge">${escapeHtml(item.category)}</span>
            </div>
            <div class="item-content">
                ${escapeHtml(item.content.substring(0, 150))}${item.content.length > 150 ? '...' : ''}
            </div>
            <div class="item-footer">
                <span class="item-tags">${item.tags ? item.tags.split(',').map(tag => `<span class="tag">${escapeHtml(tag.trim())}</span>`).join('') : ''}</span>
                <span class="item-date">${formatDate(item.updated_at)}</span>
            </div>
            <div class="item-actions">
                <button class="btn-view" onclick="event.stopPropagation(); showKnowledgeDetail(${item.id})">
                    <i class="fas fa-eye"></i> 查看详情
                </button>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

// 显示知识详情
function showKnowledgeDetail(knowledgeId) {
    fetch(`/admin/knowledge/${knowledgeId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('获取知识详情失败: ' + data.error);
                return;
            }
            
            document.getElementById('detailTitle').textContent = data.title;
            document.getElementById('detailCategory').textContent = data.category;
            document.getElementById('detailTags').textContent = data.tags || '无标签';
            document.getElementById('detailContent').innerHTML = formatContent(data.content);
            document.getElementById('detailCreated').textContent = formatDate(data.created_at);
            document.getElementById('detailUpdated').textContent = formatDate(data.updated_at);
            
            document.getElementById('knowledgeDetailModal').style.display = 'block';
        })
        .catch(error => {
            console.error('获取知识详情失败:', error);
            alert('获取知识详情失败');
        });
}

// 加载分类列表
function loadCategories() {
    fetch('/admin/categories')
        .then(response => response.json())
        .then(categories => {
            const select = document.getElementById('categoryFilter');
            select.innerHTML = '<option value="">所有分类</option>';
            
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('加载分类失败:', error);
        });
}

// 搜索知识库
function searchKnowledge() {
    const searchTerm = document.getElementById('knowledgeSearch').value;
    loadKnowledgeList(1, searchTerm, currentCategory);
}

// 按分类筛选
function filterByCategory() {
    const category = document.getElementById('categoryFilter').value;
    loadKnowledgeList(1, currentSearch, category);
}

// 分页相关变量
let currentPage = 1;
let currentSearch = '';
let currentCategory = '';

// 切换页面
function changePage(delta) {
    const newPage = currentPage + delta;
    if (newPage >= 1) {
        loadKnowledgeList(newPage, currentSearch, currentCategory);
    }
}

// 更新分页信息
function updatePagination(page, totalPages) {
    document.getElementById('pageInfo').textContent = `第 ${page} 页，共 ${totalPages} 页`;
    document.getElementById('prevPage').disabled = page <= 1;
    document.getElementById('nextPage').disabled = page >= totalPages;
}

// 格式化内容（支持Markdown）
function formatContent(content) {
    // 简单的Markdown格式化
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

// 工具函数
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '未知';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN');
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
        loadAdminKnowledgeList();
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
                loadAdminKnowledgeList();
            }
        } else {
            throw new Error(data.error || '添加失败');
        }
        
    } catch (error) {
        console.error('添加知识条目失败:', error);
        showNotification('添加失败，请重试', 'error');
    }
}

// 加载管理界面的知识列表
async function loadAdminKnowledgeList() {
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
            // 如果是反馈弹窗，清除数据
            if (modal.id === 'feedbackModal') {
                currentFeedbackData = null;
            }
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

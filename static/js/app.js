// 全局变量
let currentAnswerMode = 'hybrid';
let currentInteractionId = null;
let currentRating = null;
let loadingMessageId = null;
let currentFeedbackData = null; // 存储当前反馈数据

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
function initializeApp() {
    // 绑定输入框事件
    const userInput = document.getElementById('userInput');
    
    // 绑定回车键发送
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendQuestion();
        }
    });
    
    // 绑定发送按钮
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.addEventListener('click', function() {
        sendQuestion();
    });
    
    // 绑定知识表单提交
    const knowledgeForm = document.getElementById('knowledgeForm');
    if (knowledgeForm) {
        knowledgeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addKnowledgeItem();
        });
    }

    // 初始化回答模式选择器
    initAnswerModeSelector();
}

// 初始化回答模式选择器
function initAnswerModeSelector() {
    const modeToggle = document.getElementById('modeToggle');
    const modeDropdown = document.getElementById('modeDropdown');
    const currentModeSpan = document.getElementById('currentMode');
    
    // 切换下拉菜单
    modeToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        modeDropdown.classList.toggle('show');
        modeToggle.classList.toggle('active');
    });
    
    // 选择模式
    modeDropdown.addEventListener('click', function(e) {
        if (e.target.closest('.mode-option')) {
            const modeOption = e.target.closest('.mode-option');
            const mode = modeOption.dataset.mode;
            const modeText = modeOption.querySelector('span').textContent;
            
            currentAnswerMode = mode;
            currentModeSpan.textContent = modeText;
            
            // 关闭下拉菜单
            modeDropdown.classList.remove('show');
            modeToggle.classList.remove('active');
            
            // 显示选择提示
            showNotification(`已切换到${modeText}模式`, 'success');
        }
    });
    
    // 点击外部关闭下拉菜单
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.answer-mode-selector')) {
            modeDropdown.classList.remove('show');
            modeToggle.classList.remove('active');
        }
    });
}

// 修改发送问题函数，支持回答模式和上下文对话
async function sendQuestion() {
    const userInput = document.getElementById('userInput');
    const question = userInput.value.trim();
    
    if (!question) {
        showNotification('请输入您的问题', 'warning');
        return;
    }
    
    // 添加用户消息
    addUserMessage(question);
    userInput.value = '';
    
    // 显示加载状态
    showLoading();
    
    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                answer_mode: currentAnswerMode // 传递回答模式
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addAIMessage(data.answer, data.confidence, data.sources, data.ticket_id, data.escalated, data.interaction_id, data.answer_type);
            
            // 处理对话上下文信息
            if (data.conversation_id && data.has_context) {
                showConversationContext(data.conversation_id);
            }
        } else {
            addAIMessage('抱歉，处理您的问题时出现错误。', 0, [], null, false, null, 'error');
        }
    } catch (error) {
        console.error('发送问题失败:', error);
        addAIMessage('网络错误，请稍后重试。', 0, [], null, false, null, 'error');
    } finally {
        hideLoading();
    }
}

// 添加用户消息
function addUserMessage(question, autoScroll = true) {
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
    if (autoScroll) {
        scrollToBottom();
    }
}

// 添加AI消息
function addAIMessage(response, confidence, sources, ticketId, escalated, interactionId, answerType, autoScroll = true) {
    console.log('addAIMessage - 调试信息:', {
        response: response ? response.substring(0, 100) + '...' : 'null',
        confidence: confidence,
        interactionId: interactionId,
        typeOfInteractionId: typeof interactionId,
        answerType: answerType
    });

    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';

    const currentTime = new Date().toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
    });

    // Render response content using Markdown
    let messageContent = '';
    if (response && typeof response === 'string') {
        try {
            messageContent = marked.parse(response);
        } catch (error) {
            console.error('Markdown解析失败:', error);
            messageContent = response; // 如果解析失败，直接使用原始文本
        }
    } else {
        messageContent = '抱歉，无法显示回答内容。';
    }

    // Add different identifiers based on answer type
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
    } else if (answerType === '问候回应') {
        sourceInfo = `<div class="source-info greeting-source">
            <i class="fas fa-hand-wave"></i> 问候回应
        </div>`;
    } else if (answerType === '身份介绍') {
        sourceInfo = `<div class="source-info identity-source">
            <i class="fas fa-info-circle"></i> 身份介绍
        </div>`;
    } else if (answerType === '无结果') {
        sourceInfo = `<div class="source-info no-result-source">
            <i class="fas fa-exclamation-triangle"></i> 知识库无相关结果
        </div>`;
    } else {
        sourceInfo = `<div class="source-info default-source">
            <i class="fas fa-robot"></i> AI回答
        </div>`;
    }

    // Add confidence info
    if (confidence > 0) {
        messageContent += `<div class="confidence-info">置信度: ${(confidence * 100).toFixed(1)}%</div>`;
    }

    // Add source info
    if (sources && sources.length > 0) {
        messageContent += `<div class="sources-info">
            <i class="fas fa-book"></i> 参考来源: ${sources.join(', ')}
        </div>`;
    }

    // If there's a ticket ID, display a separate notification
    if (ticketId) {
        showNotification(`由于置信度较低，已为您创建工单 ${ticketId}，技术人员将尽快联系您。`, 'info', 8000);
    }

    // 检查interactionId是否有效，如果无效，则生成临时ID
    let finalInteractionId = interactionId;
    if (!interactionId) {
        // 为新消息生成临时ID，格式：temp_时间戳
        finalInteractionId = 'temp_' + Date.now();
        console.log('为新消息生成临时interactionId:', finalInteractionId);
    }

    // 如果有有效的interactionId，就显示评分功能
    if (finalInteractionId) {
        // 添加满意度评价
        const ratingHtml = `
            <div class="rating-container">
                <div class="rating-label">这个回答对您有帮助吗？</div>
                <div class="rating-stars" data-interaction-id="${finalInteractionId}">
                    <i class="fas fa-star" data-rating="1" title="非常不满意"></i>
                    <i class="fas fa-star" data-rating="2" title="不满意"></i>
                    <i class="fas fa-star" data-rating="3" title="一般"></i>
                    <i class="fas fa-star" data-rating="4" title="满意"></i>
                    <i class="fas fa-star" data-rating="5" title="非常满意"></i>
                </div>
                <div class="rating-actions">
                    <button class="btn btn-sm btn-outline" onclick="requestRevision('${finalInteractionId}')">
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

        // 绑定星级评价事件
        bindRatingEvents(messageDiv, finalInteractionId);
    } else {
        console.log('addAIMessage: 没有interactionId，不显示评分功能');
        // 没有interactionId，不显示评分功能
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                ${sourceInfo}
                <div class="message-text">${messageContent}</div>
                <div class="message-time">${currentTime}</div>
            </div>
        `;
    }

    chatMessages.appendChild(messageDiv);

    if (autoScroll) {
        scrollToBottom();
    }
}

// 滚动到底部
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 添加AI加载消息
function addAILoadingMessage() {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    const loadingId = 'loading-' + Date.now();
    messageDiv.id = loadingId;
    messageDiv.className = 'message ai-message loading-message';
    
    const currentTime = new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="loading-indicator">
                <div class="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <div class="loading-text">AI正在思考中...</div>
            </div>
            <div class="message-time">${currentTime}</div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    return loadingId;
}

// 移除AI加载消息
function removeAILoadingMessage(loadingId) {
    const loadingMessage = document.getElementById(loadingId);
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// 移除所有AI加载消息
function removeAllAILoadingMessages() {
    const loadingMessages = document.querySelectorAll('.loading-message');
    loadingMessages.forEach(message => message.remove());
}

// 绑定星级评价事件
function bindRatingEvents(messageDiv, interactionId) {
    console.log('bindRatingEvents - 调试信息:', {
        interactionId: interactionId,
        typeOfInteractionId: typeof interactionId,
        messageDiv: messageDiv
    });
    
    // 检查interactionId是否有效
    if (!interactionId) {
        console.error('bindRatingEvents: interactionId无效:', interactionId);
        return;
    }
    
    const stars = messageDiv.querySelectorAll('.rating-stars i');
    const ratingContainer = messageDiv.querySelector('.rating-container');
    
    // 存储interaction_id到rating容器
    ratingContainer.dataset.interactionId = interactionId;
    
    stars.forEach(star => {
        star.addEventListener('click', function() {
            const rating = this.dataset.rating;
            
            console.log('星星点击事件 - 调试信息:', {
                rating: rating,
                interactionId: interactionId,
                currentInteractionId: currentInteractionId
            });
            
            // 设置当前交互ID和评分
            currentInteractionId = interactionId;
            currentRating = rating;
            
            console.log('设置后的变量值:', {
                currentInteractionId: currentInteractionId,
                currentRating: currentRating
            });
            
            // 高亮选中的星星
            stars.forEach(s => s.classList.remove('active'));
            for (let i = 0; i < rating; i++) {
                stars[i].classList.add('active');
            }
            
            // 显示评分和重新回答选择窗口
            showRatingAndRevisionModal(interactionId, rating);
        });
    });
    
    // 绑定重新回答按钮事件
    const revisionBtn = messageDiv.querySelector('.btn-outline');
    if (revisionBtn) {
        revisionBtn.onclick = function() {
            console.log('重新回答按钮点击 - 调试信息:', {
                interactionId: interactionId,
                currentInteractionId: currentInteractionId
            });
            
            currentInteractionId = interactionId;
            showRatingAndRevisionModal(interactionId, null);
        };
    }
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
    let loadingMessageId = null;
    try {
        // 添加AI加载消息
        loadingMessageId = addAILoadingMessage();
        
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
            // 移除加载消息并添加新的AI回复
            if (loadingMessageId) {
                removeAILoadingMessage(loadingMessageId);
            }
            addAIMessage(data.answer, data.confidence, data.sources, data.ticket_id, data.escalated, data.interaction_id, data.answer_type);
            showNotification('正在重新生成回答...', 'info');
        } else {
            throw new Error(data.error || '重新回答失败');
        }
    } catch (error) {
        console.error('请求重新回答失败:', error);
        if (loadingMessageId) {
            removeAILoadingMessage(loadingMessageId);
        }
        showNotification('重新回答失败，请重试', 'error');
    }
}

// 根据满意度评分重新回答
async function requestRevisionWithFeedback(interactionId, feedbackScore) {
    let loadingMessageId = null;
    try {
        // 添加AI加载消息
        loadingMessageId = addAILoadingMessage();
        
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
            // 移除加载消息并添加新的AI回复
            if (loadingMessageId) {
                removeAILoadingMessage(loadingMessageId);
            }
            addAIMessage(data.answer, data.confidence, data.sources, data.ticket_id, data.escalated, data.interaction_id, data.answer_type);
            
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
        if (loadingMessageId) {
            removeAILoadingMessage(loadingMessageId);
        }
        showNotification('重新回答失败，请重试', 'error');
    }
}

// 显示评分和重新回答选择模态框
function showRatingAndRevisionModal(interactionId, rating) {
    const modal = document.getElementById('ratingRevisionModal');
    if (modal) {
        modal.style.display = 'block';
        currentInteractionId = interactionId;
        
        // 设置评分显示
        const ratingDisplay = modal.querySelector('.rating-display');
        const stars = modal.querySelectorAll('.stars i');
        
        if (rating) {
            // 如果传入了评分，显示已选择的评分
            currentRating = rating; // 确保设置currentRating
            stars.forEach((star, index) => {
                if (index < rating) {
                    star.classList.add('active');
                } else {
                    star.classList.remove('active');
                }
            });
            ratingDisplay.textContent = `已选择 ${rating} 星评分`;
        } else {
            // 如果没有传入评分，重置评分
            currentRating = null; // 重置currentRating
            stars.forEach(star => star.classList.remove('active'));
            ratingDisplay.textContent = '请选择评分';
            
            // 绑定星级评分事件
            stars.forEach(star => {
                star.onclick = function() {
                    const newRating = this.dataset.rating;
                    stars.forEach(s => s.classList.remove('active'));
                    for (let i = 0; i < newRating; i++) {
                        stars[i].classList.add('active');
                    }
                    ratingDisplay.textContent = `已选择 ${newRating} 星评分`;
                    currentRating = newRating;
                };
            });
        }
        
        console.log('showRatingAndRevisionModal - 调试信息:', {
            interactionId: interactionId,
            rating: rating,
            currentInteractionId: currentInteractionId,
            currentRating: currentRating
        });
    }
}

// 关闭评分和重新回答选择模态框
function closeRatingRevisionModal() {
    const modal = document.getElementById('ratingRevisionModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 只提交评分
async function submitRatingOnly() {
    if (!currentRating) {
        showNotification('请先选择评分', 'error');
        return;
    }
    
    // 检查是否是临时ID
    if (typeof currentInteractionId === 'string' && currentInteractionId.startsWith('temp_')) {
        console.log('检测到临时ID，无法提交评分');
        showNotification('此消息为临时显示，无法进行评分。请刷新页面后重新提问以获得评分功能。', 'warning');
        closeRatingRevisionModal();
        return;
    }
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                interaction_id: currentInteractionId,
                rating: parseInt(currentRating)
            })
        });
        
        if (response.ok) {
            showNotification('评分提交成功', 'success');
            closeRatingRevisionModal();
            
            // 更新UI显示评分成功
            updateRatingDisplay(currentInteractionId, currentRating);
        } else {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || '评分提交失败');
        }
    } catch (error) {
        console.error('提交评分失败:', error);
        showNotification('评分提交失败，请重试', 'error');
    }
}

// 提交评分和重新回答
async function submitRatingAndRevision() {
    console.log('提交评分和重新回答 - 调试信息:', {
        currentRating: currentRating,
        currentInteractionId: currentInteractionId,
        typeOfRating: typeof currentRating,
        typeOfInteractionId: typeof currentInteractionId
    });
    
    if (!currentRating) {
        showNotification('请先选择评分', 'error');
        return;
    }
    
    if (!currentInteractionId) {
        showNotification('交互ID无效，无法提交评分', 'error');
        return;
    }
    
    try {
        // 检查是否是临时ID或历史消息ID
        if (typeof currentInteractionId === 'string' && 
            (currentInteractionId.startsWith('temp_') || currentInteractionId.startsWith('hist_'))) {
            console.log('检测到临时ID或历史消息ID，无法直接提交评分');
            
            if (currentInteractionId.startsWith('temp_')) {
                showNotification('此消息为临时显示，无法进行评分。请刷新页面后重新提问以获得评分功能。', 'warning');
            } else {
                showNotification('历史消息无法直接评分，但您可以继续对话。', 'info');
            }
            
            closeRatingRevisionModal();
            return;
        }
        
        // 先提交评分
        const feedbackResponse = await fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                interaction_id: currentInteractionId,
                rating: parseInt(currentRating)
            })
        });
        
        if (!feedbackResponse.ok) {
            const errorData = await feedbackResponse.json().catch(() => ({}));
            throw new Error(errorData.error || '评分提交失败');
        }
        
        const feedbackData = await feedbackResponse.json();
        
        // 检查连续低分情况
        if (feedbackData.consecutiveCount >= 3) {
            // 连续3次低分，显示IT支持链接
            showNotification(`您已连续给出${feedbackData.consecutiveCount}次低分，建议联系IT支持团队`, 'warning');
            
            // 在聊天区域显示IT支持信息
            const supportMessage = `
                <div class="ai-message">
                    <div class="message-content">
                        <div class="message-text">
                            <p>您已连续给出${feedbackData.consecutiveCount}次低分，建议您联系IT支持团队获取帮助：</p>
                            <p><a href="https://support.tomra.com" target="_blank" class="support-link">IT支持团队</a></p>
                        </div>
                    </div>
                </div>
            `;
            
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.insertAdjacentHTML('beforeend', supportMessage);
            scrollToBottom();
            
            closeRatingRevisionModal();
            updateRatingDisplay(currentInteractionId, currentRating);
            return;
        }
        
        // 如果是低分（3星及以下），自动触发重新回答
        if (parseInt(currentRating) <= 3) {
            try {
                // 请求重新回答
                const revisionResponse = await fetch('/api/revise', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        interaction_id: currentInteractionId,
                        feedback_score: parseInt(currentRating),
                        feedback: `用户评分${currentRating}星，要求重新回答`
                    })
                });
                
                if (revisionResponse.ok) {
                    const data = await revisionResponse.json();
                    
                    // 添加新的AI回复
                    addAIMessage(data.new_answer, data.confidence, data.sources, data.ticket_id, data.escalated, data.interaction_id, data.answer_type);
                    
                    showNotification('评分已提交，正在重新生成回答...', 'success');
                    closeRatingRevisionModal();
                    
                    // 更新UI显示评分成功
                    updateRatingDisplay(currentInteractionId, currentRating);
                } else {
                    const errorData = await revisionResponse.json().catch(() => ({}));
                    throw new Error(errorData.error || '重新回答失败');
                }
            } catch (revisionError) {
                console.error('重新回答失败:', revisionError);
                showNotification('评分已提交，但重新回答失败，请稍后再试', 'warning');
                closeRatingRevisionModal();
                updateRatingDisplay(currentInteractionId, currentRating);
            }
        } else {
            // 高分，只提交评分
            showNotification('评分已提交，感谢您的反馈！', 'success');
            closeRatingRevisionModal();
            updateRatingDisplay(currentInteractionId, currentRating);
        }
        
    } catch (error) {
        console.error('提交评分和重新回答失败:', error);
        showNotification(error.message || '操作失败，请重试', 'error');
    }
}

// 更新评分显示
function updateRatingDisplay(interactionId, rating) {
    const messageDiv = document.querySelector(`.rating-stars[data-interaction-id="${interactionId}"]`).closest('.message');
    if (messageDiv) {
        const ratingContainer = messageDiv.querySelector('.rating-container');
        if (ratingContainer) {
            ratingContainer.innerHTML = `
                <div class="rating-success">
                    <i class="fas fa-check-circle"></i>
                    感谢您的评价！
                </div>
            `;
        }
    }
}

// 显示反馈模态框
function showFeedbackModal(interactionId) {
    const modal = document.getElementById('feedbackModal');
    if (modal) {
        modal.style.display = 'block';
        currentInteractionId = interactionId;
        
        // 重置评分
        const stars = modal.querySelectorAll('.stars i');
        stars.forEach(star => star.classList.remove('active'));
        modal.querySelector('.rating-text').textContent = '请选择评分';
        
        // 绑定星级评分事件
        stars.forEach(star => {
            star.onclick = function() {
                const rating = this.dataset.rating;
                stars.forEach(s => s.classList.remove('active'));
                for (let i = 0; i < rating; i++) {
                    stars[i].classList.add('active');
                }
                modal.querySelector('.rating-text').textContent = `已选择 ${rating} 星评分`;
                currentRating = rating;
            };
        });
    }
}

// 关闭反馈模态框
function closeFeedbackModal() {
    const modal = document.getElementById('feedbackModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 提交反馈
function submitFeedback() {
    if (!currentRating) {
        showNotification('请先选择评分', 'warning');
        return;
    }
    
    if (!currentInteractionId) {
        showNotification('无法获取交互ID', 'error');
        return;
    }
    
    // 显示加载状态
    showNotification('正在提交评分...', 'info');
    
    fetch('/api/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            interaction_id: parseInt(currentInteractionId),
            rating: parseInt(currentRating)
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification('评分提交成功！', 'success');
            closeFeedbackModal();
        } else {
            showNotification('评分提交失败：' + (data.message || '未知错误'), 'error');
        }
    })
    .catch(error => {
        console.error('提交反馈失败:', error);
        showNotification('网络错误：' + error.message, 'error');
    });
}

// 请求重新回答
function requestRevision() {
    closeFeedbackModal();
    showRevisionModal();
}

// 显示重新回答模态框
function showRevisionModal() {
    const modal = document.getElementById('revisionModal');
    if (modal) {
        modal.style.display = 'block';
        
        // 绑定单选按钮事件
        const radioButtons = modal.querySelectorAll('input[name="revisionType"]');
        const customFeedback = document.getElementById('customFeedback');
        
        radioButtons.forEach(radio => {
            radio.onchange = function() {
                if (this.value === 'custom') {
                    customFeedback.style.display = 'block';
                } else {
                    customFeedback.style.display = 'none';
                }
            };
        });
    }
}

// 关闭重新回答模态框
function closeRevisionModal() {
    const modal = document.getElementById('revisionModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 提交重新回答请求
function submitRevision() {
    const selectedType = document.querySelector('input[name="revisionType"]:checked');
    if (!selectedType) {
        showNotification('请选择重新回答的类型', 'warning');
        return;
    }
    
    let feedback = selectedType.value;
    
    if (selectedType.value === 'custom') {
        const customText = document.getElementById('customFeedbackText').value.trim();
        if (!customText) {
            showNotification('请输入自定义反馈内容', 'warning');
            return;
        }
        feedback = customText;
    }
    
    if (!currentInteractionId) {
        showNotification('无法获取交互ID', 'error');
        return;
    }
    
    // 显示加载状态
    showNotification('正在处理您的请求...', 'info');
    
    fetch('/api/revise', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            interaction_id: parseInt(currentInteractionId),
            feedback: feedback
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showNotification('重新回答请求已提交', 'success');
            closeRevisionModal();
            
            // 显示新的AI回答
            if (data.new_answer) {
                addAIMessage(data.new_answer, data.confidence, data.sources, data.ticket_id, data.escalated, data.interaction_id, data.answer_type);
            }
        } else {
            showNotification('请求失败：' + (data.message || '未知错误'), 'error');
        }
    })
    .catch(error => {
        console.error('请求重新回答失败:', error);
        showNotification('网络错误：' + error.message, 'error');
    });
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

// 显示管理后台
function showAdminDashboard() {
    window.location.href = '/admin';
}

// 显示对话历史
function showConversations() {
    window.location.href = '/conversations';
}

// 加载知识库列表
function loadKnowledgeList(page = 1, search = '', category = '') {
    const params = new URLSearchParams({
        page: page,
        page_size: 5,  // 修改为每页显示5条
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
    const searchTerm = document.getElementById('knowledgeSearch') ? document.getElementById('knowledgeSearch').value.trim() : '';
    
    if (!items || items.length === 0) {
        if (searchTerm) {
            container.innerHTML = `<p class="no-data">没有找到包含"${escapeHtml(searchTerm)}"的知识条目</p>`;
        } else {
            container.innerHTML = '<p class="no-data">暂无知识库数据</p>';
        }
        return;
    }
    
    const html = items.map(item => {
        // 高亮搜索关键词
        const highlightedTitle = searchTerm ? highlightSearchTerm(item.title, searchTerm) : escapeHtml(item.title);
        const highlightedContent = searchTerm ? highlightSearchTerm(item.content.substring(0, 150), searchTerm) : escapeHtml(item.content.substring(0, 150));
        
        return `
            <div class="knowledge-item" onclick="window.location.href='/knowledge?id=${item.id}'">
                <div class="item-header">
                    <h4 class="item-title">${highlightedTitle}</h4>
                    <span class="category-badge">${escapeHtml(item.category)}</span>
                </div>
                <div class="item-content">
                    ${highlightedContent}${item.content.length > 150 ? '...' : ''}
                </div>
                <div class="item-footer">
                    <span class="item-tags">${item.tags ? item.tags.split(',').map(tag => `<span class="tag">${escapeHtml(tag.trim())}</span>`).join('') : ''}</span>
                    <span class="item-date">${formatDate(item.updated_at)}</span>
                </div>
                <div class="item-actions">
                    <button class="btn-view" onclick="event.stopPropagation(); window.location.href='/knowledge?id=${item.id}'">
                        <i class="fas fa-eye"></i> 查看详情
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = html;
}

// 高亮搜索关键词
function highlightSearchTerm(text, searchTerm) {
    if (!searchTerm) return escapeHtml(text);
    
    const escapedText = escapeHtml(text);
    const searchTerms = searchTerm.split(/\s+/).filter(term => term.length > 0);
    
    let highlightedText = escapedText;
    searchTerms.forEach(term => {
        const regex = new RegExp(`(${escapeHtml(term)})`, 'gi');
        highlightedText = highlightedText.replace(regex, '<mark class="search-highlight">$1</mark>');
    });
    
    return highlightedText;
}

// 跳转到知识详情页面
function goToKnowledgeDetail(knowledgeId) {
    window.location.href = `/knowledge?id=${knowledgeId}`;
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
    const searchTerm = document.getElementById('knowledgeSearch').value.trim();
    loadKnowledgeList(1, searchTerm, currentCategory);
}

// 实时搜索（带防抖）
let searchTimeout = null;
function searchKnowledgeRealTime() {
    const searchTerm = document.getElementById('knowledgeSearch').value.trim();
    
    // 清除之前的定时器
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // 设置新的定时器，300ms后执行搜索
    searchTimeout = setTimeout(() => {
        loadKnowledgeList(1, searchTerm, currentCategory);
    }, 300);
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

// HTML转义函数已在上面定义

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

// 显示加载状态
function showLoading() {
    const chatMessages = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai-message loading-message';
    loadingDiv.id = 'loadingMessage';
    
    loadingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="loading-indicator">
                <div class="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
                <div class="loading-text">正在思考中...</div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(loadingDiv);
    scrollToBottom();
}

// 隐藏加载状态
function hideLoading() {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// 滚动到底部
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 转义HTML函数已在上面定义

// 对话上下文相关函数
let currentConversationId = null;

// 显示对话上下文指示器
function showConversationContext(conversationId) {
    currentConversationId = conversationId;
    const contextIndicator = document.getElementById('contextIndicator');
    const contextText = document.getElementById('contextText');
    
    if (contextIndicator && contextText) {
        contextText.textContent = '正在使用对话上下文，AI会记住之前的对话内容';
        contextIndicator.style.display = 'flex';
    }
    
    // 加载并显示对话历史
    loadConversationHistory(conversationId);
}

// 清除对话上下文
async function clearConversationContext() {
    if (!currentConversationId) return;
    
    try {
        const response = await fetch('/api/conversations/close', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ conversation_id: currentConversationId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // 隐藏上下文指示器
            const contextIndicator = document.getElementById('contextIndicator');
            if (contextIndicator) {
                contextIndicator.style.display = 'none';
            }
            
            currentConversationId = null;
            showNotification('对话上下文已清除，开始新的对话', 'success');
        } else {
            showNotification('清除对话上下文失败: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('清除对话上下文失败:', error);
        showNotification('清除对话上下文失败，请检查网络连接', 'error');
    }
}

// 加载对话历史
async function loadConversationHistory(conversationId) {
    try {
        const response = await fetch(`/api/conversations/${conversationId}/messages`);
        const data = await response.json();
        
        if (data.success && data.messages.length > 0) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = '';
            
            console.log('原始消息数据:', data.messages);
            
            // 按时间戳排序所有消息，确保正确的时序顺序
            const sortedMessages = data.messages.sort((a, b) => {
                const timeA = new Date(a.timestamp);
                const timeB = new Date(b.timestamp);
                console.log(`比较: ${a.message_type} (${a.timestamp}) vs ${b.message_type} (${b.timestamp})`);
                console.log(`时间A: ${timeA}, 时间B: ${timeB}, 差值: ${timeA - timeB}`);
                return timeA - timeB;
            });
            
            console.log('排序后的消息:', sortedMessages);
            
            // 按排序后的顺序显示所有消息
            for (let i = 0; i < sortedMessages.length; i++) {
                const msg = sortedMessages[i];
                if (msg.message_type === 'user_question') {
                    addUserMessage(msg.content, false); // false表示不自动滚动
                } else if (msg.message_type === 'ai_response') {
                    // 尝试查找对应的交互记录来获取真实的interaction_id
                    let interactionId = null;
                    if (msg.content && msg.timestamp) {
                        try {
                            // 通过问题内容和时间戳查找对应的交互记录
                            const interactionResponse = await fetch('/api/interactions/find', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    question: msg.content,
                                    timestamp: msg.timestamp,
                                    conversation_id: conversationId
                                })
                            });
                            
                            if (interactionResponse.ok) {
                                const interactionData = await interactionResponse.json();
                                if (interactionData.success && interactionData.interaction_id) {
                                    interactionId = interactionData.interaction_id;
                                    console.log(`找到对应的交互记录: ${interactionId}`);
                                }
                            }
                        } catch (error) {
                            console.warn('查找交互记录失败:', error);
                        }
                    }
                    
                    // 如果没有找到真实的interaction_id，为历史消息生成一个可用的ID
                    if (!interactionId) {
                        // 使用时间戳和内容哈希生成一个稳定的ID，避免中文字符问题
                        const contentStr = msg.timestamp + msg.content.substring(0, 50);
                        let hash = '';
                        try {
                            // 尝试使用btoa，如果失败则使用替代方法
                            hash = btoa(unescape(encodeURIComponent(contentStr))).replace(/[^a-zA-Z0-9]/g, '');
                        } catch (error) {
                            // 如果btoa失败，使用简单的字符串处理
                            hash = contentStr.replace(/[^a-zA-Z0-9]/g, '').substring(0, 20);
                        }
                        interactionId = `hist_${hash}_${Date.now()}`;
                        console.log(`为历史消息生成ID: ${interactionId}`);
                    }
                    
                    addAIMessage(
                        msg.content, 
                        msg.relevance_score || 0.8, // 使用实际分数（如果有的话），否则使用默认值
                        [], // 来源通常不在此上下文中存储
                        null, // 没有工单ID
                        false, // 不升级
                        interactionId, // 使用找到的真实交互ID或生成的ID
                        'AI回答', // 默认答案类型
                        false // false表示不自动滚动
                    );
                }
            }
            
            // 所有历史消息加载完成后滚动到底部
            scrollToBottom();
        } else {
            showNotification('未能加载对话历史或对话为空。', 'warning');
        }
    } catch (error) {
        console.error('加载对话历史失败:', error);
        showNotification('加载对话历史失败，请稍后再试。', 'error');
    }
}

// 页面加载时检查是否有对话上下文
document.addEventListener('DOMContentLoaded', function() {
    // 检查URL参数中是否有对话ID
    const urlParams = new URLSearchParams(window.location.search);
    const conversationId = urlParams.get('conversation_id');
    
    if (conversationId) {
        // 如果有对话ID，显示上下文指示器
        showConversationContext(conversationId);
    }
});



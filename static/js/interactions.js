// 全局变量
let currentPage = 1;
let pageSize = 10;
let totalPages = 1;
let currentSearch = '';
let currentUserFilter = '';
let currentRatingFilter = '';
let currentSortBy = 'time';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成，开始初始化');
    
    // 检查是否已登录
    fetch('/api/check-login')
        .then(response => response.json())
        .then(data => {
            if (data.logged_in) {
                console.log('用户已登录，开始加载数据');
                console.log('初始状态:', {
                    currentPage: currentPage,
                    pageSize: pageSize,
                    totalPages: totalPages
                });
                
                loadInteractions();
                loadUsers();
                
                // 绑定搜索框回车事件
                document.getElementById('searchInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        searchInteractions();
                    }
                });
            } else {
                console.log('用户未登录，重定向到登录页面');
                window.location.href = '/login';
            }
        })
        .catch(error => {
            console.error('检查登录状态失败:', error);
            window.location.href = '/login';
        });
});

// 加载交互记录
function loadInteractions() {
    const params = new URLSearchParams({
        page: currentPage,
        page_size: pageSize,
        search: currentSearch,
        user: currentUserFilter,
        rating: currentRatingFilter,
        sort_by: currentSortBy
    });
    
    console.log('loadInteractions被调用:', {
        currentPage: currentPage,
        pageSize: pageSize,
        params: params.toString()
    });
    
    fetch(`/admin/interactions/list?${params}`)
        .then(response => {
            console.log('API响应状态:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('API响应数据:', data);
            if (data.success) {
                // 更新全局变量
                totalPages = data.pages;
                console.log('更新totalPages:', totalPages);
                
                displayInteractions(data.interactions);
                updatePagination(data.total, data.page, data.pages);
            } else {
                showNotification('加载交互记录失败：' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('加载交互记录失败:', error);
            showNotification('网络错误：' + error.message, 'error');
        });
}

// 显示交互记录
function displayInteractions(interactions) {
    const tbody = document.getElementById('interactionsTableBody');
    tbody.innerHTML = '';
    
    if (interactions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="no-data">暂无交互记录</td>
            </tr>
        `;
        return;
    }
    
    interactions.forEach(interaction => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="time-cell">
                <div class="time-text">${formatTime(interaction.created_at)}</div>
            </td>
            <td class="user-cell">
                <div class="user-text">${interaction.username || '未知用户'}</div>
            </td>
            <td class="question-cell">
                <div class="question-text">${truncateText(interaction.question, 100)}</div>
            </td>
            <td class="answer-cell">
                <div class="answer-text">${truncateText(interaction.answer, 100)}</div>
            </td>
            <td class="rating-cell">
                ${interaction.rating ? generateRatingStars(interaction.rating) : '<span class="no-rating">未评分</span>'}
            </td>
            <td class="revision-cell">
                ${interaction.revision_count > 0 ? 
                    `<span class="revision-count">${interaction.revision_count}次</span>` : 
                    '<span class="no-revision">无</span>'}
            </td>
            <td class="actions-cell">
                <button class="btn-view-detail" onclick="viewInteractionDetail(${interaction.id})">
                    <i class="fas fa-eye"></i> 详情
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// 生成评分星星
function generateRatingStars(rating) {
    let stars = '';
    for (let i = 1; i <= 5; i++) {
        if (i <= rating) {
            stars += '<i class="fas fa-star"></i>';
        } else {
            stars += '<i class="far fa-star"></i>';
        }
    }
    return `<div class="rating-stars">${stars}</div>`;
}

// 查看交互详情
function viewInteractionDetail(interactionId) {
    fetch(`/admin/interactions/${interactionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayInteractionDetail(data.interaction);
                document.getElementById('interactionDetailModal').style.display = 'block';
            } else {
                showNotification('加载交互详情失败：' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('加载交互详情失败:', error);
            showNotification('网络错误：' + error.message, 'error');
        });
}

// 显示交互详情
function displayInteractionDetail(interaction) {
    const content = document.getElementById('interactionDetailContent');
    
    let revisionsHtml = '';
    if (interaction.revisions && interaction.revisions.length > 0) {
        interaction.revisions.forEach((revision, index) => {
            revisionsHtml += `
                <div class="revision-item">
                    <div class="revision-header">
                        <span>重新回答 #${index + 1}</span>
                        <span>${formatTime(revision.created_at)}</span>
                    </div>
                    <div class="revision-content">
                        <strong>反馈：</strong>${revision.feedback}<br>
                        <strong>新回答：</strong>${revision.new_answer}
                        ${revision.rating ? `<br><strong>评分：</strong>${generateRatingStars(revision.rating)}` : ''}
                    </div>
                </div>
            `;
        });
    } else {
        revisionsHtml = '<p>无重新回答记录</p>';
    }
    
    content.innerHTML = `
        <div class="interaction-detail-content">
            <div class="interaction-header">
                <h4>交互详情</h4>
                <div class="interaction-meta">
                    <span><i class="fas fa-user"></i> ${interaction.username || '未知用户'}</span>
                    <span><i class="fas fa-clock"></i> ${formatTime(interaction.created_at)}</span>
                    <span><i class="fas fa-star"></i> ${interaction.rating ? interaction.rating + '星' : '未评分'}</span>
                </div>
            </div>
            
            <div class="interaction-section">
                <h5><i class="fas fa-question-circle"></i> 用户问题</h5>
                <div class="interaction-content">${interaction.question}</div>
            </div>
            
            <div class="interaction-section">
                <h5><i class="fas fa-comment"></i> AI回答</h5>
                <div class="interaction-content">${interaction.answer}</div>
            </div>
            
            <div class="interaction-section">
                <h5><i class="fas fa-redo"></i> 重新回答记录</h5>
                ${revisionsHtml}
            </div>
        </div>
    `;
}

// 搜索交互记录
function searchInteractions() {
    currentSearch = document.getElementById('searchInput').value.trim();
    currentPage = 1;
    loadInteractions();
}

// 按用户筛选
function filterByUser() {
    currentUserFilter = document.getElementById('userFilter').value;
    currentPage = 1;
    loadInteractions();
}

// 按评分筛选
function filterByRating() {
    currentRatingFilter = document.getElementById('ratingFilter').value;
    currentPage = 1;
    loadInteractions();
}

// 排序交互记录
function sortInteractions() {
    currentSortBy = document.getElementById('sortBy').value;
    currentPage = 1;
    loadInteractions();
}

// 加载用户列表
function loadUsers() {
    fetch('/admin/users')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const userFilter = document.getElementById('userFilter');
                data.users.forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.username;
                    option.textContent = user.username;
                    userFilter.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('加载用户列表失败:', error);
        });
}

// 更新分页
function updatePagination(total, currentPage, totalPages) {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // 上一页按钮
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '上一页';
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener('click', function() {
        console.log('点击上一页按钮');
        changePage(-1);
    });
    pagination.appendChild(prevBtn);
    
    // 页码信息
    const pageInfo = document.createElement('span');
    pageInfo.textContent = `第 ${currentPage} 页，共 ${totalPages} 页`;
    pageInfo.style.margin = '0 15px';
    pagination.appendChild(pageInfo);
    
    // 下一页按钮
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '下一页';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.addEventListener('click', function() {
        console.log('点击下一页按钮');
        changePage(1);
    });
    pagination.appendChild(nextBtn);
}

// 切换页面
function changePage(delta) {
    console.log('changePage被调用:', {
        delta: delta,
        currentPage: currentPage,
        totalPages: totalPages,
        newPage: currentPage + delta
    });
    
    const newPage = currentPage + delta;
    if (newPage >= 1 && newPage <= totalPages) {
        console.log('页面有效，更新currentPage:', newPage);
        currentPage = newPage;
        loadInteractions();
    } else {
        console.log('页面超出范围:', newPage);
    }
}

// 导出数据
function exportInteractions() {
    const params = new URLSearchParams({
        search: currentSearch,
        user: currentUserFilter,
        rating: currentRatingFilter,
        sort_by: currentSortBy
    });
    
    window.open(`/admin/interactions/export?${params}`, '_blank');
}

// 关闭模态框
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// 工具函数
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN');
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function showNotification(message, type) {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // 显示通知
    setTimeout(() => notification.classList.add('show'), 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// 点击模态框外部关闭
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

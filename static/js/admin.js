// 管理后台JavaScript功能

// 全局变量
let currentPage = 1;
let pageSize = 10;
let totalPages = 1;
let currentKnowledgeList = [];
let currentFilters = {
    search: '',
    category: '',
    sortBy: 'updated'
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loadAdminStats();
    loadKnowledgeList();
    loadCategories();
    
    // 绑定搜索框回车事件
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchKnowledge();
        }
    });
    
    // 绑定表单提交事件
    document.getElementById('knowledgeForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveKnowledge();
    });
});

// 加载管理统计信息
async function loadAdminStats() {
    try {
        const response = await fetch('/admin/stats');
        if (response.ok) {
            const stats = await response.json();
            
            document.getElementById('totalKnowledge').textContent = stats.total_knowledge || 0;
            document.getElementById('totalCategories').textContent = stats.total_categories || 0;
            document.getElementById('lastUpdated').textContent = stats.last_updated || '无';
        }
    } catch (error) {
        console.error('加载统计信息失败:', error);
    }
}

// 加载知识库列表
async function loadKnowledgeList(page = 1, search = '', category = '', sortBy = 'updated') {
    try {
        const params = new URLSearchParams({
            page: page.toString(),
            page_size: pageSize.toString(),
            search: search,
            category: category,
            sort_by: sortBy
        });
        
        const response = await fetch(`/admin/knowledge/list?${params}`);
        const data = await response.json();
        
        if (response.ok) {
            currentKnowledgeList = data.items || [];
            currentPage = data.page || 1;
            totalPages = Math.ceil((data.total || 0) / pageSize);
            
            renderKnowledgeTable(currentKnowledgeList);
            renderPagination();
        } else {
            throw new Error(data.error || '获取知识库列表失败');
        }
    } catch (error) {
        console.error('加载知识库列表失败:', error);
        showNotification('加载知识库列表失败', 'error');
        currentKnowledgeList = [];
        renderKnowledgeTable([]);
    }
}

// 渲染知识库表格
function renderKnowledgeTable(items) {
    const tbody = document.getElementById('knowledgeTableBody');
    
    if (!items || items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">暂无知识库数据</td></tr>';
        return;
    }
    
    const html = items.map((item, index) => `
        <tr class="knowledge-row" data-id="${item.id}">
            <td class="title-cell">
                <div class="title-content">
                    <span class="title-text">${escapeHtml(item.title)}</span>
                    <button class="btn-expand" onclick="toggleContent(${index})" title="展开/收起">
                        <i class="fas fa-chevron-down"></i>
                    </button>
                </div>
            </td>
            <td class="category-cell">
                <span class="category-badge">${escapeHtml(item.category)}</span>
            </td>
            <td class="content-cell">
                <div class="content-preview" id="content-preview-${index}">
                    <div class="preview-text">
                        ${escapeHtml(item.content.substring(0, 100))}${item.content.length > 100 ? '...' : ''}
                    </div>
                    <div class="full-content" id="full-content-${index}" style="display: none;">
                        <div class="content-header">
                            <strong>完整内容：</strong>
                            <button class="btn-collapse" onclick="toggleContent(${index})" title="收起">
                                <i class="fas fa-chevron-up"></i>
                            </button>
                        </div>
                        <div class="content-body">
                            ${formatContent(item.content)}
                        </div>
                    </div>
                </div>
            </td>
            <td class="tags-cell">
                <div class="tags-container">
                    ${item.tags ? item.tags.split(',').map(tag => 
                        `<span class="tag">${escapeHtml(tag.trim())}</span>`
                    ).join('') : '<span class="no-tags">无标签</span>'}
                </div>
            </td>
            <td class="date-cell">
                <span class="date-text">${formatDate(item.updated_at)}</span>
            </td>
            <td class="actions-cell">
                <div class="action-buttons">
                    <button class="btn btn-edit" onclick="editKnowledge(${item.id})" title="编辑">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-delete" onclick="deleteKnowledge(${item.id})" title="删除">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
    
    tbody.innerHTML = html;
}

// 渲染分页
function renderPagination() {
    const pagination = document.getElementById('pagination');
    pagination.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // 上一页按钮
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '上一页';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => loadKnowledgeList(currentPage - 1);
    pagination.appendChild(prevBtn);
    
    // 页码按钮
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === currentPage ? 'active' : '';
        pageBtn.onclick = () => loadKnowledgeList(i);
        pagination.appendChild(pageBtn);
    }
    
    // 下一页按钮
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '下一页';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => loadKnowledgeList(currentPage + 1);
    pagination.appendChild(nextBtn);
}

// 切换页面
function changePage(delta) {
    const newPage = currentPage + delta;
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        loadKnowledgeList(currentPage, currentFilters.search, currentFilters.category, currentFilters.sortBy);
    }
}

// 跳转到指定页面
function goToPage(page) {
    if (page >= 1 && page <= totalPages) {
        currentPage = page;
        loadKnowledgeList(currentPage, currentFilters.search, currentFilters.category, currentFilters.sortBy);
    }
}

// 加载分类列表
async function loadCategories() {
    try {
        const response = await fetch('/admin/categories');
        if (response.ok) {
            const categories = await response.json();
            const categoryFilter = document.getElementById('categoryFilter');
            
            // 保留"所有分类"选项
            categoryFilter.innerHTML = '<option value="">所有分类</option>';
            
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                categoryFilter.appendChild(option);
            });
        }
    } catch (error) {
        console.error('加载分类列表失败:', error);
    }
}

// 搜索知识库
function searchKnowledge() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    currentFilters.search = searchTerm;
    currentPage = 1;
    loadKnowledgeList(currentPage, searchTerm, currentFilters.category, currentFilters.sortBy);
}

// 按分类筛选
function filterByCategory() {
    const category = document.getElementById('categoryFilter').value;
    currentFilters.category = category;
    currentPage = 1;
    loadKnowledgeList(currentPage, currentFilters.search, category, currentFilters.sortBy);
}

// 按排序方式筛选
function filterBySort() {
    const sortBy = document.getElementById('sortFilter').value;
    currentFilters.sortBy = sortBy;
    currentPage = 1;
    loadKnowledgeList(currentPage, currentFilters.search, currentFilters.category, sortBy);
}

// 显示添加知识模态框
function showAddKnowledgeModal() {
    document.getElementById('modalTitle').innerHTML = '<i class="fas fa-plus"></i> 添加知识条目';
    document.getElementById('knowledgeForm').reset();
    document.getElementById('knowledgeId').value = '';
    document.getElementById('knowledgeModal').style.display = 'block';
}

// 显示编辑知识模态框
async function editKnowledge(id) {
    try {
        const response = await fetch(`/admin/knowledge/${id}`);
        if (response.ok) {
            const knowledge = await response.json();
            
            document.getElementById('modalTitle').innerHTML = '<i class="fas fa-edit"></i> 编辑知识条目';
            document.getElementById('knowledgeId').value = knowledge.id;
            document.getElementById('knowledgeTitle').value = knowledge.title;
            document.getElementById('knowledgeCategory').value = knowledge.category;
            document.getElementById('knowledgeContent').value = knowledge.content;
            document.getElementById('knowledgeTags').value = knowledge.tags || '';
            
            document.getElementById('knowledgeModal').style.display = 'block';
        }
    } catch (error) {
        console.error('加载知识条目失败:', error);
        showNotification('加载知识条目失败', 'error');
    }
}

// 关闭知识模态框
function closeKnowledgeModal() {
    document.getElementById('knowledgeModal').style.display = 'none';
}

// 保存知识条目
async function saveKnowledge() {
    const formData = new FormData(document.getElementById('knowledgeForm'));
    const knowledgeData = {
        title: formData.get('title'),
        category: formData.get('category'),
        content: formData.get('content'),
        tags: formData.get('tags')
    };
    
    const id = formData.get('id');
    const isEdit = id && id !== '';
    
    try {
        const url = isEdit ? `/admin/knowledge/${id}` : '/admin/knowledge';
        const method = isEdit ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(knowledgeData)
        });
        
        if (response.ok) {
            showNotification(isEdit ? '知识条目更新成功' : '知识条目添加成功', 'success');
            closeKnowledgeModal();
            loadKnowledgeList(currentPage);
            loadAdminStats();
        } else {
            const error = await response.json();
            showNotification(error.message || '操作失败', 'error');
        }
    } catch (error) {
        console.error('保存知识条目失败:', error);
        showNotification('保存失败，请稍后重试', 'error');
    }
}

// 删除知识条目
function deleteKnowledge(id, title) {
    document.getElementById('deleteItemTitle').textContent = title;
    document.getElementById('deleteModal').style.display = 'block';
    
    // 存储要删除的ID
    window.deleteKnowledgeId = id;
}

// 确认删除
async function confirmDelete() {
    const id = window.deleteKnowledgeId;
    if (!id) return;
    
    try {
        const response = await fetch(`/admin/knowledge/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('知识条目删除成功', 'success');
            closeDeleteModal();
            loadKnowledgeList(currentPage);
            loadAdminStats();
        } else {
            const error = await response.json();
            showNotification(error.message || '删除失败', 'error');
        }
    } catch (error) {
        console.error('删除知识条目失败:', error);
        showNotification('删除失败，请稍后重试', 'error');
    }
}

// 关闭删除模态框
function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    window.deleteKnowledgeId = null;
}

// 导出知识库
function exportKnowledge() {
    try {
        const data = currentKnowledgeList.map(item => ({
            title: item.title,
            category: item.category,
            content: item.content,
            tags: item.tags || '',
            created_at: item.created_at,
            updated_at: item.updated_at
        }));
        
        const csvContent = convertToCSV(data);
        downloadFile(csvContent, 'knowledge_base.csv', 'text/csv');
        
        showNotification('知识库导出成功', 'success');
    } catch (error) {
        console.error('导出失败:', error);
        showNotification('导出失败，请稍后重试', 'error');
    }
}

// 导入知识库
function importKnowledge() {
    document.getElementById('importModal').style.display = 'block';
}

// 关闭导入模态框
function closeImportModal() {
    document.getElementById('importModal').style.display = 'none';
    document.getElementById('importFile').value = '';
    document.getElementById('importContent').value = '';
}

// 处理文件选择
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('importContent').value = e.target.result;
    };
    reader.readAsText(file);
}

// 处理导入
async function processImport() {
    const content = document.getElementById('importContent').value.trim();
    if (!content) {
        showNotification('请输入要导入的内容', 'error');
        return;
    }
    
    try {
        let data;
        if (content.startsWith('[') && content.endsWith(']')) {
            // JSON格式
            data = JSON.parse(content);
        } else {
            // CSV格式
            data = parseCSV(content);
        }
        
        if (!Array.isArray(data) || data.length === 0) {
            showNotification('导入数据格式不正确', 'error');
            return;
        }
        
        const response = await fetch('/admin/knowledge/import', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ data: data })
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification(`成功导入 ${result.imported_count} 条知识条目`, 'success');
            closeImportModal();
            loadKnowledgeList();
            loadAdminStats();
        } else {
            const error = await response.json();
            showNotification(error.message || '导入失败', 'error');
        }
    } catch (error) {
        console.error('导入失败:', error);
        showNotification('导入失败，请检查数据格式', 'error');
    }
}

// 工具函数

// 转义HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '未知';
    
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // 1分钟内
        return '刚刚';
    } else if (diff < 3600000) { // 1小时内
        return `${Math.floor(diff / 60000)}分钟前`;
    } else if (diff < 86400000) { // 1天内
        return `${Math.floor(diff / 3600000)}小时前`;
    } else if (diff < 2592000000) { // 30天内
        return `${Math.floor(diff / 86400000)}天前`;
    } else {
        return date.toLocaleDateString('zh-CN');
    }
}

// 格式化内容，处理换行和特殊字符
function formatContent(content) {
    if (!content) return '';
    return content.replace(/\n/g, '<br>').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// 展开/收起内容
function toggleContent(index) {
    const preview = document.getElementById(`content-preview-${index}`);
    const fullContent = document.getElementById(`full-content-${index}`);
    const expandBtn = preview.querySelector('.btn-expand');
    const collapseBtn = fullContent.querySelector('.btn-collapse');

    if (fullContent.style.display === 'none') {
        fullContent.style.display = 'block';
        preview.style.display = 'none';
        expandBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
        collapseBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
    } else {
        fullContent.style.display = 'none';
        preview.style.display = 'block';
        expandBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
        collapseBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
    }
}

// 显示通知
function showNotification(message, type = 'info', duration = 3000) {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => notification.classList.add('show'), 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// 转换数据为CSV格式
function convertToCSV(data) {
    if (data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvRows = [headers.join(',')];
    
    for (const row of data) {
        const values = headers.map(header => {
            const value = row[header] || '';
            // 如果值包含逗号、引号或换行符，用引号包围
            if (value.includes(',') || value.includes('"') || value.includes('\n')) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        });
        csvRows.push(values.join(','));
    }
    
    return csvRows.join('\n');
}

// 解析CSV内容
function parseCSV(csvContent) {
    const lines = csvContent.trim().split('\n');
    if (lines.length < 2) return [];
    
    const headers = lines[0].split(',').map(h => h.trim());
    const result = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        const row = {};
        
        headers.forEach((header, index) => {
            row[header] = values[index] || '';
        });
        
        result.push(row);
    }
    
    return result;
}

// 下载文件
function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
}

// 模态框点击外部关闭
window.onclick = function(event) {
    const knowledgeModal = document.getElementById('knowledgeModal');
    const deleteModal = document.getElementById('deleteModal');
    const importModal = document.getElementById('importModal');
    
    if (event.target === knowledgeModal) {
        closeKnowledgeModal();
    } else if (event.target === deleteModal) {
        closeDeleteModal();
    } else if (event.target === importModal) {
        closeImportModal();
    }
};

// 全局变量
let currentPermissions = [];
let editingUsername = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('权限管理页面加载完成');
    loadPermissions();
    
    // 绑定搜索框回车事件
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchPermissions();
        }
    });
    
    // 绑定表单提交事件
    document.getElementById('permissionForm').addEventListener('submit', function(e) {
        e.preventDefault();
        savePermission();
    });
    
    // 绑定添加用户表单提交事件
    document.getElementById('addUserForm').addEventListener('submit', function(e) {
        e.preventDefault();
        createUser();
    });
});

// 加载权限列表
function loadPermissions() {
    fetch('/admin/permissions/list')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                currentPermissions = data.permissions;
                displayPermissions(data.permissions);
            } else {
                showNotification('加载权限列表失败：' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('加载权限列表失败:', error);
            showNotification('网络错误：' + error.message, 'error');
        });
}

// 显示权限列表
function displayPermissions(permissions) {
    const tbody = document.getElementById('permissionsTableBody');
    tbody.innerHTML = '';
    
    if (permissions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="no-data">暂无权限记录</td>
            </tr>
        `;
        return;
    }
    
    permissions.forEach(permission => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="username-cell">
                <div class="username-text">${permission.username}</div>
            </td>
            <td class="admin-cell">
                <span class="permission-badge ${permission.can_access_admin ? 'granted' : 'denied'}">
                    ${permission.can_access_admin ? '<i class="fas fa-check"></i> 是' : '<i class="fas fa-times"></i> 否'}
                </span>
            </td>
            <td class="permissions-cell">
                <span class="permission-badge ${permission.can_manage_permissions ? 'granted' : 'denied'}">
                    ${permission.can_manage_permissions ? '<i class="fas fa-check"></i> 是' : '<i class="fas fa-times"></i> 否'}
                </span>
            </td>
            <td class="interactions-cell">
                <span class="permission-badge ${permission.can_view_interactions ? 'granted' : 'denied'}">
                    ${permission.can_view_interactions ? '<i class="fas fa-check"></i> 是' : '<i class="fas fa-times"></i> 否'}
                </span>
            </td>
            <td class="export-cell">
                <span class="permission-badge ${permission.can_export_data ? 'granted' : 'denied'}">
                    ${permission.can_export_data ? '<i class="fas fa-check"></i> 是' : '<i class="fas fa-times"></i> 否'}
                </span>
            </td>
            <td class="created-cell">
                <div class="time-text">${formatTime(permission.created_at)}</div>
            </td>
            <td class="updated-cell">
                <div class="time-text">${formatTime(permission.updated_at)}</div>
            </td>
            <td class="actions-cell">
                <button class="btn-edit" onclick="editPermission('${permission.username}')">
                    <i class="fas fa-edit"></i> 编辑
                </button>
                <button class="btn-delete" onclick="deletePermission('${permission.username}')">
                    <i class="fas fa-trash"></i> 删除
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// 搜索权限
function searchPermissions() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    const filteredPermissions = currentPermissions.filter(permission => 
        permission.username.toLowerCase().includes(searchTerm.toLowerCase())
    );
    displayPermissions(filteredPermissions);
}

// 按权限筛选
function filterByPermission() {
    const filterValue = document.getElementById('permissionFilter').value;
    let filteredPermissions = currentPermissions;
    
    if (filterValue) {
        filteredPermissions = currentPermissions.filter(permission => {
            switch (filterValue) {
                case 'admin':
                    return permission.can_access_admin;
                case 'permissions':
                    return permission.can_manage_permissions;
                case 'interactions':
                    return permission.can_view_interactions;
                case 'export':
                    return permission.can_export_data;
                default:
                    return true;
            }
        });
    }
    
    displayPermissions(filteredPermissions);
}

// 显示添加权限模态框
function showAddPermissionModal() {
    editingUsername = null;
    document.getElementById('permissionModalTitle').innerHTML = '<i class="fas fa-user-plus"></i> 添加用户权限';
    document.getElementById('username').value = '';
    document.getElementById('username').disabled = false;
    
    // 重置复选框
    document.getElementById('can_access_admin').checked = false;
    document.getElementById('can_manage_permissions').checked = false;
    document.getElementById('can_view_interactions').checked = false;
    document.getElementById('can_export_data').checked = false;
    
    document.getElementById('permissionModal').style.display = 'block';
}

// 编辑权限
function editPermission(username) {
    editingUsername = username;
    document.getElementById('permissionModalTitle').innerHTML = '<i class="fas fa-user-edit"></i> 编辑用户权限';
    document.getElementById('username').value = username;
    document.getElementById('username').disabled = true;
    
    // 获取用户当前权限
    const permission = currentPermissions.find(p => p.username === username);
    if (permission) {
        document.getElementById('can_access_admin').checked = permission.can_access_admin;
        document.getElementById('can_manage_permissions').checked = permission.can_manage_permissions;
        document.getElementById('can_view_interactions').checked = permission.can_view_interactions;
        document.getElementById('can_export_data').checked = permission.can_export_data;
    }
    
    document.getElementById('permissionModal').style.display = 'block';
}

// 保存权限
function savePermission() {
    const username = document.getElementById('username').value.trim();
    const permissionsData = {
        can_access_admin: document.getElementById('can_access_admin').checked,
        can_manage_permissions: document.getElementById('can_manage_permissions').checked,
        can_view_interactions: document.getElementById('can_view_interactions').checked,
        can_export_data: document.getElementById('can_export_data').checked
    };
    
    if (!username) {
        showNotification('请输入用户名', 'error');
        return;
    }
    
    const url = editingUsername ? '/admin/permissions/update' : '/admin/permissions/create';
    const method = editingUsername ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            permissions: permissionsData
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(editingUsername ? '权限更新成功' : '权限创建成功', 'success');
            closePermissionModal();
            loadPermissions();
        } else {
            showNotification('操作失败：' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('保存权限失败:', error);
        showNotification('网络错误：' + error.message, 'error');
    });
}

// 删除权限
function deletePermission(username) {
    document.getElementById('deleteUsername').textContent = username;
    document.getElementById('deleteModal').style.display = 'block';
}

// 确认删除
function confirmDelete() {
    const username = document.getElementById('deleteUsername').textContent;
    
    fetch('/admin/permissions/delete', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('权限删除成功', 'success');
            closeDeleteModal();
            loadPermissions();
        } else {
            showNotification('删除失败：' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('删除权限失败:', error);
        showNotification('网络错误：' + error.message, 'error');
    });
}

// 关闭权限模态框
function closePermissionModal() {
    document.getElementById('permissionModal').style.display = 'none';
    editingUsername = null;
}

// 关闭删除模态框
function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

// 工具函数
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN');
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

// 用户列表相关功能
let allUsers = [];

// 显示所有用户模态框
function showAllUsersModal() {
    document.getElementById('allUsersModal').style.display = 'block';
    loadAllUsers();
    
    // 绑定搜索事件
    document.getElementById('usersSearchInput').addEventListener('input', function(e) {
        filterUsers(e.target.value);
    });
}

// 关闭所有用户模态框
function closeAllUsersModal() {
    document.getElementById('allUsersModal').style.display = 'none';
    document.getElementById('usersSearchInput').value = '';
}

// 加载所有用户
function loadAllUsers() {
    fetch('/admin/users/all')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allUsers = data.users;
                displayAllUsers(data.users);
            } else {
                showNotification('加载用户列表失败：' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('加载用户列表失败:', error);
            showNotification('网络错误：' + error.message, 'error');
        });
}

// 显示所有用户
function displayAllUsers(users) {
    const usersList = document.getElementById('usersList');
    
    if (users.length === 0) {
        usersList.innerHTML = `
            <div class="no-users">
                <i class="fas fa-users"></i>
                <p>暂无注册用户</p>
            </div>
        `;
        return;
    }
    
    usersList.innerHTML = '';
    
    users.forEach(user => {
        const userItem = document.createElement('div');
        userItem.className = 'user-item';
        
        // 生成用户头像（使用用户名首字母）
        const avatarText = user.username.charAt(0).toUpperCase();
        
        // 生成用户邮箱（如果没有则显示默认值）
        const userEmail = user.email || '';
        
        userItem.innerHTML = `
            <div class="user-info">
                <div class="user-avatar">${avatarText}</div>
                <div class="user-details">
                    <div class="user-name">${user.username}</div>
                    <div class="user-email">${userEmail}</div>
                </div>
            </div>
            <div class="user-status">
                <span class="status-badge ${user.has_permissions ? 'has-permission' : 'no-permission'}">
                    ${user.has_permissions ? '已有权限' : '无权限'}
                </span>
                <div class="user-actions">
                    ${user.has_permissions ? 
                        `<button class="btn-view-permission" onclick="viewUserPermission('${user.username}')">
                            <i class="fas fa-eye"></i> 查看权限
                        </button>` :
                        `<button class="btn-add-permission" onclick="addPermissionForUser('${user.username}')">
                            <i class="fas fa-plus"></i> 添加权限
                        </button>`
                    }
                </div>
            </div>
        `;
        
        usersList.appendChild(userItem);
    });
}

// 筛选用户
function filterUsers(searchTerm) {
    const filteredUsers = allUsers.filter(user => 
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (user.email && user.email.toLowerCase().includes(searchTerm.toLowerCase()))
    );
    displayAllUsers(filteredUsers);
}

// 为用户添加权限
function addPermissionForUser(username) {
    // 关闭用户列表模态框
    closeAllUsersModal();
    
    // 打开添加权限模态框并预填用户名
    editingUsername = null;
    document.getElementById('permissionModalTitle').innerHTML = '<i class="fas fa-user-plus"></i> 添加用户权限';
    document.getElementById('username').value = username;
    document.getElementById('username').disabled = false;
    
    // 重置复选框
    document.getElementById('can_access_admin').checked = false;
    document.getElementById('can_manage_permissions').checked = false;
    document.getElementById('can_view_interactions').checked = false;
    document.getElementById('can_export_data').checked = false;
    
    document.getElementById('permissionModal').style.display = 'block';
}

// 查看用户权限
function viewUserPermission(username) {
    // 关闭用户列表模态框
    closeAllUsersModal();
    
    // 打开编辑权限模态框
    editingUsername = username;
    document.getElementById('permissionModalTitle').innerHTML = '<i class="fas fa-user-edit"></i> 编辑用户权限';
    document.getElementById('username').value = username;
    document.getElementById('username').disabled = true;
    
    // 获取用户当前权限
    const permission = currentPermissions.find(p => p.username === username);
    if (permission) {
        document.getElementById('can_access_admin').checked = permission.can_access_admin;
        document.getElementById('can_manage_permissions').checked = permission.can_manage_permissions;
        document.getElementById('can_view_interactions').checked = permission.can_view_interactions;
        document.getElementById('can_export_data').checked = permission.can_export_data;
    } else {
        // 如果没有权限记录，重置复选框
        document.getElementById('can_access_admin').checked = false;
        document.getElementById('can_manage_permissions').checked = false;
        document.getElementById('can_view_interactions').checked = false;
        document.getElementById('can_export_data').checked = false;
    }
    
    document.getElementById('permissionModal').style.display = 'block';
}

// 显示添加用户模态框
function showAddUserModal() {
    document.getElementById('addUserModal').style.display = 'block';
    // 清空表单
    document.getElementById('addUserForm').reset();
}

// 关闭添加用户模态框
function closeAddUserModal() {
    document.getElementById('addUserModal').style.display = 'none';
}

// 创建新用户
function createUser() {
    const username = document.getElementById('newUsername').value.trim();
    const password = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // 验证输入
    if (!username || !password || !confirmPassword) {
        showNotification('请填写所有必填字段', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showNotification('两次输入的密码不一致', 'error');
        return;
    }
    
    if (password.length < 3) {
        showNotification('密码长度至少3位', 'error');
        return;
    }
    
    // 获取权限设置
    const permissions = {
        can_access_admin: document.getElementById('new_can_access_admin').checked,
        can_manage_permissions: document.getElementById('new_can_manage_permissions').checked,
        can_view_interactions: document.getElementById('new_can_view_interactions').checked,
        can_export_data: document.getElementById('new_can_export_data').checked
    };
    
    // 发送创建用户请求
    fetch('/admin/users/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password,
            permissions: permissions
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('用户创建成功！', 'success');
            closeAddUserModal();
            // 重新加载权限列表
            loadPermissions();
        } else {
            showNotification('创建用户失败：' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('创建用户失败:', error);
        showNotification('网络错误：' + error.message, 'error');
    });
}

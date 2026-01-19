// 全局变量
let currentPage = 'index';
let messages = [];
let conversations = [];
let isLoading = false;
let currentConversationId = null;
let userInfo = null;

// API基础URL
const API_BASE_URL = window.location.origin;

// 页面导航
function navigateTo(page) {
    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab-item').forEach(t => t.classList.remove('active'));
    
    // 显示目标页面
    document.getElementById(`page-${page}`).classList.add('active');
    document.querySelectorAll('.tab-item')[getPageIndex(page)].classList.add('active');
    
    currentPage = page;
    
    // 加载页面数据
    if (page === 'history') {
        loadHistory();
    } else if (page === 'profile') {
        loadProfile();
    }
}

function getPageIndex(page) {
    const pages = ['index', 'chat', 'history', 'profile'];
    return pages.indexOf(page);
}

// 聊天功能
function handleKeyPress(event) {
    if (event.key === 'Enter' && !isLoading) {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    
    if (!text || isLoading) return;
    
    // 添加用户消息
    addMessage('user', text);
    input.value = '';
    
    // 显示加载状态
    isLoading = true;
    showLoading();
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/api/chat/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token ? `Bearer ${token}` : ''
            },
            body: JSON.stringify({
                message: text,
                conversation_id: currentConversationId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // 添加AI回复
            addMessage('assistant', data.reply, data.source);
            currentConversationId = data.conversation_id;
        } else {
            addMessage('assistant', '抱歉，发生了错误，请稍后重试。');
        }
    } catch (error) {
        console.error('发送消息失败:', error);
        addMessage('assistant', '网络错误，请检查连接后重试。');
    } finally {
        isLoading = false;
        hideLoading();
    }
}

function addMessage(role, content, source = null) {
    const messageList = document.getElementById('messageList');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-item ${role}`;
    
    const avatar = role === 'user' ? '👤' : '🤖';
    let sourceHtml = '';
    
    if (source) {
        const sourceText = source === 'internal' 
            ? '来源：北京市学校体育联合会' 
            : '来源：互联网，请斟酌使用';
        sourceHtml = `<div class="message-source">${sourceText}</div>`;
    }
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div>${content}</div>
            ${sourceHtml}
        </div>
    `;
    
    messageList.appendChild(messageDiv);
    messageList.scrollTop = messageList.scrollHeight;
    
    messages.push({ role, content, source });
}

function showLoading() {
    const messageList = document.getElementById('messageList');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading';
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.textContent = 'AI正在思考中...';
    messageList.appendChild(loadingDiv);
    messageList.scrollTop = messageList.scrollHeight;
}

function hideLoading() {
    const loading = document.getElementById('loadingIndicator');
    if (loading) {
        loading.remove();
    }
}

// 历史记录功能
async function loadHistory() {
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = '<div class="loading">加载中...</div>';
    
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            showEmptyHistory();
            return;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/conversation/list`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.conversations && data.conversations.length > 0) {
            conversations = data.conversations;
            renderConversations();
        } else {
            showEmptyHistory();
        }
    } catch (error) {
        console.error('加载历史失败:', error);
        showEmptyHistory();
    }
}

function showEmptyHistory() {
    const historyContent = document.getElementById('historyContent');
    historyContent.innerHTML = `
        <div class="empty">
            <span class="empty-icon">📝</span>
            <span class="empty-text">暂无对话记录</span>
            <button class="start-btn" onclick="navigateTo('chat')">开始对话</button>
        </div>
    `;
}

function renderConversations() {
    const historyContent = document.getElementById('historyContent');
    const listHtml = conversations.map(conv => `
        <div class="conversation-item" onclick="openConversation('${conv.id}')">
            <div class="conversation-content">
                <div class="conversation-title">${conv.title || '对话'}</div>
                <div class="conversation-message">${conv.lastMessage || ''}</div>
                <div class="conversation-time">${formatTime(conv.updated_at)}</div>
            </div>
            <div class="delete-btn" onclick="deleteConversation(event, '${conv.id}')">🗑️</div>
        </div>
    `).join('');
    
    historyContent.innerHTML = `<div class="conversation-list">${listHtml}</div>`;
}

function openConversation(id) {
    currentConversationId = id;
    navigateTo('chat');
    loadConversationMessages(id);
}

async function loadConversationMessages(id) {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/api/conversation/${id}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok && data.messages) {
            const messageList = document.getElementById('messageList');
            messageList.innerHTML = '';
            messages = [];
            
            data.messages.forEach(msg => {
                addMessage(msg.role, msg.content, msg.source);
            });
        }
    } catch (error) {
        console.error('加载对话失败:', error);
    }
}

async function deleteConversation(event, id) {
    event.stopPropagation();
    
    if (!confirm('确定要删除这条对话记录吗？')) {
        return;
    }
    
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/api/conversation/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            loadHistory();
        }
    } catch (error) {
        console.error('删除对话失败:', error);
        alert('删除失败，请重试');
    }
}

// 个人中心功能
function loadProfile() {
    const token = localStorage.getItem('token');
    userInfo = JSON.parse(localStorage.getItem('userInfo') || 'null');
    
    if (userInfo && token) {
        document.getElementById('loginSection').style.display = 'none';
        document.getElementById('userSection').style.display = 'flex';
        document.getElementById('logoutBtn').style.display = 'block';
        
        document.getElementById('userAvatar').src = userInfo.avatar || 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="60" height="60"><text y="40" font-size="40">👤</text></svg>';
        document.getElementById('userNickname').textContent = userInfo.nickname || '用户';
        document.getElementById('userRole').textContent = userInfo.role || '普通用户';
    } else {
        document.getElementById('loginSection').style.display = 'block';
        document.getElementById('userSection').style.display = 'none';
        document.getElementById('logoutBtn').style.display = 'none';
    }
}

async function handleLogin() {
    // 简单的登录实现（实际项目中应该有完整的登录流程）
    const username = prompt('请输入用户名:');
    if (!username) return;
    
    const password = prompt('请输入密码:');
    if (!password) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            localStorage.setItem('userInfo', JSON.stringify(data.user));
            userInfo = data.user;
            loadProfile();
            alert('登录成功！');
        } else {
            alert(data.detail || '登录失败');
        }
    } catch (error) {
        console.error('登录失败:', error);
        alert('登录失败，请重试');
    }
}

function handleLogout() {
    if (confirm('确定要退出登录吗？')) {
        localStorage.removeItem('token');
        localStorage.removeItem('userInfo');
        userInfo = null;
        currentConversationId = null;
        messages = [];
        document.getElementById('messageList').innerHTML = '';
        loadProfile();
    }
}

// 工具函数
function formatTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) {
        return '刚刚';
    } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`;
    } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}小时前`;
    } else if (diff < 604800000) {
        return `${Math.floor(diff / 86400000)}天前`;
    } else {
        return date.toLocaleDateString('zh-CN');
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI大健康助手 Web版已加载');
    
    // 检查登录状态
    const token = localStorage.getItem('token');
    if (token) {
        userInfo = JSON.parse(localStorage.getItem('userInfo') || 'null');
    }
});

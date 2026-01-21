// 全局变量
let currentPage = 'role-select';
let currentRole = null; // teacher/student/parent/admin
let messages = [];
let conversations = [];
let isLoading = false;
let currentConversationId = null;
let userInfo = null;

// API基础URL
const API_BASE_URL = window.location.origin;

// 角色配置
const ROLE_CONFIG = {
    teacher: {
        name: '教师',
        icon: '👨‍🏫',
        color: '#1890ff',
        features: ['数据上传', '课课练方案', '运动会设计', '班级分析', 'AI咨询']
    },
    student: {
        name: '学生',
        icon: '🎓',
        color: '#52c41a',
        features: ['我的体测', '训练方案', '运动指导', '心理健康', 'AI咨询']
    },
    parent: {
        name: '家长',
        icon: '👨‍👩‍👧',
        color: '#fa8c16',
        features: ['孩子体测', '家庭锻炼', '健康知识', '营养指导', 'AI咨询']
    },
    admin: {
        name: '主管部门',
        icon: '📊',
        color: '#722ed1',
        features: ['数据统计', '区域分析', '学校对比', '报表导出', 'AI咨询']
    }
};

// 页面导航
function navigateTo(page) {
    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    
    // 显示目标页面
    const targetPage = document.getElementById(`page-${page}`);
    if (targetPage) {
        targetPage.classList.add('active');
        currentPage = page;
        
        // 更新底部导航栏
        updateTabBar();
        
        // 加载页面数据
        if (page === 'history') {
            loadHistory();
        } else if (page === 'profile') {
            loadProfile();
        }
    }
}

function updateTabBar() {
    document.querySelectorAll('.tab-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const activeTab = document.querySelector(`.tab-item[data-page="${currentPage}"]`);
    if (activeTab) {
        activeTab.classList.add('active');
    }
}

// 角色选择
function selectRole(role) {
    currentRole = role;
    localStorage.setItem('userRole', role);
    
    // 显示对应角色的首页
    showRoleHomePage(role);
}

function showRoleHomePage(role) {
    // 隐藏角色选择页
    document.getElementById('page-role-select').classList.remove('active');
    
    // 显示对应角色的首页
    const homePage = document.getElementById(`page-${role}-home`);
    if (homePage) {
        homePage.classList.add('active');
        currentPage = `${role}-home`;
    }
    
    // 更新底部导航栏
    updateTabBar();
}

// 切换角色
function changeRole() {
    currentRole = null;
    localStorage.removeItem('userRole');
    navigateTo('role-select');
}

// 数据上传处理
function handleFileUpload(type) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.xlsx,.xls,.csv';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        let result;
        if (type === 'fitness') {
            result = await uploadFitnessData(file);
        } else if (type === 'exercises') {
            result = await uploadSportsExercises(file);
        }
        
        if (result) {
            showToast('数据上传成功！', 'success');
        }
    };
    
    input.click();
}

// 查询学生数据
async function queryStudentData() {
    const studentId = prompt('请输入学生学号：');
    if (!studentId) return;
    
    const data = await getStudentData(studentId);
    if (data) {
        // 显示数据
        displayStudentDataModal(data);
        
        // 获取训练推荐
        const recommendations = await getExerciseRecommendations(studentId);
        if (recommendations) {
            displayExerciseRecommendations(recommendations);
        }
    }
}

// 查询班级数据
async function queryClassData() {
    const className = prompt('请输入班级名称（如：1班）：');
    if (!className) return;
    
    const data = await getClassData(className);
    if (data) {
        displayClassData(data);
    }
}

// 显示学生数据弹窗
function displayStudentDataModal(data) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>学生体测数据</h3>
                <button class="close-btn" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <div class="modal-body" id="student-data-display">
                <div class="data-card">
                    <div class="data-header">
                        <h4>基本信息</h4>
                    </div>
                    <div class="data-content">
                        <div class="data-item">
                            <span class="label">学号：</span>
                            <span class="value">${data.student_id}</span>
                        </div>
                        <div class="data-item">
                            <span class="label">年级：</span>
                            <span class="value">${data.grade}</span>
                        </div>
                        <div class="data-item">
                            <span class="label">班级：</span>
                            <span class="value">${data.class}</span>
                        </div>
                        <div class="data-item">
                            <span class="label">性别：</span>
                            <span class="value">${data.gender}</span>
                        </div>
                        <div class="data-item">
                            <span class="label">身高：</span>
                            <span class="value">${data.basic_info.height} cm</span>
                        </div>
                        <div class="data-item">
                            <span class="label">体重：</span>
                            <span class="value">${data.basic_info.weight} kg (${data.basic_info.weight_level})</span>
                        </div>
                    </div>
                </div>
                
                <div class="data-card">
                    <div class="data-header">
                        <h4>体测成绩</h4>
                    </div>
                    <div class="data-content">
                        ${renderTestItem('肺活量', data.test_results.lung_capacity)}
                        ${renderTestItem('50米跑', data.test_results.run_50m)}
                        ${renderTestItem('坐位体前屈', data.test_results.sit_reach)}
                        ${renderTestItem('仰卧起坐', data.test_results.sit_up)}
                        ${renderTestItem('跳绳', data.test_results.rope_skip)}
                        ${renderTestItem('立定跳远', data.test_results.standing_jump)}
                    </div>
                </div>
                
                <div class="data-card">
                    <div class="data-header">
                        <h4>总分</h4>
                    </div>
                    <div class="data-content">
                        <div class="score-summary">
                            <div class="score-item">
                                <div class="score-label">标准分</div>
                                <div class="score-value">${data.total.standard_score}</div>
                            </div>
                            <div class="score-item">
                                <div class="score-label">附加分</div>
                                <div class="score-value">${data.total.bonus_score}</div>
                            </div>
                            <div class="score-item highlight">
                                <div class="score-label">总分</div>
                                <div class="score-value">${data.total.total_score}</div>
                            </div>
                            <div class="score-item">
                                <div class="score-label">等级</div>
                                <div class="score-value level-${data.total.level}">${data.total.level}</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div id="exercise-recommendations"></div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('show'), 10);
}

function renderTestItem(name, item) {
    if (!item || !item.value) return '';
    
    return `
        <div class="test-item">
            <div class="test-name">${name}</div>
            <div class="test-details">
                <span class="test-value">${item.value}</span>
                <span class="test-score">得分: ${item.score}</span>
                <span class="test-level level-${item.level}">${item.level}</span>
            </div>
        </div>
    `;
}

// 显示班级数据
function displayClassData(data) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content large">
            <div class="modal-header">
                <h3>${data.class_name} 体测数据</h3>
                <button class="close-btn" onclick="this.closest('.modal').remove()">×</button>
            </div>
            <div class="modal-body">
                <div class="class-stats">
                    <div class="stat-item">
                        <div class="stat-label">总人数</div>
                        <div class="stat-value">${data.total_count}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">平均分</div>
                        <div class="stat-value">${data.avg_score}</div>
                    </div>
                </div>
                <div class="level-distribution">
                    <h4>等级分布</h4>
                    ${Object.entries(data.level_stats).map(([level, count]) => `
                        <div class="level-bar">
                            <span class="level-name">${level}</span>
                            <div class="bar-container">
                                <div class="bar-fill" style="width: ${(count / data.total_count * 100)}%"></div>
                            </div>
                            <span class="level-count">${count}人</span>
                        </div>
                    `).join('')}
                </div>
                <div class="student-list">
                    <h4>学生列表</h4>
                    <table>
                        <thead>
                            <tr>
                                <th>学号</th>
                                <th>性别</th>
                                <th>总分</th>
                                <th>等级</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.students.map(s => `
                                <tr>
                                    <td>${s.student_id}</td>
                                    <td>${s.gender}</td>
                                    <td>${s.total_score}</td>
                                    <td><span class="level-badge level-${s.level}">${s.level}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    setTimeout(() => modal.classList.add('show'), 10);
}

// 显示训练推荐
function displayExerciseRecommendations(data) {
    const container = document.getElementById('exercise-recommendations');
    if (!container) return;
    
    let html = '<div class="recommendations-container">';
    
    if (data.weak_items && data.weak_items.length > 0) {
        html += `
            <div class="weak-items">
                <h4>需要加强的项目：</h4>
                <div class="weak-tags">
                    ${data.weak_items.map(item => `<span class="weak-tag">${item}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    if (data.recommended_exercises && data.recommended_exercises.length > 0) {
        html += '<div class="exercise-list">';
        data.recommended_exercises.forEach(ex => {
            html += `
                <div class="exercise-card">
                    <div class="exercise-header">
                        <h4>${ex.name}</h4>
                        <span class="difficulty-badge">${ex.difficulty}</span>
                    </div>
                    <div class="exercise-body">
                        <p>${ex.description.substring(0, 100)}...</p>
                        <div class="exercise-tags">
                            <span class="tag">提升：${ex.improve_test}</span>
                        </div>
                    </div>
                    ${ex.image_url && ex.image_url !== 'nan' ? `<img src="${ex.image_url}" alt="${ex.name}" class="exercise-image">` : ''}
                </div>
            `;
        });
        html += '</div>';
    } else {
        html += '<div class="no-recommendations">暂无推荐动作</div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}

// 发送消息到AI
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message || isLoading) return;
    
    // 添加用户消息到界面
    addMessageToUI('user', message);
    input.value = '';
    isLoading = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/send`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                role: currentRole
            })
        });
        
        const data = await response.json();
        
        if (data.reply) {
            addMessageToUI('assistant', data.reply);
        } else {
            addMessageToUI('assistant', '抱歉，我现在无法回答。请稍后再试。');
        }
    } catch (error) {
        console.error('发送消息失败:', error);
        addMessageToUI('assistant', '抱歉，发送消息失败。请检查网络连接。');
    } finally {
        isLoading = false;
    }
}

// 添加消息到UI
function addMessageToUI(role, content) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-content">${content}</div>
        <div class="message-time">${new Date().toLocaleTimeString('zh-CN', {hour: '2-digit', minute: '2-digit'})}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 快速提示点击
function sendQuickPrompt(prompt) {
    const input = document.getElementById('message-input');
    if (input) {
        input.value = prompt;
        sendMessage();
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('AI大健康助手 Web版已加载');
    
    // 检查是否已选择角色
    const savedRole = localStorage.getItem('userRole');
    if (savedRole && ROLE_CONFIG[savedRole]) {
        currentRole = savedRole;
        showRoleHomePage(savedRole);
    } else {
        navigateTo('role-select');
    }
    
    // 检查登录状态
    const token = localStorage.getItem('token');
    if (token) {
        userInfo = JSON.parse(localStorage.getItem('userInfo') || 'null');
    }
    
    // 绑定消息输入框回车事件
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});

// 导航到首页
function navigateToHome() {
    if (currentRole) {
        navigateTo(`${currentRole}-home`);
    } else {
        navigateTo('role-select');
    }
}

// 导航到数据页面
function navigateToData() {
    if (currentRole === 'teacher') {
        navigateTo('teacher-data');
    } else if (currentRole === 'student') {
        navigateTo('student-query');
    } else if (currentRole === 'parent') {
        navigateTo('parent-query');
    } else if (currentRole === 'admin') {
        navigateTo('admin-data');
    } else {
        navigateTo('role-select');
    }
}

// 通过输入框查询学生数据
async function queryStudentDataByInput() {
    const input = document.getElementById('student-id-input');
    const studentId = input.value.trim();
    
    if (!studentId) {
        showToast('请输入学号', 'warning');
        return;
    }
    
    const data = await getStudentData(studentId);
    if (data) {
        displayStudentDataInContainer(data, 'student-data-container');
        
        // 获取训练推荐
        const recommendations = await getExerciseRecommendations(studentId);
        if (recommendations) {
            displayExerciseRecommendationsInContainer(recommendations, 'student-data-container');
        }
    }
}

// 查询孩子数据
async function queryChildData() {
    const input = document.getElementById('child-id-input');
    const studentId = input.value.trim();
    
    if (!studentId) {
        showToast('请输入孩子的学号', 'warning');
        return;
    }
    
    const data = await getStudentData(studentId);
    if (data) {
        displayStudentDataInContainer(data, 'child-data-container');
        
        // 获取训练推荐
        const recommendations = await getExerciseRecommendations(studentId);
        if (recommendations) {
            displayExerciseRecommendationsInContainer(recommendations, 'child-data-container');
        }
    }
}

// 督导端查询班级数据
async function queryClassDataByAdmin() {
    const input = document.getElementById('admin-class-input');
    const className = input.value.trim();
    
    if (!className) {
        showToast('请输入班级名称', 'warning');
        return;
    }
    
    const data = await getClassData(className);
    if (data) {
        displayClassDataInContainer(data, 'admin-data-container');
    }
}

// 在容器中显示学生数据
function displayStudentDataInContainer(data, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="data-card">
            <div class="data-header">
                <h4>基本信息</h4>
            </div>
            <div class="data-content">
                <div class="data-item">
                    <span class="label">学号：</span>
                    <span class="value">${data.student_id}</span>
                </div>
                <div class="data-item">
                    <span class="label">年级：</span>
                    <span class="value">${data.grade}</span>
                </div>
                <div class="data-item">
                    <span class="label">班级：</span>
                    <span class="value">${data.class}</span>
                </div>
                <div class="data-item">
                    <span class="label">性别：</span>
                    <span class="value">${data.gender}</span>
                </div>
                <div class="data-item">
                    <span class="label">身高：</span>
                    <span class="value">${data.basic_info.height} cm</span>
                </div>
                <div class="data-item">
                    <span class="label">体重：</span>
                    <span class="value">${data.basic_info.weight} kg (${data.basic_info.weight_level})</span>
                </div>
            </div>
        </div>
        
        <div class="data-card">
            <div class="data-header">
                <h4>体测成绩</h4>
            </div>
            <div class="data-content">
                ${renderTestItem('肺活量', data.test_results.lung_capacity)}
                ${renderTestItem('50米跑', data.test_results.run_50m)}
                ${renderTestItem('坐位体前屈', data.test_results.sit_reach)}
                ${renderTestItem('仰卧起坐', data.test_results.sit_up)}
                ${renderTestItem('跳绳', data.test_results.rope_skip)}
                ${renderTestItem('立定跳远', data.test_results.standing_jump)}
            </div>
        </div>
        
        <div class="data-card">
            <div class="data-header">
                <h4>总分</h4>
            </div>
            <div class="data-content">
                <div class="score-summary">
                    <div class="score-item">
                        <div class="score-label">标准分</div>
                        <div class="score-value">${data.total.standard_score}</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">附加分</div>
                        <div class="score-value">${data.total.bonus_score}</div>
                    </div>
                    <div class="score-item highlight">
                        <div class="score-label">总分</div>
                        <div class="score-value">${data.total.total_score}</div>
                    </div>
                    <div class="score-item">
                        <div class="score-label">等级</div>
                        <div class="score-value level-${data.total.level}">${data.total.level}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="recommendations-${containerId}"></div>
    `;
}

// 在容器中显示训练推荐
function displayExerciseRecommendationsInContainer(data, containerId) {
    const container = document.getElementById(`recommendations-${containerId}`);
    if (!container) return;
    
    let html = '<div class="data-card"><div class="data-header"><h4>训练建议</h4></div><div class="data-content">';
    
    if (data.weak_items && data.weak_items.length > 0) {
        html += `
            <div class="weak-items">
                <p><strong>需要加强的项目：</strong></p>
                <div class="weak-tags">
                    ${data.weak_items.map(item => `<span class="weak-tag">${item}</span>`).join('')}
                </div>
            </div>
        `;
    }
    
    if (data.recommended_exercises && data.recommended_exercises.length > 0) {
        html += '<div class="exercise-list">';
        data.recommended_exercises.forEach(ex => {
            html += `
                <div class="exercise-card">
                    <div class="exercise-header">
                        <h5>${ex.name}</h5>
                        <span class="difficulty-badge">${ex.difficulty}</span>
                    </div>
                    <div class="exercise-body">
                        <p>${ex.description.substring(0, 100)}...</p>
                        <div class="exercise-tags">
                            <span class="tag">提升：${ex.improve_test}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
    } else {
        html += '<p class="no-data">暂无推荐动作</p>';
    }
    
    html += '</div></div>';
    container.innerHTML = html;
}

// 在容器中显示班级数据
function displayClassDataInContainer(data, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="data-card">
            <div class="data-header">
                <h4>${data.class_name} 统计数据</h4>
            </div>
            <div class="data-content">
                <div class="class-stats">
                    <div class="stat-item">
                        <div class="stat-label">总人数</div>
                        <div class="stat-value">${data.total_count}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-label">平均分</div>
                        <div class="stat-value">${data.avg_score}</div>
                    </div>
                </div>
                <div class="level-distribution">
                    <h5>等级分布</h5>
                    ${Object.entries(data.level_stats).map(([level, count]) => `
                        <div class="level-bar">
                            <span class="level-name">${level}</span>
                            <div class="bar-container">
                                <div class="bar-fill" style="width: ${(count / data.total_count * 100)}%"></div>
                            </div>
                            <span class="level-count">${count}人</span>
                        </div>
                    `).join('')}
                </div>
                <div class="student-list">
                    <h5>学生列表</h5>
                    <table>
                        <thead>
                            <tr>
                                <th>学号</th>
                                <th>性别</th>
                                <th>总分</th>
                                <th>等级</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.students.map(s => `
                                <tr>
                                    <td>${s.student_id}</td>
                                    <td>${s.gender}</td>
                                    <td>${s.total_score}</td>
                                    <td><span class="level-badge level-${s.level}">${s.level}</span></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// Toast提示
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
/**
 * 数据管理模块
 * 处理体测数据和动作库的上传、查询
 */

// 上传体测数据
async function uploadFitnessData(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoading('正在上传体测数据...');
        
        const response = await fetch(`${API_BASE_URL}/api/data/upload/fitness-data`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            },
            body: formData
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showToast(`上传成功！成功导入${result.success_count}条数据`, 'success');
            if (result.error_count > 0) {
                showToast(`失败${result.error_count}条`, 'warning');
            }
            return result;
        } else {
            showToast(result.detail || '上传失败', 'error');
            return null;
        }
    } catch (error) {
        hideLoading();
        showToast('上传失败：' + error.message, 'error');
        return null;
    }
}

// 上传体育动作库
async function uploadSportsExercises(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showLoading('正在上传动作库数据...');
        
        const response = await fetch(`${API_BASE_URL}/api/data/upload/sports-exercises`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            },
            body: formData
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showToast(`上传成功！成功导入${result.success_count}条数据`, 'success');
            if (result.error_count > 0) {
                showToast(`失败${result.error_count}条`, 'warning');
            }
            return result;
        } else {
            showToast(result.detail || '上传失败', 'error');
            return null;
        }
    } catch (error) {
        hideLoading();
        showToast('上传失败：' + error.message, 'error');
        return null;
    }
}

// 查询学生体测数据
async function getStudentData(studentId) {
    try {
        showLoading('正在查询数据...');
        
        const response = await fetch(`${API_BASE_URL}/api/data/student/${studentId}`);
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            return result.data;
        } else {
            showToast(result.detail || '查询失败', 'error');
            return null;
        }
    } catch (error) {
        hideLoading();
        showToast('查询失败：' + error.message, 'error');
        return null;
    }
}

// 查询班级体测数据
async function getClassData(className) {
    try {
        showLoading('正在查询班级数据...');
        
        const response = await fetch(`${API_BASE_URL}/api/data/class/${className}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            return result.data;
        } else {
            showToast(result.detail || '查询失败', 'error');
            return null;
        }
    } catch (error) {
        hideLoading();
        showToast('查询失败：' + error.message, 'error');
        return null;
    }
}

// 获取训练动作推荐
async function getExerciseRecommendations(studentId) {
    try {
        showLoading('正在生成推荐...');
        
        const response = await fetch(`${API_BASE_URL}/api/data/exercises/recommend?student_id=${studentId}`);
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            return result.data;
        } else {
            showToast(result.detail || '获取推荐失败', 'error');
            return null;
        }
    } catch (error) {
        hideLoading();
        showToast('获取推荐失败：' + error.message, 'error');
        return null;
    }
}

// 显示学生体测数据
function displayStudentData(data) {
    const container = document.getElementById('student-data-display');
    if (!container) return;
    
    const html = `
        <div class="data-card">
            <div class="data-header">
                <h3>基本信息</h3>
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
                <h3>体测成绩</h3>
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
                <h3>总分</h3>
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
    `;
    
    container.innerHTML = html;
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
                        <p>${ex.description}</p>
                        <div class="exercise-tags">
                            <span class="tag">提升：${ex.improve_test}</span>
                        </div>
                    </div>
                    ${ex.image_url ? `<img src="${ex.image_url}" alt="${ex.name}" class="exercise-image">` : ''}
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

// 获取Token
function getToken() {
    return localStorage.getItem('authToken') || '';
}

// 显示加载提示
function showLoading(message = '加载中...') {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.querySelector('.loading-text').textContent = message;
        loading.style.display = 'flex';
    }
}

// 隐藏加载提示
function hideLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.style.display = 'none';
    }
}

// 显示提示消息
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

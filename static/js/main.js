// 项目管理器前端逻辑 - 苹果风格亮色主题

let projects = [];
let allProjects = [];
let sortBy = 'recent';
let currentFilter = 'all';

// 页面加载时获取项目列表
document.addEventListener('DOMContentLoaded', () => {
    loadProjects();
    setInterval(() => loadProjects(true), 30000);
});

// 筛选项目
function filterProjects(filter) {
    currentFilter = filter;
    const now = Date.now() / 1000;
    const oneWeekAgo = now - (7 * 24 * 60 * 60);

    if (filter === 'all') {
        projects = [...allProjects];
        showNotification('显示全部项目', 'info');
    } else if (filter === 'thisWeek') {
        projects = allProjects.filter(p => p.last_modified && p.last_modified > oneWeekAgo);
        showNotification(`本周活跃项目 (${projects.length}个)`, 'success');
    }
    renderProjects();

    // 滚动到项目列表
    document.getElementById('projects').scrollIntoView({ behavior: 'smooth' });
}

// 加载项目列表
async function loadProjects(silent = false) {
    try {
        const response = await fetch('/api/projects');
        const data = await response.json();

        if (data.success) {
            allProjects = data.projects;
            const now = Date.now() / 1000;
            const oneWeekAgo = now - (7 * 24 * 60 * 60);

            if (currentFilter === 'all') {
                projects = [...allProjects];
            } else if (currentFilter === 'thisWeek') {
                projects = allProjects.filter(p => p.last_modified && p.last_modified > oneWeekAgo);
            }
            renderProjects();
            updateStats();
        } else if (!silent) {
            showError('加载项目失败: ' + data.message);
        }
    } catch (error) {
        if (!silent) showError('加载项目失败: ' + error.message);
    }
}

// 渲染项目列表
function renderProjects() {
    const container = document.getElementById('projectsList');

    if (projects.length === 0) {
        container.innerHTML = `
            <div class="text-center py-20">
                <div class="text-6xl mb-4 opacity-50">📁</div>
                <p class="text-gray-500 text-lg">暂无项目</p>
            </div>
        `;
        return;
    }

    // 按类别分组
    const categories = {};
    projects.forEach(project => {
        const category = project.category || '其他';
        if (!categories[category]) categories[category] = [];
        categories[category].push(project);
    });

    const categoryOrder = ['管理工具', '数据同步', '网站应用', '监控工具', '测试/问卷', '自动化工作流', 'API服务', '前端应用', '机器人', '其他'];
    const categoryIcons = {
        '管理工具': '⚙️', '数据同步': '🔄', '网站应用': '🌐', '监控工具': '📡',
        '测试/问卷': '📝', '自动化工作流': '🤖', 'API服务': '🔌', '前端应用': '🎨',
        '机器人': '🤖', '其他': '📁'
    };

    // 分类卡片
    let categoryHtml = '<div class="mb-12"><div class="grid grid-cols-2 md:grid-cols-5 gap-4">';
    categoryOrder.forEach(category => {
        const count = categories[category] ? categories[category].length : 0;
        if (count > 0) {
            categoryHtml += `
                <div onclick="scrollToCategory('${category}')" class="category-card p-5 text-center cursor-pointer">
                    <div class="text-3xl mb-2">${categoryIcons[category]}</div>
                    <div class="text-sm font-medium text-gray-500 mb-1">${category}</div>
                    <div class="text-2xl font-bold text-title">${count}</div>
                </div>
            `;
        }
    });
    categoryHtml += '</div></div>';

    let html = categoryHtml;

    // 排序切换
    html += `
        <div class="mb-8 flex items-center justify-between">
            <span class="text-gray-500">${sortBy === 'recent' ? '🕐 按最近修改排序' : '📁 按分类排序'}</span>
            <button onclick="sortBy = sortBy === 'recent' ? 'category' : 'recent'; renderProjects();"
                class="apple-button apple-button-secondary px-4 py-2 text-sm">
                切换视图
            </button>
        </div>
    `;

    if (sortBy === 'recent') {
        html += `<div class="space-y-6">
            ${projects.sort((a, b) => (b.last_modified || 0) - (a.last_modified || 0)).map(project => createProjectCard(project)).join('')}
        </div>`;
    } else {
        categoryOrder.forEach(category => {
            if (categories[category] && categories[category].length > 0) {
                html += `
                    <div id="category-${category}" class="mb-12 scroll-mt-24">
                        <div class="flex items-center mb-6">
                            <span class="text-2xl mr-3">${categoryIcons[category]}</span>
                            <h3 class="text-xl font-semibold text-title">${category}</h3>
                            <span class="ml-3 text-gray-500">(${categories[category].length})</span>
                        </div>
                        <div class="space-y-6">
                            ${categories[category].map(project => createProjectCard(project)).join('')}
                        </div>
                    </div>
                `;
            }
        });
    }

    container.innerHTML = html;
}

// 滚动到指定分类
function scrollToCategory(category) {
    sortBy = 'category';
    renderProjects();
    setTimeout(() => {
        const element = document.getElementById(`category-${category}`);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
            element.classList.add('highlight-flash');
            setTimeout(() => element.classList.remove('highlight-flash'), 2000);
        }
    }, 100);
}

// 创建项目卡片 - 亮色主题
function createProjectCard(project) {
    const isRunning = project.status === 'running';
    const websiteUrl = project.port ? `http://localhost:${project.port}` : null;

    const formatTime = (timestamp) => {
        if (!timestamp) return '';
        const now = Date.now() / 1000;
        const diff = now - timestamp;
        if (diff < 60) return '刚刚';
        if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
        if (diff < 604800) return `${Math.floor(diff / 86400)}天前`;
        const date = new Date(timestamp * 1000);
        return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' });
    };

    return `
        <div class="project-card p-6">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <!-- 项目信息 -->
                <div class="flex-1">
                    <div class="flex items-center flex-wrap gap-3 mb-3">
                        <h3 class="text-xl font-semibold text-title">${project.chinese_name || project.name}</h3>
                        ${isRunning ? '<span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700 border border-green-200">运行中</span>' : ''}
                        ${project.port ? `<span class="px-2 py-1 text-xs font-mono text-indigo-600 bg-indigo-50 rounded-lg border border-indigo-100">:${project.port}</span>` : ''}
                        ${project.last_modified ? `<span class="text-xs text-gray-400">🕐 ${formatTime(project.last_modified)}</span>` : ''}
                    </div>

                    <div class="space-y-2 text-sm">
                        <div class="text-gray-500">
                            <span class="text-gray-400">📁</span>
                            <code class="text-gray-500">${project.name}</code>
                        </div>

                        ${project.online_url ? `
                            <div>
                                <span class="text-gray-400">🌐</span>
                                <a href="${project.online_url}" target="_blank" class="apple-link">${project.online_url}</a>
                            </div>
                        ` : ''}

                        ${project.description && project.description !== '无描述' ? `
                            <p class="text-gray-500 leading-relaxed">${project.description.slice(0, 100)}${project.description.length > 100 ? '...' : ''}</p>
                        ` : ''}

                        ${project.tech_stack.length > 0 ? `
                            <div class="flex flex-wrap gap-2 mt-3">
                                ${project.tech_stack.map(tech => `
                                    <span class="px-2 py-1 text-xs rounded-lg bg-purple-50 text-purple-600 border border-purple-100">${tech}</span>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>

                <!-- 操作按钮 -->
                <div class="flex flex-col gap-2 md:w-40">
                    ${project.online_url ? `
                        <button onclick="window.open('${project.online_url}', '_blank')"
                            class="apple-button w-full px-4 py-2.5 bg-green-500 hover:bg-green-600 text-white rounded-xl text-sm font-medium shadow-sm">
                            🌐 线上
                        </button>
                    ` : ''}
                    ${project.has_start_script ? `
                        ${isRunning ? `
                            ${project.port ? `
                                <button onclick="openProject('${project.port}')"
                                    class="apple-button w-full px-4 py-2.5 bg-blue-500 hover:bg-blue-600 text-white rounded-xl text-sm font-medium shadow-sm">
                                    🖥 本地
                                </button>
                            ` : ''}
                            <button onclick="stopProject('${project.port}')"
                                class="apple-button w-full px-4 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-xl text-sm font-medium shadow-sm">
                                ⏹ 停止
                            </button>
                        ` : `
                            <button onclick="startProject('${project.path}')"
                                class="apple-button apple-button-primary w-full px-4 py-2.5 rounded-xl text-sm font-medium">
                                ▶ 启动
                            </button>
                        `}
                    ` : ''}
                    <button onclick="openInTerminal('${project.path}')"
                        class="apple-button apple-button-secondary w-full px-4 py-2.5 rounded-xl text-sm font-medium">
                        💻 终端
                    </button>
                </div>
            </div>
        </div>
    `;
}

// 更新统计数据
function updateStats() {
    const total = allProjects.length;
    const now = Date.now() / 1000;
    const oneWeekAgo = now - (7 * 24 * 60 * 60);
    const weeklyActive = allProjects.filter(p => p.last_modified && p.last_modified > oneWeekAgo).length;
    const sortedByTime = [...allProjects].sort((a, b) => (b.last_modified || 0) - (a.last_modified || 0));
    const recentProject = sortedByTime[0];

    // 数字动画效果
    animateNumber('totalProjects', total);
    animateNumber('weeklyProjects', weeklyActive);

    if (recentProject) {
        const el = document.getElementById('recentProjectName');
        if (el) {
            el.textContent = recentProject.chinese_name || recentProject.name;
            el.title = recentProject.chinese_name || recentProject.name;
        }
    }
}

// 数字动画
function animateNumber(id, target) {
    const el = document.getElementById(id);
    if (!el) return;

    const start = parseInt(el.textContent) || 0;
    const duration = 800;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * easeOut);
        el.textContent = current;
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// 启动项目
async function startProject(path) {
    try {
        showNotification('正在启动项目...', 'info');
        const response = await fetch('/api/projects/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path })
        });
        const data = await response.json();
        if (data.success) {
            showNotification('启动成功！', 'success');
            setTimeout(refreshProjects, 3000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('启动失败: ' + error.message, 'error');
    }
}

// 停止项目
async function stopProject(port) {
    if (!confirm('确定要停止这个项目吗？')) return;
    try {
        showNotification('正在停止项目...', 'info');
        const response = await fetch('/api/projects/stop', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ port })
        });
        const data = await response.json();
        if (data.success) {
            showNotification('已停止', 'success');
            setTimeout(refreshProjects, 1000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('停止失败: ' + error.message, 'error');
    }
}

// 打开项目
function openProject(port) {
    window.open(`http://localhost:${port}`, '_blank');
}

// 在终端打开项目
async function openInTerminal(path) {
    try {
        const response = await fetch('/api/projects/open-terminal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path })
        });
        const data = await response.json();
        if (data.success) {
            showNotification('已在终端打开', 'success');
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('打开失败: ' + error.message, 'error');
    }
}

// 刷新项目列表
function refreshProjects() {
    loadProjects();
}

// 显示通知 - 苹果风格亮色
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = 'fixed top-24 right-6 z-50 transform transition-all duration-500 opacity-0 translate-y-[-20px]';

    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        info: 'bg-indigo-500'
    };
    const icons = { success: '✓', error: '✕', info: 'ℹ' };

    notification.innerHTML = `
        <div class="${colors[type]} text-white px-6 py-4 rounded-2xl shadow-lg flex items-center space-x-3 min-w-[280px]">
            <span class="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-sm">${icons[type]}</span>
            <span class="font-medium">${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    requestAnimationFrame(() => {
        notification.classList.remove('opacity-0', 'translate-y-[-20px]');
    });

    setTimeout(() => {
        notification.classList.add('opacity-0', 'translate-y-[-20px]');
        setTimeout(() => notification.remove(), 500);
    }, 3000);
}

// API基础URL
const API_BASE = '/api';

// 显示/隐藏加载提示
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// 显示消息
function showMessage(message, type = 'success', containerId = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    
    const container = containerId ? document.getElementById(containerId) : document.body;
    container.insertBefore(messageDiv, container.firstChild);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// 列出Google Drive中的文件
async function listDriveFiles() {
    showLoading();
    try {
        const folderId = document.getElementById('folderId').value;
        const url = folderId 
            ? `${API_BASE}/drive/files?folder_id=${encodeURIComponent(folderId)}`
            : `${API_BASE}/drive/files`;
        
        const response = await fetch(url);
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            displayDriveFiles(result.data);
        } else {
            showMessage('获取文件列表失败: ' + result.error, 'error', 'driveFilesList');
        }
    } catch (error) {
        hideLoading();
        showMessage('错误: ' + error.message, 'error', 'driveFilesList');
    }
}

// 显示Google Drive文件列表
function displayDriveFiles(files) {
    const container = document.getElementById('driveFilesList');
    
    if (files.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>未找到数据库文件</p></div>';
        return;
    }
    
    container.innerHTML = files.map(file => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-meta">
                    ${file.size ? `大小: ${(file.size / 1024 / 1024).toFixed(2)} MB` : ''}
                </div>
            </div>
            <button class="btn btn-primary" onclick="downloadFile('${file.id}', '${file.name}')">
                下载
            </button>
        </div>
    `).join('');
}

// 下载单个文件
async function downloadFile(fileId, fileName) {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/drive/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ file_id: fileId })
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showMessage('下载成功: ' + result.data.name, 'success');
            loadDatabases(); // 刷新数据库列表
        } else {
            showMessage('下载失败: ' + result.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showMessage('错误: ' + error.message, 'error');
    }
}

// 下载所有数据库
async function downloadAllDatabases() {
    showLoading();
    try {
        const folderId = document.getElementById('folderId').value;
        const response = await fetch(`${API_BASE}/drive/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ folder_id: folderId || null })
        });
        
        const result = await response.json();
        hideLoading();
        
        if (result.success) {
            showMessage(result.message, 'success');
            loadDatabases(); // 刷新数据库列表
        } else {
            showMessage('下载失败: ' + result.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showMessage('错误: ' + error.message, 'error');
    }
}

// 加载本地数据库列表
async function loadDatabases() {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/databases`);
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            displayDatabases(result.data);
        } else {
            showMessage('获取数据库列表失败: ' + result.error, 'error', 'databasesList');
        }
    } catch (error) {
        hideLoading();
        showMessage('错误: ' + error.message, 'error', 'databasesList');
    }
}

// 显示数据库列表
function displayDatabases(databases) {
    const container = document.getElementById('databasesList');
    
    if (databases.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>暂无数据库文件，请先从Google Drive下载</p></div>';
        return;
    }
    
    container.innerHTML = databases.map(db => `
        <div class="database-item">
            <div class="database-info">
                <div class="database-name">${db.name}</div>
                <div class="database-meta">大小: ${db.size_mb} MB</div>
            </div>
            <button class="btn btn-primary" onclick="openDatabase('${db.name}')">
                浏览
            </button>
        </div>
    `).join('');
}

// 打开数据库浏览
async function openDatabase(dbName) {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/databases/${encodeURIComponent(dbName)}/tables`);
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            document.getElementById('currentDb').textContent = `数据库: ${dbName}`;
            document.getElementById('currentTable').textContent = '表: -';
            displayTables(dbName, result.data);
            document.getElementById('dataViewer').style.display = 'block';
            document.getElementById('tableData').innerHTML = '';
            
            // 滚动到查看器
            document.getElementById('dataViewer').scrollIntoView({ behavior: 'smooth' });
        } else {
            showMessage('获取表列表失败: ' + result.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showMessage('错误: ' + error.message, 'error');
    }
}

// 显示表列表
function displayTables(dbName, tables) {
    const container = document.getElementById('tablesList');
    
    if (tables.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>该数据库中没有表</p></div>';
        return;
    }
    
    container.innerHTML = tables.map(table => `
        <div class="table-item">
            <div class="file-info">
                <div class="file-name">${table}</div>
            </div>
            <div class="button-group">
                <button class="btn btn-secondary" onclick="showTableInfo('${dbName}', '${table}')">
                    结构
                </button>
                <button class="btn btn-primary" onclick="showTableData('${dbName}', '${table}')">
                    数据
                </button>
            </div>
        </div>
    `).join('');
}

// 显示表结构
async function showTableInfo(dbName, tableName) {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/databases/${encodeURIComponent(dbName)}/tables/${encodeURIComponent(tableName)}/info`);
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            const columns = result.data.map(col => `
                <tr>
                    <td>${col.name}</td>
                    <td>${col.type}</td>
                    <td>${col.notnull ? '是' : '否'}</td>
                    <td>${col.pk ? '是' : '否'}</td>
                    <td>${col.default_value || '-'}</td>
                </tr>
            `).join('');
            
            document.getElementById('tableData').innerHTML = `
                <h3>表结构: ${tableName}</h3>
                <table>
                    <thead>
                        <tr>
                            <th>列名</th>
                            <th>类型</th>
                            <th>非空</th>
                            <th>主键</th>
                            <th>默认值</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${columns}
                    </tbody>
                </table>
            `;
            
            document.getElementById('currentTable').textContent = `表: ${tableName}`;
        } else {
            showMessage('获取表结构失败: ' + result.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showMessage('错误: ' + error.message, 'error');
    }
}

// 显示表数据
async function showTableData(dbName, tableName, offset = 0) {
    showLoading();
    try {
        const response = await fetch(`${API_BASE}/databases/${encodeURIComponent(dbName)}/tables/${encodeURIComponent(tableName)}/data?limit=100&offset=${offset}`);
        const result = await response.json();
        
        hideLoading();
        
        if (result.success && result.data.length > 0) {
            const columns = Object.keys(result.data[0]);
            const rows = result.data.map(row => `
                <tr>
                    ${columns.map(col => `<td>${row[col] !== null ? row[col] : '-'}</td>`).join('')}
                </tr>
            `).join('');
            
            const pagination = offset > 0 || result.offset + result.limit < result.total ? `
                <div class="button-group" style="margin-top: 15px;">
                    ${offset > 0 ? `<button class="btn btn-secondary" onclick="showTableData('${dbName}', '${tableName}', ${Math.max(0, offset - 100)})">上一页</button>` : ''}
                    ${result.offset + result.limit < result.total ? `<button class="btn btn-secondary" onclick="showTableData('${dbName}', '${tableName}', ${offset + 100})">下一页</button>` : ''}
                </div>
                <p style="margin-top: 10px; color: #666;">显示 ${offset + 1}-${Math.min(offset + result.limit, result.total)} / 共 ${result.total} 条记录</p>
            ` : '';
            
            document.getElementById('tableData').innerHTML = `
                <h3>表数据: ${tableName}</h3>
                <table>
                    <thead>
                        <tr>
                            ${columns.map(col => `<th>${col}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
                ${pagination}
            `;
            
            document.getElementById('currentTable').textContent = `表: ${tableName}`;
        } else if (result.success) {
            document.getElementById('tableData').innerHTML = '<div class="empty-state"><p>表中没有数据</p></div>';
        } else {
            showMessage('获取表数据失败: ' + result.error, 'error');
        }
    } catch (error) {
        hideLoading();
        showMessage('错误: ' + error.message, 'error');
    }
}

// 关闭查看器
function closeViewer() {
    document.getElementById('dataViewer').style.display = 'none';
}

// 页面加载时自动加载数据库列表
window.addEventListener('DOMContentLoaded', () => {
    loadDatabases();
});


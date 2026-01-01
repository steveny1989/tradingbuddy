# 🚀 快速测试指南

## 测试后端（无需前端依赖）

### 1. 运行单元测试
```bash
python3 -m pytest src/web/tests/ -v
```
**预期结果：** 9个测试全部通过 ✅

### 2. 启动后端服务器
```bash
PORT=5001 python3 src/web/app.py
```
**预期结果：** 服务器在 http://localhost:5001 启动

### 3. 测试API端点

**测试根路径：**
```bash
curl http://localhost:5001/
```
**预期响应：**
```json
{
    "message": "TradingBuddy API Server",
    "version": "1.0.0"
}
```

**测试错误处理：**
```bash
curl http://localhost:5001/nonexistent
```
**预期响应：**
```json
{
    "error": "资源未找到",
    "error_code": "NOT_FOUND",
    "success": false
}
```

---

## 测试前端（需要安装依赖）

### 1. 安装依赖（首次运行）
```bash
cd frontend
npm install
```
⏱️ **注意：** 这需要5-10分钟

### 2. 启动开发服务器
```bash
npm run dev
```
**预期结果：** 服务器在 http://localhost:3000 启动

### 3. 运行前端测试
```bash
npm test
```

### 4. 代码检查
```bash
npm run lint
```

---

## 完整系统测试

### 方式1: 使用启动脚本（推荐）
```bash
./start_ui.sh
```

### 方式2: 手动启动

**终端1 - 启动后端：**
```bash
PORT=5001 python3 src/web/app.py
```

**终端2 - 启动前端：**
```bash
cd frontend
npm run dev
```

### 访问系统
- 前端界面: http://localhost:3000
- 后端API: http://localhost:5001

---

## 故障排除

### 问题1: 端口5000被占用
**解决方案：** 使用5001端口
```bash
PORT=5001 python3 src/web/app.py
```

### 问题2: npm install 失败
**解决方案：**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 问题3: Python依赖缺失
**解决方案：**
```bash
pip install -r requirements.txt
```

---

## 测试检查清单

### 后端 ✅
- [ ] 单元测试通过
- [ ] 服务器成功启动
- [ ] API端点正常响应
- [ ] 错误处理正常工作
- [ ] 日志正常输出

### 前端 ✅
- [ ] 依赖安装成功
- [ ] 开发服务器启动
- [ ] 页面正常加载
- [ ] 代码检查通过
- [ ] 测试运行正常

### 集成 ✅
- [ ] 前后端通信正常
- [ ] API代理配置正确
- [ ] CORS配置正常

---

## 快速验证命令

**一键测试后端：**
```bash
python3 -m pytest src/web/tests/ -v && \
PORT=5001 python3 src/web/app.py &
sleep 3 && \
curl http://localhost:5001/ && \
pkill -f "python3 src/web/app.py"
```

**查看测试报告：**
```bash
cat TEST_RESULTS.md
```

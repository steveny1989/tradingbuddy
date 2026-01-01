# TradingBuddy UI System 使用指南

## 概述

TradingBuddy UI System 是一个基于Web的量化交易系统用户界面，提供直观的数据可视化、策略管理、回测分析和模拟盘监控功能。

## 技术架构

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI库**: Ant Design 5
- **图表**: Apache ECharts
- **路由**: React Router 6
- **状态管理**: React Context + Hooks
- **HTTP客户端**: Axios

### 后端
- **框架**: Flask 3.0
- **API风格**: RESTful
- **数据库**: SQLite (复用现有的 a_share.db)
- **CORS**: Flask-CORS

## 快速开始

### 方式1: 使用启动脚本（推荐）

```bash
./start_ui.sh
```

### 方式2: 手动启动

**启动后端:**
```bash
cd src/web
python app.py
```

**启动前端:**
```bash
cd frontend
npm install  # 首次运行
npm run dev
```

## 访问地址

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:5000

## 项目结构

```
tradingbuddy/
├── frontend/              # 前端项目
│   ├── src/
│   │   ├── components/   # 组件
│   │   ├── pages/        # 页面
│   │   ├── services/     # API服务
│   │   ├── types/        # 类型定义
│   │   └── utils/        # 工具函数
│   ├── package.json
│   └── vite.config.ts
│
├── src/web/              # 后端API
│   ├── routes/          # API路由
│   ├── utils/           # 工具函数
│   └── app.py           # 应用入口
│
└── docs/
    └── UI_SYSTEM_GUIDE.md  # 本文档
```

## 开发指南

### 前端开发

```bash
cd frontend

# 开发
npm run dev

# 测试
npm test

# 代码检查
npm run lint

# 格式化
npm run format

# 构建
npm run build
```

### 后端开发

```bash
cd src/web

# 运行
python app.py

# 测试
pytest

# 代码格式化
black .
```

## 功能模块

### 1. 仪表板
- 系统状态概览
- 数据库状态
- 模拟盘概览
- 最近回测结果

### 2. 股票浏览
- 股票列表查询
- 个股详情
- K线图展示
- 技术指标分析

### 3. 策略管理
- 策略列表
- 参数配置
- 回测执行

### 4. 回测结果
- 回测历史
- 绩效分析
- 交易记录
- 资金曲线

### 5. 模拟盘监控
- 账户状态
- 持仓管理
- 交易记录
- 实时更新

### 6. 数据管理
- 数据同步
- 状态监控
- 进度跟踪

## API文档

详细的API文档请参考设计文档：`.kiro/specs/trading-ui-system/design.md`

## 故障排除

### 前端无法启动
- 检查Node.js版本 (需要 >= 16)
- 删除 `node_modules` 和 `package-lock.json`，重新安装

### 后端无法启动
- 检查Python版本 (需要 >= 3.8)
- 检查依赖是否安装: `pip install -r requirements.txt`

### API请求失败
- 检查后端是否正常运行
- 检查CORS配置
- 查看浏览器控制台和后端日志

## 下一步

当前已完成基础架构搭建，后续任务将逐步实现各个功能模块。

参考任务列表：`.kiro/specs/trading-ui-system/tasks.md`

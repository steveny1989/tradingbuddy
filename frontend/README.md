# TradingBuddy UI - Frontend

基于React + TypeScript + Vite的量化交易系统前端界面。

## 技术栈

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **UI库**: Ant Design 5
- **图表**: Apache ECharts
- **路由**: React Router 6
- **HTTP客户端**: Axios
- **测试**: Vitest + React Testing Library + fast-check

## 开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 运行测试
npm test

# 代码检查
npm run lint

# 代码格式化
npm run format

# 构建生产版本
npm run build
```

## 项目结构

```
src/
├── components/       # 可复用组件
│   ├── layout/      # 布局组件
│   ├── common/      # 通用组件
│   └── features/    # 功能组件
├── pages/           # 页面组件
├── services/        # API服务
├── types/           # TypeScript类型定义
├── utils/           # 工具函数
├── hooks/           # 自定义Hooks
├── test/            # 测试配置
└── main.tsx         # 应用入口
```

## API代理

开发环境下，所有 `/api` 请求会被代理到 `http://localhost:5000`。

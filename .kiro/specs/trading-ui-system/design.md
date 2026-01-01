# Design Document - Trading UI System

## Overview

TradingBuddy UI System是一个基于Web的量化交易系统用户界面，采用前后端分离架构。前端使用现代JavaScript框架构建响应式单页应用（SPA），后端基于Flask提供RESTful API，连接现有的业务层和数据层。系统提供直观的数据可视化、策略管理、回测分析和模拟盘监控功能。

### Design Goals

1. **用户友好**：提供直观、流畅的用户体验，降低量化交易的技术门槛
2. **高性能**：快速加载和渲染，支持大量数据的高效展示
3. **可扩展**：模块化设计，便于添加新功能和策略
4. **响应式**：适配桌面、平板和移动设备
5. **可维护**：清晰的代码结构，完善的文档

## Architecture

### System Architecture


```
┌─────────────────────────────────────────────────────────────┐
│                      Browser (Client)                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │  React UI  │  │  Chart.js  │  │  State Management      │ │
│  │  Components│  │  (Echarts) │  │  (Redux/Context)       │ │
│  └────────────┘  └────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask Backend (Server)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              API Layer (routes.py)                     │ │
│  │  /api/stocks  /api/strategies  /api/backtest          │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Business Layer (src/business/)               │ │
│  │  Strategies  │  Backtest Engine  │  Trading           │ │
│  └────────────────────────────────────────────────────────┘ │
│                            │                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │             Data Layer (src/data/)                     │ │
│  │  Database  │  Fetcher  │  Cache                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  SQLite DB   │
                    │  a_share.db  │
                    └──────────────┘
```

### Technology Stack

**Frontend:**
- Framework: React 18+ (组件化、虚拟DOM、生态丰富)
- UI Library: Ant Design (企业级UI组件库)
- Charts: Apache ECharts (专业金融图表库)
- State Management: React Context + Hooks (轻量级状态管理)
- HTTP Client: Axios (Promise-based HTTP客户端)
- Build Tool: Vite (快速的开发服务器和构建工具)

**Backend:**
- Framework: Flask 3.0+ (轻量级、灵活)
- API: Flask-RESTful (RESTful API扩展)
- CORS: Flask-CORS (跨域支持)
- Validation: Marshmallow (数据验证和序列化)
- Cache: Flask-Caching (响应缓存)

**Development:**
- Language: Python 3.8+, JavaScript ES6+
- Package Manager: pip (Python), npm (JavaScript)
- Code Style: Black (Python), ESLint + Prettier (JavaScript)


## Components and Interfaces

### Frontend Components

#### 1. Layout Components

**AppLayout**
- 职责：应用主布局，包含顶部导航、侧边栏、内容区域
- Props: `children` (React节点)
- State: `sidebarCollapsed` (布尔值)

**Sidebar**
- 职责：侧边导航菜单
- Props: `collapsed` (布尔值), `onCollapse` (回调函数)
- 菜单项：Dashboard, Stocks, Strategies, Backtest, Paper Trading, Data

**Header**
- 职责：顶部导航栏，显示标题、用户信息、系统状态
- Props: `title` (字符串)
- State: `systemStatus` (对象)

#### 2. Page Components

**DashboardPage**
- 职责：系统仪表板页面
- 子组件：`SystemStatusCard`, `PaperTradingCard`, `RecentBacktestCard`
- API调用：`GET /api/dashboard/summary`

**StockListPage**
- 职责：股票列表页面
- 子组件：`StockTable`, `SearchBar`, `FilterPanel`
- API调用：`GET /api/stocks`

**StockDetailPage**
- 职责：股票详情页面
- 子组件：`StockInfo`, `KLineChart`, `TechnicalIndicators`
- API调用：`GET /api/stocks/{code}`, `GET /api/stocks/{code}/daily`

**StrategyListPage**
- 职责：策略列表页面
- 子组件：`StrategyCard`, `StrategyConfigModal`
- API调用：`GET /api/strategies`

**BacktestResultPage**
- 职责：回测结果页面
- 子组件：`PerformanceMetrics`, `EquityCurve`, `TradeTable`
- API调用：`GET /api/backtest/{id}`

**PaperTradingPage**
- 职责：模拟盘监控页面
- 子组件：`AccountSummary`, `PositionTable`, `TradeHistory`
- API调用：`GET /api/paper-trading/status`

**DataManagementPage**
- 职责：数据管理页面
- 子组件：`SyncStatusTable`, `SyncControlPanel`
- API调用：`GET /api/data/status`, `POST /api/data/sync`

**FinancialDataPage**
- 职责：财务数据查看页面（股票详情页的子页面）
- 子组件：`FinancialStatementsTable`, `FinancialIndicatorsChart`, `PeriodSelector`
- API调用：`GET /api/stocks/{code}/financials`, `GET /api/stocks/{code}/indicators/financial`

#### 3. Feature Components

**KLineChart**
- 职责：K线图表组件
- Props: `data` (数组), `indicators` (数组), `timeRange` (字符串)
- 技术：ECharts candlestick + line series
- 功能：缩放、平移、十字光标、数据提示

**EquityCurve**
- 职责：资金曲线图表
- Props: `data` (数组), `showDrawdown` (布尔值)
- 技术：ECharts line series
- 功能：双Y轴（资金、回撤）

**StockTable**
- 职责：股票列表表格
- Props: `data` (数组), `loading` (布尔值), `onRowClick` (回调)
- 功能：排序、筛选、分页、虚拟滚动

**StrategyConfigModal**
- 职责：策略配置对话框
- Props: `strategy` (对象), `visible` (布尔值), `onSubmit` (回调)
- 功能：表单验证、参数配置

#### 4. Common Components

**LoadingSpinner**
- 职责：加载指示器
- Props: `size` (字符串), `tip` (字符串)

**ErrorBoundary**
- 职责：错误边界组件
- Props: `children` (React节点)
- 功能：捕获子组件错误，显示友好错误页面

**ConfirmDialog**
- 职责：确认对话框
- Props: `title`, `content`, `onConfirm`, `onCancel`

**Notification**
- 职责：通知提示
- 方法：`success()`, `error()`, `warning()`, `info()`

**FinancialStatementsTable**
- 职责：财务报表表格组件
- Props: `data` (数组), `reportType` (字符串), `periodType` (字符串)
- 功能：展示资产负债表、利润表、现金流量表

**FinancialIndicatorsChart**
- 职责：财务指标图表组件
- Props: `data` (数组), `indicators` (数组)
- 技术：ECharts line series
- 功能：展示财务指标的时间序列趋势

**PeriodSelector**
- 职责：报告期选择器
- Props: `periodType` (字符串), `onChange` (回调)
- 功能：切换季报/年报


### Backend API Endpoints

#### Stock APIs

```python
GET /api/stocks
# 获取股票列表
# Query params: market (sh/sz), min_cap, max_cap, page, page_size
# Response: { stocks: [...], total: int, page: int, page_size: int }

GET /api/stocks/{code}
# 获取股票详情
# Response: { code, name, market, industry, market_cap, ... }

GET /api/stocks/{code}/daily
# 获取日线数据
# Query params: start_date, end_date
# Response: { data: [{ date, open, high, low, close, volume, ... }] }

GET /api/stocks/{code}/indicators
# 获取技术指标
# Query params: indicators (ma5,ma10,ma20), start_date, end_date
# Response: { data: [{ date, ma5, ma10, ma20, ... }] }
```

#### Strategy APIs

```python
GET /api/strategies
# 获取策略列表
# Response: { strategies: [{ id, name, type, description, params }] }

GET /api/strategies/{id}
# 获取策略详情
# Response: { id, name, type, description, params, default_config }

POST /api/strategies/{id}/backtest
# 执行回测
# Body: { start_date, end_date, initial_capital, config }
# Response: { task_id, status }

GET /api/strategies/{id}/config
# 获取策略配置
# Response: { config: {...} }

PUT /api/strategies/{id}/config
# 更新策略配置
# Body: { config: {...} }
# Response: { success: bool, message }
```

#### Backtest APIs

```python
GET /api/backtest
# 获取回测历史列表
# Query params: strategy_id, page, page_size
# Response: { backtests: [...], total, page, page_size }

GET /api/backtest/{id}
# 获取回测结果详情
# Response: { 
#   id, strategy_name, start_date, end_date,
#   metrics: { total_return, annual_return, max_drawdown, sharpe_ratio, win_rate },
#   equity_curve: [...],
#   trades: [...]
# }

GET /api/backtest/{id}/trades
# 获取交易记录
# Query params: page, page_size
# Response: { trades: [...], total, page, page_size }

DELETE /api/backtest/{id}
# 删除回测记录
# Response: { success: bool, message }

GET /api/backtest/{id}/export
# 导出交易记录为CSV
# Response: CSV file download
```

#### Paper Trading APIs

```python
GET /api/paper-trading/status
# 获取模拟盘状态
# Response: {
#   running: bool,
#   account: { total_value, cash, position_value, daily_pnl },
#   positions: [...],
#   today_trades: [...]
# }

POST /api/paper-trading/start
# 启动模拟盘
# Body: { strategy_id, initial_capital }
# Response: { success: bool, message }

POST /api/paper-trading/stop
# 停止模拟盘
# Response: { success: bool, message }

POST /api/paper-trading/reset
# 重置模拟盘账户
# Response: { success: bool, message }

GET /api/paper-trading/performance
# 获取模拟盘绩效
# Response: {
#   equity_curve: [...],
#   metrics: { total_return, max_drawdown, ... }
# }
```

#### Data Management APIs

```python
GET /api/data/status
# 获取数据同步状态
# Response: {
#   total_stocks: int,
#   synced_stocks: int,
#   failed_stocks: int,
#   last_update: datetime,
#   sync_in_progress: bool
# }

GET /api/data/stocks-status
# 获取每只股票的同步状态
# Query params: page, page_size, status (all/synced/failed)
# Response: { stocks: [...], total, page, page_size }

POST /api/data/sync
# 触发数据同步
# Body: { mode: 'full' | 'incremental', codes: [...] }
# Response: { task_id, status }

GET /api/data/sync/{task_id}
# 获取同步任务进度
# Response: {
#   task_id, status, progress: { current, total },
#   current_stock, errors: [...]
# }

POST /api/data/sync/{task_id}/cancel
# 取消同步任务
# Response: { success: bool, message }
```

#### Financial Data APIs

```python
GET /api/stocks/{code}/financials
# 获取财务报表数据
# Query params: report_type (balance_sheet/income_statement/cash_flow), 
#               period_type (quarterly/annual), limit (default: 8)
# Response: {
#   data: [{
#     report_date: str,
#     report_type: str,
#     period_type: str,
#     items: {
#       total_assets: float,
#       total_liabilities: float,
#       total_equity: float,
#       revenue: float,
#       net_profit: float,
#       operating_cash_flow: float,
#       ...
#     }
#   }]
# }

GET /api/stocks/{code}/indicators/financial
# 获取财务分析指标
# Query params: period_type (quarterly/annual), limit (default: 8)
# Response: {
#   data: [{
#     report_date: str,
#     period_type: str,
#     profitability: {
#       roe: float,           # 净资产收益率
#       roa: float,           # 总资产收益率
#       gross_margin: float,  # 毛利率
#       net_margin: float,    # 净利率
#       operating_margin: float  # 营业利润率
#     },
#     solvency: {
#       debt_to_asset: float,    # 资产负债率
#       current_ratio: float,    # 流动比率
#       quick_ratio: float       # 速动比率
#     },
#     valuation: {
#       pe: float,    # 市盈率
#       pb: float,    # 市净率
#       ps: float     # 市销率
#     },
#     growth: {
#       revenue_growth: float,      # 营收增长率
#       profit_growth: float,       # 净利润增长率
#       roe_growth: float          # ROE增长率
#     }
#   }]
# }

POST /api/data/sync/financials
# 触发财务数据同步
# Body: { codes: [...] }  # 可选，不传则同步所有股票
# Response: { task_id, status }

GET /api/data/financials-status
# 获取财务数据同步状态
# Query params: page, page_size
# Response: {
#   total_stocks: int,
#   synced_stocks: int,
#   failed_stocks: int,
#   no_data_stocks: int,
#   last_update: datetime,
#   stocks: [{
#     code: str,
#     name: str,
#     status: 'synced' | 'failed' | 'no_data',
#     last_sync: datetime,
#     latest_report_date: str
#   }]
# }
```

#### Dashboard APIs

```python
GET /api/dashboard/summary
# 获取仪表板摘要
# Response: {
#   database: { total_stocks, last_update, data_completeness },
#   paper_trading: { running, total_value, daily_pnl },
#   recent_backtests: [...]
# }
```


## Data Models

### Frontend Data Models

```typescript
// Stock Model
interface Stock {
  code: string;           // 股票代码 (e.g., "600000")
  name: string;           // 股票名称
  market: 'sh' | 'sz';    // 市场
  full_code: string;      // 完整代码 (e.g., "sh.600000")
  industry?: string;      // 行业
  market_cap?: number;    // 市值
  list_date?: string;     // 上市日期
}

// Daily Data Model
interface DailyData {
  date: string;           // 日期 YYYY-MM-DD
  open: number;           // 开盘价
  high: number;           // 最高价
  low: number;            // 最低价
  close: number;          // 收盘价
  volume: number;         // 成交量
  amount: number;         // 成交额
  turnover?: number;      // 换手率
  pct_change?: number;    // 涨跌幅
}

// Strategy Model
interface Strategy {
  id: string;
  name: string;
  type: 'technical' | 'fundamental' | 'quant';
  description: string;
  params: StrategyParam[];
  enabled: boolean;
}

interface StrategyParam {
  name: string;
  label: string;
  type: 'number' | 'string' | 'boolean' | 'select';
  default: any;
  min?: number;
  max?: number;
  options?: { label: string; value: any }[];
  description?: string;
}

// Backtest Result Model
interface BacktestResult {
  id: string;
  strategy_id: string;
  strategy_name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_value: number;
  metrics: PerformanceMetrics;
  equity_curve: EquityPoint[];
  trades: Trade[];
  created_at: string;
}

interface PerformanceMetrics {
  total_return: number;       // 总收益率
  annual_return: number;      // 年化收益率
  max_drawdown: number;       // 最大回撤
  sharpe_ratio: number;       // 夏普比率
  win_rate: number;           // 胜率
  total_trades: number;       // 总交易次数
  avg_profit: number;         // 平均盈利
  avg_loss: number;           // 平均亏损
}

interface EquityPoint {
  date: string;
  value: number;
  drawdown: number;
}

interface Trade {
  date: string;
  code: string;
  name: string;
  action: 'buy' | 'sell';
  price: number;
  quantity: number;
  amount: number;
  pnl?: number;
  pnl_pct?: number;
}

// Paper Trading Model
interface PaperTradingStatus {
  running: boolean;
  account: Account;
  positions: Position[];
  today_trades: Trade[];
}

interface Account {
  total_value: number;      // 总资产
  cash: number;             // 可用资金
  position_value: number;   // 持仓市值
  daily_pnl: number;        // 当日盈亏
  daily_pnl_pct: number;    // 当日盈亏率
}

interface Position {
  code: string;
  name: string;
  quantity: number;         // 持仓数量
  cost_price: number;       // 成本价
  current_price: number;    // 现价
  market_value: number;     // 市值
  pnl: number;              // 盈亏
  pnl_pct: number;          // 盈亏率
}

// Data Sync Model
interface DataSyncStatus {
  total_stocks: number;
  synced_stocks: number;
  failed_stocks: number;
  last_update: string;
  sync_in_progress: boolean;
}

interface StockSyncStatus {
  code: string;
  name: string;
  status: 'synced' | 'syncing' | 'failed';
  last_sync: string;
  error_message?: string;
}

interface SyncTask {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: {
    current: number;
    total: number;
  };
  current_stock?: string;
  errors: string[];
  started_at: string;
  completed_at?: string;
}

// Financial Data Models
interface FinancialStatement {
  report_date: string;        // 报告期 YYYY-MM-DD
  report_type: 'balance_sheet' | 'income_statement' | 'cash_flow';
  period_type: 'quarterly' | 'annual';
  items: FinancialItems;
}

interface FinancialItems {
  // 资产负债表项目
  total_assets?: number;           // 总资产
  total_liabilities?: number;      // 总负债
  total_equity?: number;           // 所有者权益
  current_assets?: number;         // 流动资产
  current_liabilities?: number;    // 流动负债
  cash?: number;                   // 货币资金
  accounts_receivable?: number;    // 应收账款
  inventory?: number;              // 存货
  fixed_assets?: number;           // 固定资产
  intangible_assets?: number;      // 无形资产
  
  // 利润表项目
  revenue?: number;                // 营业收入
  operating_cost?: number;         // 营业成本
  gross_profit?: number;           // 毛利润
  operating_profit?: number;       // 营业利润
  net_profit?: number;             // 净利润
  eps?: number;                    // 每股收益
  
  // 现金流量表项目
  operating_cash_flow?: number;    // 经营活动现金流
  investing_cash_flow?: number;    // 投资活动现金流
  financing_cash_flow?: number;    // 筹资活动现金流
  net_cash_flow?: number;          // 现金流量净额
}

interface FinancialIndicators {
  report_date: string;
  period_type: 'quarterly' | 'annual';
  
  // 盈利能力指标
  profitability: {
    roe: number;              // 净资产收益率 (%)
    roa: number;              // 总资产收益率 (%)
    gross_margin: number;     // 毛利率 (%)
    net_margin: number;       // 净利率 (%)
    operating_margin: number; // 营业利润率 (%)
  };
  
  // 偿债能力指标
  solvency: {
    debt_to_asset: number;    // 资产负债率 (%)
    current_ratio: number;    // 流动比率
    quick_ratio: number;      // 速动比率
  };
  
  // 估值指标
  valuation: {
    pe: number;               // 市盈率
    pb: number;               // 市净率
    ps: number;               // 市销率
  };
  
  // 成长性指标
  growth: {
    revenue_growth: number;   // 营收增长率 (%)
    profit_growth: number;    // 净利润增长率 (%)
    roe_growth: number;       // ROE增长率 (%)
  };
}

interface FinancialSyncStatus {
  total_stocks: number;
  synced_stocks: number;
  failed_stocks: number;
  no_data_stocks: number;
  last_update: string;
}

interface StockFinancialStatus {
  code: string;
  name: string;
  status: 'synced' | 'failed' | 'no_data';
  last_sync: string;
  latest_report_date?: string;
  error_message?: string;
}
```

### Backend Data Models

```python
# Database Schema (SQLite)

# stock_basic table
CREATE TABLE stock_basic (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    market TEXT NOT NULL,
    full_code TEXT NOT NULL,
    industry TEXT,
    list_date TEXT
);

# market_cap_data table
CREATE TABLE market_cap_data (
    code TEXT,
    date TEXT,
    market_cap REAL,
    PRIMARY KEY (code, date)
);

# industry_data table
CREATE TABLE industry_data (
    code TEXT PRIMARY KEY,
    industry TEXT
);

# daily_{market}_{code} tables (动态创建)
CREATE TABLE daily_sh_600000 (
    date TEXT PRIMARY KEY,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    amount REAL,
    turnover REAL,
    pct_change REAL
);

# sync_status table
CREATE TABLE sync_status (
    code TEXT PRIMARY KEY,
    last_sync TEXT,
    status TEXT,
    error_message TEXT
);

# backtest_results table
CREATE TABLE backtest_results (
    id TEXT PRIMARY KEY,
    strategy_id TEXT,
    strategy_name TEXT,
    start_date TEXT,
    end_date TEXT,
    initial_capital REAL,
    final_value REAL,
    metrics TEXT,  -- JSON
    equity_curve TEXT,  -- JSON
    trades TEXT,  -- JSON
    created_at TEXT
);

# paper_trading_account table
CREATE TABLE paper_trading_account (
    id INTEGER PRIMARY KEY,
    total_value REAL,
    cash REAL,
    position_value REAL,
    daily_pnl REAL,
    updated_at TEXT
);

# paper_trading_positions table
CREATE TABLE paper_trading_positions (
    code TEXT PRIMARY KEY,
    name TEXT,
    quantity INTEGER,
    cost_price REAL,
    current_price REAL
);

# paper_trading_trades table
CREATE TABLE paper_trading_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    code TEXT,
    name TEXT,
    action TEXT,
    price REAL,
    quantity INTEGER,
    amount REAL,
    pnl REAL
);

# financial_balance_sheet table
CREATE TABLE financial_balance_sheet (
    code TEXT,
    report_date TEXT,
    period_type TEXT,  -- 'Q' for quarterly, 'A' for annual
    total_assets REAL,
    total_liabilities REAL,
    total_equity REAL,
    current_assets REAL,
    current_liabilities REAL,
    cash REAL,
    accounts_receivable REAL,
    inventory REAL,
    fixed_assets REAL,
    intangible_assets REAL,
    PRIMARY KEY (code, report_date, period_type)
);

# financial_income_statement table
CREATE TABLE financial_income_statement (
    code TEXT,
    report_date TEXT,
    period_type TEXT,
    revenue REAL,
    operating_cost REAL,
    gross_profit REAL,
    operating_profit REAL,
    net_profit REAL,
    eps REAL,
    PRIMARY KEY (code, report_date, period_type)
);

# financial_cash_flow table
CREATE TABLE financial_cash_flow (
    code TEXT,
    report_date TEXT,
    period_type TEXT,
    operating_cash_flow REAL,
    investing_cash_flow REAL,
    financing_cash_flow REAL,
    net_cash_flow REAL,
    PRIMARY KEY (code, report_date, period_type)
);

# financial_indicators table
CREATE TABLE financial_indicators (
    code TEXT,
    report_date TEXT,
    period_type TEXT,
    roe REAL,
    roa REAL,
    gross_margin REAL,
    net_margin REAL,
    operating_margin REAL,
    debt_to_asset REAL,
    current_ratio REAL,
    quick_ratio REAL,
    pe REAL,
    pb REAL,
    ps REAL,
    revenue_growth REAL,
    profit_growth REAL,
    roe_growth REAL,
    PRIMARY KEY (code, report_date, period_type)
);

# financial_sync_status table
CREATE TABLE financial_sync_status (
    code TEXT PRIMARY KEY,
    last_sync TEXT,
    status TEXT,  -- 'synced', 'failed', 'no_data'
    latest_report_date TEXT,
    error_message TEXT
);
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Frontend Properties

**Property 1: Dashboard displays all required database status fields**
*For any* database status data, when rendered in the Dashboard component, the output should contain stock count, last update time, and data completeness information.
**Validates: Requirements 1.2**

**Property 2: Dashboard displays all required paper trading fields**
*For any* paper trading status data, when rendered in the Dashboard component, the output should contain account balance, position count, and daily return rate.
**Validates: Requirements 1.3**

**Property 3: Dashboard displays all required backtest summary fields**
*For any* backtest result data, when rendered in the Dashboard component, the output should contain strategy name, return rate, and maximum drawdown.
**Validates: Requirements 1.4**

**Property 4: Stock list displays all required fields**
*For any* stock data, when rendered in the Stock Explorer table, each row should contain code, name, market cap, and industry fields.
**Validates: Requirements 2.1**

**Property 5: Stock search filters correctly**
*For any* stock list and search query, the filtered results should only contain stocks whose code or name matches the query.
**Validates: Requirements 2.2**

**Property 6: K-line chart includes all technical indicators**
*For any* stock daily data, when rendered in the Chart Component, the chart configuration should include MA5, MA10, MA20, and volume indicators.
**Validates: Requirements 2.5**

**Property 7: Time range change updates chart data**
*For any* time range selection, when the user changes the time range, the chart data should be filtered to match the selected date range.
**Validates: Requirements 2.7**

**Property 8: Strategy list displays all required fields**
*For any* strategy data, when rendered in the Strategy Manager, each strategy should display name, type, and description fields.
**Validates: Requirements 3.1**

**Property 9: Invalid strategy parameters show validation errors**
*For any* invalid strategy parameter input, the Strategy Manager should display specific validation error messages.
**Validates: Requirements 3.6**

**Property 10: Backtest list displays all required fields**
*For any* backtest result data, when rendered in the Backtest Viewer list, each item should display strategy name, time range, return rate, and drawdown.
**Validates: Requirements 4.1**

**Property 11: Backtest metrics display all required indicators**
*For any* backtest result, the performance metrics section should display total return, annual return, max drawdown, Sharpe ratio, and win rate.
**Validates: Requirements 4.3**

**Property 12: Trade table displays all required fields**
*For any* trade record, when rendered in the trade table, each row should display date, stock code, action, price, quantity, and P&L.
**Validates: Requirements 4.6**

**Property 13: Paper trading account displays all required fields**
*For any* account status data, the Paper Trading Monitor should display total value, cash, position value, and daily P&L.
**Validates: Requirements 5.1**

**Property 14: Position list displays all required fields**
*For any* position data, when rendered in the position table, each row should display code, name, quantity, cost price, current price, and P&L.
**Validates: Requirements 5.2**

**Property 15: Today's trades display all required fields**
*For any* trade record from today, the trade list should display time, stock, action, price, and quantity.
**Validates: Requirements 5.3**

**Property 16: Paper trading auto-refresh triggers correctly**
*For any* paper trading monitor in running state, after 30 seconds elapse, a data refresh should be triggered.
**Validates: Requirements 5.5**

**Property 17: Sync status table displays all required fields**
*For any* stock sync status data, the table should display code, name, status (synced/syncing/failed), and last sync time.
**Validates: Requirements 6.2**

**Property 18: K-line chart renders with correct data format**
*For any* valid daily data array, the K-line chart should render with candlestick series containing open, high, low, and close values.
**Validates: Requirements 7.1**

**Property 19: Chart supports all moving average indicators**
*For any* chart configuration, when MA indicators are enabled, the chart should include MA5, MA10, MA20, and MA60 line series.
**Validates: Requirements 7.3**

**Property 20: Chart uses configurable color scheme**
*For any* chart component, the color configuration should support both red-up-green-down and green-up-red-down schemes.
**Validates: Requirements 7.7**

**Property 21: Responsive layout switches at correct breakpoint**
*For any* screen width less than 768px, the UI layout should switch to mobile mode.
**Validates: Requirements 8.4**

**Property 22: Touch-friendly button sizes**
*For all* interactive buttons in the UI, the minimum size should be at least 44px × 44px.
**Validates: Requirements 8.5**

**Property 23: Mobile layout hides secondary features**
*For any* mobile layout (width < 768px), secondary features should be hidden while core features remain visible.
**Validates: Requirements 8.6**

**Property 24: Long lists use pagination**
*For any* data list with more than 100 items, the UI should implement pagination or virtual scrolling with page size between 50-100 items.
**Validates: Requirements 9.3**

**Property 25: Stock data is cached to avoid duplicate requests**
*For any* stock data request, if the same stock data was previously loaded, no new API request should be made.
**Validates: Requirements 9.4**

**Property 26: Large chart datasets use data sampling**
*For any* chart data with more than 1000 data points, the Chart Component should apply data sampling or aggregation.
**Validates: Requirements 9.5**

**Property 27: Lazy loading for large components**
*For any* large component (chart library, heavy modules), the component should be loaded on-demand rather than at initial page load.
**Validates: Requirements 9.6**

**Property 28: API errors display friendly messages**
*For any* failed API request, the UI should display a user-friendly error message rather than technical error details.
**Validates: Requirements 10.1**

**Property 29: Success notifications auto-dismiss**
*For any* successful operation, the success notification should automatically disappear after 3 seconds.
**Validates: Requirements 10.2**

**Property 30: Dangerous operations show confirmation**
*For any* dangerous operation (like account reset), a confirmation dialog should be displayed before execution.
**Validates: Requirements 10.3**

**Property 31: Form validation shows specific errors**
*For any* form validation failure, specific error messages should be displayed for each invalid field.
**Validates: Requirements 10.4**

**Property 32: Navigation menu contains all main sections**
*For any* sidebar navigation, it should contain links to Dashboard, Stocks, Strategies, Backtest, Paper Trading, and Data sections.
**Validates: Requirements 12.3**

**Property 33: Loading operations disable buttons**
*For any* ongoing operation, the trigger button should be disabled and show loading state.
**Validates: Requirements 12.4**

**Property 34: User preferences persist to local storage**
*For any* user preference change (chart colors, time range), the setting should be saved to browser localStorage.
**Validates: Requirements 12.5**

**Property 35: Table sorting works correctly**
*For any* sortable table column, clicking the column header should sort the data in ascending/descending order.
**Validates: Requirements 12.7**

**Property 36: Table filtering works correctly**
*For any* filterable table column, entering a filter value should show only rows matching the filter criteria.
**Validates: Requirements 12.8**

### Backend Properties

**Property 37: API error responses follow standard format**
*For any* API error condition, the response should include HTTP status code, error message, and error code in a consistent JSON structure.
**Validates: Requirements 11.10**

**Property 38: Financial statements display all required fields**
*For any* financial statement data, when rendered in the Financial Data page, each statement should contain report date, period type, and all relevant financial items.
**Validates: Requirements 13.2**

**Property 39: Financial indicators display all required categories**
*For any* financial indicators data, the display should include profitability, solvency, valuation, and growth indicators.
**Validates: Requirements 13.3, 13.4, 13.5**

**Property 40: Financial data time series chart renders correctly**
*For any* valid financial indicators array, the chart should render with line series for each selected indicator over time.
**Validates: Requirements 13.7**

**Property 41: Financial sync status displays all required fields**
*For any* stock financial sync status data, the table should display code, name, status, last sync time, and latest report date.
**Validates: Requirements 14.2**


## Error Handling

### Frontend Error Handling

**Network Errors**
- Catch all API request failures using Axios interceptors
- Display user-friendly error messages (avoid technical jargon)
- Provide retry mechanism for transient failures
- Show offline indicator when network is unavailable

**Component Errors**
- Implement Error Boundary components at page level
- Catch and log unhandled exceptions
- Display fallback UI with error message and recovery options
- Prevent entire app crash from component errors

**Validation Errors**
- Validate form inputs before submission
- Display inline error messages for invalid fields
- Highlight invalid fields with red border
- Prevent form submission until all validations pass

**Data Errors**
- Handle missing or malformed data gracefully
- Show placeholder or empty state when data is unavailable
- Log data errors for debugging
- Provide clear feedback to users

**Example Error Handling Code:**

```javascript
// API Error Interceptor
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      if (status === 404) {
        notification.error({ message: '资源未找到' });
      } else if (status === 500) {
        notification.error({ message: '服务器错误，请稍后重试' });
      } else {
        notification.error({ message: data.message || '请求失败' });
      }
    } else if (error.request) {
      // Request made but no response
      notification.error({ message: '网络连接失败，请检查网络' });
    } else {
      // Something else happened
      notification.error({ message: '请求配置错误' });
    }
    return Promise.reject(error);
  }
);

// Error Boundary Component
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-page">
          <h1>出错了</h1>
          <p>页面加载失败，请刷新重试</p>
          <button onClick={() => window.location.reload()}>
            刷新页面
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

### Backend Error Handling

**Input Validation**
- Validate all request parameters and body data
- Return 400 Bad Request for invalid inputs
- Include specific validation error messages

**Resource Not Found**
- Return 404 Not Found for non-existent resources
- Include helpful error message

**Server Errors**
- Catch all unhandled exceptions
- Return 500 Internal Server Error
- Log error details for debugging
- Never expose internal error details to clients

**Database Errors**
- Handle database connection failures
- Handle query errors gracefully
- Rollback transactions on error
- Return appropriate error responses

**Example Error Handling Code:**

```python
# Error Response Helper
def error_response(message, code=None, status=400):
    return jsonify({
        'success': False,
        'error': message,
        'error_code': code
    }), status

# Global Error Handler
@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
    
    # Return generic error response
    return error_response(
        '服务器内部错误，请稍后重试',
        code='INTERNAL_ERROR',
        status=500
    )

# Validation Example
@api.route('/api/stocks/<code>/daily', methods=['GET'])
def get_daily_data(code):
    try:
        # Validate parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not code:
            return error_response('股票代码不能为空', 'INVALID_CODE')
        
        # Validate date format
        if start_date and not is_valid_date(start_date):
            return error_response('开始日期格式错误', 'INVALID_DATE')
        
        # Fetch data
        data = db.get_daily_data(code, start_date, end_date)
        
        if data is None or data.empty:
            return error_response(
                f'未找到股票 {code} 的数据',
                'DATA_NOT_FOUND',
                404
            )
        
        return jsonify({
            'success': True,
            'data': data.to_dict('records')
        })
        
    except Exception as e:
        app.logger.error(f'Error fetching daily data: {str(e)}')
        return error_response(
            '获取数据失败',
            'FETCH_ERROR',
            500
        )
```


## Testing Strategy

### Dual Testing Approach

This project requires both unit testing and property-based testing to ensure comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs
- Together they provide comprehensive coverage: unit tests catch concrete bugs, property tests verify general correctness

### Frontend Testing

**Testing Framework:**
- Test Runner: Vitest (fast, Vite-native)
- Testing Library: React Testing Library (user-centric testing)
- Property Testing: fast-check (property-based testing for JavaScript)
- E2E Testing: Playwright (optional, for critical user flows)

**Unit Testing Focus:**
- Component rendering with specific props
- User interactions (clicks, inputs, form submissions)
- Navigation and routing
- Error boundary behavior
- Specific edge cases (empty data, loading states)

**Property Testing Focus:**
- Data display properties (all required fields shown)
- Filtering and sorting correctness
- Validation logic
- State management consistency
- Responsive layout behavior

**Example Unit Test:**

```javascript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Dashboard from './Dashboard';

describe('Dashboard Component', () => {
  it('should render database status card', () => {
    const mockData = {
      database: {
        total_stocks: 5000,
        last_update: '2026-01-01',
        data_completeness: 0.95
      }
    };
    
    render(<Dashboard data={mockData} />);
    
    expect(screen.getByText('5000')).toBeInTheDocument();
    expect(screen.getByText('2026-01-01')).toBeInTheDocument();
  });
});
```

**Example Property Test:**

```javascript
import fc from 'fast-check';
import { describe, it } from 'vitest';
import { filterStocks } from './stockUtils';

describe('Stock Filtering Properties', () => {
  it('Property 5: Stock search filters correctly', () => {
    // Feature: trading-ui-system, Property 5: Stock search filters correctly
    fc.assert(
      fc.property(
        fc.array(fc.record({
          code: fc.string(),
          name: fc.string(),
          market_cap: fc.float(),
          industry: fc.string()
        })),
        fc.string(),
        (stocks, query) => {
          const filtered = filterStocks(stocks, query);
          
          // All filtered results should match the query
          return filtered.every(stock =>
            stock.code.includes(query) || stock.name.includes(query)
          );
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### Backend Testing

**Testing Framework:**
- Test Runner: pytest (Python standard)
- Property Testing: Hypothesis (property-based testing for Python)
- API Testing: pytest + requests
- Database Testing: pytest fixtures with test database

**Unit Testing Focus:**
- API endpoint responses
- Request validation
- Error handling
- Database operations
- Business logic functions

**Property Testing Focus:**
- API response format consistency
- Data validation rules
- Query result correctness
- Error response format

**Example Unit Test:**

```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_stock_list(client):
    """Test stock list API endpoint"""
    response = client.get('/api/stocks')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'stocks' in data
    assert isinstance(data['stocks'], list)

def test_get_stock_not_found(client):
    """Test stock detail with invalid code"""
    response = client.get('/api/stocks/INVALID')
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data
```

**Example Property Test:**

```python
from hypothesis import given, strategies as st
import pytest

@given(
    status_code=st.integers(min_value=400, max_value=599),
    error_message=st.text(min_size=1)
)
def test_api_error_response_format(status_code, error_message):
    """
    Property 37: API error responses follow standard format
    Feature: trading-ui-system, Property 37
    """
    # Simulate error response
    response = error_response(error_message, status=status_code)
    data = response[0].get_json()
    
    # Verify standard format
    assert 'success' in data
    assert data['success'] is False
    assert 'error' in data
    assert isinstance(data['error'], str)
    assert 'error_code' in data or data['error_code'] is None
```

### Integration Testing

**Focus Areas:**
- Frontend-Backend API integration
- Database operations with real data
- End-to-end user workflows
- Performance under load

**Example Integration Test:**

```python
def test_backtest_workflow(client, db):
    """Test complete backtest workflow"""
    # 1. Get strategy list
    response = client.get('/api/strategies')
    assert response.status_code == 200
    strategies = response.get_json()['strategies']
    strategy_id = strategies[0]['id']
    
    # 2. Start backtest
    response = client.post(f'/api/strategies/{strategy_id}/backtest', json={
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'initial_capital': 1000000
    })
    assert response.status_code == 200
    task_id = response.get_json()['task_id']
    
    # 3. Get backtest result
    response = client.get(f'/api/backtest/{task_id}')
    assert response.status_code == 200
    result = response.get_json()
    assert 'metrics' in result
    assert 'equity_curve' in result
```

### Test Configuration

**Property Test Configuration:**
- Minimum 100 iterations per property test
- Each property test must reference its design document property
- Tag format: `Feature: trading-ui-system, Property {number}: {property_text}`

**Coverage Goals:**
- Unit test coverage: > 80%
- Property test coverage: All correctness properties implemented
- Integration test coverage: All critical user workflows

### Continuous Testing

**Pre-commit:**
- Run linters (ESLint, Black)
- Run fast unit tests
- Type checking (TypeScript, mypy)

**CI Pipeline:**
- Run all unit tests
- Run all property tests
- Run integration tests
- Generate coverage reports
- Build and deploy preview


# Design Document - 极简选股助手

## Overview

极简选股助手是 TradingBuddy 的产品化封装层，专为 99% 不懂技术的中国股民设计。系统将复杂的量化逻辑、数据同步和技术分析全部"折叠"在后台，只给用户呈现最直观、最有价值的选股信号。

### Design Goals

1. **零配置**：用户无需了解任何技术参数，开箱即用
2. **一键操作**：所有复杂操作简化为一个按钮
3. **直觉化**：用红绿灯、颜色、进度条代替数字和参数
4. **移动优先**：手机上也能流畅使用
5. **建立信任**：通过历史表现数据让用户相信系统

### Key Principles

- **隐藏复杂性**：技术参数（MA5、MA20）、数据库状态、API 调用等全部隐藏
- **大白话交流**：避免技术术语，用普通股民能理解的语言
- **视觉化决策**：用颜色、图标、信号灯帮助用户快速决策
- **保持主动权**：系统提供建议而非指令，用户保持决策权

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (用户界面)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              极简选股助手 UI                            │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐ │ │
│  │  │今日精选  │  │我的自选  │  │策略历史表现          │ │ │
│  │  │(前10只)  │  │(红绿灯)  │  │(胜率/收益/回撤)      │ │ │
│  │  └──────────┘  └──────────┘  └──────────────────────┘ │ │
│  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │         一键同步按钮 + 数据状态指示器            │ │ │
│  │  └──────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   产品化 API 层 (新增)                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  /api/picker/daily-picks      今日精选                 │ │
│  │  /api/picker/watchlist         自选监控                │ │
│  │  /api/picker/strategies        金牌策略                │ │
│  │  /api/picker/sync              一键同步                │ │
│  │  /api/picker/alerts            止损止盈预警            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   现有技术层 (复用)                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Stock Scoring Engine    评分引擎                      │ │
│  │  Strategy Scanner         策略扫描器                   │ │
│  │  Data Fetcher            数据获取器                    │ │
│  │  Backtest Engine         回测引擎                      │ │
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

**Frontend (新增/修改):**
- Framework: React 18+ (已有)
- UI Library: Ant Design (已有)
- Charts: Apache ECharts (已有)
- State Management: React Context + localStorage (简化状态管理)
- 新增组件：
  - `DailyPicksCard` - 今日精选卡片
  - `WatchlistCard` - 自选监控卡片
  - `StrategyPerformanceCard` - 策略表现卡片
  - `OneSyncButton` - 一键同步按钮
  - `SignalLight` - 信号灯组件
  - `StopLossAlert` - 止损止盈预警组件

**Backend (新增 API 路由):**
- Framework: Flask 3.0+ (已有)
- 新增路由文件: `src/web/routes/picker.py`
- 复用现有模块:
  - `src/business/scoring/stock_scoring_engine.py`
  - `src/business/strategies/volume_shrink.py`
  - `src/business/strategies/ma_crossover.py`
  - `src/data/fetcher.py`


## Components and Interfaces

### Frontend Components

#### 1. SimpleDashboard (极简仪表板)

**职责**：首页主组件，只显示 3 个核心模块

**Props**: 无

**State**:
```typescript
interface SimpleDashboardState {
  dailyPicks: DailyPick[];      // 今日精选
  watchlist: WatchlistItem[];   // 自选股
  strategies: StrategyPerformance[];  // 策略表现
  syncStatus: SyncStatus;       // 同步状态
  loading: boolean;
}
```

**子组件**:
- `OneSyncButton` - 一键同步按钮
- `DailyPicksCard` - 今日精选卡片
- `WatchlistCard` - 自选监控卡片
- `StrategyPerformanceCard` - 策略表现卡片

#### 2. OneSyncButton (一键同步按钮)

**职责**：触发数据同步，显示同步状态

**Props**:
```typescript
interface OneSyncButtonProps {
  onSync: () => Promise<void>;
  syncStatus: SyncStatus;
}
```

**State**:
```typescript
interface SyncStatus {
  syncing: boolean;
  progress: number;           // 0-100
  currentStock?: string;      // 当前正在同步的股票
  lastUpdate?: string;        // 最后更新时间
  error?: string;             // 错误信息
}
```

**行为**:
- 点击触发 `/api/picker/sync` API
- 显示进度条和当前状态
- 根据最后更新时间显示黄色/红色警告

#### 3. DailyPicksCard (今日精选卡片)

**职责**：显示今日精选的前 10 只股票

**Props**:
```typescript
interface DailyPicksCardProps {
  picks: DailyPick[];
  loading: boolean;
  onStockClick: (code: string) => void;
}

interface DailyPick {
  code: string;
  name: string;
  price: number;
  pct_change: number;
  confidence_score: number;   // 0-100
  reason: string;             // 大白话选股理由
  signal_strength: 'strong' | 'medium' | 'weak';  // 强/中/弱
}
```

**行为**:
- 按信号强度降序排列
- 用颜色标识信号强度（绿色=强，黄色=中，灰色=弱）
- 点击股票跳转到详情页

#### 4. WatchlistCard (自选监控卡片)

**职责**：显示用户的自选股和信号灯

**Props**:
```typescript
interface WatchlistCardProps {
  watchlist: WatchlistItem[];
  loading: boolean;
  onRemove: (code: string) => void;
  onStockClick: (code: string) => void;
}

interface WatchlistItem {
  code: string;
  name: string;
  price: number;
  pct_change: number;
  signal: 'buy' | 'sell' | 'hold';  // 买入/卖出/观望
  added_at: string;                 // 添加时间
  added_price: number;              // 添加时价格
  stop_loss: number;                // 止损价格
  take_profit: number;              // 止盈价格
  alert?: Alert;                    // 预警信息
}

interface Alert {
  type: 'stop_loss' | 'take_profit';
  message: string;                  // 建议操作
  current_price: number;
  target_price: number;
}
```

**行为**:
- 用红绿灯表示买卖建议
- 显示止损止盈进度条
- 触发预警时显示红色/绿色提示

#### 5. StrategyPerformanceCard (策略表现卡片)

**职责**：显示金牌策略的历史表现

**Props**:
```typescript
interface StrategyPerformanceCardProps {
  strategies: StrategyPerformance[];
  loading: boolean;
  onStrategyClick: (id: string) => void;
}

interface StrategyPerformance {
  id: string;
  name: string;                     // 策略名称（大白话）
  description: string;              // 一句话描述
  suitable_for: string;             // 适合人群（稳健型/激进型）
  win_rate: number;                 // 近30天胜率 (%)
  avg_return: number;               // 平均收益率 (%)
  max_drawdown: number;             // 最大回撤 (%)
  equity_curve: EquityPoint[];      // 资金曲线
  recent_picks: HistoricalPick[];   // 最近选股记录
}

interface EquityPoint {
  date: string;
  value: number;
}

interface HistoricalPick {
  code: string;
  name: string;
  pick_date: string;
  pick_price: number;
  result: 'success' | 'failure';    // 成功/失败
  return: number;                   // 收益率 (%)
}
```

**行为**:
- 显示胜率、平均收益率、最大回撤
- 用图表展示资金曲线
- 点击策略显示历史选股记录


#### 6. SignalLight (信号灯组件)

**职责**：用红绿灯表示买卖建议

**Props**:
```typescript
interface SignalLightProps {
  signal: 'buy' | 'sell' | 'hold';
  showLabel?: boolean;  // 是否显示文字标签
}
```

**行为**:
- 绿灯 = 买入建议
- 红灯 = 卖出建议
- 黄灯 = 观望

#### 7. SimpleStockDetail (极简股票详情页)

**职责**：显示股票详情，包含 K 线图和选股理由

**Props**:
```typescript
interface SimpleStockDetailProps {
  code: string;
}
```

**State**:
```typescript
interface SimpleStockDetailState {
  stock: StockInfo;
  dailyData: DailyData[];
  signals: SignalPoint[];     // 买入/卖出信号点
  reason: string;             // 选股理由（大白话）
  keyMetrics: KeyMetrics;     // 关键指标
  inWatchlist: boolean;
}

interface SignalPoint {
  date: string;
  type: 'buy' | 'sell';
  price: number;
}

interface KeyMetrics {
  volume_ratio: number;       // 成交量比
  ma_trend: string;           // 均线趋势（大白话）
  market_cap: string;         // 市值（格式化）
  industry: string;           // 行业
}
```

**子组件**:
- `KLineChart` - K 线图（已有，需增强）
- `ReasonCard` - 选股理由卡片
- `KeyMetricsCard` - 关键指标卡片
- `AddToWatchlistButton` - 加入自选按钮

#### 8. OnboardingGuide (新手引导)

**职责**：首次访问时显示引导页

**Props**:
```typescript
interface OnboardingGuideProps {
  onComplete: () => void;
  onSkip: () => void;
}
```

**State**:
```typescript
interface OnboardingGuideState {
  currentStep: number;  // 当前步骤 (0-3)
  steps: GuideStep[];
}

interface GuideStep {
  title: string;
  description: string;
  image?: string;
}
```

**行为**:
- 检查 localStorage 中的 `onboarding_completed` 标记
- 显示 4 个引导步骤
- 提供"跳过"和"下一步"按钮
- 完成后设置 localStorage 标记

### Backend API Endpoints

#### Picker APIs (新增)

```python
GET /api/picker/daily-picks
# 获取今日精选股票
# Query params: strategy (可选，默认"low-volume-breakout")
# Response: {
#   picks: [{
#     code, name, price, pct_change,
#     confidence_score, reason, signal_strength
#   }],
#   generated_at: datetime,
#   strategy_name: str
# }

GET /api/picker/watchlist
# 获取用户自选股（从 localStorage 读取代码列表，后端补充数据）
# Query params: codes (逗号分隔的股票代码)
# Response: {
#   watchlist: [{
#     code, name, price, pct_change, signal,
#     stop_loss, take_profit, alert
#   }]
# }

POST /api/picker/watchlist/add
# 添加自选股
# Body: { code, added_price, stop_loss_pct, take_profit_pct }
# Response: { success: bool, message: str }

GET /api/picker/strategies
# 获取金牌策略列表
# Response: {
#   strategies: [{
#     id, name, description, suitable_for,
#     win_rate, avg_return, max_drawdown
#   }]
# }

GET /api/picker/strategies/{id}/performance
# 获取策略详细表现
# Response: {
#   strategy: {...},
#   equity_curve: [...],
#   recent_picks: [...]
# }

POST /api/picker/sync
# 触发一键数据同步
# Body: { mode: 'incremental' | 'full' }
# Response: { task_id, status }

GET /api/picker/sync/{task_id}
# 获取同步进度
# Response: {
#   task_id, status, progress,
#   current_stock, errors
# }

GET /api/picker/sync/status
# 获取数据同步状态
# Response: {
#   last_update: datetime,
#   total_stocks: int,
#   synced_stocks: int,
#   warning_level: 'none' | 'yellow' | 'red'
# }
```


## Data Models

### Frontend Data Models

```typescript
// Daily Pick Model
interface DailyPick {
  code: string;
  name: string;
  price: number;
  pct_change: number;
  confidence_score: number;   // 0-100
  reason: string;             // 大白话选股理由
  signal_strength: 'strong' | 'medium' | 'weak';
  key_metrics: {
    volume_ratio: number;
    ma_trend: string;
    market_cap: string;
  };
}

// Watchlist Item Model
interface WatchlistItem {
  code: string;
  name: string;
  price: number;
  pct_change: number;
  signal: 'buy' | 'sell' | 'hold';
  added_at: string;
  added_price: number;
  stop_loss: number;
  take_profit: number;
  current_pnl: number;        // 当前盈亏 (%)
  alert?: {
    type: 'stop_loss' | 'take_profit';
    message: string;
    current_price: number;
    target_price: number;
  };
}

// Strategy Performance Model
interface StrategyPerformance {
  id: string;
  name: string;
  description: string;
  suitable_for: string;
  win_rate: number;
  avg_return: number;
  max_drawdown: number;
  equity_curve: { date: string; value: number }[];
  recent_picks: {
    code: string;
    name: string;
    pick_date: string;
    pick_price: number;
    result: 'success' | 'failure';
    return: number;
  }[];
}

// Sync Status Model
interface SyncStatus {
  syncing: boolean;
  progress: number;
  current_stock?: string;
  last_update?: string;
  warning_level: 'none' | 'yellow' | 'red';
  error?: string;
}
```

### Backend Data Models

```python
# Golden Strategy Configuration
GOLDEN_STRATEGIES = {
    'low-volume-breakout': {
        'id': 'low-volume-breakout',
        'name': '低位放量突破',
        'description': '股价在低位缩量后突然放量上涨，可能有资金进场',
        'suitable_for': '稳健型',
        'strategy_class': VolumeShrinkStrategy,
        'params': {
            'min_cap': 50e8,
            'max_cap': 200e8,
            'min_avg_turnover': 1e8
        }
    },
    'ma-golden-cross': {
        'id': 'ma-golden-cross',
        'name': '多头排列启动',
        'description': '短期均线上穿长期均线，趋势可能转强',
        'suitable_for': '激进型',
        'strategy_class': MACrossoverStrategy,
        'params': {
            'short_window': 5,
            'long_window': 20
        }
    },
    'pullback-support': {
        'id': 'pullback-support',
        'name': '回踩支撑买入',
        'description': '股价回调到重要支撑位后企稳，可能反弹',
        'suitable_for': '稳健型',
        'strategy_class': None,  # 待实现
        'params': {}
    }
}

# Database Schema (新增表)

# picker_daily_picks table
CREATE TABLE picker_daily_picks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    strategy_id TEXT NOT NULL,
    pick_date TEXT NOT NULL,
    pick_price REAL NOT NULL,
    confidence_score REAL NOT NULL,
    reason TEXT NOT NULL,
    signal_strength TEXT NOT NULL,
    key_metrics TEXT NOT NULL,  -- JSON
    created_at TEXT NOT NULL,
    UNIQUE(code, strategy_id, pick_date)
);

# picker_watchlist table (可选，也可以只用 localStorage)
CREATE TABLE picker_watchlist (
    code TEXT PRIMARY KEY,
    added_at TEXT NOT NULL,
    added_price REAL NOT NULL,
    stop_loss_pct REAL NOT NULL,
    take_profit_pct REAL NOT NULL
);

# picker_strategy_performance table
CREATE TABLE picker_strategy_performance (
    strategy_id TEXT PRIMARY KEY,
    win_rate REAL NOT NULL,
    avg_return REAL NOT NULL,
    max_drawdown REAL NOT NULL,
    total_picks INTEGER NOT NULL,
    successful_picks INTEGER NOT NULL,
    equity_curve TEXT NOT NULL,  -- JSON
    last_updated TEXT NOT NULL
);
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Frontend Properties

**Property 1: 一键同步触发数据更新**
*For any* user click on the sync button, the system should trigger an API call to `/api/picker/sync` and update the sync status state.
**Validates: Requirements 1.2**

**Property 2: 同步进度显示**
*For any* sync status with `syncing: true`, the UI should display a progress bar and current status text.
**Validates: Requirements 1.3**

**Property 3: 同步完成显示统计**
*For any* sync status with `syncing: false` and no error, the UI should display a success message and update statistics.
**Validates: Requirements 1.4**

**Property 4: 同步失败显示友好错误**
*For any* sync status with an error, the error message should not contain technical terms (like "API", "database", "connection").
**Validates: Requirements 1.5, 11.5**

**Property 5: 数据更新时间警告**
*For any* last update time more than 24 hours ago, the UI should display a yellow warning; for more than 72 hours, a red warning.
**Validates: Requirements 1.7, 1.8**

**Property 6: 策略列表显示必需字段**
*For any* strategy object, the rendered UI should contain name, description, and win_rate fields.
**Validates: Requirements 2.5**

**Property 7: 技术参数隐藏**
*For any* strategy display, the UI should not contain technical terms like "MA5", "MA20", "RSI", "MACD".
**Validates: Requirements 2.8**

**Property 8: 今日精选按信号强度排序**
*For any* daily picks list, the stocks should be sorted in descending order by confidence_score.
**Validates: Requirements 3.8**

**Property 9: 低分信号过滤**
*For any* daily picks list, all stocks should have confidence_score >= 30.
**Validates: Requirements 3.9**

**Property 10: 精选股票显示必需字段**
*For any* daily pick, the rendered UI should contain code, name, price, and confidence_score fields.
**Validates: Requirements 3.4**

**Property 11: 信号强度颜色映射**
*For any* signal strength value, the color should be: strong → green, medium → yellow, weak → gray.
**Validates: Requirements 3.5, 4.5**

**Property 12: 选股理由用大白话**
*For any* pick reason text, it should not contain technical terms and should be understandable by non-technical users.
**Validates: Requirements 3.7**

**Property 13: 加入自选更新列表**
*For any* add-to-watchlist operation, the stock should appear in the watchlist after the operation completes.
**Validates: Requirements 4.2**

**Property 14: 自选股显示必需字段**
*For any* watchlist item, the rendered UI should contain price, pct_change, signal, added_at, and added_price fields.
**Validates: Requirements 4.4, 4.9**

**Property 15: 信号标签显示**
*For any* watchlist item with signal 'buy', the UI should display a "买入" label; for 'sell', a "卖出" label.
**Validates: Requirements 4.6, 4.7**

**Property 16: 移除自选更新列表**
*For any* remove-from-watchlist operation, the stock should not appear in the watchlist after the operation completes.
**Validates: Requirements 4.8**

**Property 17: 默认止损止盈设置**
*For any* newly added watchlist item, the default stop_loss should be -10% and take_profit should be +20%.
**Validates: Requirements 5.2**

**Property 18: 止损预警显示**
*For any* watchlist item where current_price <= stop_loss, the UI should display a red alert with "建议止损卖出" message.
**Validates: Requirements 5.4, 5.7**

**Property 19: 止盈预警显示**
*For any* watchlist item where current_price >= take_profit, the UI should display a green alert with "建议止盈卖出" message.
**Validates: Requirements 5.5, 5.7**

**Property 20: 预警包含价格信息**
*For any* alert, the UI should display current_price and target_price fields.
**Validates: Requirements 5.8**

**Property 21: 策略表现包含必需字段**
*For any* strategy performance data, the UI should display win_rate, avg_return, and max_drawdown fields.
**Validates: Requirements 6.3, 6.4, 6.5**

**Property 22: 历史记录标注成功失败**
*For any* historical pick, the UI should display a "成功" or "失败" label based on the result field.
**Validates: Requirements 6.8**

**Property 23: 响应式布局切换**
*For any* screen width < 768px, the UI should apply mobile layout styles.
**Validates: Requirements 9.2**

**Property 24: 移动端按钮尺寸**
*For any* button in mobile layout, the minimum size should be 44px × 44px.
**Validates: Requirements 9.4**

**Property 25: 首次访问显示引导**
*For any* user without `onboarding_completed` flag in localStorage, the onboarding guide should be displayed.
**Validates: Requirements 10.1**

**Property 26: 完成引导设置标记**
*For any* onboarding completion, the `onboarding_completed` flag should be set to true in localStorage.
**Validates: Requirements 10.7**

**Property 27: 错误消息用户友好**
*For any* error message, it should not contain technical terms like "API error", "database connection failed", "500 Internal Server Error".
**Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5**

**Property 28: 错误提示包含客服按钮**
*For any* error message display, the UI should include a "联系客服" button.
**Validates: Requirements 11.6**

**Property 29: 长时间加载显示提示**
*For any* loading operation exceeding 3 seconds, the UI should display a loading indicator.
**Validates: Requirements 12.6**

### Backend Properties

**Property 30: 今日精选返回格式**
*For any* `/api/picker/daily-picks` response, it should contain picks array, generated_at, and strategy_name fields.
**Validates: Requirements 3.2**

**Property 31: 自选股信号计算**
*For any* watchlist item, the signal field should be calculated based on current technical indicators.
**Validates: Requirements 4.5**

**Property 32: 止损止盈预警计算**
*For any* watchlist item, if current_price <= stop_loss or current_price >= take_profit, an alert should be generated.
**Validates: Requirements 5.4, 5.5**

**Property 33: 策略表现数据完整性**
*For any* strategy performance response, it should contain win_rate, avg_return, max_drawdown, and equity_curve fields.
**Validates: Requirements 6.2, 6.3, 6.4, 6.5, 6.6**


## Error Handling

### Frontend Error Handling

**Network Errors**
- 将所有网络错误转换为用户友好的消息
- 避免显示技术术语（API、HTTP、状态码等）
- 提供"重试"按钮和"联系客服"按钮

**Error Message Mapping**:
```typescript
const ERROR_MESSAGES = {
  'network_error': '网络不稳定，请稍后重试',
  'timeout': '请求超时，请检查网络连接',
  'not_found': '未找到该股票',
  'server_error': '服务暂时不可用，请稍后重试',
  'sync_failed': '数据更新失败，请稍后重试',
  'invalid_code': '股票代码不正确',
  'maintenance': '系统维护中，预计 XX:XX 恢复'
};
```

**Loading States**
- 使用骨架屏而非空白页面
- 超过 3 秒显示加载提示
- 提供取消按钮（如果适用）

**Data Validation**
- 在前端验证用户输入
- 显示内联错误提示
- 防止无效数据提交

### Backend Error Handling

**Input Validation**
- 验证所有请求参数
- 返回 400 Bad Request 和友好错误消息
- 记录验证错误日志

**Resource Not Found**
- 返回 404 Not Found
- 提供建议（如"该股票可能已退市"）

**Server Errors**
- 捕获所有未处理异常
- 返回 500 Internal Server Error
- 记录详细错误日志
- 向用户返回通用错误消息

**Example Error Response**:
```python
{
    'success': False,
    'error': '网络不稳定，请稍后重试',
    'error_code': 'NETWORK_ERROR',
    'support_contact': 'support@tradingbuddy.com'
}
```

## Testing Strategy

### Dual Testing Approach

This project requires both unit testing and property-based testing:

- **Unit tests**: Verify specific examples, edge cases, and UI component rendering
- **Property tests**: Verify universal properties across all inputs
- Together they provide comprehensive coverage

### Frontend Testing

**Testing Framework:**
- Test Runner: Vitest
- Testing Library: React Testing Library
- Property Testing: fast-check
- Minimum 100 iterations per property test

**Unit Testing Focus:**
- Component rendering with specific props
- User interactions (clicks, inputs)
- Navigation and routing
- Specific edge cases (empty data, loading states)

**Property Testing Focus:**
- Data display properties (all required fields shown)
- Sorting and filtering correctness
- Color mapping logic
- Error message friendliness
- Responsive layout behavior

**Example Unit Test:**

```javascript
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import DailyPicksCard from './DailyPicksCard';

describe('DailyPicksCard Component', () => {
  it('should display top 10 picks', () => {
    const picks = Array.from({ length: 15 }, (_, i) => ({
      code: `60000${i}`,
      name: `股票${i}`,
      price: 10 + i,
      pct_change: i % 2 === 0 ? 5 : -3,
      confidence_score: 80 - i,
      reason: '成交量放大',
      signal_strength: 'strong'
    }));
    
    render(<DailyPicksCard picks={picks} loading={false} />);
    
    // 应该只显示前10只
    const rows = screen.getAllByRole('row');
    expect(rows.length).toBe(11); // 10 + header
  });
});
```

**Example Property Test:**

```javascript
import fc from 'fast-check';
import { describe, it } from 'vitest';
import { sortByConfidenceScore } from './utils';

describe('Daily Picks Properties', () => {
  it('Property 8: Daily picks sorted by confidence score', () => {
    // Feature: user-friendly-stock-picker, Property 8
    fc.assert(
      fc.property(
        fc.array(fc.record({
          code: fc.string(),
          confidence_score: fc.float({ min: 0, max: 100 })
        })),
        (picks) => {
          const sorted = sortByConfidenceScore(picks);
          
          // 验证降序排列
          for (let i = 0; i < sorted.length - 1; i++) {
            if (sorted[i].confidence_score < sorted[i + 1].confidence_score) {
              return false;
            }
          }
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
  
  it('Property 9: Low score signals filtered', () => {
    // Feature: user-friendly-stock-picker, Property 9
    fc.assert(
      fc.property(
        fc.array(fc.record({
          code: fc.string(),
          confidence_score: fc.float({ min: 0, max: 100 })
        })),
        (picks) => {
          const filtered = filterLowScoreSignals(picks);
          
          // 所有结果的分数应该 >= 30
          return filtered.every(pick => pick.confidence_score >= 30);
        }
      ),
      { numRuns: 100 }
    );
  });
  
  it('Property 12: Reason uses plain language', () => {
    // Feature: user-friendly-stock-picker, Property 12
    fc.assert(
      fc.property(
        fc.string(),
        (reason) => {
          const technicalTerms = ['MA5', 'MA20', 'RSI', 'MACD', 'KDJ', 'BOLL'];
          
          // 选股理由不应该包含技术术语
          return !technicalTerms.some(term => reason.includes(term));
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### Backend Testing

**Testing Framework:**
- Test Runner: pytest
- Property Testing: Hypothesis
- API Testing: pytest + requests

**Unit Testing Focus:**
- API endpoint responses
- Data transformation logic
- Error handling
- Business logic functions

**Property Testing Focus:**
- API response format consistency
- Data validation rules
- Signal calculation correctness
- Error message friendliness

**Example Unit Test:**

```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_daily_picks_endpoint(client):
    """Test daily picks API endpoint"""
    response = client.get('/api/picker/daily-picks')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'picks' in data
    assert 'generated_at' in data
    assert 'strategy_name' in data
    assert isinstance(data['picks'], list)
    assert len(data['picks']) <= 10  # 最多10只

def test_daily_picks_required_fields(client):
    """Test that each pick has required fields"""
    response = client.get('/api/picker/daily-picks')
    data = response.get_json()
    
    for pick in data['picks']:
        assert 'code' in pick
        assert 'name' in pick
        assert 'price' in pick
        assert 'confidence_score' in pick
        assert 'reason' in pick
```

**Example Property Test:**

```python
from hypothesis import given, strategies as st
import pytest

@given(
    confidence_score=st.floats(min_value=0, max_value=100)
)
def test_signal_strength_mapping(confidence_score):
    """
    Property 11: Signal strength color mapping
    Feature: user-friendly-stock-picker, Property 11
    """
    strength = calculate_signal_strength(confidence_score)
    
    if confidence_score >= 70:
        assert strength == 'strong'
    elif confidence_score >= 50:
        assert strength == 'medium'
    else:
        assert strength == 'weak'

@given(
    error_message=st.text(min_size=1)
)
def test_error_message_friendliness(error_message):
    """
    Property 27: Error messages are user-friendly
    Feature: user-friendly-stock-picker, Property 27
    """
    friendly_message = make_error_friendly(error_message)
    
    # 不应该包含技术术语
    technical_terms = ['API', 'database', 'connection', '500', 'HTTP', 'SQL']
    for term in technical_terms:
        assert term.lower() not in friendly_message.lower()

@given(
    picks=st.lists(st.fixed_dictionaries({
        'code': st.text(min_size=6, max_size=6),
        'confidence_score': st.floats(min_value=0, max_value=100)
    }))
)
def test_low_score_filtering(picks):
    """
    Property 9: Low score signals filtered
    Feature: user-friendly-stock-picker, Property 9
    """
    filtered = filter_daily_picks(picks)
    
    # 所有结果的分数应该 >= 30
    for pick in filtered:
        assert pick['confidence_score'] >= 30
```

### Integration Testing

**Focus Areas:**
- Frontend-Backend API integration
- Data flow from database to UI
- User workflows (add to watchlist, sync data, view details)
- Error handling across layers

**Example Integration Test:**

```python
def test_add_to_watchlist_workflow(client):
    """Test complete add-to-watchlist workflow"""
    # 1. 获取今日精选
    response = client.get('/api/picker/daily-picks')
    assert response.status_code == 200
    picks = response.get_json()['picks']
    assert len(picks) > 0
    
    # 2. 添加第一只股票到自选
    pick = picks[0]
    response = client.post('/api/picker/watchlist/add', json={
        'code': pick['code'],
        'added_price': pick['price'],
        'stop_loss_pct': -10,
        'take_profit_pct': 20
    })
    assert response.status_code == 200
    assert response.get_json()['success'] is True
    
    # 3. 获取自选列表，验证股票已添加
    response = client.get(f'/api/picker/watchlist?codes={pick["code"]}')
    assert response.status_code == 200
    watchlist = response.get_json()['watchlist']
    assert len(watchlist) == 1
    assert watchlist[0]['code'] == pick['code']
```

### Test Configuration

**Property Test Configuration:**
- Minimum 100 iterations per property test
- Each property test must reference its design document property
- Tag format: `Feature: user-friendly-stock-picker, Property {number}: {property_text}`

**Coverage Goals:**
- Unit test coverage: > 80%
- Property test coverage: All correctness properties implemented
- Integration test coverage: All critical user workflows


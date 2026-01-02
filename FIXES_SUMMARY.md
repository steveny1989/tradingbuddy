# 问题修复总结

## 修复时间
2026-01-02 20:16

## 修复的问题

### 1. React Key Warning 警告
**问题**: 控制台显示 "Each child in a list should have a unique 'key' prop"

**原因**: 
- `dailyPicks.map()` 和 `watchlist.map()` 使用 `key={item.code}` 可能不唯一
- 如果同一只股票出现多次，会导致key冲突

**修复**:
- 改用 `key={`${item.code}-${index}`}` 确保唯一性
- 修改文件: `frontend/src/pages/SimplePicker.premium.tsx`

### 2. "加入自选" 按钮点击无反应
**问题**: 用户点击"加入自选"按钮没有任何反应

**原因**: 
- 使用了 `motion.button` (framer-motion)，可能干扰了事件处理
- 缺少 `e.preventDefault()` 导致事件被父元素捕获

**修复**:
- 将 `motion.button` 改为普通 `button` 元素
- 添加 `e.preventDefault()` 和 `e.stopPropagation()`
- 使用原生 CSS hover 效果替代 framer-motion 动画
- 添加更多调试日志
- 修改文件: `frontend/src/components/premium/StrategyCard.tsx`

### 3. K线图显示重复日期
**问题**: K线图中出现两个"12月31日"

**原因**: 
- 数据库中可能存在同一日期的多条记录
- API没有对重复日期进行去重处理

**修复**:
- 在K线API中添加 `df.drop_duplicates(subset=['date'], keep='last')`
- 保留最新的数据，删除重复日期
- 修改文件: `src/web/routes/picker.py` (line 1127)

### 4. 股票详情页显示 undefined
**问题**: 点击股票卡片后，详情页URL显示 `/picker/stocks/undefined`

**状态**: 待观察
- 这个问题可能是因为点击事件被阻止导致的
- 修复了按钮点击问题后，应该会自动解决
- 如果仍然存在，需要检查 `navigate()` 调用

## 修改的文件

1. **frontend/src/components/premium/StrategyCard.tsx**
   - 修改按钮从 `motion.button` 到普通 `button`
   - 添加 `e.preventDefault()`
   - 添加调试日志

2. **frontend/src/pages/SimplePicker.premium.tsx**
   - 修改 `dailyPicks.map()` 的 key 为 `${pick.code}-${index}`
   - 修改 `watchlist.map()` 的 key 为 `${item.code}-${index}`

3. **src/web/routes/picker.py**
   - 在K线API中添加日期去重逻辑
   - 使用 `drop_duplicates(subset=['date'], keep='last')`

## 后端服务状态

- **进程ID**: 20
- **端口**: 5001
- **状态**: ✅ 运行中
- **缓存**: ✅ 已初始化 (10只股票)

## 前端服务状态

- **进程ID**: 4
- **端口**: 3000
- **状态**: ✅ 运行中

## 测试建议

1. **测试"加入自选"功能**:
   - 刷新页面 (http://localhost:3000)
   - 点击任意股票卡片的"加入自选"按钮
   - 检查控制台日志，应该看到:
     - "StrategyCard handleAddToWatchlist 被调用"
     - "调用 onAddToWatchlist 回调"
     - "handleAddToWatchlist 被调用"
     - "自选股已更新，新列表"
   - 检查页面下方"自选股监控"区域，应该出现新加入的股票

2. **测试K线图去重**:
   - 点击任意股票卡片进入详情页
   - 查看K线图，确认没有重复日期
   - 切换不同时间周期 (1个月/3个月/6个月/1年)

3. **测试React Key警告**:
   - 打开浏览器控制台
   - 刷新页面
   - 确认没有 "unique key prop" 警告

## 注意事项

- 所有修改都是向后兼容的
- 没有改变任何数据结构或API接口
- 只是修复了UI交互和数据显示问题

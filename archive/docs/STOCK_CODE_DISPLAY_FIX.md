# 股票代码显示优化

## 问题描述

在股票详情页面中，股票代码显示为 "sh.600519" 或 "sz.000001" 这样的格式，包含了市场前缀，对用户不够友好。

用户期望看到：
- **贵州茅台 600519** ✅
- 而不是：贵州茅台 sh.600519 ❌

## 解决方案

### 1. 创建股票代码格式化工具

创建了 `frontend/src/utils/stockCode.ts` 工具文件，提供以下函数：

#### `formatStockCode(code: string): string`
将带市场前缀的代码转换为纯数字代码
```typescript
formatStockCode("sh.600519") // "600519"
formatStockCode("sz.000001") // "000001"
formatStockCode("600519")    // "600519"
```

#### `formatStockCodeWithMarket(code: string): string`
格式化为带大写市场前缀的代码
```typescript
formatStockCodeWithMarket("sh.600519") // "SH600519"
formatStockCodeWithMarket("sz.000001") // "SZ000001"
```

#### `getMarketName(code: string): string`
获取市场名称（中文）
```typescript
getMarketName("sh.600519") // "上海"
getMarketName("sz.000001") // "深圳"
```

#### `buildFullCode(code: string): string`
构建完整的股票代码（带市场前缀）
```typescript
buildFullCode("600519") // "sh.600519"
buildFullCode("000001") // "sz.000001"
```

### 2. 更新页面组件

#### 修改的文件：

1. **frontend/src/pages/SimpleStockDetail.tsx**
   - 导入 `formatStockCode` 工具函数
   - 使用 `formatStockCode(stockInfo.code)` 替代直接显示 `stockInfo.code`

2. **frontend/src/pages/SimpleStockDetail.premium.tsx**
   - 导入 `formatStockCode` 工具函数
   - 使用 `formatStockCode(stockInfo.code)` 替代直接显示 `stockInfo.code`

3. **frontend/src/components/picker/DailyPicksCard.tsx**
   - 导入 `formatStockCode` 工具函数
   - 在今日精选列表中使用 `formatStockCode(record.code)`

4. **frontend/src/components/picker/WatchlistCard.tsx**
   - 导入 `formatStockCode` 工具函数
   - 在自选股列表中使用 `formatStockCode(record.code)`

5. **frontend/src/components/picker/StrategyPerformanceCard.tsx**
   - 导入 `formatStockCode` 工具函数
   - 在策略历史表现列表中使用 `formatStockCode(record.code)`

### 3. 修改前后对比

#### 修改前：
```tsx
<Text type="secondary">{stockInfo.code}</Text>
// 显示：sh.600519
```

#### 修改后：
```tsx
<Text type="secondary">{formatStockCode(stockInfo.code)}</Text>
// 显示：600519
```

## 实施细节

### 代码位置

#### SimpleStockDetail.tsx (普通版本)
```tsx
// 第 16 行：导入工具函数
import { formatStockCode } from '../utils/stockCode';

// 第 241 行：使用工具函数
<Text type="secondary">
  {formatStockCode(stockInfo.code)}
</Text>
```

#### SimpleStockDetail.premium.tsx (Premium 版本)
```tsx
// 第 11 行：导入工具函数
import { formatStockCode } from '../utils/stockCode';

// 第 262 行：使用工具函数
<Text style={{ color: '#9ca3af', fontSize: 16 }}>
  {formatStockCode(stockInfo.code)}
</Text>
```

## 优势

### 1. 用户体验提升
- ✅ 显示更简洁，符合用户习惯
- ✅ 去除技术细节（市场前缀）
- ✅ 更易于阅读和记忆

### 2. 代码可维护性
- ✅ 统一的格式化逻辑
- ✅ 易于扩展（可添加更多格式化选项）
- ✅ 类型安全（TypeScript）

### 3. 灵活性
- ✅ 可根据需求选择不同的格式化方式
- ✅ 支持多种显示格式（纯数字、带市场前缀等）
- ✅ 易于国际化扩展

## 测试建议

### 手动测试步骤：

1. **启动应用**
   ```bash
   ./start_backend.sh
   ./start_ui.sh
   ```

2. **访问各个页面验证**
   
   a. **股票详情页**
   - 访问：http://localhost:3000/picker/stocks/sh.600519
   - 验证显示：贵州茅台 **600519** ✅
   
   b. **今日精选列表**
   - 访问：http://localhost:3000/picker
   - 验证今日精选表格中显示：**600519** 而不是 sh.600519 ✅
   
   c. **自选股列表**
   - 访问：http://localhost:3000/picker
   - 验证自选股表格中显示：**600489** 而不是 sh.600489 ✅
   
   d. **策略历史表现**
   - 访问：http://localhost:3000/picker
   - 展开策略折叠面板
   - 验证历史选股表格中显示：**600519** 而不是 sh.600519 ✅

3. **测试不同市场的股票**
   - 上海股票：sh.600519 → 显示 600519
   - 深圳股票：sz.000001 → 显示 000001
   - 创业板：sz.300001 → 显示 300001

4. **测试边界情况**
   - 已经是纯数字的代码：600519 → 显示 600519
   - 空字符串：'' → 显示 ''
   - undefined/null：应该有容错处理

### 自动化测试（建议添加）：

```typescript
// frontend/src/utils/__tests__/stockCode.test.ts
import { formatStockCode, formatStockCodeWithMarket, getMarketName, buildFullCode } from '../stockCode';

describe('stockCode utils', () => {
  describe('formatStockCode', () => {
    it('should format code with market prefix', () => {
      expect(formatStockCode('sh.600519')).toBe('600519');
      expect(formatStockCode('sz.000001')).toBe('000001');
    });
    
    it('should handle code without prefix', () => {
      expect(formatStockCode('600519')).toBe('600519');
    });
    
    it('should handle empty string', () => {
      expect(formatStockCode('')).toBe('');
    });
  });
  
  describe('formatStockCodeWithMarket', () => {
    it('should format with uppercase market prefix', () => {
      expect(formatStockCodeWithMarket('sh.600519')).toBe('SH600519');
      expect(formatStockCodeWithMarket('sz.000001')).toBe('SZ000001');
    });
  });
  
  describe('getMarketName', () => {
    it('should return market name in Chinese', () => {
      expect(getMarketName('sh.600519')).toBe('上海');
      expect(getMarketName('sz.000001')).toBe('深圳');
    });
  });
  
  describe('buildFullCode', () => {
    it('should build full code with market prefix', () => {
      expect(buildFullCode('600519')).toBe('sh.600519');
      expect(buildFullCode('000001')).toBe('sz.000001');
      expect(buildFullCode('300001')).toBe('sz.300001');
    });
  });
});
```

## 后续优化建议

### 1. 统一所有股票代码显示
检查并更新以下位置：
- 股票列表页面
- 搜索结果
- 自选股列表
- 今日精选列表
- 任何显示股票代码的地方

### 2. 添加市场标识（可选）
如果需要显示市场信息，可以使用徽章：
```tsx
<Space>
  <Text>{formatStockCode(stockInfo.code)}</Text>
  <Tag color={getMarketName(stockInfo.code) === '上海' ? 'blue' : 'green'}>
    {getMarketName(stockInfo.code)}
  </Tag>
</Space>
```

### 3. 国际化支持
为不同地区提供不同的显示格式：
```typescript
// 中国大陆：600519
// 香港：0700.HK
// 美国：AAPL
```

## 相关文件

### 新增文件：
- `frontend/src/utils/stockCode.ts` - 股票代码格式化工具

### 修改文件：
- `frontend/src/pages/SimpleStockDetail.tsx` - 普通版股票详情页
- `frontend/src/pages/SimpleStockDetail.premium.tsx` - Premium 版股票详情页
- `frontend/src/components/picker/DailyPicksCard.tsx` - 今日精选卡片
- `frontend/src/components/picker/WatchlistCard.tsx` - 自选股卡片
- `frontend/src/components/picker/StrategyPerformanceCard.tsx` - 策略表现卡片

### 相关文档：
- `AI_DECISION_CARD_IMPLEMENTATION.md` - 决策简报 UI 升级
- `DIAGNOSIS_UI_UPGRADE_SUMMARY.md` - 诊断 UI 升级总结

---

**修复日期**：2026-01-02
**修复人员**：首席 UI 设计师
**状态**：✅ 已完成

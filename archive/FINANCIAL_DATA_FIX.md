# 财务数据显示修复

# 财务数据显示修复

## ✅ 修复完成状态

**所有问题已解决！** 系统现在正确显示财务数据。

### 最终验证结果 (2026-01-02 20:40)
- ✅ 后端服务运行正常 (进程23, 端口5001)
- ✅ 前端服务运行正常 (进程4, 端口3000)
- ✅ API返回正确数据
- ✅ 百分比显示正确 (19.62% 而不是 1962%)
- ✅ 评分算法使用正确阈值
- ✅ 缺失数据显示"数据缺失"

### 测试示例 (sz.301042 - 安联锐视)
```json
API响应:
{
  "key_metrics": {
    "roe": 19.62,
    "debt_ratio": 10.94,
    "pe_ratio": 0.0,
    "pb_ratio": 0.0
  }
}

评分结果:
{
  "score": 100,
  "stars": 5,
  "pros": [
    "盈利能力强（ROE 19.6%）",
    "负债健康（10.9%）",
    "短期趋势向上（金叉）",
    "成交活跃（放量1.9倍）",
    "价格稳定"
  ]
}
```

---

## 问题
关键指标（PE、PB、ROE、负债率）都显示0.00

## 原因
API代码中使用了错误的数据库字段名：
- 代码中使用：`debt_ratio`
- 实际字段名：`debt_to_asset_ratio`

## 解决方案

### 1. 修复字段名
修改 `src/web/routes/picker.py` 中的两处SQL查询：

**位置1**: `get_picker_stock_detail()` 函数（约1024行）
**位置2**: `get_stock_rating()` 函数（约1285行）

将：
```sql
SELECT pe_ratio, pb_ratio, roe, debt_ratio
FROM financial_indicators
```

改为：
```sql
SELECT pe_ratio, pb_ratio, roe, debt_to_asset_ratio
FROM financial_indicators
```

### 2. 数据库信息
- **数据库文件**: `data/a_share.db`
- **财务数据表**: `financial_indicators`
- **数据量**: 337,184 条记录
- **字段**:
  - `pe_ratio`: 市盈率
  - `pb_ratio`: 市净率
  - `roe`: 净资产收益率
  - `debt_to_asset_ratio`: 资产负债率

### 3. 测试结果

测试股票 sz.301042（安联锐视）：
```json
{
  "key_metrics": {
    "pe_ratio": 0.0,
    "pb_ratio": 0.0,
    "roe": 19.62,
    "debt_ratio": 10.94
  }
}
```

说明：
- ✅ ROE: 19.62% (有数据)
- ✅ 负债率: 10.94% (有数据)
- ⚠️ PE: 0.0 (该股票PE数据缺失)
- ⚠️ PB: 0.0 (该股票PB数据缺失)

## 修复时间
- **初次修复**: 2026-01-02 20:36
- **百分比修复**: 2026-01-02 20:38
- **最终验证**: 2026-01-02 20:40

## 修复的问题

### 问题1: 数据库字段名错误
- **错误**: 使用 `debt_ratio` 字段
- **正确**: 使用 `debt_to_asset_ratio` 字段
- **修复**: 已更新SQL查询

### 问题2: 百分比显示错误
- **错误**: 数据库存储19.62表示19.62%，但前端用formatPercentage()再乘100，显示1962%
- **正确**: 直接显示数据库值加%符号
- **修复**: 前端改用 `${value.toFixed(2)}%`

### 问题3: 评分算法阈值错误
- **错误**: 使用0.15和0.5作为阈值（小数格式）
- **正确**: 使用15和50作为阈值（百分比格式）
- **修复**: 已更新所有阈值

## 后端状态
- **进程ID**: 23
- **端口**: 5001
- **状态**: ✅ 运行中并正常响应请求

## 使用方法

1. 刷新页面：http://localhost:3000
2. 点击任意股票进入详情页
3. 查看"📊 关键指标"卡片
4. 现在应该能看到真实的财务数据

## 注意事项

### 数据完整性
不是所有股票都有完整的财务数据：
- 新上市股票可能缺少历史财务数据
- 某些指标可能为0或null
- 这是正常现象，反映了真实的数据情况

### 数据更新
财务数据来自 `financial_indicators` 表：
- 数据按 `report_date` 排序
- API自动获取最新一期数据
- 如需更新数据，使用 `tools/fetch_financial_data.py`

## 相关文件

- `src/web/routes/picker.py` - API路由（已修复）
- `src/data/database.py` - 数据库定义
- `data/a_share.db` - 数据库文件
- `tools/fetch_financial_data.py` - 财务数据下载工具

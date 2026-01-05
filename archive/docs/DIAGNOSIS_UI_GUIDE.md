# 个股诊断系统 UI 使用指南

## 🎉 系统已启动！

### 访问地址
- **前端界面**: http://localhost:3000/diagnosis
- **后端 API**: http://localhost:5001/api/diagnosis

### 快速开始

1. **打开浏览器**，访问: http://localhost:3000/diagnosis

2. **搜索股票**
   - 在搜索框输入股票代码（如：000060）或股票名称（如：中金岭南）
   - 系统会自动显示匹配的股票列表

3. **查看诊断报告**
   - 点击搜索结果中的任意股票
   - 系统会自动生成完整的诊断报告

## 📊 诊断报告包含的信息

### 1. 基本信息
- 股票名称和代码
- 当前价格
- 涨跌幅

### 2. 综合评分（0-100分）
- 整体评价分数
- 分数越高表示股票表现越好

### 3. 各维度评分
- **📈 技术面评分**：均线、成交量、MACD、RSI 等技术指标
- **💰 流动性评分**：日均成交额、换手率、稳定性
- **🌍 市场环境评分**：大盘状态、板块表现

### 4. 信号灯评价
- 🟢 **绿灯**：可以关注（评分 ≥ 70）
- 🟡 **黄灯**：建议观望（评分 40-70）
- 🔴 **红灯**：建议回避（评分 < 40）

### 5. 风险管理指南
- 建议止损价格和比例
- 建议止盈价格和比例
- 盈亏比
- 风险等级（LOW/MEDIUM/HIGH/EXTREME）
- 波动率
- 风险警告（如有）

### 6. 诊断意见（大白话）
- 用通俗易懂的语言解释技术指标
- 避免使用 MA5、MA20、MACD 等专业术语
- 给出客观的操作建议

### 7. 免责声明
- 数据来源说明
- 数据覆盖范围
- 数据更新时间

## 🔍 示例股票

您可以尝试诊断以下股票：

1. **铜陵有色（000630）**
   - 综合评分：95.0 分
   - 信号灯：🟢 绿灯
   - 技术面强势，流动性优秀

2. **中金岭南（000060）**
   - 综合评分：83.0 分
   - 信号灯：🟢 绿灯
   - RSI 超买，注意短期回调

3. **安凯微（688620）**
   - 综合评分：69.0 分
   - 信号灯：🟡 黄灯
   - 横盘整理，建议观望

## 🛠️ 技术说明

### 后端服务
- **端口**: 5001
- **框架**: Flask
- **数据库**: SQLite (data/a_share.db)

### 前端服务
- **端口**: 3000
- **框架**: React + TypeScript
- **样式**: 自定义 CSS

### API 接口

#### 1. 搜索股票
```bash
GET /api/diagnosis/search?q=关键词
```

**示例**:
```bash
curl "http://localhost:5001/api/diagnosis/search?q=中金"
```

**响应**:
```json
{
  "stocks": [
    {
      "code": "000060",
      "name": "中金岭南",
      "market": "sz"
    }
  ]
}
```

#### 2. 诊断股票
```bash
GET /api/diagnosis/:code
```

**示例**:
```bash
curl "http://localhost:5001/api/diagnosis/000060"
```

**响应**:
```json
{
  "code": "sz.000060",
  "name": "sz.000060",
  "current_price": 5.85,
  "change_pct": 0.0,
  "overall_score": 83.0,
  "technical_score": {
    "value": 80.0,
    "reasons": ["均线呈多头排列，趋势向上", "..."]
  },
  "liquidity_score": {
    "value": 100.0,
    "reasons": ["日均成交额 7.7 亿，流动性优秀", "..."]
  },
  "market_score": {
    "value": 75.0,
    "reasons": ["大盘站上 20 日均线，市场环境良好"]
  },
  "signal_light": {
    "color": "GREEN",
    "label": "可以关注",
    "confidence": 83.0,
    "reason": "技术形态良好，流动性充足，市场环境支持，可以考虑关注"
  },
  "risk_info": {
    "current_price": 5.85,
    "stop_loss_price": 5.38,
    "stop_loss_pct": -0.08,
    "take_profit_price": 6.73,
    "take_profit_pct": 0.15,
    "risk_reward_ratio": 1.88,
    "volatility": 0.341,
    "risk_level": "MEDIUM",
    "warnings": []
  },
  "diagnosis_text": "从客观数据看，sz.000060目前表现不错...",
  "disclaimer": "本诊断仅供参考，不构成投资建议。投资者据此操作，风险自担。",
  "data_source": "同花顺 API",
  "data_coverage": "最近 90 天 K 线数据",
  "data_update_time": "2025-12-31"
}
```

## 🎨 UI 特点

### 1. 响应式设计
- 支持桌面端和移动端
- 自适应不同屏幕尺寸

### 2. 实时搜索
- 输入 2 个字符即开始搜索
- 自动显示匹配结果

### 3. 加载状态
- 搜索时显示"搜索中..."
- 诊断时显示加载动画

### 4. 错误处理
- 友好的错误提示
- 自动重试机制

### 5. 视觉反馈
- 信号灯颜色编码
- 涨跌幅颜色区分（红涨绿跌）
- 风险等级颜色标识

## 📝 注意事项

1. **数据更新**
   - 系统使用的是历史数据
   - 数据更新时间显示在报告底部

2. **诊断缓存**
   - 诊断结果会缓存 5 分钟
   - 避免重复计算，提升性能

3. **股票代码格式**
   - 支持多种格式：000060、sh.600000、SH.600000
   - 系统会自动标准化

4. **免责声明**
   - 本系统仅供参考，不构成投资建议
   - 投资有风险，决策需谨慎

## 🚀 下一步计划

根据 `.kiro/specs/stock-diagnosis/tasks.md`，后续可以实现：

- [ ] 多股票对比功能
- [ ] 诊断历史记录
- [ ] 分享功能（生成图片卡片）
- [ ] 移动端优化
- [ ] 性能优化和缓存

## 🐛 问题反馈

如果遇到问题，请检查：

1. **后端服务是否运行**
   ```bash
   curl http://localhost:5001/
   ```

2. **前端服务是否运行**
   ```bash
   curl http://localhost:3000/
   ```

3. **数据库是否存在**
   ```bash
   ls -lh data/a_share.db
   ```

## 📚 相关文档

- 需求文档: `.kiro/specs/stock-diagnosis/requirements.md`
- 设计文档: `.kiro/specs/stock-diagnosis/design.md`
- 任务列表: `.kiro/specs/stock-diagnosis/tasks.md`
- 实现总结: `STOCK_DIAGNOSIS_IMPLEMENTATION.md`

---

**祝您使用愉快！** 🎉

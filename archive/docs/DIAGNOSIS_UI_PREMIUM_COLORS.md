# 个股诊断页面 - Premium 配色方案

## 🎨 Chief UI Designer 确认的配色标准

### 核心原则
1. **深航海蓝背景** - `#0d1117`
2. **玻璃拟态效果** - `rgba(255, 255, 255, 0.05)` + `backdrop-filter: blur(10px)`
3. **半透明边框** - `rgba(255, 255, 255, 0.1)`
4. **深色叠加层** - `rgba(0, 0, 0, 0.2)` ~ `rgba(0, 0, 0, 0.4)`
5. **文字颜色** - `rgba(255, 255, 255, 0.95)` (主要) / `rgba(255, 255, 255, 0.6)` (次要)

---

## 📋 各部分配色详解

### 1. 页面背景
```css
body {
  background: #0d1117;  /* 深航海蓝 */
}
```

### 2. 搜索框
```css
.search-input {
  background: rgba(255, 255, 255, 0.05);  /* 半透明白 */
  border: 2px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
}

.search-input:focus {
  border-color: rgba(59, 130, 246, 0.5);  /* 蓝色高亮 */
  background: rgba(255, 255, 255, 0.08);
}
```

### 3. 报告卡片（所有 section）
```css
.report-section {
  background: rgba(255, 255, 255, 0.05);  /* 玻璃拟态 */
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.report-section:hover {
  background: rgba(255, 255, 255, 0.08);  /* 悬停加深 */
  border-color: rgba(255, 255, 255, 0.2);
}
```

### 4. 基本信息卡片
```css
.info-item {
  background: rgba(0, 0, 0, 0.2);  /* 深色叠加 */
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.info-item:hover {
  background: rgba(0, 0, 0, 0.3);  /* 悬停更深 */
  border-color: rgba(59, 130, 246, 0.3);  /* 蓝色边框 */
}
```

### 5. 各维度评分卡片
```css
.dimension-card {
  background: rgba(0, 0, 0, 0.3);  /* 深色背景 */
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dimension-card:hover {
  background: rgba(0, 0, 0, 0.4);  /* 悬停更深 */
  border-color: rgba(59, 130, 246, 0.3);
}
```

### 6. 信号灯显示
```css
.signal-display {
  background: rgba(0, 0, 0, 0.3);  /* 深色背景 */
  border: 2px solid;  /* 边框颜色由信号灯决定 */
}

.signal-display:hover {
  background: rgba(0, 0, 0, 0.4);
}
```

### 7. 风险管理卡片
```css
.risk-item {
  background: rgba(0, 0, 0, 0.3);  /* 深色背景 */
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.risk-warnings {
  background: rgba(239, 68, 68, 0.1);  /* 红色半透明 */
  border: 2px solid rgba(239, 68, 68, 0.3);
}
```

### 8. 诊断意见
```css
.diagnosis-text p {
  background: rgba(0, 0, 0, 0.2);  /* 深色背景 */
  border-left: 3px solid #3b82f6;  /* 蓝色左边框 */
  color: rgba(255, 255, 255, 0.8);
}
```

### 9. 免责声明（低调风格）
```css
.disclaimer {
  background: rgba(0, 0, 0, 0.2) !important;  /* 更深的背景 */
  border: 1px solid rgba(255, 255, 255, 0.05) !important;  /* 几乎不可见的边框 */
}

.disclaimer:hover {
  background: rgba(0, 0, 0, 0.3) !important;  /* 悬停才变明显 */
  border-color: rgba(255, 255, 255, 0.1) !important;
}

.disclaimer p {
  color: rgba(255, 255, 255, 0.5);  /* 低调的灰色文字 */
}
```

---

## 🌈 特殊颜色使用

### 中国股市配色（重要！）
```css
/* 红色 = 上涨 */
.price-up, .info-value.positive {
  color: #ef4444;
  text-shadow: 0 0 15px rgba(239, 68, 68, 0.5);
}

/* 绿色 = 下跌 */
.price-down, .info-value.negative {
  color: #10b981;
  text-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
}
```

### 信号灯颜色
```css
/* 绿灯 - 建议买入 */
GREEN: #10b981

/* 黄灯 - 观望 */
YELLOW: #f59e0b

/* 红灯 - 建议卖出 */
RED: #ef4444
```

### 风险等级颜色
```css
.risk-level-low {
  color: #10b981;  /* 绿色 - 低风险 */
}

.risk-level-medium {
  color: #f59e0b;  /* 黄色 - 中等风险 */
}

.risk-level-high {
  color: #ef4444;  /* 红色 - 高风险 */
}

.risk-level-extreme {
  color: #dc2626;  /* 深红色 - 极高风险 */
  animation: blink-warning 1s ease-in-out infinite;
}
```

### 渐变色使用
```css
/* 综合评分 */
.score-number {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* 维度评分 */
.dimension-score {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

---

## ✨ 视觉效果增强

### 1. 文字发光效果
```css
text-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
```

### 2. 盒子阴影
```css
/* 普通卡片 */
box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);

/* 悬停卡片 */
box-shadow: 0 12px 40px rgba(31, 38, 135, 0.45);

/* 深色卡片 */
box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
```

### 3. 内部高光
```css
inset 0 1px 0 rgba(255, 255, 255, 0.1);
```

### 4. 玻璃拟态核心
```css
backdrop-filter: blur(10px) saturate(180%);
-webkit-backdrop-filter: blur(10px) saturate(180%);
```

---

## 🚫 禁止使用的颜色

### ❌ 不要使用白色背景
```css
/* 错误 */
background: white;
background: #ffffff;
background: #f9fafb;

/* 正确 */
background: rgba(255, 255, 255, 0.05);
background: rgba(0, 0, 0, 0.2);
```

### ❌ 不要使用纯黑文字
```css
/* 错误 */
color: #000000;
color: #1f2937;
color: #4b5563;

/* 正确 */
color: rgba(255, 255, 255, 0.95);  /* 主要文字 */
color: rgba(255, 255, 255, 0.7);   /* 次要文字 */
color: rgba(255, 255, 255, 0.5);   /* 辅助文字 */
```

### ❌ 不要使用实色边框
```css
/* 错误 */
border: 1px solid #e5e7eb;
border: 2px solid #d1d5db;

/* 正确 */
border: 1px solid rgba(255, 255, 255, 0.1);
border: 2px solid rgba(59, 130, 246, 0.3);
```

---

## 📱 响应式颜色调整

在移动端，所有颜色保持一致，只调整尺寸和间距：

```css
@media (max-width: 768px) {
  /* 颜色不变，只调整尺寸 */
  .report-section {
    padding: 24px;  /* 减少内边距 */
  }
}
```

---

## 🎯 关键改动总结

### 改动前（错误）
- ❌ 白色背景 `background: white`
- ❌ 浅灰背景 `background: #f9fafb`
- ❌ 黑色文字 `color: #1f2937`
- ❌ 实色边框 `border: 1px solid #e5e7eb`

### 改动后（正确）
- ✅ 玻璃拟态 `background: rgba(255, 255, 255, 0.05)`
- ✅ 深色叠加 `background: rgba(0, 0, 0, 0.2)`
- ✅ 半透明文字 `color: rgba(255, 255, 255, 0.95)`
- ✅ 半透明边框 `border: 1px solid rgba(255, 255, 255, 0.1)`

---

## 🎨 Chief UI Designer 签名

> "这才是 TradingBuddy 该有的样子！深色背景 + 玻璃拟态 + 数据流颗粒，营造出专业量化终端的氛围。免责声明用低调的深色，只有悬停才变明显，不会抢走主要内容的风头。所有卡片都用半透明黑色叠加，保持视觉统一性。完美！"

---

## 📅 更新日期
2026-01-02

## 👤 实现者
Kiro AI Assistant (遵循 Chief UI Designer 的配色标准)

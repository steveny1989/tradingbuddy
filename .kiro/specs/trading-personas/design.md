# Design Document: 股票综合诊断系统

## Overview

本文档描述股票综合诊断系统的设计。该系统整合现有的所有分析模块（技术面、基本面、行业面、资金面），加上大盘对比分析，为每只股票生成一个统一的、易懂的综合诊断报告。

就像医生看病一样，从多个维度检查股票的"健康状况"，给出明确的评级和投资建议。

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend / API Client                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    REST API Layer                            │
│  /api/diagnosis/{code}                                       │
│  /api/diagnosis/batch                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Stock Diagnosis Engine                          │
│  - 协调所有分析维度                                            │
│  - 生成综合评分                                                │
│  - 缓存层                                                      │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬──────────────┐
         ▼               ▼               ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Technical    │ │ Fundamental  │ │ Sector       │ │ Capital      │
│ Analyzer     │ │ Analyzer     │ │ Analyzer     │ │ Analyzer     │
│ (复用现有)    │ │ (新建)        │ │ (复用现有)    │ │ (复用现有)    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │                │
       └────────────────┼────────────────┴────────────────┘
                        ▼
              ┌──────────────────┐
              │ Market Comparison│
              │ Analyzer (新建)   │
              └──────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│  - daily_data (K线、成交量、大盘指数)                          │
│  - financial_indicators (PE, ROE, ROA等)                     │
│  - industry_data (行业归属)                                   │
│  - capital_flow, northbound_capital (资金流向)                │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
用户请求 → API → Diagnosis Engine → 检查缓存
                                    │
                                    ├─ 缓存命中 → 返回结果
                                    │
                                    └─ 缓存未命中 → 并行调用5个分析器
                                                  │
                                                  ├─ Technical Analyzer
                                                  ├─ Fundamental Analyzer
                                                  ├─ Sector Analyzer
                                                  ├─ Capital Analyzer
                                                  └─ Market Comparison
                                                        │
                                                        ▼
                                                  聚合结果
                                                        │
                                                        ▼
                                                  计算综合评分
                                                        │
                                                        ▼
                                                  生成诊断报告
                                                        │
                                                        ▼
                                                  缓存结果
                                                        │
                                                        ▼
                                                  返回给用户
```

---

## Components and Interfaces

### 1. Stock Diagnosis Engine (核心协调器)

**Module**: `src/business/diagnosis/diagnosis_engine.py`

**Purpose**: 协调所有分析维度，生成综合诊断报告

**Interface**:
```python
class StockDiagnosisEngine:
    def __init__(self, db_path: str, cache_ttl: int = 3600)
    
    def diagnose(self, code: str) -> DiagnosisReport:
        """
        对单只股票进行综合诊断
        
        Returns:
            {
                'code': '600519',
                'name': '贵州茅台',
                'overall_score': 85,  # 0-100
                'overall_rating': '优秀',  # 优秀/良好/一般/较差/很差
                'overall_status': 'green',  # green/yellow/red
                'dimensions': {
                    'technical': {...},
                    'fundamental': {...},
                    'sector': {...},
                    'capital': {...},
                    'market_comparison': {...}
                },
                'strengths': ['基本面优秀', '行业领先'],
                'weaknesses': ['短期技术面偏弱'],
                'suggestions': ['建议逢低布局，关注回调机会'],
                'summary': '综合来看，该股基本面优秀...',
                'updated_at': '2026-01-04 10:30:00'
            }
        """
    
    def diagnose_batch(self, codes: List[str]) -> List[DiagnosisReport]:
        """批量诊断（并行处理）"""
    
    def clear_cache(self, code: Optional[str] = None):
        """清除缓存"""
```

**综合评分算法**:
```python
overall_score = (
    technical_score * 0.20 +      # 技术面 20%
    fundamental_score * 0.30 +    # 基本面 30%
    sector_score * 0.15 +         # 行业面 15%
    capital_score * 0.20 +        # 资金面 20%
    market_comparison_score * 0.15  # 大盘对比 15%
)

# 评级映射
if overall_score >= 80: rating = '优秀'
elif overall_score >= 65: rating = '良好'
elif overall_score >= 50: rating = '一般'
elif overall_score >= 35: rating = '较差'
else: rating = '很差'
```

---

### 2. Technical Analyzer (技术面分析器)

**Module**: 复用现有模块
- `src/business/post_market/candlestick_patterns.py`
- `src/business/post_market/portfolio_health.py`

**Purpose**: 分析K线形态、技术指标、趋势

**Interface**:
```python
class TechnicalAnalyzer:
    def __init__(self, db_path: str)
    
    def analyze(self, code: str) -> Dict:
        """
        技术面分析
        
        Returns:
            {
                'score': 75,  # 0-100
                'status': 'yellow',  # green/yellow/red
                'trend': '震荡',  # 上涨/下跌/震荡
                'ma20_position': 'above',  # above/below/near
                'rsi': 55.2,
                'volume_ratio': 1.2,
                'candlestick_pattern': {
                    'name': 'Doji',
                    'description': '...'
                },
                'support_level': 1650.0,
                'resistance_level': 1750.0,
                'message': '短期震荡整理，等待方向选择'
            }
        """
```

**评分逻辑**:
- 趋势向上 + RSI健康 + 成交量放大 = 高分
- K线形态看涨 = 加分
- 突破阻力位 = 加分
- 跌破支撑位 = 减分

---

### 3. Fundamental Analyzer (基本面分析器)

**Module**: `src/business/diagnosis/fundamental_analyzer.py` (新建)

**Purpose**: 分析财务指标、盈利能力、财务健康

**Interface**:
```python
class FundamentalAnalyzer:
    def __init__(self, db_path: str)
    
    def analyze(self, code: str) -> Dict:
        """
        基本面分析
        
        Returns:
            {
                'score': 85,  # 0-100
                'status': 'green',
                'pe': 25.5,
                'pe_percentile': 65,  # 行业内百分位
                'pb': 5.2,
                'roe': 28.5,
                'roa': 15.2,
                'net_profit_margin': 45.3,
                'debt_ratio': 15.2,
                'current_ratio': 2.5,
                'profit_growth_yoy': 15.2,  # 同比增长
                'profit_growth_qoq': 8.5,   # 环比增长
                'message': '基本面优秀，盈利能力强，财务健康'
            }
        """
```

**评分逻辑**:
- ROE > 15% = 高分
- 净利润增长 > 10% = 加分
- PE合理（不过高不过低）= 加分
- 负债率低 = 加分
- 与行业平均对比 = 调整分数

---

### 4. Sector Analyzer (行业面分析器)

**Module**: 复用 `src/business/post_market/sector_analysis.py`

**Purpose**: 分析行业表现、板块联动

**Interface**:
```python
class SectorAnalyzer:
    # 已存在，直接复用
    def generate_sector_report(self, code: str) -> Dict:
        """
        Returns:
            {
                'score': 70,  # 根据行业排名和相对强弱计算
                'status': 'green',
                'industry': '食品饮料',
                'industry_rank': 3,
                'relative_strength': 'strong',
                'correlation': 0.85,
                'message': '所属行业表现强势，个股跑赢行业'
            }
        """
```

**评分逻辑**:
- 行业排名前5 = 高分
- 个股跑赢行业 = 加分
- 板块联动性强 = 加分

---

### 5. Capital Analyzer (资金面分析器)

**Module**: 复用 `src/business/post_market/capital_analysis.py`

**Purpose**: 分析北向资金、主力资金流向

**Interface**:
```python
class CapitalAnalyzer:
    # 已存在，直接复用
    def generate_capital_report(self, code: str) -> Dict:
        """
        Returns:
            {
                'score': 65,  # 根据资金流向计算
                'status': 'yellow',
                'northbound': {...},
                'capital_flow': {...},
                'message': '北向资金持仓稳定；主力资金小幅流出'
            }
        """
```

**评分逻辑**:
- 北向资金增持 = 高分
- 主力资金大幅流入 = 高分
- 资金持续流出 = 低分

---

### 6. Market Comparison Analyzer (大盘对比分析器)

**Module**: `src/business/diagnosis/market_comparison.py` (新建)

**Purpose**: 对比个股与大盘表现

**Interface**:
```python
class MarketComparisonAnalyzer:
    def __init__(self, db_path: str)
    
    def analyze(self, code: str, days: int = 30) -> Dict:
        """
        大盘对比分析
        
        Returns:
            {
                'score': 80,  # 0-100
                'status': 'green',
                'stock_return_30d': 15.5,
                'sh_index_return_30d': 8.2,
                'sz_index_return_30d': 10.1,
                'outperformance_sh': 7.3,  # 跑赢上证
                'outperformance_sz': 5.4,  # 跑赢深证
                'beta': 1.2,  # 相对大盘波动率
                'relative_strength': 'strong',
                'message': '近30日跑赢大盘7.3%，表现强势'
            }
        """
```

**评分逻辑**:
- 跑赢大盘 > 5% = 高分
- 跑赢大盘 0-5% = 中等分
- 跑输大盘 = 低分
- Beta适中（0.8-1.2）= 加分

---

## Data Models

### Diagnosis Report Model

```python
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class DimensionAnalysis:
    """单个维度的分析结果"""
    score: int  # 0-100
    status: str  # green/yellow/red
    message: str
    details: Dict  # 详细数据

@dataclass
class DiagnosisReport:
    """完整的诊断报告"""
    code: str
    name: str
    overall_score: int  # 0-100
    overall_rating: str  # 优秀/良好/一般/较差/很差
    overall_status: str  # green/yellow/red
    
    # 五个维度的分析
    dimensions: Dict[str, DimensionAnalysis]
    
    # 综合判断
    strengths: List[str]  # 优势
    weaknesses: List[str]  # 劣势
    suggestions: List[str]  # 投资建议
    summary: str  # 综合总结
    
    updated_at: str
```

---

## Error Handling

### Error Categories

1. **数据缺失错误**:
   - 股票代码不存在
   - 某个维度数据不可用
   - 历史数据不足

2. **计算错误**:
   - 除零错误
   - 数据异常值

3. **系统错误**:
   - 数据库连接失败
   - 缓存错误

### Graceful Degradation

- 如果某个维度分析失败，其他维度继续
- 缺失维度的权重重新分配给其他维度
- 在报告中明确标注哪些维度不可用
- 提供降级的评分和建议

**示例**:
```python
# 如果资金面数据缺失
overall_score = (
    technical_score * 0.25 +      # 20% → 25%
    fundamental_score * 0.35 +    # 30% → 35%
    sector_score * 0.20 +         # 15% → 20%
    market_comparison_score * 0.20  # 15% → 20%
)
# 资金面 20% 被分配给其他维度
```

---

## API Specification

### Endpoint 1: Get Single Stock Diagnosis

```
GET /api/diagnosis/{code}
```

**Response**:
```json
{
  "code": "600519",
  "name": "贵州茅台",
  "overall_score": 85,
  "overall_rating": "优秀",
  "overall_status": "green",
  "dimensions": {
    "technical": {
      "score": 75,
      "status": "yellow",
      "message": "短期震荡整理，等待方向选择",
      "details": {
        "trend": "震荡",
        "ma20_position": "above",
        "rsi": 55.2,
        "volume_ratio": 1.2
      }
    },
    "fundamental": {
      "score": 90,
      "status": "green",
      "message": "基本面优秀，盈利能力强",
      "details": {
        "pe": 25.5,
        "roe": 28.5,
        "profit_growth_yoy": 15.2
      }
    },
    "sector": {
      "score": 85,
      "status": "green",
      "message": "所属行业表现强势，个股跑赢行业",
      "details": {
        "industry": "食品饮料",
        "industry_rank": 3,
        "relative_strength": "strong"
      }
    },
    "capital": {
      "score": 70,
      "status": "yellow",
      "message": "北向资金持仓稳定；主力资金小幅流出",
      "details": {
        "northbound_change": -0.14,
        "main_inflow": -7.47
      }
    },
    "market_comparison": {
      "score": 80,
      "status": "green",
      "message": "近30日跑赢大盘7.3%，表现强势",
      "details": {
        "stock_return_30d": 15.5,
        "sh_index_return_30d": 8.2,
        "outperformance": 7.3
      }
    }
  },
  "strengths": [
    "基本面优秀，ROE高达28.5%",
    "所属行业表现强势",
    "跑赢大盘，相对强势明显"
  ],
  "weaknesses": [
    "短期技术面震荡，缺乏明确方向",
    "主力资金小幅流出"
  ],
  "suggestions": [
    "建议逢低布局，关注1650元支撑位",
    "中长期持有，基本面支撑强劲",
    "短期可等待技术面明朗后再加仓"
  ],
  "summary": "综合来看，该股基本面优秀，行业地位稳固，长期投资价值显著。短期技术面虽有震荡，但不改变中长期向好趋势。建议投资者逢低布局，耐心持有。",
  "updated_at": "2026-01-04T10:30:00"
}
```

### Endpoint 2: Batch Diagnosis

```
POST /api/diagnosis/batch
Content-Type: application/json

{
  "codes": ["600519", "000858", "600036"]
}
```

**Response**: Array of diagnosis reports

---

## Implementation Notes

### Module Reuse Strategy

**已存在的模块（直接复用）**:
1. `candlestick_patterns.py` - K线形态识别
2. `portfolio_health.py` - 技术指标计算
3. `sector_analysis.py` - 行业面分析
4. `capital_analysis.py` - 资金面分析

**需要新建的模块**:
1. `diagnosis_engine.py` - 核心协调器
2. `fundamental_analyzer.py` - 基本面分析器
3. `market_comparison.py` - 大盘对比分析器

### Performance Optimizations

1. **并行处理**: 5个分析器并行调用（ThreadPoolExecutor）
2. **缓存策略**: 1小时TTL，LRU淘汰
3. **数据库优化**: 确保索引存在
4. **批量查询**: 减少数据库往返次数

### Code Organization

```
src/business/diagnosis/
├── __init__.py
├── diagnosis_engine.py          # 核心协调器
├── fundamental_analyzer.py      # 基本面分析器（新建）
├── market_comparison.py         # 大盘对比分析器（新建）
└── models.py                    # 数据模型

src/web/routes/
└── diagnosis.py                 # API endpoints

tests/diagnosis/
├── test_diagnosis_engine.py
├── test_fundamental_analyzer.py
├── test_market_comparison.py
└── test_diagnosis_api.py
```

---

## Deployment Considerations

### Database Requirements

- 确保索引存在:
  - `daily_data(code, date)`
  - `financial_indicators(code, report_date)`
  - `industry_data(code)`
  - `capital_flow(code, date)`

### Memory Requirements

- 缓存大小: ~20MB for 1000 stocks
- 峰值内存: ~150MB during batch processing

### Monitoring

**关键指标**:
- API响应时间 (p50, p95, p99)
- 缓存命中率
- 各维度分析失败率
- 数据缺失频率

---

*Design Version: 1.0*  
*Date: 2026-01-04*

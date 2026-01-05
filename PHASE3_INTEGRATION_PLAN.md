# Phase 3: 业务逻辑集成计划

## 目标

将现有业务代码从旧的 `StockDatabase` 迁移到新的三层数据架构。

---

## 迁移策略

### 原则

1. **渐进式迁移**: 逐模块迁移，不影响现有功能
2. **向后兼容**: 保留旧接口，逐步废弃
3. **充分测试**: 每个模块迁移后都要测试
4. **性能优先**: 利用 Aggregated Layer 提升性能

### 方法

**方案 A: 创建适配器层（推荐）**
- 创建 `DatabaseAdapter` 类，包装新数据层
- 提供与 `StockDatabase` 相同的接口
- 业务代码无需修改，只需替换导入
- 优点: 快速、安全、可回退
- 缺点: 多一层抽象

**方案 B: 直接替换**
- 直接修改业务代码使用新数据层
- 优点: 代码更清晰
- 缺点: 工作量大、风险高

**选择**: 方案 A（适配器层）

---

## 实施步骤

### Step 1: 创建适配器层 ✅ 当前步骤

创建 `src/data/database_adapter.py`，提供与 `StockDatabase` 兼容的接口：

```python
class DatabaseAdapter:
    """数据库适配器 - 兼容旧的 StockDatabase 接口"""
    
    def __init__(self):
        self.cleaned = CleanedLayer()
        self.aggregated = AggregatedLayer()
    
    def get_daily_data(self, code, start_date=None, end_date=None):
        """获取日线数据（兼容旧接口）"""
        return self.cleaned.get_daily_data(
            code, 
            start_date=start_date,
            end_date=end_date,
            only_valid=True
        )
    
    def get_all_stock_codes(self):
        """获取所有股票代码"""
        return self.cleaned.get_all_stock_codes()
    
    # ... 更多兼容方法
```

### Step 2: 更新核心模块

#### 2.1 数据获取模块
- **文件**: `src/data/fetcher.py`
- **任务**: 新数据写入 Raw Layer
- **优先级**: P0（最高）

#### 2.2 诊断系统
- **文件**: `src/business/diagnosis/`
  - `diagnosis_engine.py`
  - `technical_analyzer.py`
  - `fundamental_analyzer.py`
  - `market_comparison.py`
- **任务**: 使用适配器层读取数据
- **优先级**: P1

#### 2.3 策略系统
- **文件**: `src/business/strategies/`
  - `volume_shrink.py`
  - `ma_crossover.py`
  - `reverse_value.py`
- **任务**: 使用 Aggregated Layer 的预计算指标
- **优先级**: P1

#### 2.4 Web API
- **文件**: `src/web/routes/`
  - `stocks.py`
  - `diagnosis.py`
  - `strategies.py`
  - `dashboard.py`
  - `indices.py`
- **任务**: 使用适配器层，优化缓存
- **优先级**: P2

#### 2.5 后市分析
- **文件**: `src/business/post_market/`
  - `portfolio_health.py`
  - `candlestick_patterns.py`
  - `capital_analysis.py`
  - `sector_analysis.py`
- **任务**: 使用适配器层
- **优先级**: P2

### Step 3: 更新工具脚本

- **文件**: `tools/` 下的各种工具
- **任务**: 使用适配器层
- **优先级**: P3

### Step 4: 更新测试和示例

- **文件**: `tests/`, `examples/`
- **任务**: 使用适配器层
- **优先级**: P3

### Step 5: 性能优化

- 批量预计算技术指标
- 优化缓存策略
- 并行处理

### Step 6: 废弃旧代码

- 标记 `StockDatabase` 为 deprecated
- 更新文档
- 清理冗余代码

---

## 适配器接口设计

### 核心方法

```python
class DatabaseAdapter:
    """数据库适配器"""
    
    # 日线数据
    def get_daily_data(self, code, start_date=None, end_date=None)
    def get_latest_data(self, code, days=1)
    def get_all_stock_codes(self)
    
    # 技术指标（使用 Aggregated Layer）
    def get_indicators(self, code, start_date=None, end_date=None)
    def calculate_ma(self, code, periods=[5, 10, 20, 50, 200])
    def calculate_rsi(self, code, period=14)
    def calculate_macd(self, code)
    
    # 财务数据
    def get_financial_data(self, code)
    def get_latest_financial(self, code)
    
    # 市场数据
    def get_capital_flow(self, code, start_date=None, end_date=None)
    def get_north_flow(self, date=None)
    
    # 统计信息
    def get_stats(self)
    def get_data_range(self, code)
```

---

## 测试计划

### 单元测试

每个适配器方法都要有单元测试：

```python
def test_get_daily_data():
    adapter = DatabaseAdapter()
    df = adapter.get_daily_data('600519')
    assert df is not None
    assert not df.empty
    assert 'close' in df.columns
```

### 集成测试

测试业务模块使用适配器：

```python
def test_diagnosis_with_adapter():
    # 使用适配器的诊断系统
    engine = DiagnosisEngine()
    result = engine.diagnose('600519')
    assert result is not None
```

### 性能测试

对比新旧架构的性能：

```python
def test_performance():
    # 旧架构
    old_time = benchmark_old_database()
    
    # 新架构
    new_time = benchmark_new_adapter()
    
    # 新架构应该更快
    assert new_time < old_time
```

---

## 风险和应对

### 风险 1: 接口不兼容

**应对**: 
- 仔细分析 `StockDatabase` 的所有方法
- 确保适配器完全兼容
- 充分测试

### 风险 2: 性能下降

**应对**:
- 使用 Aggregated Layer 预计算
- 优化查询逻辑
- 性能测试验证

### 风险 3: 数据不一致

**应对**:
- 对比新旧数据
- 抽样验证
- 监控数据质量

### 风险 4: 业务逻辑错误

**应对**:
- 充分的单元测试
- 集成测试
- 回归测试

---

## 时间估算

| 步骤 | 工作量 | 预计时间 |
|------|--------|----------|
| Step 1: 适配器层 | 中 | 2-3小时 |
| Step 2: 核心模块 | 大 | 4-6小时 |
| Step 3: 工具脚本 | 小 | 1-2小时 |
| Step 4: 测试示例 | 小 | 1-2小时 |
| Step 5: 性能优化 | 中 | 2-3小时 |
| Step 6: 清理文档 | 小 | 1小时 |
| **总计** | - | **11-17小时** |

---

## 成功标准

### 功能完整性

- ✅ 所有业务功能正常工作
- ✅ 所有测试通过
- ✅ 无数据丢失

### 性能提升

- ✅ 查询速度提升 40%+
- ✅ 指标计算速度提升 75%+
- ✅ 批量操作速度提升 75%+

### 代码质量

- ✅ 代码清晰易懂
- ✅ 充分的测试覆盖
- ✅ 完善的文档

---

## 下一步

**立即开始 Step 1**: 创建适配器层

```bash
# 创建适配器
touch src/data/database_adapter.py

# 创建测试
touch tests/data/test_database_adapter.py
```

---

**文档版本**: 1.0  
**创建时间**: 2026-01-05  
**状态**: 📋 计划中

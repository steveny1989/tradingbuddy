# 数据层架构 - 快速开始

## 5分钟快速上手

### 1. 运行测试（验证安装）

```bash
python3 tools/test_data_layers.py
```

预期输出：
```
✅ 所有测试完成！
有效率: 92.3%
```

### 2. 基本使用

#### 保存数据到Raw Layer

```python
from src.data.layers import RawLayer
import pandas as pd

# 创建Raw Layer实例
raw = RawLayer()

# 准备数据（从API获取或模拟）
df = pd.DataFrame({
    'code': ['600519'],
    'date': ['2026-01-05'],
    'open': [1400],
    'high': [1420],
    'low': [1390],
    'close': [1410],
    'volume': [1000000],
    'amount': [1.4e9]
})

# 保存
count = raw.save_daily_data(df, source='akshare')
print(f"保存了 {count} 条数据")
```

#### 清洗数据到Cleaned Layer

```python
from src.data.layers import CleanedLayer

# 创建Cleaned Layer实例
cleaned = CleanedLayer()

# 清洗并保存
stats = cleaned.clean_and_save_daily_data(df, source='akshare')

print(f"总数: {stats['total']}")
print(f"有效: {stats['valid']}")
print(f"无效: {stats['invalid']}")
print(f"有效率: {stats['valid_rate']*100:.1f}%")
```

#### 读取清洗后的数据

```python
# 读取有效数据
df_valid = cleaned.get_daily_data('600519', only_valid=True)

# 读取所有数据
df_all = cleaned.get_daily_data('600519', only_valid=False)

# 指定日期范围
df_range = cleaned.get_daily_data(
    '600519',
    start_date='2025-01-01',
    end_date='2026-01-05',
    only_valid=True
)
```

### 3. 数据验证

#### 手动验证单条数据

```python
from src.data.layers import DailyDataValidator
import pandas as pd

# 准备数据
row = pd.Series({
    'open': 100,
    'high': 105,
    'low': 98,
    'close': 103,
    'volume': 1000000
})

# 验证
result = DailyDataValidator.validate_row(row)

if result.is_valid:
    print("✅ 数据有效")
else:
    print(f"❌ 数据无效: {result.errors}")

if result.warnings:
    print(f"⚠️  警告: {result.warnings}")
```

#### 验证整个DataFrame

```python
# 验证整个数据框
stats = DailyDataValidator.validate_dataframe(df)

print(f"总记录: {stats['total']}")
print(f"有效: {stats['valid']}")
print(f"无效: {stats['invalid']}")
print(f"有效率: {stats['valid_rate']*100:.1f}%")

# 查看错误类型
for error_type, count in stats['error_types'].items():
    print(f"  {error_type}: {count}")
```

### 4. 查看统计信息

```python
# Raw Layer统计
raw_stats = raw.get_stats()
print("Raw Layer:")
print(f"  日线数据: {raw_stats['daily']['total_records']} 条")
print(f"  股票数量: {raw_stats['daily']['total_stocks']} 只")

# Cleaned Layer统计
cleaned_stats = cleaned.get_stats()
print("\nCleaned Layer:")
print(f"  总记录: {cleaned_stats['daily']['total_records']}")
print(f"  有效记录: {cleaned_stats['daily']['valid_records']}")
print(f"  有效率: {cleaned_stats['daily']['valid_rate']*100:.1f}%")
print(f"  停牌记录: {cleaned_stats['daily']['suspended_records']}")
```

### 5. 数据恢复

```python
# 场景：Cleaned Layer数据损坏，需要从Raw Layer恢复

# 1. 从Raw Layer读取原始数据
raw_df = raw.get_daily_data('600519')

# 2. 重新清洗
if raw_df is not None:
    stats = cleaned.clean_and_save_daily_data(raw_df, source='recovery')
    print(f"✅ 恢复完成: {stats['valid']}/{stats['total']} 条有效数据")
```

## 常见问题

### Q1: 数据保存失败怎么办？

检查数据格式：
```python
# 必需字段
required_fields = ['code', 'date', 'open', 'high', 'low', 'close', 'volume']

# 检查
for field in required_fields:
    if field not in df.columns:
        print(f"❌ 缺少字段: {field}")
```

### Q2: 如何处理异常数据？

```python
# 读取所有数据（包括无效数据）
df_all = cleaned.get_daily_data('600519', only_valid=False)

# 查看无效数据
invalid_df = df_all[df_all['is_valid'] == 0]

for _, row in invalid_df.iterrows():
    print(f"日期: {row['date']}")
    print(f"错误: {row['validation_errors']}")
    print(f"警告: {row['validation_warnings']}")
```

### Q3: 如何批量处理多只股票？

```python
codes = ['600519', '000858', '600036']

for code in codes:
    # 获取数据（从API或其他来源）
    df = get_stock_data(code)  # 你的数据获取函数
    
    # 保存到Raw Layer
    raw.save_daily_data(df, source='akshare')
    
    # 清洗到Cleaned Layer
    stats = cleaned.clean_and_save_daily_data(df, source='akshare')
    
    print(f"{code}: {stats['valid']}/{stats['total']} 有效")
```

### Q4: 数据存储在哪里？

```
data/
├── raw/                    # 原始数据
│   ├── daily_raw.db       # 日线原始数据
│   ├── financial_raw.db   # 财务原始数据
│   └── market_raw.db      # 市场数据
└── cleaned/               # 清洗数据
    ├── daily_cleaned.db   # 日线清洗数据
    └── financial_cleaned.db  # 财务清洗数据
```

### Q5: 如何清空测试数据？

```bash
# 删除数据库文件
rm -rf data/raw/
rm -rf data/cleaned/

# 重新初始化
python3 -c "from src.data.layers import RawLayer, CleanedLayer; RawLayer(); CleanedLayer()"
```

## 完整示例

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的数据处理流程示例
"""
from src.data.layers import RawLayer, CleanedLayer
import pandas as pd
from datetime import datetime, timedelta

def main():
    # 1. 初始化
    raw = RawLayer()
    cleaned = CleanedLayer()
    
    # 2. 模拟从API获取数据
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') 
             for i in range(10, 0, -1)]
    
    df = pd.DataFrame({
        'code': ['600519'] * 10,
        'date': dates,
        'open': [1400 + i*10 for i in range(10)],
        'high': [1420 + i*10 for i in range(10)],
        'low': [1390 + i*10 for i in range(10)],
        'close': [1410 + i*10 for i in range(10)],
        'volume': [1000000 + i*100000 for i in range(10)],
        'amount': [1.4e9 + i*1e8 for i in range(10)],
    })
    
    # 3. 保存到Raw Layer
    print("保存原始数据...")
    count = raw.save_daily_data(df, source='example')
    print(f"✓ 保存了 {count} 条原始数据")
    
    # 4. 清洗到Cleaned Layer
    print("\n清洗数据...")
    stats = cleaned.clean_and_save_daily_data(df, source='example')
    print(f"✓ 清洗完成:")
    print(f"  总数: {stats['total']}")
    print(f"  有效: {stats['valid']}")
    print(f"  有效率: {stats['valid_rate']*100:.1f}%")
    
    # 5. 读取清洗后的数据
    print("\n读取数据...")
    df_cleaned = cleaned.get_daily_data('600519', only_valid=True)
    print(f"✓ 读取到 {len(df_cleaned)} 条有效数据")
    print(f"  日期范围: {df_cleaned['date'].min()} ~ {df_cleaned['date'].max()}")
    
    # 6. 统计信息
    print("\n统计信息:")
    raw_stats = raw.get_stats()
    cleaned_stats = cleaned.get_stats()
    
    print(f"Raw Layer: {raw_stats['daily']['total_records']} 条")
    print(f"Cleaned Layer: {cleaned_stats['daily']['valid_records']} 条有效")
    
    print("\n✅ 完成！")

if __name__ == "__main__":
    main()
```

## 下一步

- 阅读 [完整架构文档](DATA_LAYER_ARCHITECTURE.md)
- 查看 [实施总结](DATA_LAYER_IMPLEMENTATION_SUMMARY.md)
- 运行测试工具: `python3 tools/test_data_layers.py`

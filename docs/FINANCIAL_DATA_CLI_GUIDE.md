# 财务数据下载工具使用指南

## 快速开始

### 1. 下载单只股票财务数据
```bash
python tools/fetch_financial_data.py --code 600000
```

输出示例：
```
🚀 开始下载 600000 的财务数据...

✅ 600000 财务数据下载完成！
  - 资产负债表: SUCCESS
  - 利润表: SUCCESS
  - 现金流量表: SUCCESS
  - 财务指标: SUCCESS
```

### 2. 查看数据库统计
```bash
python tools/fetch_financial_data.py --stats
```

输出示例：
```
============================================================
📊 财务数据统计
============================================================

balance_sheet:
  - 股票数量: 150
  - 记录总数: 1200
  - 平均记录数: 8.0

income_statement:
  - 股票数量: 150
  - 记录总数: 1200
  - 平均记录数: 8.0
...
```

### 3. 批量下载（测试模式）
```bash
# 下载前10只股票
python tools/fetch_financial_data.py --batch --max 10
```

输出示例：
```
🚀 开始批量下载财务数据...
⚠️ 测试模式：仅下载前 10 只股票

财务数据下载: 100%|████████████| 10/10 [00:25<00:00, 2.5s/it]

✅ 批量下载完成！
  - 总数: 10
  - 成功: 8
  - 失败: 2
  - 成功率: 80.0%
  - 耗时: 25秒
  - 平均速度: 0.4股票/秒

📋 错误统计:
  - EMPTY_DATA: 2

📄 报告文件: logs/financial_data_report_20260101_120000.json
📄 失败列表: logs/financial_data_failed_20260101_120000.json
```

## 高级功能

### 4. 强制更新模式
默认情况下，7天内已更新的股票会被跳过。使用 `--force` 强制更新所有股票：

```bash
python tools/fetch_financial_data.py --batch --max 10 --force
```

### 5. 断点续传
如果下载中断，可以从指定股票代码继续：

```bash
# 从600519继续下载
python tools/fetch_financial_data.py --batch --resume-from 600519
```

### 6. 从失败列表重试
批量下载后会生成失败列表文件，可以重试失败的股票：

```bash
python tools/fetch_financial_data.py --retry-failed logs/financial_data_failed_20260101_120000.json
```

### 7. 自定义股票列表
只下载指定的股票：

```bash
python tools/fetch_financial_data.py --batch --codes 600000,000001,600519
```

### 8. 组合使用
```bash
# 强制更新指定股票列表
python tools/fetch_financial_data.py --batch --codes 600000,000001 --force

# 从指定位置继续，最多下载50只
python tools/fetch_financial_data.py --batch --resume-from 600519 --max 50
```

## 全市场下载

### 推荐流程

#### 第1步：小规模测试
```bash
# 测试10只股票，验证功能正常
python tools/fetch_financial_data.py --batch --max 10
```

#### 第2步：中等规模测试
```bash
# 测试100只股票，观察失败率和错误类型
python tools/fetch_financial_data.py --batch --max 100
```

#### 第3步：全市场下载
```bash
# 下载全市场（约5792只股票，预计3-5小时）
python tools/fetch_financial_data.py --batch
```

#### 第4步：重试失败股票
```bash
# 从失败列表重试
python tools/fetch_financial_data.py --retry-failed logs/financial_data_failed_YYYYMMDD_HHMMSS.json
```

#### 第5步：查看最终统计
```bash
python tools/fetch_financial_data.py --stats
```

## 输出文件说明

### 报告文件 (JSON格式)
位置: `logs/financial_data_report_YYYYMMDD_HHMMSS.json`

内容示例：
```json
{
  "total": 100,
  "success": 85,
  "failed": 15,
  "success_rate": 85.0,
  "start_time": "2026-01-01 12:00:00",
  "end_time": "2026-01-01 12:05:30",
  "elapsed_seconds": 330,
  "avg_speed": 0.303,
  "error_stats": {
    "EMPTY_DATA": 10,
    "API_ERROR": 3,
    "NETWORK_ERROR": 2
  }
}
```

### 失败列表 (JSON格式)
位置: `logs/financial_data_failed_YYYYMMDD_HHMMSS.json`

内容示例：
```json
{
  "EMPTY_DATA": ["600001", "600002", "600003"],
  "API_ERROR": ["600004", "600005"],
  "NETWORK_ERROR": ["600006"]
}
```

## 错误类型说明

| 错误类型 | 说明 | 是否重试 | 重试次数 |
|---------|------|---------|---------|
| API_ERROR | API返回错误（如JSON解析失败） | 是 | 2次 |
| NETWORK_ERROR | 网络连接错误 | 是 | 3次 |
| EMPTY_DATA | API返回空数据 | 否 | 0次 |
| VALIDATION_ERROR | 数据验证失败 | 否 | 0次 |
| CALCULATION_ERROR | 指标计算失败 | 否 | 0次 |
| UNKNOWN_ERROR | 未知错误 | 否 | 0次 |

## 常见问题

### Q1: 为什么有些股票显示EMPTY_DATA？
A: 可能是以下原因：
- 新上市股票，还没有财务报表
- 退市股票，数据已清除
- ST股票，数据不完整
- API暂时没有该股票数据

这是正常现象，不需要重试。

### Q2: 如何提高成功率？
A: 
1. 使用 `--retry-failed` 重试失败的股票
2. 在网络状况好的时候下载
3. 适当增加限速时间（修改代码中的sleep时间）

### Q3: 下载速度太慢怎么办？
A: 当前限速策略是每10只股票休息2秒，这是为了避免被API封禁。不建议提高速度。

### Q4: 如何定期更新数据？
A: 
```bash
# 每周运行一次，自动跳过7天内已更新的股票
python tools/fetch_financial_data.py --batch

# 或者使用cron定时任务
0 2 * * 0 cd /path/to/project && python tools/fetch_financial_data.py --batch
```

### Q5: 数据库文件太大怎么办？
A: 
1. 定期清理logs目录
2. 使用数据库优化工具压缩
3. 考虑只保留最近几年的数据

## 性能参考

基于实际测试：
- 单只股票耗时: 2-3秒
- 10只股票: ~25秒
- 100只股票: ~4分钟
- 全市场(5792只): 3-5小时

成功率通常在80-90%之间，主要失败原因是EMPTY_DATA（新股、退市股等）。

## 最佳实践

1. **首次下载**: 使用 `--max 10` 测试，确认功能正常
2. **增量更新**: 不使用 `--force`，让系统自动跳过近期已更新的股票
3. **失败重试**: 批量下载后，使用 `--retry-failed` 重试失败的股票
4. **定期维护**: 每周或每月运行一次，保持数据最新
5. **监控日志**: 关注错误统计，了解数据质量
6. **备份数据**: 大规模下载前备份数据库

## 技术支持

如遇问题，请查看：
1. 日志文件: 查看详细错误信息
2. 报告文件: 了解整体下载情况
3. 失败列表: 分析失败原因

或参考其他文档：
- `docs/FINANCIAL_DATA_README.md`: 系统架构说明
- `docs/FINANCIAL_DATA_DESIGN.md`: 设计文档
- `docs/FINANCIAL_DATA_IMPLEMENTATION_SUMMARY.md`: 实现总结

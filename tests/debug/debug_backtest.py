#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试回测引擎"""
import logging
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.business.backtest.engine import BacktestEngine

# 设置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

db = StockDatabase("data/a_share.db")

# 获取交易日列表
start_date = '2024-10-18'
end_date = '2024-10-22'
df_index = db.get_daily_data('sh.000001', start_date=start_date, end_date=end_date)
trade_dates = df_index['date'].tolist()

print("="*80)
print(f"交易日列表 ({start_date} 至 {end_date}):")
print("="*80)
for i, date in enumerate(trade_dates):
    print(f"{i}: {date}")

print(f"\n总共 {len(trade_dates)} 个交易日")
print(f"应该没有: 2024-10-19 (周六), 2024-10-20 (周日)")

# 检查某只股票的数据
code = 'sz.301160'
print(f"\n检查 {code} 的数据:")
for date in ['2024-10-18', '2024-10-19', '2024-10-20', '2024-10-21']:
    df = db.get_daily_data(code, start_date=date, end_date=date)
    if df.empty:
        print(f"{date}: 无数据 (非交易日或停牌)")
    else:
        print(f"{date}: 有数据, 收盘价 {df['close'].iloc[0]:.2f}")

db.close()

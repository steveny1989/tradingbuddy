#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试周末bug"""
import sys
import logging
import pandas as pd

# 强制重新加载模块
if 'strategy.backtest_engine' in sys.modules:
    del sys.modules['strategy.backtest_engine']
if 'strategy.volume_shrink_strategy' in sys.modules:
    del sys.modules['strategy.volume_shrink_strategy']
if 'core.database' in sys.modules:
    del sys.modules['core.database']

from core.database import StockDatabase
from strategy.volume_shrink_strategy import VolumeShrinkStrategy
from strategy.backtest_engine import BacktestEngine

logging.basicConfig(level=logging.INFO, format='%(message)s')

db = StockDatabase('data/a_share.db')
strategy = VolumeShrinkStrategy(db=db)

# 修改scan方法
original_scan = strategy.scan
def custom_scan(date=None, max_stocks=None, **kwargs):
    return original_scan(
        date=date, 
        max_stocks=max_stocks or 100,
        use_volume_stabilize=False, 
        check_market=False, 
        check_liquidity_filter=False, 
        **kwargs
    )
strategy.scan = custom_scan

backtest = BacktestEngine(db=db, strategy=strategy, initial_capital=1000000)

print("="*80)
print("运行回测: 2024-10-14 至 2024-10-25")
print("="*80)

result = backtest.run(
    start_date='2024-10-14', 
    end_date='2024-10-25', 
    hold_days=5, 
    stop_loss=-0.10, 
    take_profit=0.15
)

print("\n" + "="*80)
print("每日净值记录:")
print("="*80)
df = pd.DataFrame(result['daily_values'])
print(df[['date', 'cash', 'position_value', 'total_value', 'position_count']])

print("\n检查日期:")
for date in df['date']:
    dt = pd.to_datetime(date)
    print(f"{date} - {dt.day_name()}")

db.close()

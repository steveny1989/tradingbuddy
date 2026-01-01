#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试交易日列表"""
from src.data.database import StockDatabase
import pandas as pd

db = StockDatabase("data/a_share.db")

# 获取指数数据
start_date = '2024-10-14'
end_date = '2024-10-25'
market_index_code = 'sh.000001'

df_index = db.get_daily_data(market_index_code, start_date=start_date, end_date=end_date)

print(f"指数数据 ({market_index_code}):")
print(df_index[['date', 'close']])

trade_dates = df_index['date'].tolist()
print(f"\n交易日列表 (共{len(trade_dates)}天):")
for i, date in enumerate(trade_dates):
    dt = pd.to_datetime(date)
    print(f"{i}: {date} ({dt.day_name()})")

db.close()

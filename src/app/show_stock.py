#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看单只股票数据"""
import sys
from src.data.database import StockDatabase

def show_stock(code):
    """显示股票数据"""
    db = StockDatabase("data/a_share.db")
    
    # 获取股票信息
    stock_list = db.get_stock_list()
    stock_info = stock_list[stock_list['code'] == code.split('.')[-1]]
    
    if stock_info.empty:
        print(f"❌ 未找到股票: {code}")
        db.close()
        return
    
    stock_name = stock_info.iloc[0]['name']
    full_code = stock_info.iloc[0].get('full_code', code)
    
    print("="*80)
    print(f"📊 {stock_name} ({full_code})")
    print("="*80)
    
    # 获取数据
    df = db.get_daily_data(full_code)
    
    if df.empty:
        print("❌ 该股票暂无数据")
        db.close()
        return
    
    print(f"\n数据条数: {len(df)} 条")
    print(f"日期范围: {df['date'].min()} 至 {df['date'].max()}")
    print(f"数据字段: {', '.join(df.columns.tolist())}")
    
    print("\n最近10天数据:")
    print(df[['date', 'open', 'high', 'low', 'close', 'volume', 'pct_chg']].tail(10).to_string(index=False))
    
    print(f"\n统计信息:")
    print(f"  最高价: {df['high'].max():.2f}")
    print(f"  最低价: {df['low'].min():.2f}")
    print(f"  最新价: {df['close'].iloc[-1]:.2f}")
    print(f"  平均价: {df['close'].mean():.2f}")
    print(f"  平均成交量: {df['volume'].mean():,.0f}")
    
    if len(df) > 1:
        total_return = (df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100
        print(f"  期间涨跌幅: {total_return:.2f}%")
    
    db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        show_stock(sys.argv[1])
    else:
        print("用法: python3 show_stock.py <股票代码>")
        print("示例: python3 show_stock.py 600000")
        print("     python3 show_stock.py sh.600000")

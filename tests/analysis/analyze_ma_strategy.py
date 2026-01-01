#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析均线突破策略的表现"""
import logging
import pandas as pd
from src.data.database import StockDatabase
from src.business.strategies.ma_crossover import MACrossoverStrategy
from src.business.backtest.engine import BacktestEngine

logging.basicConfig(level=logging.WARNING)

def main():
    print("="*80)
    print("均线突破策略详细分析")
    print("="*80)
    
    db = StockDatabase("data/a_share.db")
    
    strategy = MACrossoverStrategy(
        db=db,
        short_window=5,
        long_window=20,
        volume_window=5,
        market_index_code='sh.000001',
        min_avg_turnover=1e8
    )
    
    backtest = BacktestEngine(
        db=db,
        strategy=strategy,
        initial_capital=1000000,
        max_positions=10,
        position_size=0.1
    )
    
    result = backtest.run(
        start_date='2024-10-01',
        end_date='2024-12-31',
        hold_days=10,
        stop_loss=-0.08,
        take_profit=0.15,
        scan_interval=1,
        time_stop_days=5
    )
    
    # 分析交易记录
    trades = result['trades']
    sell_trades = trades[trades['action'] == 'sell'].copy()
    
    print("\n【1. 交易统计】")
    print("-"*80)
    print(f"总交易次数: {len(sell_trades)}")
    print(f"盈利次数: {len(sell_trades[sell_trades['profit'] > 0])}")
    print(f"亏损次数: {len(sell_trades[sell_trades['profit'] <= 0])}")
    print(f"胜率: {len(sell_trades[sell_trades['profit'] > 0]) / len(sell_trades):.2%}")
    
    # 按退出原因分类
    print("\n【2. 退出原因分析】")
    print("-"*80)
    reason_stats = sell_trades.groupby('reason').agg({
        'profit': ['count', 'mean', 'sum'],
        'profit_rate': 'mean'
    }).round(2)
    print(reason_stats)
    
    # 盈亏分布
    print("\n【3. 盈亏分布】")
    print("-"*80)
    print(f"平均盈利: {sell_trades[sell_trades['profit'] > 0]['profit'].mean():.2f}")
    print(f"平均亏损: {sell_trades[sell_trades['profit'] <= 0]['profit'].mean():.2f}")
    print(f"最大盈利: {sell_trades['profit'].max():.2f}")
    print(f"最大亏损: {sell_trades['profit'].min():.2f}")
    print(f"盈亏比: {abs(sell_trades[sell_trades['profit'] > 0]['profit'].mean() / sell_trades[sell_trades['profit'] <= 0]['profit'].mean()):.2f}")
    
    # 持仓天数分析
    print("\n【4. 持仓天数分析】")
    print("-"*80)
    print(f"平均持仓天数: {sell_trades['hold_days'].mean():.1f}")
    print(f"最短持仓: {sell_trades['hold_days'].min():.0f} 天")
    print(f"最长持仓: {sell_trades['hold_days'].max():.0f} 天")
    
    # 按持仓天数分组
    sell_trades['hold_group'] = pd.cut(sell_trades['hold_days'], 
                                       bins=[0, 3, 5, 10, 100],
                                       labels=['1-3天', '4-5天', '6-10天', '>10天'])
    hold_stats = sell_trades.groupby('hold_group').agg({
        'profit': ['count', 'mean'],
        'profit_rate': 'mean'
    }).round(2)
    print("\n按持仓天数分组:")
    print(hold_stats)
    
    # 查看亏损交易
    print("\n【5. 典型亏损交易（前10笔）】")
    print("-"*80)
    loss_trades = sell_trades[sell_trades['profit'] < 0].sort_values('profit')
    cols = ['date', 'code', 'cost_price', 'price', 'profit', 'profit_rate', 'reason', 'hold_days']
    print(loss_trades[cols].head(10))
    
    # 查看盈利交易
    print("\n【6. 典型盈利交易（前10笔）】")
    print("-"*80)
    win_trades = sell_trades[sell_trades['profit'] > 0].sort_values('profit', ascending=False)
    print(win_trades[cols].head(10))
    
    # 市场环境分析
    print("\n【7. 市场环境分析】")
    print("-"*80)
    index_data = db.get_daily_data('sh.000001', start_date='2024-10-01', end_date='2024-12-31')
    if not index_data.empty:
        start_price = index_data.iloc[0]['close']
        end_price = index_data.iloc[-1]['close']
        market_return = (end_price - start_price) / start_price
        print(f"上证指数表现: {market_return:.2%}")
        print(f"起始点位: {start_price:.2f}")
        print(f"结束点位: {end_price:.2f}")
        
        # 计算市场波动
        index_data['return'] = index_data['close'].pct_change()
        volatility = index_data['return'].std() * (252 ** 0.5)
        print(f"市场波动率: {volatility:.2%}")
    
    # 时间分布
    print("\n【8. 交易时间分布】")
    print("-"*80)
    sell_trades['month'] = pd.to_datetime(sell_trades['date']).dt.to_period('M')
    time_stats = sell_trades.groupby('month').agg({
        'profit': ['count', 'sum', 'mean']
    }).round(2)
    print(time_stats)
    
    db.close()
    
    print("\n" + "="*80)
    print("分析完成")
    print("="*80)

if __name__ == "__main__":
    main()

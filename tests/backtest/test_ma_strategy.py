#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试均线突破策略"""
import logging
from src.data.database import StockDatabase
from src.business.strategies.ma_crossover import MACrossoverStrategy
from src.business.backtest.engine import BacktestEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("="*80)
    print("均线突破策略测试 (MA5/MA20)")
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
    
    print("\n【测试1: 扫描最新信号】")
    print("-"*80)
    signals = strategy.scan(
        min_cap=50e8,
        max_cap=200e8,
        check_volume=True,
        check_liquidity_filter=True,
        max_stocks=100
    )
    
    if not signals.empty:
        print(f"\n找到 {len(signals)} 个金叉信号:")
        cols = ['code', 'name', 'date', 'price', 'ma_short', 'ma_long']
        print(signals[cols].head(10))
    else:
        print("未找到符合条件的信号")
    
    print("\n【测试2: 历史回测】")
    print("-"*80)
    
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
    
    print("\n" + "="*80)
    print("回测结果")
    print("="*80)
    print(f"初始资金: {result['initial_capital']:,.0f}")
    print(f"最终资金: {result['final_value']:,.0f}")
    print(f"总收益率: {result['total_return']:.2%}")
    print(f"总交易次数: {result['total_trades']}")
    print(f"胜率: {result['win_rate']:.2%}")
    print(f"最大回撤: {result['max_drawdown']:.2%}")
    
    db.close()
    print("\n测试完成")

if __name__ == "__main__":
    main()

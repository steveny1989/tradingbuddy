#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试优化后的均线策略"""
import logging
from core.database import StockDatabase
from strategy.ma_crossover_strategy import MACrossoverStrategy
from strategy.backtest_engine import BacktestEngine

logging.basicConfig(level=logging.WARNING)

def test_strategy(name, params):
    """测试策略"""
    db = StockDatabase("data/a_share.db")
    
    strategy = MACrossoverStrategy(
        db=db,
        short_window=params['short_window'],
        long_window=params['long_window'],
        volume_window=5,
        market_index_code='sh.000001',
        min_avg_turnover=1e8
    )
    
    backtest = BacktestEngine(
        db=db,
        strategy=strategy,
        initial_capital=1000000,
        max_positions=params['max_positions'],
        position_size=params['position_size']
    )
    
    result = backtest.run(
        start_date='2024-10-01',
        end_date='2024-12-31',
        hold_days=params['hold_days'],
        stop_loss=params['stop_loss'],
        take_profit=params['take_profit'],
        scan_interval=1,
        time_stop_days=params['time_stop_days']
    )
    
    db.close()
    return result

def main():
    print("="*80)
    print("均线策略参数优化测试")
    print("="*80)
    
    # 测试不同参数组合
    strategies = [
        {
            'name': '原始策略 (MA5/20)',
            'params': {
                'short_window': 5,
                'long_window': 20,
                'hold_days': 10,
                'stop_loss': -0.08,
                'take_profit': 0.15,
                'time_stop_days': 5,
                'max_positions': 10,
                'position_size': 0.1
            }
        },
        {
            'name': '优化1: 放宽止损',
            'params': {
                'short_window': 5,
                'long_window': 20,
                'hold_days': 15,
                'stop_loss': -0.12,  # 放宽止损
                'take_profit': 0.20,  # 提高止盈
                'time_stop_days': 8,  # 延长时间止损
                'max_positions': 10,
                'position_size': 0.1
            }
        },
        {
            'name': '优化2: 减少仓位',
            'params': {
                'short_window': 5,
                'long_window': 20,
                'hold_days': 10,
                'stop_loss': -0.08,
                'take_profit': 0.15,
                'time_stop_days': 5,
                'max_positions': 5,  # 减少持仓数
                'position_size': 0.15  # 增加单笔仓位
            }
        },
        {
            'name': '优化3: 长周期均线',
            'params': {
                'short_window': 10,  # 10日均线
                'long_window': 30,   # 30日均线
                'hold_days': 15,
                'stop_loss': -0.10,
                'take_profit': 0.20,
                'time_stop_days': 8,
                'max_positions': 10,
                'position_size': 0.1
            }
        }
    ]
    
    results = []
    for strat in strategies:
        print(f"\n测试: {strat['name']}")
        print("-"*80)
        result = test_strategy(strat['name'], strat['params'])
        results.append({
            'name': strat['name'],
            'return': result['total_return'],
            'trades': result['completed_trades'],
            'win_rate': result['win_rate'],
            'max_dd': result['max_drawdown'],
            'avg_profit': result['avg_profit']
        })
        print(f"收益率: {result['total_return']:.2%}")
        print(f"交易次数: {result['completed_trades']}")
        print(f"胜率: {result['win_rate']:.2%}")
        print(f"最大回撤: {result['max_drawdown']:.2%}")
    
    # 对比结果
    print("\n" + "="*80)
    print("策略对比")
    print("="*80)
    print(f"{'策略':<25} {'收益率':>10} {'交易次数':>10} {'胜率':>10} {'最大回撤':>10}")
    print("-"*80)
    for r in results:
        print(f"{r['name']:<25} {r['return']:>9.2%} {r['trades']:>10} {r['win_rate']:>9.2%} {r['max_dd']:>9.2%}")
    
    print("\n结论:")
    best = max(results, key=lambda x: x['return'])
    print(f"最佳策略: {best['name']} (收益率 {best['return']:.2%})")

if __name__ == "__main__":
    main()

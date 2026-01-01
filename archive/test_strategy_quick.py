#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试：对比激进版 vs 稳健版策略"""
import logging
from core.database import StockDatabase
from strategy.volume_shrink_strategy import VolumeShrinkStrategy
from strategy.backtest_engine import BacktestEngine

logging.basicConfig(
    level=logging.WARNING,  # 只显示警告和错误
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_backtest(strategy_name, use_volume_stabilize, check_market, check_liquidity):
    """运行回测"""
    db = StockDatabase("data/a_share.db")
    
    strategy = VolumeShrinkStrategy(
        db=db,
        market_index_code='sh.000001',
        min_avg_turnover=1e8
    )
    
    # 临时修改策略的scan方法默认参数
    original_scan = strategy.scan
    def custom_scan(date=None, min_cap=50e8, max_cap=200e8, min_decline=0.10, 
                   check_reversal=True, max_stocks=None, **kwargs):
        return original_scan(
            date=date, min_cap=min_cap, max_cap=max_cap, min_decline=min_decline,
            check_reversal=check_reversal, max_stocks=max_stocks,
            use_volume_stabilize=use_volume_stabilize,
            check_market=check_market,
            check_liquidity_filter=check_liquidity
        )
    strategy.scan = custom_scan
    
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
        hold_days=5,
        stop_loss=-0.10,
        take_profit=0.15,
        scan_interval=1,
        time_stop_days=3
    )
    
    db.close()
    return result

def main():
    print("="*80)
    print("策略对比测试（2024-10-01 至 2024-12-31）")
    print("="*80)
    
    # 测试1: 激进版（原版逻辑，无风控）
    print("\n【测试1: 激进版】")
    print("- 三连跌缩量")
    print("- 无市场环境过滤")
    print("- 无流动性过滤")
    print("-"*80)
    result1 = run_backtest("激进版", use_volume_stabilize=False, check_market=False, check_liquidity=False)
    
    # 测试2: 稳健版（放量企稳 + 全风控）
    print("\n【测试2: 稳健版】")
    print("- 下跌后放量企稳")
    print("- 大盘20日均线过滤")
    print("- 流动性过滤（ST股、成交额>1亿）")
    print("-"*80)
    result2 = run_backtest("稳健版", use_volume_stabilize=True, check_market=True, check_liquidity=True)
    
    # 测试3: 混合版（放量企稳，但无风控）
    print("\n【测试3: 混合版】")
    print("- 下跌后放量企稳")
    print("- 无市场环境过滤")
    print("- 无流动性过滤")
    print("-"*80)
    result3 = run_backtest("混合版", use_volume_stabilize=True, check_market=False, check_liquidity=False)
    
    # 对比结果
    print("\n" + "="*80)
    print("对比结果")
    print("="*80)
    print(f"{'指标':<20} {'激进版':>15} {'稳健版':>15} {'混合版':>15}")
    print("-"*80)
    print(f"{'总收益率':<20} {result1['total_return']:>14.2%} {result2['total_return']:>14.2%} {result3['total_return']:>14.2%}")
    print(f"{'最大回撤':<20} {result1['max_drawdown']:>14.2%} {result2['max_drawdown']:>14.2%} {result3['max_drawdown']:>14.2%}")
    print(f"{'交易次数':<20} {result1['completed_trades']:>15} {result2['completed_trades']:>15} {result3['completed_trades']:>15}")
    print(f"{'胜率':<20} {result1['win_rate']:>14.2%} {result2['win_rate']:>14.2%} {result3['win_rate']:>14.2%}")
    print(f"{'平均收益率':<20} {result1['avg_profit_rate']:>14.2%} {result2['avg_profit_rate']:>14.2%} {result3['avg_profit_rate']:>14.2%}")
    print(f"{'平均持仓天数':<20} {result1['avg_hold_days']:>14.1f} {result2['avg_hold_days']:>14.1f} {result3['avg_hold_days']:>14.1f}")
    print("="*80)
    
    # 结论
    print("\n结论:")
    best = max([('激进版', result1), ('稳健版', result2), ('混合版', result3)], 
               key=lambda x: x[1]['total_return'])
    print(f"- 收益最高: {best[0]} ({best[1]['total_return']:.2%})")
    
    safest = max([('激进版', result1), ('稳健版', result2), ('混合版', result3)], 
                 key=lambda x: x[1]['max_drawdown'])
    print(f"- 回撤最小: {safest[0]} ({safest[1]['max_drawdown']:.2%})")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

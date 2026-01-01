#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比测试：激进版 vs 稳健版"""
import logging
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.business.backtest.engine import BacktestEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_backtest(name, strategy, db, use_volume_stabilize, check_market, check_liquidity):
    """运行回测"""
    print(f"\n{'='*80}")
    print(f"回测: {name}")
    print(f"{'='*80}")
    
    # 修改策略的扫描方法参数
    original_scan = strategy.scan
    
    def custom_scan(date=None, **kwargs):
        kwargs['use_volume_stabilize'] = use_volume_stabilize
        kwargs['check_market'] = check_market
        kwargs['check_liquidity_filter'] = check_liquidity
        return original_scan(date=date, **kwargs)
    
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
    
    # 恢复原始方法
    strategy.scan = original_scan
    
    return result

def print_result(name, result):
    """打印回测结果"""
    print(f"\n{'='*80}")
    print(f"{name} - 回测结果")
    print(f"{'='*80}")
    print(f"初始资金: {result['initial_capital']:,.0f}")
    print(f"最终资金: {result['final_value']:,.0f}")
    print(f"总收益: {result['final_value'] - result['initial_capital']:,.0f}")
    print(f"总收益率: {result['total_return']:.2%}")
    print(f"总交易次数: {result['total_trades']}")
    print(f"完成交易: {result['completed_trades']}")
    print(f"胜率: {result['win_rate']:.2%}")
    print(f"平均收益率: {result['avg_profit_rate']:.2%}")
    print(f"最大回撤: {result['max_drawdown']:.2%}")
    print(f"平均持仓天数: {result['avg_hold_days']:.1f}")

def main():
    print("="*80)
    print("缩量三连跌策略 - 激进版 vs 稳健版对比测试")
    print("="*80)
    
    db = StockDatabase("data/a_share.db")
    strategy = VolumeShrinkStrategy(db=db, min_avg_turnover=1e8)
    
    # 测试1: 激进版（原版逻辑，无过滤器）
    result1 = run_backtest(
        name="激进版（三连跌缩量，无过滤器）",
        strategy=strategy,
        db=db,
        use_volume_stabilize=False,  # 使用原版三连跌缩量逻辑
        check_market=False,          # 不检查市场环境
        check_liquidity=False        # 不检查流动性
    )
    
    # 测试2: 稳健版（放量企稳 + 全部过滤器）
    result2 = run_backtest(
        name="稳健版（放量企稳 + 全部过滤器）",
        strategy=strategy,
        db=db,
        use_volume_stabilize=True,   # 使用放量企稳逻辑
        check_market=True,           # 检查市场环境
        check_liquidity=True         # 检查流动性
    )
    
    # 测试3: 混合版（三连跌缩量 + 过滤器）
    result3 = run_backtest(
        name="混合版（三连跌缩量 + 过滤器）",
        strategy=strategy,
        db=db,
        use_volume_stabilize=False,  # 使用原版逻辑
        check_market=True,           # 检查市场环境
        check_liquidity=True         # 检查流动性
    )
    
    # 打印对比结果
    print("\n" + "="*80)
    print("对比总结")
    print("="*80)
    
    print_result("激进版", result1)
    print_result("稳健版", result2)
    print_result("混合版", result3)
    
    # 对比表格
    print(f"\n{'='*80}")
    print("关键指标对比")
    print(f"{'='*80}")
    print(f"{'指标':<20} {'激进版':>15} {'稳健版':>15} {'混合版':>15}")
    print("-"*80)
    print(f"{'总收益率':<20} {result1['total_return']:>14.2%} {result2['total_return']:>14.2%} {result3['total_return']:>14.2%}")
    print(f"{'最大回撤':<20} {result1['max_drawdown']:>14.2%} {result2['max_drawdown']:>14.2%} {result3['max_drawdown']:>14.2%}")
    print(f"{'胜率':<20} {result1['win_rate']:>14.2%} {result2['win_rate']:>14.2%} {result3['win_rate']:>14.2%}")
    print(f"{'交易次数':<20} {result1['completed_trades']:>15} {result2['completed_trades']:>15} {result3['completed_trades']:>15}")
    print(f"{'平均收益率':<20} {result1['avg_profit_rate']:>14.2%} {result2['avg_profit_rate']:>14.2%} {result3['avg_profit_rate']:>14.2%}")
    
    db.close()
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    main()

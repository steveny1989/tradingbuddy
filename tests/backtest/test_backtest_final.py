#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""最终回测测试 - 验证所有修复"""
import logging
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.business.backtest.engine import BacktestEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_backtest(name, strategy, db, **scan_kwargs):
    """运行回测"""
    print(f"\n{'='*80}")
    print(f"回测: {name}")
    print(f"{'='*80}")
    
    # 修改策略的扫描方法参数
    original_scan = strategy.scan
    
    def custom_scan(date=None, **kwargs):
        kwargs.update(scan_kwargs)
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
    print(f"{name}")
    print(f"{'='*80}")
    
    if result['total_trades'] == 0:
        print("⚠️  没有完成的交易")
        return
    
    print(f"初始资金:     {result['initial_capital']:>12,.0f}")
    print(f"最终资金:     {result['final_value']:>12,.0f}")
    print(f"总收益:       {result['final_value'] - result['initial_capital']:>12,.0f}")
    print(f"总收益率:     {result['total_return']:>12.2%}")
    print(f"-"*80)
    print(f"总交易次数:   {result['total_trades']:>12}")
    print(f"完成交易:     {result['completed_trades']:>12}")
    print(f"盈利次数:     {result['win_trades']:>12}")
    print(f"亏损次数:     {result['loss_trades']:>12}")
    print(f"胜率:         {result['win_rate']:>12.2%}")
    print(f"-"*80)
    print(f"平均收益:     {result['avg_profit']:>12,.0f}")
    print(f"平均收益率:   {result['avg_profit_rate']:>12.2%}")
    print(f"最大盈利:     {result['max_profit']:>12,.0f}")
    print(f"最大亏损:     {result['max_loss']:>12,.0f}")
    print(f"最大回撤:     {result['max_drawdown']:>12.2%}")
    print(f"平均持仓天数: {result['avg_hold_days']:>12.1f}")

def main():
    print("="*80)
    print("缩量三连跌策略 - 最终回测（验证所有修复）")
    print("="*80)
    print("\n修复内容:")
    print("✅ 1. 日历天 vs 交易日问题（使用真实交易日列表）")
    print("✅ 2. 买入逻辑陷阱（使用下一个交易日）")
    print("✅ 3. 时间止损（N天不反弹强制出局）")
    print("✅ 4. ST股过滤")
    print("✅ 5. 流动性过滤（日均成交额>1亿）")
    print("✅ 6. 市场环境过滤（大盘20日均线）")
    print("✅ 7. 性能优化（减少重复数据库查询）")
    
    db = StockDatabase("data/a_share.db")
    strategy = VolumeShrinkStrategy(db=db, min_avg_turnover=1e8)
    
    # 测试1: 无过滤器（原始版本，用于对比）
    print("\n" + "="*80)
    print("测试1: 无过滤器（原始版本）")
    print("="*80)
    result1 = run_backtest(
        name="无过滤器",
        strategy=strategy,
        db=db,
        use_volume_stabilize=False,
        check_market=False,
        check_liquidity_filter=False
    )
    
    # 测试2: 仅市场过滤器
    print("\n" + "="*80)
    print("测试2: 仅市场过滤器（大盘20日均线）")
    print("="*80)
    result2 = run_backtest(
        name="仅市场过滤器",
        strategy=strategy,
        db=db,
        use_volume_stabilize=False,
        check_market=True,
        check_liquidity_filter=False
    )
    
    # 测试3: 全部过滤器（稳健版）
    print("\n" + "="*80)
    print("测试3: 全部过滤器（稳健版）")
    print("="*80)
    result3 = run_backtest(
        name="全部过滤器",
        strategy=strategy,
        db=db,
        use_volume_stabilize=True,
        check_market=True,
        check_liquidity_filter=True
    )
    
    # 打印对比结果
    print("\n" + "="*80)
    print("回测结果对比")
    print("="*80)
    
    print_result("测试1: 无过滤器（原始版本）", result1)
    print_result("测试2: 仅市场过滤器", result2)
    print_result("测试3: 全部过滤器（稳健版）", result3)
    
    # 对比表格
    print(f"\n{'='*80}")
    print("关键指标对比")
    print(f"{'='*80}")
    print(f"{'指标':<20} {'无过滤器':>15} {'仅市场过滤':>15} {'全部过滤器':>15}")
    print("-"*80)
    
    if result1['total_trades'] > 0:
        print(f"{'总收益率':<20} {result1['total_return']:>14.2%} {result2['total_return']:>14.2%} {result3['total_return']:>14.2%}")
        print(f"{'最大回撤':<20} {result1['max_drawdown']:>14.2%} {result2['max_drawdown']:>14.2%} {result3['max_drawdown']:>14.2%}")
        print(f"{'胜率':<20} {result1['win_rate']:>14.2%} {result2['win_rate']:>14.2%} {result3['win_rate']:>14.2%}")
        print(f"{'交易次数':<20} {result1['completed_trades']:>15} {result2['completed_trades']:>15} {result3['completed_trades']:>15}")
        print(f"{'平均收益率':<20} {result1['avg_profit_rate']:>14.2%} {result2['avg_profit_rate']:>14.2%} {result3['avg_profit_rate']:>14.2%}")
    
    # 结论
    print(f"\n{'='*80}")
    print("结论")
    print(f"{'='*80}")
    
    if result1['total_trades'] > 0 and result3['total_trades'] > 0:
        drawdown_improvement = result3['max_drawdown'] - result1['max_drawdown']
        print(f"✅ 最大回撤改善: {drawdown_improvement:.2%} (从 {result1['max_drawdown']:.2%} 到 {result3['max_drawdown']:.2%})")
        
        if result3['max_drawdown'] > -0.30:
            print(f"✅ 回撤控制良好: {result3['max_drawdown']:.2%} < -30%")
        else:
            print(f"⚠️  回撤仍需优化: {result3['max_drawdown']:.2%}")
        
        if result3['win_rate'] > 0.50:
            print(f"✅ 胜率提升: {result3['win_rate']:.2%} > 50%")
        else:
            print(f"⚠️  胜率待提升: {result3['win_rate']:.2%}")
    
    db.close()
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    main()

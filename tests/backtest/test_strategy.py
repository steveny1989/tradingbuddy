#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试缩量三连跌策略（稳健版 vs 激进版对比）"""
import logging
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.business.backtest.engine import BacktestEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("="*80)
    print("缩量三连跌策略测试（稳健版 vs 激进版）")
    print("="*80)
    
    # 初始化数据库
    db = StockDatabase("data/a_share.db")
    
    # 初始化策略
    strategy = VolumeShrinkStrategy(
        db=db,
        market_index_code='sh.000001',  # 上证指数
        min_avg_turnover=1e8  # 日均成交额1亿
    )
    
    # 测试1: 扫描最新信号（稳健版）
    print("\n【测试1: 扫描最新信号（稳健版）】")
    print("-"*80)
    signals = strategy.scan(
        min_cap=50e8,      # 50亿
        max_cap=200e8,     # 200亿
        min_decline=0.10,  # 10%跌幅
        check_reversal=True,
        max_stocks=100,    # 先测试100只
        use_volume_stabilize=True,  # 使用"放量企稳"逻辑
        check_market=True,          # 检查大盘20日均线
        check_liquidity_filter=True # 检查流动性
    )
    
    if not signals.empty:
        print(f"\n找到 {len(signals)} 个信号:")
        print(signals[['code', 'name', 'date', 'price', 'decline_rate', 'market_cap']].head(10))
    else:
        print("未找到符合条件的信号")
    
    # 测试2: 回测（稳健版）
    print("\n【测试2: 历史回测（稳健版）】")
    print("-"*80)
    
    # 初始化回测引擎
    backtest_stable = BacktestEngine(
        db=db,
        strategy=strategy,
        initial_capital=1000000,  # 100万
        max_positions=10,         # 最多持仓10只
        position_size=0.1         # 每次买入10%
    )
    
    # 运行回测（最近3个月）
    result_stable = backtest_stable.run(
        start_date='2024-10-01',
        end_date='2024-12-31',
        hold_days=5,           # 持有5天
        stop_loss=-0.10,       # 止损-10%
        take_profit=0.15,      # 止盈15%
        scan_interval=1,       # 每天扫描
        time_stop_days=3       # 3天不反弹强制出局
    )
    
    # 打印稳健版回测结果
    print("\n" + "="*80)
    print("稳健版回测结果")
    print("="*80)
    print(f"初始资金: {result_stable['initial_capital']:,.0f}")
    print(f"最终资金: {result_stable['final_value']:,.0f}")
    print(f"总收益率: {result_stable['total_return']:.2%}")
    print(f"总交易次数: {result_stable['total_trades']}")
    print(f"完成交易: {result_stable['completed_trades']}")
    print(f"盈利次数: {result_stable['win_trades']}")
    print(f"亏损次数: {result_stable['loss_trades']}")
    print(f"胜率: {result_stable['win_rate']:.2%}")
    print(f"平均收益: {result_stable['avg_profit']:.2f}")
    print(f"平均收益率: {result_stable['avg_profit_rate']:.2%}")
    print(f"最大盈利: {result_stable['max_profit']:.2f}")
    print(f"最大亏损: {result_stable['max_loss']:.2f}")
    print(f"最大回撤: {result_stable['max_drawdown']:.2%}")
    print(f"平均持仓天数: {result_stable['avg_hold_days']:.1f}")
    
    # 显示部分交易记录
    if 'trades' in result_stable and not result_stable['trades'].empty:
        print("\n交易记录（前10条）:")
        trades = result_stable['trades']
        sell_trades = trades[trades['action'] == 'sell']
        if not sell_trades.empty:
            print(sell_trades[['date', 'code', 'price', 'profit', 'profit_rate', 'reason']].head(10))
    
    db.close()
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    main()

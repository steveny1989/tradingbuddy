#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析回测引擎的回撤问题"""
import logging
import pandas as pd
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.business.backtest.engine import BacktestEngine

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def analyze_single_trade():
    """分析单笔交易的详细过程"""
    print("="*80)
    print("分析单笔交易的详细过程")
    print("="*80)
    
    db = StockDatabase("data/a_share.db")
    
    # 选择一只在2024-10-14有信号的股票
    code = 'sz.301160'
    
    # 查看这只股票的历史数据
    df = db.get_daily_data(code, start_date='2024-10-08', end_date='2024-10-25')
    
    print(f"\n{code} 的历史数据:")
    print(df[['date', 'open', 'close', 'high', 'low', 'volume', 'amount']])
    
    # 模拟买入卖出
    print("\n模拟交易过程:")
    print("-"*80)
    
    # 假设在2024-10-15买入（2024-10-14发现信号）
    buy_date = '2024-10-15'
    buy_row = df[df['date'] == buy_date]
    if not buy_row.empty:
        buy_price = buy_row['open'].iloc[0]
        print(f"买入日期: {buy_date}")
        print(f"买入价格: {buy_price:.2f} (开盘价)")
        
        # 计算买入股数和成本
        initial_capital = 1000000
        position_size = 0.1
        buy_amount = initial_capital * position_size
        shares = int(buy_amount / buy_price / 100) * 100
        
        print(f"买入金额: {buy_amount:,.0f}")
        print(f"买入股数: {shares}")
        
        # 计算实际成本
        slippage_rate = 0.001
        commission_rate = 0.0003
        actual_price = buy_price * (1 + slippage_rate)
        amount = actual_price * shares
        commission = max(amount * commission_rate, 5)
        total_cost = amount + commission
        
        print(f"滑点后价格: {actual_price:.2f}")
        print(f"交易金额: {amount:,.2f}")
        print(f"佣金: {commission:.2f}")
        print(f"总成本: {total_cost:,.2f}")
        
        # 查看持有期间的价格变化
        print(f"\n持有期间价格变化:")
        hold_df = df[df['date'] >= buy_date].head(10)
        for _, row in hold_df.iterrows():
            profit_rate = (row['close'] - buy_price) / buy_price
            print(f"{row['date']}: 收盘 {row['close']:.2f}, 盈亏 {profit_rate:>7.2%}")
        
        # 假设在2024-10-21卖出（持有5天）
        sell_date = '2024-10-21'
        sell_row = df[df['date'] == sell_date]
        if not sell_row.empty:
            sell_price = sell_row['close'].iloc[0]
            print(f"\n卖出日期: {sell_date}")
            print(f"卖出价格: {sell_price:.2f} (收盘价)")
            
            # 计算卖出收益
            actual_sell_price = sell_price * (1 - slippage_rate)
            sell_amount = actual_sell_price * shares
            sell_commission = max(sell_amount * commission_rate, 5)
            stamp_tax = sell_amount * 0.001
            proceeds = sell_amount - sell_commission - stamp_tax
            
            print(f"滑点后价格: {actual_sell_price:.2f}")
            print(f"交易金额: {sell_amount:,.2f}")
            print(f"佣金: {sell_commission:.2f}")
            print(f"印花税: {stamp_tax:.2f}")
            print(f"实际到手: {proceeds:,.2f}")
            
            profit = proceeds - total_cost
            profit_rate = profit / total_cost
            
            print(f"\n交易结果:")
            print(f"成本: {total_cost:,.2f}")
            print(f"收益: {profit:,.2f}")
            print(f"收益率: {profit_rate:.2%}")
    
    db.close()

def analyze_daily_values():
    """分析每日净值的计算"""
    print("\n" + "="*80)
    print("分析每日净值计算")
    print("="*80)
    
    db = StockDatabase("data/a_share.db")
    
    strategy = VolumeShrinkStrategy(
        db=db,
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
    
    # 运行短期回测（关闭所有过滤器）
    # 临时修改策略的scan方法
    original_scan = strategy.scan
    def custom_scan(date=None, min_cap=50e8, max_cap=200e8, min_decline=0.10, 
                   check_reversal=True, max_stocks=None, **kwargs):
        return original_scan(
            date=date, min_cap=min_cap, max_cap=max_cap, min_decline=min_decline,
            check_reversal=check_reversal, max_stocks=max_stocks,
            use_volume_stabilize=False,  # 使用激进版
            check_market=False,          # 不检查市场
            check_liquidity_filter=False # 不检查流动性
        )
    strategy.scan = custom_scan
    
    result = backtest.run(
        start_date='2024-10-14',
        end_date='2024-10-25',
        hold_days=5,
        stop_loss=-0.10,
        take_profit=0.15,
        scan_interval=1,
        time_stop_days=3
    )
    
    # 分析每日净值
    if 'daily_values' in result and not result['daily_values'].empty:
        df_daily = result['daily_values']
        print(f"\n每日净值记录 (共{len(df_daily)}条):")
        print(df_daily[['date', 'cash', 'position_value', 'total_value', 'position_count']])
        
        # 计算每日变化
        df_daily['daily_return'] = df_daily['total_value'].pct_change()
        df_daily['cumulative_return'] = (df_daily['total_value'] / df_daily['total_value'].iloc[0] - 1)
        
        print(f"\n每日收益率:")
        print(df_daily[['date', 'total_value', 'daily_return', 'cumulative_return']])
        
        # 检查是否有异常的大幅波动
        large_moves = df_daily[abs(df_daily['daily_return']) > 0.05]
        if not large_moves.empty:
            print(f"\n发现异常波动 (单日变化>5%):")
            print(large_moves[['date', 'total_value', 'daily_return', 'position_count']])
        
        # 计算回撤
        df_daily['peak'] = df_daily['total_value'].cummax()
        df_daily['drawdown'] = (df_daily['total_value'] - df_daily['peak']) / df_daily['peak']
        
        print(f"\n回撤分析:")
        print(df_daily[['date', 'total_value', 'peak', 'drawdown']])
        print(f"\n最大回撤: {df_daily['drawdown'].min():.2%}")
        
        # 找出最大回撤发生的日期
        max_dd_idx = df_daily['drawdown'].idxmin()
        max_dd_row = df_daily.loc[max_dd_idx]
        print(f"最大回撤日期: {max_dd_row['date']}")
        print(f"当日净值: {max_dd_row['total_value']:,.0f}")
        print(f"历史峰值: {max_dd_row['peak']:,.0f}")
    
    # 分析交易记录
    if 'trades' in result and not result['trades'].empty:
        df_trades = result['trades']
        print(f"\n交易记录 (共{len(df_trades)}条):")
        print(df_trades[['date', 'code', 'action', 'price', 'shares', 'amount', 'cash']])
        
        # 分析卖出交易
        sell_trades = df_trades[df_trades['action'] == 'sell']
        if not sell_trades.empty:
            print(f"\n卖出交易详情:")
            print(sell_trades[['date', 'code', 'price', 'cost_price', 'profit', 'profit_rate', 'reason', 'hold_days']])
    
    db.close()

def check_trading_days():
    """检查交易日列表是否正确"""
    print("\n" + "="*80)
    print("检查交易日列表")
    print("="*80)
    
    db = StockDatabase("data/a_share.db")
    
    # 获取指数数据
    df_index = db.get_daily_data('sh.000001', start_date='2024-10-14', end_date='2024-10-25')
    
    print(f"\n上证指数交易日 (2024-10-14 至 2024-10-25):")
    print(df_index[['date', 'close']])
    
    # 检查是否有周末
    df_index['weekday'] = pd.to_datetime(df_index['date']).dt.day_name()
    print(f"\n星期分布:")
    print(df_index[['date', 'weekday']])
    
    weekend_days = df_index[df_index['weekday'].isin(['Saturday', 'Sunday'])]
    if not weekend_days.empty:
        print(f"\n警告: 发现周末数据!")
        print(weekend_days)
    else:
        print(f"\n✓ 没有周末数据，交易日列表正确")
    
    db.close()

if __name__ == "__main__":
    # 1. 检查交易日列表
    check_trading_days()
    
    # 2. 分析单笔交易
    analyze_single_trade()
    
    # 3. 分析每日净值
    analyze_daily_values()

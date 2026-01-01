#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试模拟盘系统"""
import logging
from datetime import datetime, timedelta
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from paper_trading import PaperTradingEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_paper_trading():
    """测试模拟盘功能"""
    print("="*80)
    print("模拟盘系统测试")
    print("="*80)
    
    # 初始化
    db = StockDatabase("data/a_share.db")
    strategy = VolumeShrinkStrategy(db=db, min_avg_turnover=1e8)
    
    # 创建测试账户（使用独立目录）
    paper = PaperTradingEngine(
        db=db,
        strategy=strategy,
        initial_capital=100000,
        max_positions=5,
        position_size=0.15,
        data_dir="paper_trading_test"  # 测试目录
    )
    
    print("\n【测试1: 初始账户状态】")
    print("-"*80)
    paper.show_status()
    
    # 测试历史数据（从2024-10-01开始运行10天）
    print("\n【测试2: 历史数据模拟（10天）】")
    print("-"*80)
    
    start_date = datetime(2024, 10, 1)
    
    for i in range(10):
        test_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        print(f"\n运行日期: {test_date}")
        print("-"*40)
        
        try:
            paper.run_daily(date=test_date)
        except Exception as e:
            print(f"错误: {e}")
            continue
    
    print("\n【测试3: 最终账户状态】")
    print("-"*80)
    paper.show_status()
    
    print("\n【测试4: 绩效报告】")
    print("-"*80)
    paper.show_performance()
    
    print("\n【测试5: 查看交易记录】")
    print("-"*80)
    import pandas as pd
    trades_file = paper.data_dir / "trades.csv"
    if trades_file.exists():
        trades = pd.read_csv(trades_file)
        print(f"\n总交易次数: {len(trades)}")
        print("\n最近5笔交易:")
        print(trades[['date', 'code', 'action', 'price', 'shares', 'reason']].tail(5).to_string(index=False))
    else:
        print("暂无交易记录")
    
    db.close()
    
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)
    print("\n提示:")
    print("- 测试数据保存在 paper_trading_test/ 目录")
    print("- 正式使用时会保存在 paper_trading_data/ 目录")
    print("- 运行 'python3 paper_trading.py run' 开始正式模拟盘")

if __name__ == "__main__":
    test_paper_trading()

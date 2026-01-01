#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试策略过滤器"""
import logging
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("="*80)
    print("策略过滤器调试")
    print("="*80)
    
    db = StockDatabase("data/a_share.db")
    strategy = VolumeShrinkStrategy(db=db, min_avg_turnover=1e8)
    
    # 测试1: 市场环境过滤器
    print("\n【测试1: 市场环境过滤器】")
    print("-"*80)
    market_ok = strategy.check_market_filter(date='2024-12-31')
    print(f"2024-12-31 市场环境: {'✅ 通过' if market_ok else '❌ 不通过'}")
    
    # 测试2: 流动性过滤器（测试几只股票）
    print("\n【测试2: 流动性过滤器】")
    print("-"*80)
    test_codes = ['sh.600000', 'sh.600519', 'sz.000001', 'sz.300001']
    for code in test_codes:
        liquidity_ok = strategy.check_liquidity(code, date='2024-12-31', days=5)
        print(f"{code}: {'✅ 通过' if liquidity_ok else '❌ 不通过'}")
    
    # 测试3: 完整扫描（小样本）
    print("\n【测试3: 完整扫描（10只股票）】")
    print("-"*80)
    signals = strategy.scan(
        date='2024-12-31',
        max_stocks=10,
        use_volume_stabilize=True,
        check_market=True,
        check_liquidity_filter=True
    )
    
    if not signals.empty:
        print(f"\n找到 {len(signals)} 个信号:")
        print(signals[['code', 'name', 'decline_rate', 'volume_stabilize']])
    else:
        print("未找到信号")
    
    db.close()
    print("\n" + "="*80)
    print("调试完成")
    print("="*80)

if __name__ == "__main__":
    main()

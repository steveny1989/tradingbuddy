#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试信号扫描"""
import logging
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("="*80)
    print("信号扫描测试")
    print("="*80)
    
    db = StockDatabase("data/a_share.db")
    strategy = VolumeShrinkStrategy(db=db, min_avg_turnover=1e8)
    
    # 测试不同日期
    test_dates = ['2024-10-15', '2024-11-15', '2024-12-15']
    
    for test_date in test_dates:
        print(f"\n{'='*80}")
        print(f"测试日期: {test_date}")
        print(f"{'='*80}")
        
        # 检查市场环境
        market_ok = strategy.check_market_filter(date=test_date)
        print(f"市场环境: {'✅ 通过' if market_ok else '❌ 不通过'}")
        
        if not market_ok:
            print("市场环境不通过，跳过扫描")
            continue
        
        # 扫描信号（小样本）
        signals = strategy.scan(
            date=test_date,
            max_stocks=50,
            use_volume_stabilize=True,
            check_market=True,
            check_liquidity_filter=True
        )
        
        if not signals.empty:
            print(f"\n找到 {len(signals)} 个信号:")
            print(signals[['code', 'name', 'decline_rate', 'market_cap']].head(10))
        else:
            print("未找到信号")
    
    db.close()
    print("\n" + "="*80)
    print("测试完成")
    print("="*80)

if __name__ == "__main__":
    main()

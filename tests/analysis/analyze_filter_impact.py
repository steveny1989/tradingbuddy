#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析过滤器影响"""
import logging
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("="*80)
    print("过滤器影响分析")
    print("="*80)
    
    db = StockDatabase("data/a_share.db")
    strategy = VolumeShrinkStrategy(db=db, min_avg_turnover=1e8)
    
    test_date = '2024-10-15'
    
    # 测试1: 原版逻辑（三连跌缩量）
    print(f"\n【测试1: 原版逻辑（三连跌缩量）】")
    print("-"*80)
    signals1 = strategy.scan(
        date=test_date,
        max_stocks=200,
        use_volume_stabilize=False,
        check_market=False,
        check_liquidity_filter=False
    )
    print(f"找到信号: {len(signals1)} 个")
    
    # 测试2: 放量企稳逻辑
    print(f"\n【测试2: 放量企稳逻辑】")
    print("-"*80)
    signals2 = strategy.scan(
        date=test_date,
        max_stocks=200,
        use_volume_stabilize=True,
        check_market=False,
        check_liquidity_filter=False
    )
    print(f"找到信号: {len(signals2)} 个")
    
    # 测试3: 原版 + 流动性过滤
    print(f"\n【测试3: 原版 + 流动性过滤】")
    print("-"*80)
    signals3 = strategy.scan(
        date=test_date,
        max_stocks=200,
        use_volume_stabilize=False,
        check_market=False,
        check_liquidity_filter=True
    )
    print(f"找到信号: {len(signals3)} 个")
    
    # 测试4: 原版 + 市场过滤
    print(f"\n【测试4: 原版 + 市场过滤】")
    print("-"*80)
    signals4 = strategy.scan(
        date=test_date,
        max_stocks=200,
        use_volume_stabilize=False,
        check_market=True,
        check_liquidity_filter=False
    )
    print(f"找到信号: {len(signals4)} 个")
    
    # 测试5: 原版 + 全部过滤
    print(f"\n【测试5: 原版 + 全部过滤】")
    print("-"*80)
    signals5 = strategy.scan(
        date=test_date,
        max_stocks=200,
        use_volume_stabilize=False,
        check_market=True,
        check_liquidity_filter=True
    )
    print(f"找到信号: {len(signals5)} 个")
    
    # 总结
    print(f"\n{'='*80}")
    print("总结")
    print(f"{'='*80}")
    print(f"{'配置':<30} {'信号数':>10}")
    print("-"*80)
    print(f"{'原版（无过滤）':<30} {len(signals1):>10}")
    print(f"{'放量企稳（无过滤）':<30} {len(signals2):>10}")
    print(f"{'原版 + 流动性过滤':<30} {len(signals3):>10}")
    print(f"{'原版 + 市场过滤':<30} {len(signals4):>10}")
    print(f"{'原版 + 全部过滤':<30} {len(signals5):>10}")
    
    print(f"\n结论:")
    print(f"- 放量企稳逻辑过于严格，信号数从 {len(signals1)} 降至 {len(signals2)}")
    print(f"- 流动性过滤影响: {len(signals1)} → {len(signals3)} (过滤 {len(signals1)-len(signals3)} 个)")
    print(f"- 市场过滤影响: {len(signals1)} → {len(signals4)} (过滤 {len(signals1)-len(signals4)} 个)")
    print(f"- 建议: 使用原版逻辑 + 适度过滤")
    
    db.close()
    print("\n" + "="*80)
    print("分析完成")
    print("="*80)

if __name__ == "__main__":
    main()

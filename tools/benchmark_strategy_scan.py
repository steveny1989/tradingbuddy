#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略扫描性能对比测试
Benchmark Strategy Scan Performance
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def benchmark_scan():
    """性能对比测试"""
    
    db = StockDatabase()
    strategy = VolumeShrinkStrategy(db)
    
    # 测试参数
    test_date = '2024-12-31'
    max_stocks = 100  # 测试100只股票
    
    print("\n" + "="*80)
    print("策略扫描性能对比测试")
    print("="*80)
    print(f"测试日期: {test_date}")
    print(f"测试股票数: {max_stocks}")
    print()
    
    # 测试1: 兼容模式（逐个查询）
    print("【测试1: 兼容模式 - 逐个查询分表】")
    start = time.time()
    
    signals_old = strategy.scan(
        date=test_date,
        max_stocks=max_stocks,
        use_unified_table=False,  # 使用旧方法
        check_market=False  # 跳过市场过滤，专注测试数据查询性能
    )
    
    time_old = time.time() - start
    print(f"⏱️  耗时: {time_old:.2f}秒")
    print(f"📊 信号数: {len(signals_old)}")
    print()
    
    # 测试2: 高性能模式（批量查询统一表）
    print("【测试2: 高性能模式 - 批量查询统一表】")
    start = time.time()
    
    signals_new = strategy.scan(
        date=test_date,
        max_stocks=max_stocks,
        use_unified_table=True,  # 使用新方法
        check_market=False
    )
    
    time_new = time.time() - start
    print(f"⏱️  耗时: {time_new:.2f}秒")
    print(f"📊 信号数: {len(signals_new)}")
    print()
    
    # 性能对比
    print("="*80)
    print("性能对比结果")
    print("="*80)
    print(f"兼容模式: {time_old:.2f}秒")
    print(f"高性能模式: {time_new:.2f}秒")
    
    if time_new > 0:
        speedup = time_old / time_new
        print(f"性能提升: {speedup:.2f}x")
        
        if speedup > 1:
            print(f"✅ 高性能模式快 {speedup:.2f} 倍")
        else:
            print(f"⚠️  高性能模式反而慢了")
    
    # 结果一致性检查
    print()
    print("结果一致性检查:")
    if len(signals_old) == len(signals_new):
        print(f"✅ 信号数量一致: {len(signals_old)}")
    else:
        print(f"⚠️  信号数量不一致: 旧={len(signals_old)}, 新={len(signals_new)}")
    
    print()
    print("="*80)
    
    db.close()


if __name__ == "__main__":
    benchmark_scan()

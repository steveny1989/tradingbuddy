#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时寻找逆向价值股票 - 放宽条件版本
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.data.database import StockDatabase
from src.business.strategies.reverse_value import ReverseValueStrategy
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_stocks():
    """寻找符合条件的股票"""
    
    print("=" * 80)
    print("🔍 逆向价值选股 - 实时搜索")
    print("=" * 80)
    print()
    
    db = StockDatabase("data/a_share.db")
    strategy = ReverseValueStrategy(db=db, min_avg_turnover=5e7)  # 降低流动性要求
    
    # 方案1：扩大市值范围，跳过质量检查
    print("【方案1】扩大市值范围（30-1000亿），跳过质量检查")
    print("-" * 80)
    
    pool = strategy.get_stock_pool(min_cap=30e8, max_cap=1000e8)
    pool = pool[~pool['name'].str.contains('ST|st', na=False)]
    
    print(f"股票池: {len(pool)} 只股票")
    print(f"开始扫描前100只...")
    print()
    
    signals = []
    for idx, row in pool.head(100).iterrows():
        code = row['full_code']
        
        # 跳过质量检查（因为可能没有财务数据）
        signal = strategy.check_signal(
            code=code,
            skip_quality=True,
            skip_defense=False,
            skip_valuation=False,
            skip_cycle=False,
            skip_reverse=False
        )
        
        if signal:
            signal['market_cap'] = row['total_cap'] / 1e8
            signals.append(signal)
            print(f"✅ 找到: {signal['name']} ({signal['code']})")
    
    print()
    print(f"方案1结果: 找到 {len(signals)} 个符合条件的股票")
    print()
    
    if signals:
        print("详细信息:")
        print("-" * 80)
        for i, sig in enumerate(signals[:10], 1):
            print(f"\n{i}. {sig['name']} ({sig['code']})")
            print(f"   价格: ¥{sig['price']:.2f}, 市值: {sig['market_cap']:.1f}亿")
            
            if 'valuation' in sig and isinstance(sig['valuation'], dict):
                val = sig['valuation']
                print(f"   估值: PE分位={val.get('pe_percentile', 0):.1f}%, PB分位={val.get('pb_percentile', 0):.1f}%")
            
            if 'cycle' in sig and isinstance(sig['cycle'], dict):
                cyc = sig['cycle']
                print(f"   周期: 乖离率={cyc.get('deviation', 0):.1f}%, 企稳={cyc.get('is_stabilizing', False)}")
    
    print()
    print("=" * 80)
    
    # 方案2：只检查估值和周期（最宽松）
    print()
    print("【方案2】只检查估值和周期（最宽松条件）")
    print("-" * 80)
    
    signals2 = []
    for idx, row in pool.head(100).iterrows():
        code = row['full_code']
        
        # 只检查估值和周期
        signal = strategy.check_signal(
            code=code,
            skip_quality=True,
            skip_defense=True,  # 跳过防守
            skip_valuation=False,
            skip_cycle=False,
            skip_reverse=True  # 跳过逆向
        )
        
        if signal:
            signal['market_cap'] = row['total_cap'] / 1e8
            signals2.append(signal)
    
    print(f"方案2结果: 找到 {len(signals2)} 个符合条件的股票")
    print()
    
    if signals2:
        print("详细信息:")
        print("-" * 80)
        for i, sig in enumerate(signals2[:10], 1):
            print(f"\n{i}. {sig['name']} ({sig['code']})")
            print(f"   价格: ¥{sig['price']:.2f}, 市值: {sig['market_cap']:.1f}亿")
            
            if 'valuation' in sig and isinstance(sig['valuation'], dict):
                val = sig['valuation']
                print(f"   估值: PE分位={val.get('pe_percentile', 0):.1f}%, PB分位={val.get('pb_percentile', 0):.1f}%")
            
            if 'cycle' in sig and isinstance(sig['cycle'], dict):
                cyc = sig['cycle']
                print(f"   周期: 乖离率={cyc.get('deviation', 0):.1f}%")
    
    print()
    print("=" * 80)
    
    # 方案3：测试几只知名股票
    print()
    print("【方案3】测试知名股票的各项指标")
    print("-" * 80)
    
    test_stocks = [
        ('sh.600000', '浦发银行'),
        ('sz.000001', '平安银行'),
        ('sh.600036', '招商银行'),
        ('sh.600519', '贵州茅台'),
        ('sz.000858', '五粮液'),
        ('sh.601318', '中国平安'),
    ]
    
    for code, name in test_stocks:
        print(f"\n{name} ({code}):")
        
        # 测试各个过滤器
        passed_defense, defense_info = strategy.check_defense_filter(code, name)
        print(f"  防守: {'✅' if passed_defense else '❌'} {defense_info if isinstance(defense_info, str) else ''}")
        
        passed_val, val_info = strategy.check_valuation_filter(code)
        if isinstance(val_info, dict) and 'current_pe' in val_info:
            print(f"  估值: {'✅' if passed_val else '❌'} PE分位={val_info.get('pe_percentile', 0):.1f}%, PB分位={val_info.get('pb_percentile', 0):.1f}%")
        else:
            print(f"  估值: {'✅' if passed_val else '❌'} {val_info.get('reason', val_info)}")
        
        passed_cyc, cyc_info = strategy.check_cycle_filter(code)
        if isinstance(cyc_info, dict) and 'current_price' in cyc_info:
            print(f"  周期: {'✅' if passed_cyc else '❌'} 乖离率={cyc_info.get('deviation', 0):.1f}%, 企稳={cyc_info.get('is_stabilizing', False)}")
        else:
            print(f"  周期: {'✅' if passed_cyc else '❌'} {cyc_info.get('reason', cyc_info)}")
        
        passed_rev, rev_info = strategy.check_reverse_signal(code)
        if isinstance(rev_info, dict):
            print(f"  逆向: {'✅' if passed_rev else '❌'} 下跌={rev_info.get('is_declining', False)}, 缩量={rev_info.get('is_shrinking', False)}, 企稳={rev_info.get('is_stabilizing', False)}")
        else:
            print(f"  逆向: {'✅' if passed_rev else '❌'} {rev_info.get('reason', rev_info)}")
    
    print()
    print("=" * 80)
    print()
    print("总结:")
    print(f"  方案1（跳过质量检查）: {len(signals)} 个股票")
    print(f"  方案2（只看估值+周期）: {len(signals2)} 个股票")
    print()
    print("建议:")
    print("  1. 当前可能不是最佳买入时机（市场不在周期底部）")
    print("  2. 可以关注方案2中的股票，等待更好的买入时机")
    print("  3. 定期运行此脚本，在市场调整时会有更多机会")
    print()

if __name__ == '__main__':
    try:
        find_stocks()
    except Exception as e:
        logger.error(f"执行失败: {e}", exc_info=True)

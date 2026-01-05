# -*- coding: utf-8 -*-
"""
测试Aggregated Layer

测试技术指标计算和存储
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data.layers import CleanedLayer, AggregatedLayer, FeatureEngine
import pandas as pd

def test_feature_engine():
    """测试特征计算引擎"""
    print("\n" + "="*60)
    print("测试特征计算引擎")
    print("="*60)
    
    # 创建测试数据
    dates = pd.date_range('2025-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'date': dates.strftime('%Y-%m-%d'),
        'open': [100 + i*0.5 for i in range(100)],
        'high': [102 + i*0.5 for i in range(100)],
        'low': [98 + i*0.5 for i in range(100)],
        'close': [101 + i*0.5 for i in range(100)],
        'volume': [1000000 + i*10000 for i in range(100)],
    })
    
    print(f"\n测试数据: {len(df)} 条记录")
    print(f"日期范围: {df['date'].min()} ~ {df['date'].max()}")
    
    # 计算所有指标
    print("\n计算技术指标...")
    df_with_indicators = FeatureEngine.calculate_all_indicators(df)
    
    # 检查指标
    indicators = ['ma5', 'ma10', 'ma20', 'ma50', 'ma200', 
                  'rsi', 'macd', 'macd_signal', 'macd_hist',
                  'kdj_k', 'kdj_d', 'kdj_j',
                  'boll_upper', 'boll_middle', 'boll_lower',
                  'volume_ma5', 'volume_ma10', 'volume_ratio']
    
    print("\n✓ 计算的指标:")
    for indicator in indicators:
        if indicator in df_with_indicators.columns:
            non_null = df_with_indicators[indicator].notna().sum()
            print(f"  {indicator}: {non_null}/{len(df)} 条有效数据")
    
    # 显示最后一条记录的指标
    last_row = df_with_indicators.iloc[-1]
    print(f"\n最新数据 ({last_row['date']}):")
    print(f"  收盘价: {last_row['close']:.2f}")
    print(f"  MA20: {last_row['ma20']:.2f}")
    print(f"  RSI: {last_row['rsi']:.2f}")
    print(f"  MACD: {last_row['macd']:.4f}")
    print(f"  KDJ_K: {last_row['kdj_k']:.2f}")
    print(f"  布林上轨: {last_row['boll_upper']:.2f}")
    print(f"  量比: {last_row['volume_ratio']:.2f}")


def test_aggregated_layer():
    """测试聚合层"""
    print("\n" + "="*60)
    print("测试Aggregated Layer")
    print("="*60)
    
    # 初始化
    cleaned = CleanedLayer()
    aggregated = AggregatedLayer()
    
    # 从Cleaned Layer读取数据
    print("\n从Cleaned Layer读取数据...")
    code = '600519'
    df = cleaned.get_daily_data(code, only_valid=True)
    
    if df is None or df.empty:
        print(f"✗ {code} 没有数据")
        return
    
    print(f"✓ 读取到 {len(df)} 条记录")
    
    # 计算并保存指标
    print(f"\n计算并保存技术指标...")
    count = aggregated.calculate_and_save_indicators(code, df)
    print(f"✓ 保存了 {count} 条指标记录")
    
    # 读取指标
    print(f"\n从Aggregated Layer读取指标...")
    df_indicators = aggregated.get_indicators(code)
    
    if df_indicators is not None:
        print(f"✓ 读取到 {len(df_indicators)} 条指标记录")
        
        # 显示最新指标
        last_row = df_indicators.iloc[-1]
        print(f"\n最新指标 ({last_row['date']}):")
        print(f"  MA20: {last_row['ma20']:.2f}")
        print(f"  RSI: {last_row['rsi']:.2f}")
        print(f"  MACD: {last_row['macd']:.4f}")
        print(f"  KDJ_K: {last_row['kdj_k']:.2f}")
        print(f"  量比: {last_row['volume_ratio']:.2f}")
    
    # 统计信息
    print("\n统计信息:")
    stats = aggregated.get_stats()
    print(f"  总记录: {stats['indicators']['total_records']:,}")
    print(f"  股票数: {stats['indicators']['total_stocks']}")


def test_batch_calculation():
    """测试批量计算"""
    print("\n" + "="*60)
    print("测试批量计算")
    print("="*60)
    
    cleaned = CleanedLayer()
    aggregated = AggregatedLayer()
    
    # 测试几只股票
    test_codes = ['600519', '000858', '600036']
    
    for code in test_codes:
        print(f"\n处理 {code}...")
        
        df = cleaned.get_daily_data(code, only_valid=True)
        if df is None or df.empty:
            print(f"  ✗ 没有数据")
            continue
        
        count = aggregated.calculate_and_save_indicators(code, df)
        print(f"  ✓ 保存了 {count} 条指标")
    
    # 最终统计
    stats = aggregated.get_stats()
    print(f"\n总计:")
    print(f"  总记录: {stats['indicators']['total_records']:,}")
    print(f"  股票数: {stats['indicators']['total_stocks']}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  Aggregated Layer 测试工具")
    print("="*60)
    
    try:
        # 测试1: 特征计算引擎
        test_feature_engine()
        
        # 测试2: 聚合层
        test_aggregated_layer()
        
        # 测试3: 批量计算
        test_batch_calculation()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

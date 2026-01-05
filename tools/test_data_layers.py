# -*- coding: utf-8 -*-
"""
测试数据层架构

测试 Raw -> Cleaned -> Aggregated 数据流
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from datetime import datetime, timedelta
from src.data.layers import RawLayer, CleanedLayer, DailyDataValidator

def test_daily_data_flow():
    """测试日线数据流程"""
    print("\n" + "="*60)
    print("测试日线数据流程")
    print("="*60)
    
    # 1. 创建模拟数据
    print("\n1. 创建模拟数据...")
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(10, 0, -1)]
    
    # 正常数据
    normal_data = pd.DataFrame({
        'code': ['600519'] * 10,
        'date': dates,
        'open': [1400 + i*10 for i in range(10)],
        'high': [1420 + i*10 for i in range(10)],
        'low': [1390 + i*10 for i in range(10)],
        'close': [1410 + i*10 for i in range(10)],
        'volume': [1000000 + i*100000 for i in range(10)],
        'amount': [1.4e9 + i*1e8 for i in range(10)],
    })
    
    # 添加一些异常数据
    abnormal_data = pd.DataFrame({
        'code': ['600000'] * 3,
        'date': dates[:3],
        'open': [10, -5, 15],      # 第2条有负数
        'high': [12, 8, 18],
        'low': [8, 3, 14],
        'close': [11, 7, 16],
        'volume': [1000000, 0, 2000000],  # 第2条停牌
        'amount': [1e9, 0, 2e9],
    })
    
    test_data = pd.concat([normal_data, abnormal_data], ignore_index=True)
    print(f"创建了 {len(test_data)} 条测试数据")
    
    # 2. 保存到Raw Layer
    print("\n2. 保存到Raw Layer...")
    raw_layer = RawLayer()
    saved_count = raw_layer.save_daily_data(test_data, source='test')
    print(f"✓ 保存了 {saved_count} 条原始数据")
    
    # 3. 验证数据
    print("\n3. 验证数据...")
    validation_stats = DailyDataValidator.validate_dataframe(test_data)
    print(f"总记录数: {validation_stats['total']}")
    print(f"有效记录: {validation_stats['valid']} ({validation_stats['valid_rate']*100:.1f}%)")
    print(f"无效记录: {validation_stats['invalid']}")
    print(f"警告记录: {validation_stats['warnings']}")
    
    if validation_stats['error_types']:
        print("\n错误类型统计:")
        for error_type, count in validation_stats['error_types'].items():
            print(f"  - {error_type}: {count}")
    
    # 4. 清洗并保存到Cleaned Layer
    print("\n4. 清洗并保存到Cleaned Layer...")
    cleaned_layer = CleanedLayer()
    clean_stats = cleaned_layer.clean_and_save_daily_data(test_data, source='test')
    print(f"✓ 清洗完成:")
    print(f"  - 总记录: {clean_stats['total']}")
    print(f"  - 有效: {clean_stats['valid']}")
    print(f"  - 无效: {clean_stats['invalid']}")
    print(f"  - 有效率: {clean_stats['valid_rate']*100:.1f}%")
    
    # 5. 从Cleaned Layer读取数据
    print("\n5. 从Cleaned Layer读取数据...")
    
    # 读取贵州茅台的数据（只要有效数据）
    df_600519 = cleaned_layer.get_daily_data('600519', only_valid=True)
    if df_600519 is not None:
        print(f"✓ 600519 有效数据: {len(df_600519)} 条")
        print(f"  日期范围: {df_600519['date'].min()} ~ {df_600519['date'].max()}")
    
    # 读取600000的数据（包括无效数据）
    df_600000 = cleaned_layer.get_daily_data('600000', only_valid=False)
    if df_600000 is not None:
        print(f"✓ 600000 全部数据: {len(df_600000)} 条")
        invalid_count = len(df_600000[df_600000['is_valid'] == 0])
        print(f"  其中无效: {invalid_count} 条")
        
        # 显示无效数据的错误信息
        if invalid_count > 0:
            print("\n  无效数据详情:")
            for _, row in df_600000[df_600000['is_valid'] == 0].iterrows():
                print(f"    日期: {row['date']}, 错误: {row['validation_errors']}")
    
    # 6. 统计信息
    print("\n6. 数据层统计信息...")
    
    raw_stats = raw_layer.get_stats()
    print("\nRaw Layer:")
    print(f"  日线数据: {raw_stats['daily']['total_records']} 条, {raw_stats['daily']['total_stocks']} 只股票")
    
    cleaned_stats = cleaned_layer.get_stats()
    print("\nCleaned Layer:")
    print(f"  日线数据: {cleaned_stats['daily']['total_records']} 条")
    print(f"  有效数据: {cleaned_stats['daily']['valid_records']} 条 ({cleaned_stats['daily']['valid_rate']*100:.1f}%)")
    print(f"  停牌数据: {cleaned_stats['daily']['suspended_records']} 条")
    print(f"  股票数量: {cleaned_stats['daily']['total_stocks']} 只")


def test_data_recovery():
    """测试数据恢复功能"""
    print("\n" + "="*60)
    print("测试数据恢复功能")
    print("="*60)
    
    print("\n场景: 如果Cleaned Layer数据损坏，可以从Raw Layer重新清洗")
    
    raw_layer = RawLayer()
    cleaned_layer = CleanedLayer()
    
    # 从Raw Layer读取原始数据
    raw_df = raw_layer.get_daily_data('600519')
    
    if raw_df is not None:
        print(f"\n✓ 从Raw Layer读取到 {len(raw_df)} 条原始数据")
        
        # 重新清洗
        print("重新清洗数据...")
        clean_stats = cleaned_layer.clean_and_save_daily_data(raw_df, source='recovery')
        print(f"✓ 恢复完成: {clean_stats['valid']}/{clean_stats['total']} 条有效数据")
    else:
        print("✗ Raw Layer中没有数据")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  数据层架构测试工具")
    print("="*60)
    
    try:
        # 测试1: 数据流程
        test_daily_data_flow()
        
        # 测试2: 数据恢复
        test_data_recovery()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

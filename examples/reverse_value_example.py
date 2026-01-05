#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逆向价值选股策略 - 快速开始示例
Quick Start Example for Reverse Value Strategy

展示如何使用逆向价值策略进行选股
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import StockDatabase
from src.business.strategies.reverse_value import ReverseValueStrategy


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("=" * 80)
    print("示例1: 基本使用 - 扫描股票池")
    print("=" * 80)
    print()
    
    # 初始化
    db = StockDatabase("data/a_share.db")
    strategy = ReverseValueStrategy(db=db)
    
    print(f"策略: {strategy.name}")
    print()
    
    # 扫描股票池（小规模测试）
    print("扫描参数:")
    print("  市值范围: 50-200亿")
    print("  最多扫描: 30只")
    print()
    
    signals = strategy.scan(
        min_cap=50e8,
        max_cap=200e8,
        max_stocks=30,
        check_liquidity=True
    )
    
    if not signals.empty:
        print(f"✅ 找到 {len(signals)} 个符合条件的股票\n")
        
        # 显示结果
        for idx, row in signals.iterrows():
            print(f"{idx+1}. {row['name']} ({row['code']})")
            print(f"   价格: ¥{row['price']:.2f}")
            print(f"   市值: {row['market_cap']:.1f}亿")
            
            # 估值信息
            if 'valuation' in row and isinstance(row['valuation'], dict):
                val = row['valuation']
                print(f"   估值: PE分位={val.get('pe_percentile', 0):.1f}%, PB分位={val.get('pb_percentile', 0):.1f}%")
            
            print()
    else:
        print("❌ 未找到符合条件的股票")
        print("提示: 可能当前市场不在周期底部，或筛选条件过于严格")
    
    print()


def example_2_check_single_stock():
    """示例2: 检查单只股票"""
    print("=" * 80)
    print("示例2: 检查单只股票")
    print("=" * 80)
    print()
    
    db = StockDatabase("data/a_share.db")
    strategy = ReverseValueStrategy(db=db)
    
    # 测试几只股票
    test_stocks = [
        ('sh.600000', '浦发银行'),
        ('sz.000001', '平安银行'),
        ('sh.600519', '贵州茅台'),
    ]
    
    for code, name in test_stocks:
        print(f"检查 {name} ({code})...")
        
        # 跳过质量检查（如果没有财务数据）
        signal = strategy.check_signal(
            code=code,
            skip_quality=True
        )
        
        if signal:
            print(f"✅ 符合逆向价值策略")
            print(f"   价格: ¥{signal['price']:.2f}")
            
            # 估值
            if 'valuation' in signal and signal['valuation']:
                val = signal['valuation']
                print(f"   估值: PE分位={val.get('pe_percentile', 0):.1f}%, PB分位={val.get('pb_percentile', 0):.1f}%")
            
            # 周期
            if 'cycle' in signal and signal['cycle']:
                cyc = signal['cycle']
                print(f"   周期: 乖离率={cyc.get('deviation', 0):.1f}%")
            
            # 逆向
            if 'reverse' in signal and signal['reverse']:
                rev = signal['reverse']
                print(f"   逆向: 缩量企稳={rev.get('has_reverse_signal', False)}")
        else:
            print(f"❌ 不符合策略")
        
        print()


def example_3_test_filters():
    """示例3: 测试各个过滤器"""
    print("=" * 80)
    print("示例3: 测试各个过滤器")
    print("=" * 80)
    print()
    
    db = StockDatabase("data/a_share.db")
    strategy = ReverseValueStrategy(db=db)
    
    test_code = 'sh.600000'
    test_name = '浦发银行'
    
    print(f"测试股票: {test_name} ({test_code})")
    print()
    
    # 1. 防守过滤
    print("【1. 防守过滤器】避免永久损失")
    passed, reason = strategy.check_defense_filter(test_code, test_name)
    print(f"结果: {'✅ 通过' if passed else '❌ 未通过'}")
    print(f"原因: {reason}")
    print()
    
    # 2. 估值过滤
    print("【2. 估值过滤器】寻找低估值")
    passed, info = strategy.check_valuation_filter(test_code)
    print(f"结果: {'✅ 通过' if passed else '❌ 未通过'}")
    if isinstance(info, dict) and 'current_pe' in info:
        print(f"当前PE: {info['current_pe']:.2f} (历史分位: {info['pe_percentile']:.1f}%)")
        print(f"当前PB: {info['current_pb']:.2f} (历史分位: {info['pb_percentile']:.1f}%)")
        print(f"历史数据: {info['historical_days']}天")
    else:
        print(f"信息: {info.get('reason', info)}")
    print()
    
    # 3. 周期过滤
    print("【3. 周期过滤器】寻找周期底部")
    passed, info = strategy.check_cycle_filter(test_code)
    print(f"结果: {'✅ 通过' if passed else '❌ 未通过'}")
    if isinstance(info, dict) and 'current_price' in info:
        print(f"当前价: ¥{info['current_price']:.2f}")
        print(f"MA250: ¥{info['ma250']:.2f}")
        print(f"乖离率: {info['deviation']:.1f}%")
        print(f"在均线下方: {info['below_ma']}")
        print(f"已企稳: {info['is_stabilizing']}")
    else:
        print(f"信息: {info.get('reason', info)}")
    print()
    
    # 4. 逆向信号
    print("【4. 逆向信号检查】寻找缩量企稳")
    passed, info = strategy.check_reverse_signal(test_code)
    print(f"结果: {'✅ 通过' if passed else '❌ 未通过'}")
    if isinstance(info, dict):
        print(f"下跌: {info.get('is_declining', False)}")
        print(f"缩量: {info.get('is_shrinking', False)}")
        print(f"企稳: {info.get('is_stabilizing', False)}")
        if 'recent_volumes' in info:
            print(f"最近成交量: {info['recent_volumes']}")
    else:
        print(f"信息: {info.get('reason', info)}")
    print()


def example_4_custom_parameters():
    """示例4: 自定义参数"""
    print("=" * 80)
    print("示例4: 自定义参数 - 扩大搜索范围")
    print("=" * 80)
    print()
    
    db = StockDatabase("data/a_share.db")
    strategy = ReverseValueStrategy(
        db=db,
        min_avg_turnover=5e7  # 降低流动性要求到5000万
    )
    
    print("自定义参数:")
    print("  市值范围: 30-1000亿（扩大范围）")
    print("  流动性要求: 5000万（降低要求）")
    print("  最多扫描: 50只")
    print()
    
    signals = strategy.scan(
        min_cap=30e8,   # 降低到30亿
        max_cap=1000e8,  # 提高到1000亿
        max_stocks=50,
        check_liquidity=True
    )
    
    if not signals.empty:
        print(f"✅ 找到 {len(signals)} 个符合条件的股票\n")
        
        # 按估值分位数排序，显示前5个
        if 'pe_percentile' in signals.columns:
            signals_sorted = signals.sort_values('pe_percentile')
            print("估值最低的5只股票:")
            for idx, row in signals_sorted.head(5).iterrows():
                print(f"{idx+1}. {row['name']} ({row['code']})")
                print(f"   PE分位: {row['pe_percentile']:.1f}%")
                print(f"   市值: {row['market_cap']:.1f}亿")
                print()
    else:
        print("❌ 未找到符合条件的股票")
    
    print()


def example_5_integration_with_other_strategies():
    """示例5: 与其他策略组合"""
    print("=" * 80)
    print("示例5: 与其他策略组合使用")
    print("=" * 80)
    print()
    
    from src.business.strategies.volume_shrink import VolumeShrinkStrategy
    import pandas as pd
    
    db = StockDatabase("data/a_share.db")
    
    # 逆向价值策略（长期）
    reverse_strategy = ReverseValueStrategy(db=db)
    print("1. 运行逆向价值策略（长期持有）...")
    reverse_signals = reverse_strategy.scan(
        min_cap=50e8,
        max_cap=200e8,
        max_stocks=30
    )
    print(f"   找到 {len(reverse_signals)} 个逆向价值机会")
    print()
    
    # 缩量三连跌策略（短期）
    volume_strategy = VolumeShrinkStrategy(db=db)
    print("2. 运行缩量三连跌策略（短期交易）...")
    volume_signals = volume_strategy.scan(
        min_cap=50e8,
        max_cap=200e8,
        max_stocks=30,
        use_volume_stabilize=True,
        check_market=False
    )
    print(f"   找到 {len(volume_signals)} 个短期交易机会")
    print()
    
    # 找交集：既有长期价值，又有短期技术信号
    if not reverse_signals.empty and not volume_signals.empty:
        print("3. 寻找交集（既有价值又有技术信号）...")
        
        reverse_codes = set(reverse_signals['code'].values)
        volume_codes = set(volume_signals['code'].values)
        
        common_codes = reverse_codes & volume_codes
        
        if common_codes:
            print(f"✅ 找到 {len(common_codes)} 个同时符合两种策略的股票:")
            print()
            
            for code in common_codes:
                reverse_row = reverse_signals[reverse_signals['code'] == code].iloc[0]
                volume_row = volume_signals[volume_signals['code'] == code].iloc[0]
                
                print(f"• {reverse_row['name']} ({code})")
                print(f"  价格: ¥{reverse_row['price']:.2f}")
                print(f"  逆向价值: PE分位={reverse_row.get('pe_percentile', 0):.1f}%")
                print(f"  短期技术: 跌幅={volume_row.get('decline_rate', 0)*100:.1f}%")
                print()
        else:
            print("❌ 没有同时符合两种策略的股票")
    
    print()


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "逆向价值选股策略 - 快速开始" + " " * 20 + "║")
    print("║" + " " * 15 + "基于霍华德·马克斯《投资最重要的事》" + " " * 15 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    examples = [
        ("1", "基本使用 - 扫描股票池", example_1_basic_usage),
        ("2", "检查单只股票", example_2_check_single_stock),
        ("3", "测试各个过滤器", example_3_test_filters),
        ("4", "自定义参数", example_4_custom_parameters),
        ("5", "与其他策略组合", example_5_integration_with_other_strategies),
    ]
    
    print("请选择示例:")
    for num, desc, _ in examples:
        print(f"  {num}. {desc}")
    print("  0. 运行所有示例")
    print()
    
    choice = input("请输入选项 (0-5): ").strip()
    print()
    
    if choice == "0":
        # 运行所有示例
        for num, desc, func in examples:
            try:
                func()
                input("按回车继续...")
                print("\n")
            except Exception as e:
                print(f"❌ 示例 {num} 执行失败: {e}")
                print()
    else:
        # 运行单个示例
        for num, desc, func in examples:
            if choice == num:
                try:
                    func()
                except Exception as e:
                    print(f"❌ 执行失败: {e}")
                    import traceback
                    traceback.print_exc()
                break
        else:
            print("❌ 无效选项")
    
    print("\n")
    print("=" * 80)
    print("更多信息请查看: REVERSE_VALUE_STRATEGY_GUIDE.md")
    print("=" * 80)
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()

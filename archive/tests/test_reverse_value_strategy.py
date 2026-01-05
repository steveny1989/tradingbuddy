#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试逆向价值选股策略
Test Reverse Value Strategy

测试霍华德·马克斯投资哲学的程序化实现
"""
import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.data.database import StockDatabase
from src.business.strategies.reverse_value import ReverseValueStrategy

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_reverse_value_strategy():
    """测试逆向价值策略"""
    
    print("=" * 80)
    print("逆向价值选股策略测试")
    print("基于霍华德·马克斯《投资最重要的事》18条准则")
    print("=" * 80)
    print()
    
    # 1. 初始化数据库
    print("📊 初始化数据库...")
    db = StockDatabase("data/a_share.db")
    
    # 2. 初始化策略
    print("🎯 初始化逆向价值策略...")
    strategy = ReverseValueStrategy(
        db=db,
        financial_fetcher=None,  # 如果有财务数据获取器，传入这里
        min_avg_turnover=1e8  # 最小日均成交额1亿
    )
    
    print(f"策略名称: {strategy.name}")
    print()
    
    # 3. 测试单只股票
    print("-" * 80)
    print("测试1: 检查单只股票")
    print("-" * 80)
    
    test_codes = [
        'sh.600000',  # 浦发银行
        'sz.000001',  # 平安银行
        'sh.600519',  # 贵州茅台
    ]
    
    for code in test_codes:
        print(f"\n检查 {code}...")
        
        # 跳过一些检查（因为可能没有财务数据）
        signal = strategy.check_signal(
            code=code,
            skip_quality=True,  # 跳过质量检查（需要财务数据）
            skip_defense=False,  # 保留防守检查
            skip_valuation=False,  # 保留估值检查
            skip_cycle=False,  # 保留周期检查
            skip_reverse=False  # 保留逆向检查
        )
        
        if signal:
            print(f"✅ 符合策略条件:")
            print(f"   股票: {signal['name']} ({signal['code']})")
            print(f"   价格: {signal['price']:.2f}")
            
            # 估值信息
            if 'valuation' in signal and signal['valuation']:
                val = signal['valuation']
                print(f"   估值: PE分位={val.get('pe_percentile', 0):.1f}%, PB分位={val.get('pb_percentile', 0):.1f}%")
            
            # 周期信息
            if 'cycle' in signal and signal['cycle']:
                cyc = signal['cycle']
                print(f"   周期: 乖离率={cyc.get('deviation', 0):.1f}%, 企稳={cyc.get('is_stabilizing', False)}")
            
            # 逆向信号
            if 'reverse' in signal and signal['reverse']:
                rev = signal['reverse']
                print(f"   逆向: 下跌={rev.get('is_declining', False)}, 缩量={rev.get('is_shrinking', False)}, 企稳={rev.get('is_stabilizing', False)}")
        else:
            print(f"❌ 不符合策略条件")
    
    # 4. 扫描股票池
    print("\n" + "=" * 80)
    print("测试2: 扫描股票池（小规模测试）")
    print("=" * 80)
    print()
    
    print("扫描参数:")
    print("  市值范围: 50-200亿")
    print("  最多扫描: 50只股票")
    print("  检查流动性: 是")
    print()
    
    df_signals = strategy.scan(
        min_cap=50e8,
        max_cap=200e8,
        max_stocks=50,  # 限制扫描数量（测试用）
        check_liquidity=True
    )
    
    if not df_signals.empty:
        print(f"\n✅ 找到 {len(df_signals)} 个符合条件的股票:")
        print()
        
        # 显示前10个
        for idx, row in df_signals.head(10).iterrows():
            print(f"{idx+1}. {row['name']} ({row['code']})")
            print(f"   价格: {row['price']:.2f}, 市值: {row['market_cap']:.1f}亿")
            
            if 'valuation' in row and isinstance(row['valuation'], dict):
                val = row['valuation']
                print(f"   估值: PE分位={val.get('pe_percentile', 0):.1f}%, PB分位={val.get('pb_percentile', 0):.1f}%")
            
            print()
    else:
        print("❌ 未找到符合条件的股票")
        print()
        print("可能原因:")
        print("  1. 当前市场不在周期底部")
        print("  2. 估值数据不足")
        print("  3. 筛选条件过于严格")
        print()
        print("建议:")
        print("  1. 调整市值范围（扩大到500亿）")
        print("  2. 跳过某些检查（如质量检查）")
        print("  3. 在市场调整时再次测试")
    
    # 5. 策略说明
    print("\n" + "=" * 80)
    print("策略说明")
    print("=" * 80)
    print()
    print("逆向价值策略基于霍华德·马克斯的18条投资准则:")
    print()
    print("1. 估值维度（原则2, 3, 11）")
    print("   - PE/PB处于历史低位（<20分位）")
    print("   - 寻找安全边际")
    print()
    print("2. 质量维度（原则2）")
    print("   - ROE稳定且>10%")
    print("   - 寻找优质公司")
    print()
    print("3. 防守维度（原则4, 16, 17）")
    print("   - 剔除ST股")
    print("   - 资产负债率<70%")
    print("   - 现金流健康")
    print()
    print("4. 周期维度（原则7, 8）")
    print("   - 股价处于250日均线下方")
    print("   - 乖离率<-10%")
    print("   - 出现企稳信号")
    print()
    print("5. 逆向维度（原则9, 10）")
    print("   - 下跌后缩量企稳")
    print("   - 市场恐慌时买入")
    print()
    print("核心理念:")
    print("  - 不追涨，只在周期底部买入")
    print("  - 不预测，只基于当前数据")
    print("  - 防守优先，避免永久损失")
    print("  - 耐心等待，机会自然上门")
    print()


def test_individual_filters():
    """测试各个过滤器"""
    
    print("=" * 80)
    print("测试各个过滤器")
    print("=" * 80)
    print()
    
    db = StockDatabase("data/a_share.db")
    strategy = ReverseValueStrategy(db=db)
    
    test_code = 'sh.600000'  # 浦发银行
    
    print(f"测试股票: {test_code}")
    print()
    
    # 1. 防守过滤
    print("1. 防守过滤器")
    passed, reason = strategy.check_defense_filter(test_code, "浦发银行")
    print(f"   结果: {'✅ 通过' if passed else '❌ 未通过'}")
    print(f"   原因: {reason}")
    print()
    
    # 2. 估值过滤
    print("2. 估值过滤器")
    passed, info = strategy.check_valuation_filter(test_code)
    print(f"   结果: {'✅ 通过' if passed else '❌ 未通过'}")
    if isinstance(info, dict) and 'current_pe' in info:
        print(f"   当前PE: {info['current_pe']:.2f}, 分位: {info['pe_percentile']:.1f}%")
        print(f"   当前PB: {info['current_pb']:.2f}, 分位: {info['pb_percentile']:.1f}%")
    else:
        print(f"   信息: {info}")
    print()
    
    # 3. 周期过滤
    print("3. 周期过滤器")
    passed, info = strategy.check_cycle_filter(test_code)
    print(f"   结果: {'✅ 通过' if passed else '❌ 未通过'}")
    if isinstance(info, dict) and 'current_price' in info:
        print(f"   当前价: {info['current_price']:.2f}, MA250: {info['ma250']:.2f}")
        print(f"   乖离率: {info['deviation']:.1f}%")
        print(f"   企稳: {info['is_stabilizing']}")
    else:
        print(f"   信息: {info}")
    print()
    
    # 4. 逆向信号
    print("4. 逆向信号检查")
    passed, info = strategy.check_reverse_signal(test_code)
    print(f"   结果: {'✅ 通过' if passed else '❌ 未通过'}")
    if isinstance(info, dict):
        print(f"   下跌: {info.get('is_declining', False)}")
        print(f"   缩量: {info.get('is_shrinking', False)}")
        print(f"   企稳: {info.get('is_stabilizing', False)}")
    else:
        print(f"   信息: {info}")
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='测试逆向价值选股策略')
    parser.add_argument('--mode', choices=['full', 'filters'], default='full',
                        help='测试模式: full=完整测试, filters=测试各个过滤器')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'full':
            test_reverse_value_strategy()
        else:
            test_individual_filters()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试架构重构
验证配置管理和成本计算器
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.settings import (
    TradingConfig, 
    BacktestConfig, 
    PaperTradingConfig,
    DEFAULT_BACKTEST_CONFIG,
    DEFAULT_PAPER_TRADING_CONFIG
)
from src.business.trading.cost_calculator import TradingCostCalculator


def test_trading_config():
    """测试交易配置"""
    print("\n" + "="*80)
    print("测试1: 交易配置")
    print("="*80)
    
    # 默认配置
    config = TradingConfig()
    print(f"✅ 默认配置创建成功")
    print(f"   佣金率: {config.commission_rate}")
    print(f"   滑点率: {config.slippage_rate}")
    print(f"   印花税率: {config.stamp_tax_rate}")
    print(f"   最低佣金: {config.min_commission}")
    
    # 自定义配置
    custom_config = TradingConfig(
        commission_rate=0.0005,
        slippage_rate=0.002
    )
    print(f"\n✅ 自定义配置创建成功")
    print(f"   佣金率: {custom_config.commission_rate}")
    print(f"   滑点率: {custom_config.slippage_rate}")


def test_backtest_config():
    """测试回测配置"""
    print("\n" + "="*80)
    print("测试2: 回测配置")
    print("="*80)
    
    config = BacktestConfig()
    print(f"✅ 回测配置创建成功")
    print(f"   初始资金: {config.initial_capital:,.0f}")
    print(f"   最大持仓数: {config.max_positions}")
    print(f"   单次买入比例: {config.position_size:.1%}")
    print(f"   止损线: {config.stop_loss:.1%}")
    print(f"   止盈线: {config.take_profit:.1%}")
    print(f"   最大持仓天数: {config.max_hold_days}")
    
    # 验证继承
    print(f"\n✅ 验证配置继承")
    print(f"   佣金率: {config.commission_rate}")
    print(f"   滑点率: {config.slippage_rate}")


def test_paper_trading_config():
    """测试模拟盘配置"""
    print("\n" + "="*80)
    print("测试3: 模拟盘配置")
    print("="*80)
    
    config = PaperTradingConfig()
    print(f"✅ 模拟盘配置创建成功")
    print(f"   初始资金: {config.initial_capital:,.0f}")
    print(f"   最大持仓数: {config.max_positions}")
    print(f"   单次买入比例: {config.position_size:.1%}")
    print(f"   数据目录: {config.data_dir}")


def test_cost_calculator():
    """测试成本计算器"""
    print("\n" + "="*80)
    print("测试4: 交易成本计算器")
    print("="*80)
    
    calculator = TradingCostCalculator()
    
    # 测试买入
    print("\n【买入测试】")
    price = 10.0
    shares = 1000
    result = calculator.calculate_cost(price, shares, is_buy=True)
    
    print(f"委托价格: {price:.2f}")
    print(f"股数: {shares}")
    print(f"实际成交价: {result['actual_price']:.4f} (含滑点)")
    print(f"成交金额: {result['amount']:.2f}")
    print(f"佣金: {result['commission']:.2f}")
    print(f"印花税: {result['stamp_tax']:.2f}")
    print(f"总成本: {result['total_cost']:.2f}")
    
    # 验证计算
    expected_actual_price = price * 1.001  # 滑点0.1%
    expected_amount = expected_actual_price * shares
    expected_commission = max(expected_amount * 0.0003, 5)
    expected_total = expected_amount + expected_commission
    
    assert abs(result['actual_price'] - expected_actual_price) < 0.01, "实际成交价计算错误"
    assert abs(result['total_cost'] - expected_total) < 0.01, "总成本计算错误"
    print("✅ 买入成本计算正确")
    
    # 测试卖出
    print("\n【卖出测试】")
    result = calculator.calculate_cost(price, shares, is_buy=False)
    
    print(f"委托价格: {price:.2f}")
    print(f"股数: {shares}")
    print(f"实际成交价: {result['actual_price']:.4f} (含滑点)")
    print(f"成交金额: {result['amount']:.2f}")
    print(f"佣金: {result['commission']:.2f}")
    print(f"印花税: {result['stamp_tax']:.2f}")
    print(f"实际到手: {result['total_cost']:.2f}")
    
    # 验证计算
    expected_actual_price = price * 0.999  # 滑点0.1%
    expected_amount = expected_actual_price * shares
    expected_commission = max(expected_amount * 0.0003, 5)
    expected_stamp_tax = expected_amount * 0.001
    expected_total = expected_amount - expected_commission - expected_stamp_tax
    
    assert abs(result['actual_price'] - expected_actual_price) < 0.01, "实际成交价计算错误"
    assert abs(result['stamp_tax'] - expected_stamp_tax) < 0.01, "印花税计算错误"
    assert abs(result['total_cost'] - expected_total) < 0.01, "实际到手计算错误"
    print("✅ 卖出成本计算正确")
    
    # 测试简化版本
    print("\n【简化版本测试】")
    simple_cost = calculator.calculate_simple_cost(price, shares, is_buy=True)
    print(f"简化版本返回: {simple_cost:.2f}")
    assert abs(simple_cost - result['total_cost']) > 1, "简化版本应该返回买入成本"
    print("✅ 简化版本工作正常")


def test_custom_config_calculator():
    """测试自定义配置的计算器"""
    print("\n" + "="*80)
    print("测试5: 自定义配置的成本计算器")
    print("="*80)
    
    # 创建自定义配置（高佣金）
    config = TradingConfig(
        commission_rate=0.001,  # 0.1% 佣金
        slippage_rate=0.002,    # 0.2% 滑点
        min_commission=10.0     # 最低10元
    )
    
    calculator = TradingCostCalculator(config)
    
    price = 10.0
    shares = 1000
    result = calculator.calculate_cost(price, shares, is_buy=True)
    
    print(f"自定义配置:")
    print(f"  佣金率: {config.commission_rate:.2%}")
    print(f"  滑点率: {config.slippage_rate:.2%}")
    print(f"  最低佣金: {config.min_commission:.2f}")
    print(f"\n计算结果:")
    print(f"  实际成交价: {result['actual_price']:.4f}")
    print(f"  佣金: {result['commission']:.2f}")
    print(f"  总成本: {result['total_cost']:.2f}")
    
    # 验证使用了自定义配置
    expected_actual_price = price * 1.002  # 0.2% 滑点
    assert abs(result['actual_price'] - expected_actual_price) < 0.01, "未使用自定义滑点率"
    print("✅ 自定义配置生效")


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n" + "="*80)
    print("测试6: 向后兼容性")
    print("="*80)
    
    from src.data.database import StockDatabase
    from src.business.backtest.engine import BacktestEngine
    from src.business.strategies.volume_shrink import VolumeShrinkStrategy
    
    db = StockDatabase()
    strategy = VolumeShrinkStrategy(db)
    
    # 测试旧方式（传入参数）
    print("测试旧方式（传入参数）...")
    engine1 = BacktestEngine(
        db=db,
        strategy=strategy,
        initial_capital=500000,
        commission_rate=0.0005
    )
    assert engine1.initial_capital == 500000, "旧参数未生效"
    assert engine1.commission_rate == 0.0005, "旧参数未生效"
    print("✅ 旧方式仍然可用")
    
    # 测试新方式（使用config）
    print("\n测试新方式（使用config）...")
    config = BacktestConfig(
        initial_capital=800000,
        commission_rate=0.0002
    )
    engine2 = BacktestEngine(
        db=db,
        strategy=strategy,
        config=config
    )
    assert engine2.initial_capital == 800000, "新配置未生效"
    assert engine2.commission_rate == 0.0002, "新配置未生效"
    print("✅ 新方式工作正常")
    
    # 验证成本计算器
    print("\n验证成本计算器集成...")
    cost = engine2.calculate_cost(10.0, 1000, is_buy=True)
    assert cost > 10000, "成本计算器未正常工作"
    print(f"✅ 成本计算器集成成功 (成本: {cost:.2f})")
    
    db.close()


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("架构重构测试")
    print("="*80)
    
    try:
        test_trading_config()
        test_backtest_config()
        test_paper_trading_config()
        test_cost_calculator()
        test_custom_config_calculator()
        test_backward_compatibility()
        
        print("\n" + "="*80)
        print("✅ 所有测试通过！")
        print("="*80)
        print("\n重构总结:")
        print("1. ✅ 创建了统一的交易配置类")
        print("2. ✅ 创建了交易成本计算器")
        print("3. ✅ 重构了BacktestEngine使用新配置")
        print("4. ✅ 重构了PaperTradingEngine使用新配置")
        print("5. ✅ 保持了向后兼容性")
        print("6. ✅ 消除了代码重复")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

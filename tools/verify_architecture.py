#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
架构验证脚本
验证项目架构是否符合设计规范
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_section(title):
    """打印章节标题"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}")


def check_file_exists(filepath, description):
    """检查文件是否存在"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists


def check_import(module_path, description):
    """检查模块是否可以导入"""
    try:
        __import__(module_path)
        print(f"✅ {description}: {module_path}")
        return True
    except ImportError as e:
        print(f"❌ {description}: {module_path} - {e}")
        return False


def check_inheritance(class_obj, base_class, description):
    """检查继承关系"""
    is_subclass = issubclass(class_obj, base_class)
    status = "✅" if is_subclass else "❌"
    print(f"{status} {description}")
    return is_subclass


def main():
    print("="*80)
    print("TradingBuddy 架构验证")
    print("="*80)
    
    all_passed = True
    
    # 1. 检查目录结构
    print_section("1. 目录结构检查")
    
    directories = [
        ("core/", "数据层目录"),
        ("strategy/", "业务层目录"),
        ("tests/", "测试目录"),
        ("tests/backtest/", "回测测试目录"),
        ("tests/debug/", "调试脚本目录"),
        ("tests/analysis/", "分析脚本目录"),
        ("tools/", "工具目录"),
        ("docs/", "文档目录"),
        ("data/", "数据目录"),
        ("archive/", "归档目录"),
        ("archive/web/", "Web功能归档"),
        ("archive/old_strategies/", "旧策略归档"),
    ]
    
    for dir_path, desc in directories:
        all_passed &= check_file_exists(dir_path, desc)
    
    # 2. 检查核心文件
    print_section("2. 核心文件检查")
    
    core_files = [
        # 应用层
        ("main.py", "数据管理入口 (应用层)"),
        ("paper_trading.py", "模拟盘入口 (应用层)"),
        ("show_stock.py", "查看股票 (应用层)"),
        # 数据层
        ("core/database.py", "数据库接口 (数据层)"),
        ("core/data_fetcher.py", "数据采集 (数据层)"),
        # 业务层
        ("strategy/base.py", "策略基类 (业务层)"),
        ("strategy/backtest_engine.py", "回测引擎 (业务层)"),
        ("strategy/volume_shrink_strategy.py", "缩量三连跌策略 (业务层)"),
        ("strategy/ma_crossover_strategy.py", "均线突破策略 (业务层)"),
        # 工具层
        ("tools/verify_architecture.py", "架构验证 (工具层)"),
        ("tools/view_data.py", "查看数据 (工具层)"),
        ("tools/supplement_data.py", "补充数据 (工具层)"),
    ]
    
    for file_path, desc in core_files:
        all_passed &= check_file_exists(file_path, desc)
    
    # 3. 检查文档
    print_section("3. 文档检查")
    
    docs = [
        ("docs/ARCHITECTURE_EXPLANATION.md", "架构说明文档"),
        ("docs/ARCHITECTURE_ISSUES.md", "架构问题分析"),
        ("docs/CRITICAL_ISSUES_FIXED.md", "严重问题修复"),
        ("docs/BUG_FIX_SUMMARY.md", "Bug修复总结"),
        ("docs/PAPER_TRADING_GUIDE.md", "模拟盘指南"),
    ]
    
    for doc_path, desc in docs:
        all_passed &= check_file_exists(doc_path, desc)
    
    # 4. 检查模块导入
    print_section("4. 模块导入检查")
    
    imports = [
        ("core.database", "数据库模块"),
        ("core.data_fetcher", "数据采集模块"),
        ("strategy.base", "策略基类模块"),
        ("strategy.backtest_engine", "回测引擎模块"),
        ("strategy.volume_shrink_strategy", "缩量三连跌策略"),
        ("strategy.ma_crossover_strategy", "均线突破策略"),
    ]
    
    for module_path, desc in imports:
        all_passed &= check_import(module_path, desc)
    
    # 5. 检查策略继承关系
    print_section("5. 策略继承关系检查")
    
    try:
        from src.business.strategies.base import BaseStrategy, TechnicalStrategy
        from src.business.strategies.volume_shrink import VolumeShrinkStrategy
        from src.business.strategies.ma_crossover import MACrossoverStrategy
        
        all_passed &= check_inheritance(
            TechnicalStrategy, BaseStrategy,
            "TechnicalStrategy 继承 BaseStrategy"
        )
        all_passed &= check_inheritance(
            VolumeShrinkStrategy, TechnicalStrategy,
            "VolumeShrinkStrategy 继承 TechnicalStrategy"
        )
        all_passed &= check_inheritance(
            MACrossoverStrategy, TechnicalStrategy,
            "MACrossoverStrategy 继承 TechnicalStrategy"
        )
        all_passed &= check_inheritance(
            VolumeShrinkStrategy, BaseStrategy,
            "VolumeShrinkStrategy 继承 BaseStrategy (间接)"
        )
        all_passed &= check_inheritance(
            MACrossoverStrategy, BaseStrategy,
            "MACrossoverStrategy 继承 BaseStrategy (间接)"
        )
    except Exception as e:
        print(f"❌ 策略继承检查失败: {e}")
        all_passed = False
    
    # 6. 检查策略接口
    print_section("6. 策略接口检查")
    
    try:
        from src.business.strategies.base import BaseStrategy
        from src.business.strategies.volume_shrink import VolumeShrinkStrategy
        from src.business.strategies.ma_crossover import MACrossoverStrategy
        
        required_methods = ['get_stock_pool', 'check_signal', 'scan']
        
        for strategy_class in [VolumeShrinkStrategy, MACrossoverStrategy]:
            strategy_name = strategy_class.__name__
            for method in required_methods:
                has_method = hasattr(strategy_class, method)
                status = "✅" if has_method else "❌"
                print(f"{status} {strategy_name}.{method}()")
                all_passed &= has_method
    except Exception as e:
        print(f"❌ 策略接口检查失败: {e}")
        all_passed = False
    
    # 7. 检查废弃代码是否已归档
    print_section("7. 废弃代码检查")
    
    deprecated_files = [
        ("app.py", "Flask应用（应已归档）"),
        ("routes.py", "API路由（应已归档）"),
        ("strategy/strategy.py", "旧策略类（应已归档）"),
        ("strategy/shrinking_volume_strategy.py", "空文件（应已归档）"),
    ]
    
    for file_path, desc in deprecated_files:
        exists = Path(file_path).exists()
        status = "❌" if exists else "✅"
        print(f"{status} {desc}: {'存在（需归档）' if exists else '已归档'}")
        all_passed &= not exists
    
    # 8. 检查归档文件
    print_section("8. 归档文件检查")
    
    archived_files = [
        ("archive/web/app.py", "Flask应用"),
        ("archive/web/routes.py", "API路由"),
        ("archive/old_strategies/strategy.py", "旧策略类"),
    ]
    
    for file_path, desc in archived_files:
        check_file_exists(file_path, desc)
    
    # 9. 测试实例化
    print_section("9. 实例化测试")
    
    try:
        from src.data.database import StockDatabase
        from src.business.strategies.volume_shrink import VolumeShrinkStrategy
        from src.business.strategies.ma_crossover import MACrossoverStrategy
        
        db = StockDatabase("data/a_share.db")
        print("✅ StockDatabase 实例化成功")
        
        strategy1 = VolumeShrinkStrategy(db)
        print(f"✅ VolumeShrinkStrategy 实例化成功: {strategy1}")
        
        strategy2 = MACrossoverStrategy(db)
        print(f"✅ MACrossoverStrategy 实例化成功: {strategy2}")
        
        db.close()
        print("✅ 数据库连接关闭成功")
    except Exception as e:
        print(f"❌ 实例化测试失败: {e}")
        all_passed = False
    
    # 总结
    print_section("验证总结")
    
    if all_passed:
        print("✅ 所有检查通过！架构符合设计规范。")
        print("\n架构特点:")
        print("  • 清晰的分层架构（应用层 → 业务层 → 数据层 → 基础设施）")
        print("  • 统一的策略接口（BaseStrategy）")
        print("  • 完整的继承体系（TechnicalStrategy, FundamentalStrategy, QuantStrategy）")
        print("  • 整洁的目录结构（tests/, archive/, docs/）")
        print("  • 完善的文档（架构说明、问题分析、修复总结）")
        return 0
    else:
        print("❌ 部分检查未通过，请查看上述错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

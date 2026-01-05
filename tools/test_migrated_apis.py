#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试迁移后的 API

验证使用 DatabaseAdapter 后的 API 是否正常工作
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_web_routes():
    """测试 Web 路由是否能正常导入"""
    print("\n" + "="*60)
    print("测试 Web 路由导入")
    print("="*60)
    
    try:
        print("\n1. 测试 stocks 路由...")
        from src.web.routes import stocks
        print("   ✅ stocks 路由导入成功")
        print(f"   数据库类型: {type(stocks.db).__name__}")
        
        print("\n2. 测试 strategies 路由...")
        from src.web.routes import strategies
        print("   ✅ strategies 路由导入成功")
        print(f"   数据库类型: {type(strategies.db).__name__}")
        
        print("\n3. 测试 dashboard 路由...")
        from src.web.routes import dashboard
        print("   ✅ dashboard 路由导入成功")
        print(f"   数据库类型: {type(dashboard.db).__name__}")
        
        print("\n4. 测试 indices 路由...")
        from src.web.routes import indices
        print("   ✅ indices 路由导入成功")
        print(f"   数据库类型: {type(indices.db).__name__}")
        
        return True
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_diagnosis_modules():
    """测试诊断模块是否能正常导入"""
    print("\n" + "="*60)
    print("测试诊断模块导入")
    print("="*60)
    
    try:
        print("\n1. 测试 technical_analyzer...")
        from src.business.diagnosis.technical_analyzer import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
        print("   ✅ TechnicalAnalyzer 导入成功")
        print(f"   数据库类型: {type(analyzer.db).__name__}")
        
        return True
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_post_market_modules():
    """测试后市分析模块是否能正常导入"""
    print("\n" + "="*60)
    print("测试后市分析模块导入")
    print("="*60)
    
    try:
        print("\n1. 测试 portfolio_health...")
        from src.business.post_market.portfolio_health import TechnicalIndicators
        print("   ✅ TechnicalIndicators 导入成功")
        
        return True
    except Exception as e:
        print(f"   ❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n" + "="*60)
    print("测试基本功能")
    print("="*60)
    
    try:
        from src.data.database_adapter import DatabaseAdapter
        
        print("\n1. 测试数据读取...")
        db = DatabaseAdapter()
        df = db.get_daily_data('600519')
        print(f"   ✅ 读取成功: {len(df)} 条记录")
        
        print("\n2. 测试股票列表...")
        codes = db.get_all_stock_codes()
        print(f"   ✅ 获取成功: {len(codes)} 只股票")
        
        print("\n3. 测试统计信息...")
        stats = db.get_stats()
        print(f"   ✅ 统计成功:")
        print(f"      总股票: {stats['total_stocks']}")
        print(f"      总记录: {stats['total_records']:,}")
        
        return True
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("="*60)
    print("测试迁移后的模块")
    print("="*60)
    
    results = []
    
    # 测试 Web 路由
    results.append(("Web 路由", test_web_routes()))
    
    # 测试诊断模块
    results.append(("诊断模块", test_diagnosis_modules()))
    
    # 测试后市分析模块
    results.append(("后市分析模块", test_post_market_modules()))
    
    # 测试基本功能
    results.append(("基本功能", test_basic_functionality()))
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(success for _, success in results)
    
    if all_passed:
        print("\n✅ 所有测试通过！迁移成功！")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查错误信息")
        return 1

if __name__ == "__main__":
    sys.exit(main())

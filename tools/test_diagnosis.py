#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票诊断系统手动测试工具

测试所有分析器、诊断引擎和 API 端点
打印详细结果，用于手动验证系统功能
"""
import sys
import os
import json
import time
from typing import Dict, List
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.business.diagnosis.diagnosis_engine import StockDiagnosisEngine
from src.business.diagnosis.fundamental_analyzer import FundamentalAnalyzer
from src.business.diagnosis.market_comparison import MarketComparisonAnalyzer
from src.business.diagnosis.technical_analyzer import TechnicalAnalyzer
from src.business.post_market.sector_analysis import SectorAnalyzer
from src.business.post_market.capital_analysis import CapitalAnalyzer


# 测试用股票代码
TEST_STOCKS = [
    ('600519', '贵州茅台'),
    ('000001', '平安银行'),
    ('000858', '五粮液'),
    ('600036', '招商银行'),
]

# API 基础 URL
API_BASE_URL = 'http://localhost:5001'


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title: str):
    """打印子章节标题"""
    print(f"\n--- {title} ---")


def print_result(label: str, value, indent: int = 0):
    """打印结果"""
    prefix = "  " * indent
    if isinstance(value, dict):
        print(f"{prefix}{label}:")
        for k, v in value.items():
            print_result(k, v, indent + 1)
    elif isinstance(value, list):
        print(f"{prefix}{label}:")
        for i, item in enumerate(value):
            if isinstance(item, (dict, list)):
                print(f"{prefix}  [{i}]:")
                print_result("", item, indent + 2)
            else:
                print(f"{prefix}  - {item}")
    else:
        print(f"{prefix}{label}: {value}")


def test_technical_analyzer():
    """测试技术面分析器"""
    print_section("测试 1: 技术面分析器 (Technical Analyzer)")
    
    analyzer = TechnicalAnalyzer()
    
    for code, name in TEST_STOCKS[:2]:  # 测试前2只
        print_subsection(f"{name} ({code})")
        
        try:
            result = analyzer.analyze(code)
            
            print(f"✓ 评分: {result['score']}")
            print(f"✓ 状态: {result['status']}")
            print(f"✓ 描述: {result['message']}")
            
            details = result['details']
            print(f"\n详细数据:")
            print(f"  - 趋势: {details.get('trend')}")
            print(f"  - MA20位置: {details.get('ma20_position')}")
            print(f"  - MA20偏离度: {details.get('ma20_deviation')}%")
            print(f"  - RSI: {details.get('rsi')}")
            print(f"  - 量比: {details.get('volume_ratio')}")
            print(f"  - 当前价: {details.get('current_price')}")
            print(f"  - 涨跌幅: {details.get('change_rate')}%")
            
            pattern = details.get('candlestick_pattern')
            if pattern:
                print(f"  - K线形态: {pattern.get('name_cn')} ({pattern.get('signal_cn')})")
            
            print(f"  - 支撑位: {details.get('support_level')}")
            print(f"  - 阻力位: {details.get('resistance_level')}")
            
            print("✓ 技术面分析成功")
            
        except Exception as e:
            print(f"✗ 技术面分析失败: {e}")
    
    print("\n✓ 技术面分析器测试完成")


def test_fundamental_analyzer():
    """测试基本面分析器"""
    print_section("测试 2: 基本面分析器 (Fundamental Analyzer)")
    
    analyzer = FundamentalAnalyzer()
    
    for code, name in TEST_STOCKS[:2]:  # 测试前2只
        print_subsection(f"{name} ({code})")
        
        try:
            result = analyzer.analyze(code)
            
            print(f"✓ 评分: {result['score']}")
            print(f"✓ 状态: {result['status']}")
            print(f"✓ 描述: {result['message']}")
            
            details = result['details']
            print(f"\n财务指标:")
            print(f"  - PE: {details.get('pe')}")
            print(f"  - PB: {details.get('pb')}")
            print(f"  - ROE: {details.get('roe')}%")
            print(f"  - ROA: {details.get('roa')}%")
            print(f"  - 净利率: {details.get('net_margin')}%")
            print(f"  - 负债率: {details.get('debt_ratio')}%")
            print(f"  - 流动比率: {details.get('current_ratio')}")
            
            if details.get('profit_growth_yoy'):
                print(f"  - 利润增长(同比): {details['profit_growth_yoy']:.2f}%")
            
            if details.get('industry'):
                print(f"\n行业信息:")
                print(f"  - 所属行业: {details['industry']}")
                
                comparison = details.get('industry_comparison', {})
                if comparison:
                    print(f"  - ROE百分位: {comparison.get('roe_percentile')}%")
                    print(f"  - PE百分位: {comparison.get('pe_percentile')}%")
            
            print("✓ 基本面分析成功")
            
        except Exception as e:
            print(f"✗ 基本面分析失败: {e}")
    
    print("\n✓ 基本面分析器测试完成")


def test_sector_analyzer():
    """测试行业面分析器"""
    print_section("测试 3: 行业面分析器 (Sector Analyzer)")
    
    analyzer = SectorAnalyzer()
    
    for code, name in TEST_STOCKS[:2]:  # 测试前2只
        print_subsection(f"{name} ({code})")
        
        try:
            result = analyzer.generate_sector_report(code)
            
            print(f"✓ 状态: {result.get('status')}")
            print(f"✓ 描述: {result.get('message')}")
            
            print(f"\n行业信息:")
            print(f"  - 所属行业: {result.get('industry')}")
            print(f"  - 行业排名: {result.get('industry_rank')}")
            print(f"  - 相对强度: {result.get('relative_strength')}")
            print(f"  - 板块相关性: {result.get('correlation')}")
            
            print("✓ 行业面分析成功")
            
        except Exception as e:
            print(f"✗ 行业面分析失败: {e}")
    
    print("\n✓ 行业面分析器测试完成")


def test_capital_analyzer():
    """测试资金面分析器"""
    print_section("测试 4: 资金面分析器 (Capital Analyzer)")
    
    analyzer = CapitalAnalyzer()
    
    for code, name in TEST_STOCKS[:2]:  # 测试前2只
        print_subsection(f"{name} ({code})")
        
        try:
            result = analyzer.generate_capital_report(code)
            
            print(f"✓ 状态: {result.get('status')}")
            print(f"✓ 描述: {result.get('message')}")
            
            northbound = result.get('northbound', {})
            if northbound:
                print(f"\n北向资金:")
                print(f"  - 持股数: {northbound.get('shares')}")
                print(f"  - 持股比例: {northbound.get('percentage')}%")
                print(f"  - 变化: {northbound.get('change')}")
            
            capital_flow = result.get('capital_flow', {})
            if capital_flow:
                print(f"\n资金流向:")
                print(f"  - 主力净流入: {capital_flow.get('main_inflow')}")
                print(f"  - 超大单净流入: {capital_flow.get('super_large_inflow')}")
                print(f"  - 大单净流入: {capital_flow.get('large_inflow')}")
            
            print("✓ 资金面分析成功")
            
        except Exception as e:
            print(f"✗ 资金面分析失败: {e}")
    
    print("\n✓ 资金面分析器测试完成")


def test_market_comparison_analyzer():
    """测试大盘对比分析器"""
    print_section("测试 5: 大盘对比分析器 (Market Comparison Analyzer)")
    
    analyzer = MarketComparisonAnalyzer()
    
    for code, name in TEST_STOCKS[:2]:  # 测试前2只
        print_subsection(f"{name} ({code})")
        
        try:
            result = analyzer.analyze(code, days=30)
            
            print(f"✓ 评分: {result['score']}")
            print(f"✓ 状态: {result['status']}")
            print(f"✓ 描述: {result['message']}")
            
            details = result['details']
            print(f"\n对比数据:")
            print(f"  - 个股30日收益: {details.get('stock_return_30d')}%")
            print(f"  - 上证指数30日收益: {details.get('sh_index_return_30d')}%")
            print(f"  - 深证成指30日收益: {details.get('sz_index_return_30d')}%")
            print(f"  - 跑赢上证: {details.get('outperformance_sh')}%")
            print(f"  - 跑赢深证: {details.get('outperformance_sz')}%")
            print(f"  - Beta: {details.get('beta')}")
            print(f"  - 相对强度: {details.get('relative_strength')}")
            
            print("✓ 大盘对比分析成功")
            
        except Exception as e:
            print(f"✗ 大盘对比分析失败: {e}")
    
    print("\n✓ 大盘对比分析器测试完成")


def test_diagnosis_engine():
    """测试诊断引擎"""
    print_section("测试 6: 诊断引擎 (Diagnosis Engine)")
    
    engine = StockDiagnosisEngine()
    
    # 测试1: 单股诊断
    print_subsection("6.1 单股诊断")
    code, name = TEST_STOCKS[0]
    
    try:
        start_time = time.time()
        report = engine.diagnose(code, use_cache=False)
        elapsed = (time.time() - start_time) * 1000
        
        print(f"✓ 股票: {report.name} ({report.code})")
        print(f"✓ 综合评分: {report.overall_score}")
        print(f"✓ 综合评级: {report.overall_rating}")
        print(f"✓ 综合状态: {report.overall_status}")
        print(f"✓ 诊断耗时: {elapsed:.2f}ms")
        
        print(f"\n各维度评分:")
        for dim_name, dim_analysis in report.dimensions.items():
            print(f"  - {dim_name}: {dim_analysis.score}分 ({dim_analysis.status}) - {dim_analysis.message}")
        
        print(f"\n优势 ({len(report.strengths)}):")
        for strength in report.strengths:
            print(f"  ✓ {strength}")
        
        print(f"\n劣势 ({len(report.weaknesses)}):")
        for weakness in report.weaknesses:
            print(f"  ✗ {weakness}")
        
        print(f"\n投资建议 ({len(report.suggestions)}):")
        for suggestion in report.suggestions:
            print(f"  → {suggestion}")
        
        print(f"\n综合总结:")
        print(f"  {report.summary}")
        
        print(f"\n✓ 单股诊断成功")
        
    except Exception as e:
        print(f"✗ 单股诊断失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试2: 缓存功能
    print_subsection("6.2 缓存功能")
    
    try:
        # 第一次调用（无缓存）
        start_time = time.time()
        report1 = engine.diagnose(code, use_cache=True)
        elapsed1 = (time.time() - start_time) * 1000
        
        # 第二次调用（有缓存）
        start_time = time.time()
        report2 = engine.diagnose(code, use_cache=True)
        elapsed2 = (time.time() - start_time) * 1000
        
        print(f"✓ 首次调用耗时: {elapsed1:.2f}ms")
        print(f"✓ 缓存调用耗时: {elapsed2:.2f}ms")
        print(f"✓ 加速比: {elapsed1/elapsed2:.2f}x")
        
        if elapsed2 < elapsed1 * 0.5:
            print("✓ 缓存功能正常")
        else:
            print("⚠ 缓存可能未生效")
        
        # 清除缓存
        engine.clear_cache(code)
        print("✓ 缓存已清除")
        
    except Exception as e:
        print(f"✗ 缓存测试失败: {e}")
    
    # 测试3: 批量诊断
    print_subsection("6.3 批量诊断")
    
    try:
        codes = [code for code, _ in TEST_STOCKS[:3]]
        
        start_time = time.time()
        reports = engine.diagnose_batch(codes, use_cache=False, max_workers=3)
        elapsed = (time.time() - start_time) * 1000
        
        print(f"✓ 批量诊断 {len(codes)} 只股票")
        print(f"✓ 成功: {len(reports)} 只")
        print(f"✓ 总耗时: {elapsed:.2f}ms")
        print(f"✓ 平均耗时: {elapsed/len(reports):.2f}ms/股")
        
        print(f"\n批量结果:")
        for report in reports:
            print(f"  - {report.name} ({report.code}): {report.overall_score}分 - {report.overall_rating}")
        
        print("✓ 批量诊断成功")
        
    except Exception as e:
        print(f"✗ 批量诊断失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✓ 诊断引擎测试完成")


def test_api_endpoints():
    """测试 API 端点"""
    print_section("测试 7: API 端点")
    
    # 测试1: 健康检查
    print_subsection("7.1 健康检查")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/diagnosis/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 状态码: {response.status_code}")
            print(f"✓ 响应: {data}")
            print("✓ 健康检查成功")
        else:
            print(f"✗ 健康检查失败: 状态码 {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到 API 服务器")
        print("  提示: 请先启动 Flask 服务器 (python src/web/app.py)")
        return
    except Exception as e:
        print(f"✗ 健康检查失败: {e}")
    
    # 测试2: 单股诊断 API
    print_subsection("7.2 单股诊断 API")
    
    code, name = TEST_STOCKS[0]
    
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/api/diagnosis/{code}", timeout=10)
        elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 状态码: {response.status_code}")
            print(f"✓ 响应时间: {elapsed:.2f}ms")
            print(f"✓ 股票: {data['name']} ({data['code']})")
            print(f"✓ 综合评分: {data['overall_score']}")
            print(f"✓ 综合评级: {data['overall_rating']}")
            print(f"✓ 维度数量: {len(data['dimensions'])}")
            
            if elapsed < 300:
                print("✓ 响应时间符合要求 (<300ms)")
            else:
                print(f"⚠ 响应时间较慢 ({elapsed:.2f}ms)")
            
            print("✓ 单股诊断 API 成功")
        else:
            print(f"✗ 单股诊断 API 失败: 状态码 {response.status_code}")
            print(f"  响应: {response.text}")
            
    except Exception as e:
        print(f"✗ 单股诊断 API 失败: {e}")
    
    # 测试3: 批量诊断 API
    print_subsection("7.3 批量诊断 API")
    
    codes = [code for code, _ in TEST_STOCKS[:3]]
    
    try:
        payload = {
            'codes': codes,
            'use_cache': False,
            'max_workers': 3
        }
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/api/diagnosis/batch",
            json=payload,
            timeout=30
        )
        elapsed = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 状态码: {response.status_code}")
            print(f"✓ 响应时间: {elapsed:.2f}ms")
            print(f"✓ 总数: {data['total']}")
            print(f"✓ 成功: {data['success']}")
            print(f"✓ 失败: {data['failed']}")
            print(f"✓ 平均耗时: {elapsed/data['success']:.2f}ms/股")
            
            if elapsed < 5000:
                print("✓ 批量响应时间符合要求 (<5s)")
            else:
                print(f"⚠ 批量响应时间较慢 ({elapsed:.2f}ms)")
            
            print("✓ 批量诊断 API 成功")
        else:
            print(f"✗ 批量诊断 API 失败: 状态码 {response.status_code}")
            print(f"  响应: {response.text}")
            
    except Exception as e:
        print(f"✗ 批量诊断 API 失败: {e}")
    
    # 测试4: 清除缓存 API
    print_subsection("7.4 清除缓存 API")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/diagnosis/cache/clear",
            json={'code': code},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 状态码: {response.status_code}")
            print(f"✓ 响应: {data['message']}")
            print("✓ 清除缓存 API 成功")
        else:
            print(f"✗ 清除缓存 API 失败: 状态码 {response.status_code}")
            
    except Exception as e:
        print(f"✗ 清除缓存 API 失败: {e}")
    
    # 测试5: 错误处理
    print_subsection("7.5 错误处理")
    
    try:
        # 测试无效股票代码
        response = requests.get(f"{API_BASE_URL}/api/diagnosis/INVALID", timeout=5)
        
        if response.status_code in [400, 404, 500]:
            print(f"✓ 错误处理正常: 状态码 {response.status_code}")
            data = response.json()
            print(f"✓ 错误信息: {data.get('message')}")
        else:
            print(f"⚠ 未预期的状态码: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 错误处理测试失败: {e}")
    
    print("\n✓ API 端点测试完成")


def test_performance():
    """性能测试"""
    print_section("测试 8: 性能测试")
    
    engine = StockDiagnosisEngine()
    
    # 测试1: 单股诊断性能
    print_subsection("8.1 单股诊断性能")
    
    code, name = TEST_STOCKS[0]
    times = []
    
    for i in range(5):
        start_time = time.time()
        engine.diagnose(code, use_cache=False)
        elapsed = (time.time() - start_time) * 1000
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"✓ 测试次数: {len(times)}")
    print(f"✓ 平均耗时: {avg_time:.2f}ms")
    print(f"✓ 最快: {min_time:.2f}ms")
    print(f"✓ 最慢: {max_time:.2f}ms")
    
    if avg_time < 200:
        print("✓ 性能符合要求 (<200ms)")
    else:
        print(f"⚠ 性能需要优化 ({avg_time:.2f}ms)")
    
    # 测试2: 批量诊断性能
    print_subsection("8.2 批量诊断性能")
    
    codes = [code for code, _ in TEST_STOCKS]
    
    start_time = time.time()
    reports = engine.diagnose_batch(codes, use_cache=False, max_workers=5)
    elapsed = (time.time() - start_time) * 1000
    
    print(f"✓ 股票数量: {len(codes)}")
    print(f"✓ 总耗时: {elapsed:.2f}ms")
    print(f"✓ 平均耗时: {elapsed/len(reports):.2f}ms/股")
    
    if elapsed < 5000:
        print("✓ 批量性能符合要求 (<5s)")
    else:
        print(f"⚠ 批量性能需要优化 ({elapsed:.2f}ms)")
    
    print("\n✓ 性能测试完成")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  股票诊断系统 - 手动测试工具")
    print("=" * 80)
    print(f"\n测试股票: {', '.join([f'{name}({code})' for code, name in TEST_STOCKS])}")
    print(f"API 地址: {API_BASE_URL}")
    
    # 运行所有测试
    try:
        test_technical_analyzer()
        test_fundamental_analyzer()
        test_sector_analyzer()
        test_capital_analyzer()
        test_market_comparison_analyzer()
        test_diagnosis_engine()
        test_api_endpoints()
        test_performance()
        
        # 总结
        print_section("测试总结")
        print("✓ 所有测试已完成")
        print("\n测试覆盖:")
        print("  ✓ 技术面分析器")
        print("  ✓ 基本面分析器")
        print("  ✓ 行业面分析器")
        print("  ✓ 资金面分析器")
        print("  ✓ 大盘对比分析器")
        print("  ✓ 诊断引擎（单股、批量、缓存）")
        print("  ✓ API 端点（健康检查、单股、批量、缓存、错误处理）")
        print("  ✓ 性能测试")
        
        print("\n如需查看详细日志，请检查上方输出")
        
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

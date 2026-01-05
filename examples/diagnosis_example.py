# -*- coding: utf-8 -*-
"""
股票综合诊断系统使用示例

演示如何使用诊断引擎进行股票分析
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.business.diagnosis.diagnosis_engine import StockDiagnosisEngine
import json


def print_separator(title=""):
    """打印分隔线"""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
    else:
        print(f"{'='*60}\n")


def example_1_single_diagnosis():
    """示例1: 单只股票诊断"""
    print_separator("示例1: 单只股票诊断")
    
    engine = StockDiagnosisEngine()
    
    # 诊断贵州茅台
    report = engine.diagnose("600519")
    
    print(f"📊 股票: {report.name} ({report.code})")
    print(f"⭐ 综合评分: {report.overall_score}/100")
    print(f"🏆 综合评级: {report.overall_rating}")
    print(f"🚦 综合状态: {report.overall_status}")
    
    print(f"\n📈 各维度分析:")
    dimension_names = {
        'technical': '技术面',
        'fundamental': '基本面',
        'sector': '行业面',
        'capital': '资金面',
        'market_comparison': '大盘对比'
    }
    
    for dim_key, dim_analysis in report.dimensions.items():
        dim_name = dimension_names.get(dim_key, dim_key)
        status_emoji = '🟢' if dim_analysis.status == 'green' else '🟡' if dim_analysis.status == 'yellow' else '🔴'
        print(f"  {status_emoji} {dim_name}: {dim_analysis.score}分")
        print(f"     {dim_analysis.message}")
    
    print(f"\n💪 优势:")
    for strength in report.strengths:
        print(f"  ✓ {strength}")
    
    print(f"\n⚠️  劣势:")
    for weakness in report.weaknesses:
        print(f"  ✗ {weakness}")
    
    print(f"\n💡 投资建议:")
    for suggestion in report.suggestions:
        print(f"  • {suggestion}")
    
    print(f"\n📝 综合总结:")
    print(f"  {report.summary}")
    
    print(f"\n🕐 更新时间: {report.updated_at}")


def example_2_batch_diagnosis():
    """示例2: 批量诊断"""
    print_separator("示例2: 批量诊断")
    
    engine = StockDiagnosisEngine()
    
    # 批量诊断多只股票
    codes = ["600519", "000858", "000001", "600036"]
    print(f"正在诊断 {len(codes)} 只股票: {', '.join(codes)}\n")
    
    reports = engine.diagnose_batch(codes)
    
    # 按评分排序
    reports_sorted = sorted(reports, key=lambda r: r.overall_score, reverse=True)
    
    print(f"{'排名':<6} {'代码':<10} {'名称':<12} {'评分':<8} {'评级':<8} {'状态':<8}")
    print("-" * 60)
    
    for i, report in enumerate(reports_sorted, 1):
        status_emoji = '🟢' if report.overall_status == 'green' else '🟡' if report.overall_status == 'yellow' else '🔴'
        print(f"{i:<6} {report.code:<10} {report.name:<12} {report.overall_score:<8} {report.overall_rating:<8} {status_emoji}")


def example_3_dimension_details():
    """示例3: 查看维度详细数据"""
    print_separator("示例3: 查看维度详细数据")
    
    engine = StockDiagnosisEngine()
    report = engine.diagnose("600519")
    
    print(f"股票: {report.name} ({report.code})\n")
    
    # 技术面详细数据
    if 'technical' in report.dimensions:
        tech = report.dimensions['technical']
        print("📈 技术面详细数据:")
        print(f"  趋势: {tech.details.get('trend')}")
        print(f"  MA20: {tech.details.get('ma20')}")
        print(f"  MA20偏离度: {tech.details.get('ma20_deviation')}%")
        print(f"  RSI: {tech.details.get('rsi')}")
        print(f"  量比: {tech.details.get('volume_ratio')}")
        print(f"  支撑位: {tech.details.get('support_level')}")
        print(f"  阻力位: {tech.details.get('resistance_level')}")
        
        pattern = tech.details.get('candlestick_pattern')
        if pattern:
            print(f"  K线形态: {pattern.get('name_cn')} ({pattern.get('signal_cn')})")
            print(f"    {pattern.get('description')}")
    
    # 基本面详细数据
    if 'fundamental' in report.dimensions:
        fund = report.dimensions['fundamental']
        print("\n💰 基本面详细数据:")
        print(f"  ROE: {fund.details.get('roe')}%")
        print(f"  ROA: {fund.details.get('roa')}%")
        print(f"  净利率: {fund.details.get('net_profit_margin')}%")
        print(f"  毛利率: {fund.details.get('gross_margin')}%")
        print(f"  负债率: {fund.details.get('debt_ratio')}%")
        print(f"  流动比率: {fund.details.get('current_ratio')}")
        print(f"  利润同比增长: {fund.details.get('profit_growth_yoy')}%")
        print(f"  所属行业: {fund.details.get('industry')}")
    
    # 大盘对比详细数据
    if 'market_comparison' in report.dimensions:
        market = report.dimensions['market_comparison']
        print("\n📊 大盘对比详细数据:")
        print(f"  个股30日收益: {market.details.get('stock_return_30d')}%")
        print(f"  上证指数30日收益: {market.details.get('sh_index_return_30d')}%")
        print(f"  跑赢/跑输: {market.details.get('outperformance_sh')}%")
        print(f"  Beta: {market.details.get('beta')}")
        print(f"  相对强弱: {market.details.get('relative_strength')}")


def example_4_export_json():
    """示例4: 导出JSON格式"""
    print_separator("示例4: 导出JSON格式")
    
    engine = StockDiagnosisEngine()
    report = engine.diagnose("600519")
    
    # 导出为JSON
    json_str = report.to_json()
    
    print("JSON格式诊断报告:")
    print(json_str)
    
    # 保存到文件
    output_file = "diagnosis_report_600519.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(json_str)
    
    print(f"\n✅ 报告已保存到: {output_file}")


def example_5_cache_usage():
    """示例5: 缓存使用"""
    print_separator("示例5: 缓存使用")
    
    engine = StockDiagnosisEngine()
    
    import time
    
    # 第一次诊断（无缓存）
    print("第一次诊断（无缓存）...")
    start = time.time()
    report1 = engine.diagnose("600519", use_cache=True)
    time1 = time.time() - start
    print(f"耗时: {time1:.2f}秒")
    print(f"评分: {report1.overall_score}")
    
    # 第二次诊断（使用缓存）
    print("\n第二次诊断（使用缓存）...")
    start = time.time()
    report2 = engine.diagnose("600519", use_cache=True)
    time2 = time.time() - start
    print(f"耗时: {time2:.2f}秒")
    print(f"评分: {report2.overall_score}")
    
    print(f"\n⚡ 缓存加速: {time1/time2:.1f}x")
    
    # 清除缓存
    print("\n清除缓存...")
    engine.clear_cache("600519")
    print("✅ 缓存已清除")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  股票综合诊断系统 - 使用示例")
    print("="*60)
    
    # 运行所有示例
    example_1_single_diagnosis()
    example_2_batch_diagnosis()
    example_3_dimension_details()
    example_4_export_json()
    example_5_cache_usage()
    
    print_separator()
    print("✅ 所有示例运行完成！")


if __name__ == "__main__":
    main()

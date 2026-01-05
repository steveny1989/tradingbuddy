#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试东方明珠（600637）的股票诊断
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.business.diagnosis.diagnosis_engine import StockDiagnosisEngine


def print_section(title, char="="):
    """打印分节标题"""
    print(f"\n{char * 60}")
    print(f"{title:^60}")
    print(f"{char * 60}\n")


def print_dimension(name, data):
    """打印单个维度的分析结果"""
    # Convert to dict if it's a DimensionAnalysis object
    if hasattr(data, 'to_dict'):
        data = data.to_dict()
    
    print(f"\n【{name}】")
    print(f"  评分: {data['score']}/100")
    print(f"  状态: {data['status']} {'🟢' if data['status'] == 'green' else '🟡' if data['status'] == 'yellow' else '🔴'}")
    print(f"  说明: {data['message']}")
    
    # 打印详细信息
    if data.get('details'):
        print(f"  详细数据:")
        for key, value in data['details'].items():
            if isinstance(value, (int, float)):
                print(f"    - {key}: {value:.2f}" if isinstance(value, float) else f"    - {key}: {value}")
            else:
                print(f"    - {key}: {value}")


def main():
    """主函数"""
    code = '600637'  # 东方明珠
    
    print_section("东方明珠（600637）股票综合诊断", "=")
    
    try:
        # 创建诊断引擎
        print("正在初始化诊断引擎...")
        engine = StockDiagnosisEngine()
        
        # 执行诊断
        print(f"正在诊断 {code}...")
        report = engine.diagnose(code, use_cache=False)
        
        # 打印基本信息
        print_section("基本信息", "-")
        print(f"股票代码: {report.code}")
        print(f"股票名称: {report.name}")
        print(f"更新时间: {report.updated_at}")
        
        # 打印综合评分
        print_section("综合评分", "-")
        print(f"综合得分: {report.overall_score}/100")
        print(f"综合评级: {report.overall_rating}")
        status_emoji = '🟢' if report.overall_status == 'green' else '🟡' if report.overall_status == 'yellow' else '🔴'
        print(f"综合状态: {report.overall_status} {status_emoji}")
        
        # 打印各维度分析
        print_section("五维度分析", "-")
        
        dimension_names = {
            'technical': '技术面分析',
            'fundamental': '基本面分析',
            'sector': '行业面分析',
            'capital': '资金面分析',
            'market_comparison': '大盘对比分析'
        }
        
        for key, name in dimension_names.items():
            if key in report.dimensions:
                print_dimension(name, report.dimensions[key])
        
        # 打印优势
        if report.strengths:
            print_section("优势分析", "-")
            for i, strength in enumerate(report.strengths, 1):
                print(f"{i}. {strength}")
        
        # 打印劣势
        if report.weaknesses:
            print_section("劣势分析", "-")
            for i, weakness in enumerate(report.weaknesses, 1):
                print(f"{i}. {weakness}")
        
        # 打印投资建议
        if report.suggestions:
            print_section("投资建议", "-")
            for i, suggestion in enumerate(report.suggestions, 1):
                print(f"{i}. {suggestion}")
        
        # 打印综合总结
        print_section("综合总结", "-")
        print(report.summary)
        
        # 保存完整报告为JSON
        print_section("保存报告", "-")
        output_file = f"diagnosis_report_{code}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"完整诊断报告已保存到: {output_file}")
        
        print_section("诊断完成", "=")
        
    except Exception as e:
        print(f"\n❌ 诊断失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

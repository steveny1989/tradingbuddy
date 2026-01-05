#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票综合诊断系统数据模型使用示例

演示如何使用 DimensionAnalysis 和 DiagnosisReport 数据模型
"""
from datetime import datetime
from src.business.diagnosis.models import (
    DimensionAnalysis,
    DiagnosisReport,
    create_empty_diagnosis,
    calculate_overall_score,
    get_rating_from_score,
    get_status_from_score
)


def example_dimension_analysis():
    """示例：创建维度分析"""
    print("=" * 60)
    print("示例 1: 创建维度分析")
    print("=" * 60)
    
    # 创建技术面分析
    technical = DimensionAnalysis(
        score=75,
        status='yellow',
        message='短期震荡整理，等待方向选择',
        details={
            'trend': '震荡',
            'ma20_position': 'above',
            'rsi': 55.2,
            'volume_ratio': 1.2
        }
    )
    
    print(f"技术面评分: {technical.score}")
    print(f"技术面状态: {technical.status}")
    print(f"技术面描述: {technical.message}")
    print(f"技术面详情: {technical.details}")
    print()


def example_diagnosis_report():
    """示例：创建完整诊断报告"""
    print("=" * 60)
    print("示例 2: 创建完整诊断报告")
    print("=" * 60)
    
    # 创建诊断报告
    report = DiagnosisReport(
        code='600519',
        name='贵州茅台',
        overall_score=85,
        overall_rating='优秀',
        overall_status='green',
        updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    # 添加各维度分析
    report.add_dimension('technical', DimensionAnalysis(
        score=75,
        status='yellow',
        message='短期震荡整理，等待方向选择',
        details={'trend': '震荡', 'rsi': 55.2}
    ))
    
    report.add_dimension('fundamental', DimensionAnalysis(
        score=90,
        status='green',
        message='基本面优秀，盈利能力强',
        details={'pe': 25.5, 'roe': 28.5, 'profit_growth_yoy': 15.2}
    ))
    
    report.add_dimension('sector', DimensionAnalysis(
        score=85,
        status='green',
        message='所属行业表现强势，个股跑赢行业',
        details={'industry': '食品饮料', 'industry_rank': 3}
    ))
    
    report.add_dimension('capital', DimensionAnalysis(
        score=70,
        status='yellow',
        message='北向资金持仓稳定；主力资金小幅流出',
        details={'northbound_change': -0.14, 'main_inflow': -7.47}
    ))
    
    report.add_dimension('market_comparison', DimensionAnalysis(
        score=80,
        status='green',
        message='近30日跑赢大盘7.3%，表现强势',
        details={'stock_return_30d': 15.5, 'outperformance': 7.3}
    ))
    
    # 添加优劣势和建议
    report.strengths = [
        '基本面优秀，ROE高达28.5%',
        '所属行业表现强势',
        '跑赢大盘，相对强势明显'
    ]
    
    report.weaknesses = [
        '短期技术面震荡，缺乏明确方向',
        '主力资金小幅流出'
    ]
    
    report.suggestions = [
        '建议逢低布局，关注1650元支撑位',
        '中长期持有，基本面支撑强劲',
        '短期可等待技术面明朗后再加仓'
    ]
    
    report.summary = '综合来看，该股基本面优秀，行业地位稳固，长期投资价值显著。短期技术面虽有震荡，但不改变中长期向好趋势。建议投资者逢低布局，耐心持有。'
    
    # 打印报告
    print(f"股票代码: {report.code}")
    print(f"股票名称: {report.name}")
    print(f"综合评分: {report.overall_score}")
    print(f"综合评级: {report.overall_rating}")
    print(f"综合状态: {report.overall_status}")
    print()
    
    print("各维度分析:")
    for dim_name, dim_analysis in report.dimensions.items():
        print(f"  {dim_name}: {dim_analysis.score}分 ({dim_analysis.status}) - {dim_analysis.message}")
    print()
    
    print("优势:")
    for strength in report.strengths:
        print(f"  ✓ {strength}")
    print()
    
    print("劣势:")
    for weakness in report.weaknesses:
        print(f"  ✗ {weakness}")
    print()
    
    print("投资建议:")
    for suggestion in report.suggestions:
        print(f"  → {suggestion}")
    print()
    
    print(f"综合总结: {report.summary}")
    print()


def example_json_serialization():
    """示例：JSON序列化和反序列化"""
    print("=" * 60)
    print("示例 3: JSON序列化和反序列化")
    print("=" * 60)
    
    # 创建报告
    report = DiagnosisReport(
        code='600519',
        name='贵州茅台',
        overall_score=85,
        overall_rating='优秀',
        overall_status='green',
        updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    report.add_dimension('technical', DimensionAnalysis(
        score=75,
        status='yellow',
        message='技术面中性',
        details={'trend': '震荡'}
    ))
    
    # 转换为JSON
    json_str = report.to_json()
    print("JSON格式:")
    print(json_str)
    print()
    
    # 从JSON恢复
    restored_report = DiagnosisReport.from_json(json_str)
    print(f"恢复后的报告: {restored_report.code} - {restored_report.name}")
    print(f"综合评分: {restored_report.overall_score}")
    print()


def example_calculate_score():
    """示例：计算综合评分"""
    print("=" * 60)
    print("示例 4: 计算综合评分")
    print("=" * 60)
    
    # 创建各维度分析
    dimensions = {
        'technical': DimensionAnalysis(80, 'green', 'test', {}),
        'fundamental': DimensionAnalysis(90, 'green', 'test', {}),
        'sector': DimensionAnalysis(70, 'yellow', 'test', {}),
        'capital': DimensionAnalysis(75, 'yellow', 'test', {}),
        'market_comparison': DimensionAnalysis(85, 'green', 'test', {})
    }
    
    # 计算综合评分
    overall_score = calculate_overall_score(dimensions)
    overall_rating = get_rating_from_score(overall_score)
    overall_status = get_status_from_score(overall_score)
    
    print("各维度评分:")
    for dim_name, dim_analysis in dimensions.items():
        print(f"  {dim_name}: {dim_analysis.score}分")
    print()
    
    print(f"综合评分: {overall_score}分")
    print(f"综合评级: {overall_rating}")
    print(f"综合状态: {overall_status}")
    print()
    
    # 测试缺失维度的情况
    print("缺失部分维度的情况:")
    partial_dimensions = {
        'technical': DimensionAnalysis(80, 'green', 'test', {}),
        'fundamental': DimensionAnalysis(90, 'green', 'test', {})
    }
    
    partial_score = calculate_overall_score(partial_dimensions)
    print(f"只有技术面和基本面时的综合评分: {partial_score}分")
    print()


def example_empty_diagnosis():
    """示例：创建空诊断报告"""
    print("=" * 60)
    print("示例 5: 创建空诊断报告")
    print("=" * 60)
    
    report = create_empty_diagnosis('600519', '贵州茅台')
    
    print(f"股票代码: {report.code}")
    print(f"股票名称: {report.name}")
    print(f"综合评分: {report.overall_score}")
    print(f"综合评级: {report.overall_rating}")
    print(f"综合状态: {report.overall_status}")
    print(f"综合总结: {report.summary}")
    print(f"可用维度数量: {len(report.get_available_dimensions())}")
    print()


if __name__ == '__main__':
    example_dimension_analysis()
    example_diagnosis_report()
    example_json_serialization()
    example_calculate_score()
    example_empty_diagnosis()
    
    print("=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)

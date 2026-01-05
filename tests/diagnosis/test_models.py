# -*- coding: utf-8 -*-
"""
测试诊断系统数据模型
"""
import pytest
import json
from datetime import datetime

from src.business.diagnosis.models import (
    DimensionAnalysis,
    DiagnosisReport,
    create_empty_diagnosis,
    calculate_overall_score,
    get_rating_from_score,
    get_status_from_score
)


class TestDimensionAnalysis:
    """测试 DimensionAnalysis 数据模型"""
    
    def test_create_dimension_analysis(self):
        """测试创建维度分析对象"""
        analysis = DimensionAnalysis(
            score=85,
            status='green',
            message='技术面向好',
            details={'trend': '上涨', 'rsi': 55.2}
        )
        
        assert analysis.score == 85
        assert analysis.status == 'green'
        assert analysis.message == '技术面向好'
        assert analysis.details['trend'] == '上涨'
    
    def test_to_dict(self):
        """测试转换为字典"""
        analysis = DimensionAnalysis(
            score=75,
            status='yellow',
            message='技术面中性',
            details={'ma20': 100.5}
        )
        
        result = analysis.to_dict()
        assert isinstance(result, dict)
        assert result['score'] == 75
        assert result['status'] == 'yellow'
        assert result['details']['ma20'] == 100.5
    
    def test_to_json(self):
        """测试转换为JSON"""
        analysis = DimensionAnalysis(
            score=90,
            status='green',
            message='基本面优秀',
            details={'roe': 28.5}
        )
        
        json_str = analysis.to_json()
        assert isinstance(json_str, str)
        
        # 验证可以解析回来
        data = json.loads(json_str)
        assert data['score'] == 90
        assert data['details']['roe'] == 28.5
    
    def test_from_dict(self):
        """测试从字典创建对象"""
        data = {
            'score': 80,
            'status': 'green',
            'message': '行业强势',
            'details': {'industry_rank': 3}
        }
        
        analysis = DimensionAnalysis.from_dict(data)
        assert analysis.score == 80
        assert analysis.status == 'green'
        assert analysis.details['industry_rank'] == 3
    
    def test_from_json(self):
        """测试从JSON创建对象"""
        json_str = '{"score": 70, "status": "yellow", "message": "资金观望", "details": {"flow": 0}}'
        
        analysis = DimensionAnalysis.from_json(json_str)
        assert analysis.score == 70
        assert analysis.status == 'yellow'
        assert analysis.message == '资金观望'


class TestDiagnosisReport:
    """测试 DiagnosisReport 数据模型"""
    
    def test_create_diagnosis_report(self):
        """测试创建诊断报告对象"""
        report = DiagnosisReport(
            code='600519',
            name='贵州茅台',
            overall_score=85,
            overall_rating='优秀',
            overall_status='green'
        )
        
        assert report.code == '600519'
        assert report.name == '贵州茅台'
        assert report.overall_score == 85
        assert report.overall_rating == '优秀'
        assert report.overall_status == 'green'
    
    def test_add_dimension(self):
        """测试添加维度分析"""
        report = DiagnosisReport(
            code='600519',
            name='贵州茅台',
            overall_score=85,
            overall_rating='优秀',
            overall_status='green'
        )
        
        technical = DimensionAnalysis(
            score=75,
            status='yellow',
            message='技术面中性',
            details={'trend': '震荡'}
        )
        
        report.add_dimension('technical', technical)
        
        assert report.has_dimension('technical')
        assert report.get_dimension('technical').score == 75
    
    def test_get_available_dimensions(self):
        """测试获取可用维度列表"""
        report = DiagnosisReport(
            code='600519',
            name='贵州茅台',
            overall_score=85,
            overall_rating='优秀',
            overall_status='green'
        )
        
        report.add_dimension('technical', DimensionAnalysis(75, 'yellow', 'test', {}))
        report.add_dimension('fundamental', DimensionAnalysis(90, 'green', 'test', {}))
        
        dimensions = report.get_available_dimensions()
        assert len(dimensions) == 2
        assert 'technical' in dimensions
        assert 'fundamental' in dimensions
    
    def test_to_dict(self):
        """测试转换为字典"""
        report = DiagnosisReport(
            code='600519',
            name='贵州茅台',
            overall_score=85,
            overall_rating='优秀',
            overall_status='green',
            strengths=['基本面优秀'],
            weaknesses=['技术面偏弱'],
            suggestions=['逢低布局'],
            summary='综合来看表现良好'
        )
        
        report.add_dimension('technical', DimensionAnalysis(75, 'yellow', 'test', {}))
        
        result = report.to_dict()
        assert isinstance(result, dict)
        assert result['code'] == '600519'
        assert result['overall_score'] == 85
        assert len(result['strengths']) == 1
        assert 'technical' in result['dimensions']
    
    def test_to_json(self):
        """测试转换为JSON"""
        report = DiagnosisReport(
            code='600519',
            name='贵州茅台',
            overall_score=85,
            overall_rating='优秀',
            overall_status='green'
        )
        
        json_str = report.to_json()
        assert isinstance(json_str, str)
        
        # 验证可以解析回来
        data = json.loads(json_str)
        assert data['code'] == '600519'
        assert data['overall_score'] == 85
    
    def test_from_dict(self):
        """测试从字典创建对象"""
        data = {
            'code': '600519',
            'name': '贵州茅台',
            'overall_score': 85,
            'overall_rating': '优秀',
            'overall_status': 'green',
            'dimensions': {
                'technical': {
                    'score': 75,
                    'status': 'yellow',
                    'message': 'test',
                    'details': {}
                }
            },
            'strengths': ['基本面优秀'],
            'weaknesses': [],
            'suggestions': ['逢低布局'],
            'summary': '综合来看表现良好',
            'updated_at': '2026-01-04 10:00:00'
        }
        
        report = DiagnosisReport.from_dict(data)
        assert report.code == '600519'
        assert report.overall_score == 85
        assert report.has_dimension('technical')
        assert len(report.strengths) == 1
    
    def test_from_json(self):
        """测试从JSON创建对象"""
        json_str = '''
        {
            "code": "600519",
            "name": "贵州茅台",
            "overall_score": 85,
            "overall_rating": "优秀",
            "overall_status": "green",
            "dimensions": {},
            "strengths": [],
            "weaknesses": [],
            "suggestions": [],
            "summary": "",
            "updated_at": ""
        }
        '''
        
        report = DiagnosisReport.from_json(json_str)
        assert report.code == '600519'
        assert report.name == '贵州茅台'
        assert report.overall_score == 85


class TestHelperFunctions:
    """测试辅助函数"""
    
    def test_create_empty_diagnosis(self):
        """测试创建空诊断报告"""
        report = create_empty_diagnosis('600519', '贵州茅台')
        
        assert report.code == '600519'
        assert report.name == '贵州茅台'
        assert report.overall_score == 0
        assert report.overall_rating == '未知'
        assert len(report.dimensions) == 0
    
    def test_calculate_overall_score_all_dimensions(self):
        """测试计算综合评分 - 所有维度"""
        dimensions = {
            'technical': DimensionAnalysis(80, 'green', 'test', {}),
            'fundamental': DimensionAnalysis(90, 'green', 'test', {}),
            'sector': DimensionAnalysis(70, 'yellow', 'test', {}),
            'capital': DimensionAnalysis(75, 'yellow', 'test', {}),
            'market_comparison': DimensionAnalysis(85, 'green', 'test', {})
        }
        
        score = calculate_overall_score(dimensions)
        
        # 计算期望值: 80*0.2 + 90*0.3 + 70*0.15 + 75*0.2 + 85*0.15 = 81.25
        assert score == 81
    
    def test_calculate_overall_score_missing_dimensions(self):
        """测试计算综合评分 - 缺失维度"""
        dimensions = {
            'technical': DimensionAnalysis(80, 'green', 'test', {}),
            'fundamental': DimensionAnalysis(90, 'green', 'test', {})
        }
        
        score = calculate_overall_score(dimensions)
        
        # 只有技术面和基本面，权重重新分配
        # 80*0.2 + 90*0.3 = 43, 总权重 0.5, 归一化: 43/0.5 = 86
        assert score == 86
    
    def test_calculate_overall_score_empty(self):
        """测试计算综合评分 - 空维度"""
        score = calculate_overall_score({})
        assert score == 0
    
    def test_get_rating_from_score(self):
        """测试根据评分获取评级"""
        assert get_rating_from_score(95) == '优秀'
        assert get_rating_from_score(80) == '优秀'
        assert get_rating_from_score(70) == '良好'
        assert get_rating_from_score(65) == '良好'
        assert get_rating_from_score(55) == '一般'
        assert get_rating_from_score(50) == '一般'
        assert get_rating_from_score(40) == '较差'
        assert get_rating_from_score(35) == '较差'
        assert get_rating_from_score(20) == '很差'
        assert get_rating_from_score(0) == '很差'
    
    def test_get_status_from_score(self):
        """测试根据评分获取状态"""
        assert get_status_from_score(90) == 'green'
        assert get_status_from_score(70) == 'green'
        assert get_status_from_score(60) == 'yellow'
        assert get_status_from_score(50) == 'yellow'
        assert get_status_from_score(40) == 'red'
        assert get_status_from_score(0) == 'red'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

# -*- coding: utf-8 -*-
"""
财务风险分析器

基于财务指标评估股票的财务健康状况：
1. 盈利能力 - ROE、净利率
2. 偿债能力 - 资产负债率、流动比率
3. 风险预警 - ST状态、财务异常
"""
import pandas as pd
import sqlite3
from typing import Dict, Optional
from src.data.database_adapter import DatabaseAdapter


class FinancialRiskAnalyzer:
    """财务风险分析器"""
    
    def __init__(self):
        self.db = DatabaseAdapter()
    
    def analyze_financial_risk(self, code: str) -> Dict:
        """
        分析财务风险
        
        Args:
            code: 股票代码
            
        Returns:
            Dict: 财务风险分析报告
        """
        # 1. 获取股票基本信息
        stock_info = self.db.get_stock_basic(code)
        if not stock_info:
            return self._empty_report(code)
        
        name = stock_info.get('name', code)
        
        # 2. 检查ST状态
        is_st = self._check_st_status(name)
        
        # 3. 获取最新财务数据
        financial_data = self._get_latest_financial_data(code)
        
        if not financial_data:
            return self._empty_report(code, name, is_st)
        
        # 4. 分析盈利能力
        profitability = self._analyze_profitability(financial_data)
        
        # 5. 分析偿债能力
        solvency = self._analyze_solvency(financial_data)
        
        # 6. 计算财务风险评分
        risk_score = self._calculate_risk_score(profitability, solvency, is_st)
        
        # 7. 生成状态和建议
        status, message = self._generate_risk_status(
            profitability, solvency, is_st, risk_score
        )
        
        return {
            'code': code,
            'name': name,
            'status': status,
            'message': message,
            'is_st': is_st,
            'risk_score': risk_score,
            'profitability': profitability,
            'solvency': solvency,
            'report_date': financial_data.get('report_date')
        }
    
    def _check_st_status(self, name: str) -> bool:
        """检查是否ST股票"""
        st_keywords = ['ST', '*ST', 'S*ST', 'SST', 'S']
        return any(keyword in name for keyword in st_keywords)
    
    def _get_latest_financial_data(self, code: str) -> Optional[Dict]:
        """
        获取最新财务数据
        
        优先使用最新年报（12-31），如果没有则使用最新季报
        """
        # 标准化代码（移除前缀）
        pure_code = code.split('.')[-1] if '.' in code else code
        
        try:
            # 连接数据库
            conn = sqlite3.connect('data/a_share.db')
            
            # 查询最新财务数据（优先年报）
            query = """
            SELECT 
                code,
                report_date,
                roe,
                net_margin,
                gross_margin,
                debt_to_asset_ratio,
                current_ratio,
                quick_ratio,
                eps
            FROM financial_indicators
            WHERE code = ?
            ORDER BY report_date DESC
            LIMIT 1
            """
            
            df = pd.read_sql_query(query, conn, params=(pure_code,))
            conn.close()
            
            if df.empty:
                return None
            
            # 转换为字典
            data = df.iloc[0].to_dict()
            
            # 处理None值
            for key in data:
                if pd.isna(data[key]):
                    data[key] = None
            
            return data
            
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return None
    
    def _analyze_profitability(self, data: Dict) -> Dict:
        """
        分析盈利能力
        
        Returns:
            Dict: {
                'roe': ROE值,
                'roe_level': ROE等级 (excellent/good/fair/poor),
                'net_margin': 净利率,
                'eps': 每股收益
            }
        """
        roe = data.get('roe')
        net_margin = data.get('net_margin')
        eps = data.get('eps')
        
        # ROE等级判断
        if roe is None:
            roe_level = 'unknown'
        elif roe >= 20:
            roe_level = 'excellent'  # 优秀
        elif roe >= 15:
            roe_level = 'good'  # 良好
        elif roe >= 10:
            roe_level = 'fair'  # 一般
        elif roe >= 0:
            roe_level = 'poor'  # 较差
        else:
            roe_level = 'negative'  # 亏损
        
        return {
            'roe': round(roe, 2) if roe is not None else None,
            'roe_level': roe_level,
            'net_margin': round(net_margin, 2) if net_margin is not None else None,
            'eps': round(eps, 2) if eps is not None else None
        }
    
    def _analyze_solvency(self, data: Dict) -> Dict:
        """
        分析偿债能力
        
        Returns:
            Dict: {
                'debt_ratio': 资产负债率,
                'debt_level': 负债等级 (low/medium/high/very_high),
                'current_ratio': 流动比率,
                'quick_ratio': 速动比率
            }
        """
        debt_ratio = data.get('debt_to_asset_ratio')
        current_ratio = data.get('current_ratio')
        quick_ratio = data.get('quick_ratio')
        
        # 负债等级判断
        if debt_ratio is None:
            debt_level = 'unknown'
        elif debt_ratio < 40:
            debt_level = 'low'  # 低负债
        elif debt_ratio < 60:
            debt_level = 'medium'  # 中等负债
        elif debt_ratio < 70:
            debt_level = 'high'  # 高负债
        else:
            debt_level = 'very_high'  # 极高负债
        
        return {
            'debt_ratio': round(debt_ratio, 2) if debt_ratio is not None else None,
            'debt_level': debt_level,
            'current_ratio': round(current_ratio, 2) if current_ratio is not None else None,
            'quick_ratio': round(quick_ratio, 2) if quick_ratio is not None else None
        }
    
    def _calculate_risk_score(
        self, 
        profitability: Dict, 
        solvency: Dict, 
        is_st: bool
    ) -> float:
        """
        计算财务风险评分（0-100，越高越好）
        
        评分规则：
        - ROE: 40分
        - 资产负债率: 30分
        - 流动比率: 20分
        - ST状态: -50分
        """
        score = 0.0
        
        # ST股票直接扣50分
        if is_st:
            score -= 50
        
        # ROE评分（40分）
        roe = profitability.get('roe')
        if roe is not None:
            if roe >= 20:
                score += 40
            elif roe >= 15:
                score += 35
            elif roe >= 10:
                score += 25
            elif roe >= 5:
                score += 15
            elif roe >= 0:
                score += 5
            else:
                score -= 10  # 亏损扣分
        
        # 资产负债率评分（30分）
        debt_ratio = solvency.get('debt_ratio')
        if debt_ratio is not None:
            if debt_ratio < 40:
                score += 30
            elif debt_ratio < 60:
                score += 20
            elif debt_ratio < 70:
                score += 10
            else:
                score += 0  # 高负债不加分
        
        # 流动比率评分（20分）
        current_ratio = solvency.get('current_ratio')
        if current_ratio is not None:
            if current_ratio >= 2:
                score += 20
            elif current_ratio >= 1.5:
                score += 15
            elif current_ratio >= 1:
                score += 10
            else:
                score += 0  # 流动性不足不加分
        
        # 速动比率加分（10分）
        quick_ratio = solvency.get('quick_ratio')
        if quick_ratio is not None:
            if quick_ratio >= 1:
                score += 10
            elif quick_ratio >= 0.8:
                score += 5
        
        return round(max(0, min(100, score)), 1)
    
    def _generate_risk_status(
        self,
        profitability: Dict,
        solvency: Dict,
        is_st: bool,
        risk_score: float
    ) -> tuple[str, str]:
        """
        生成财务风险状态和建议
        
        Returns:
            (status, message)
        """
        messages = []
        
        # ST预警
        if is_st:
            return (
                'red',
                '⚠️ 该股已被ST，存在退市风险，不建议买入'
            )
        
        # ROE分析
        roe = profitability.get('roe')
        roe_level = profitability.get('roe_level')
        
        if roe is not None:
            if roe_level == 'excellent':
                messages.append(f'盈利能力优秀（ROE={roe:.1f}%）')
            elif roe_level == 'good':
                messages.append(f'盈利能力良好（ROE={roe:.1f}%）')
            elif roe_level == 'fair':
                messages.append(f'盈利能力一般（ROE={roe:.1f}%）')
            elif roe_level == 'poor':
                messages.append(f'盈利能力较弱（ROE={roe:.1f}%）')
            elif roe_level == 'negative':
                messages.append(f'⚠️ 公司亏损（ROE={roe:.1f}%）')
        
        # 负债分析
        debt_ratio = solvency.get('debt_ratio')
        debt_level = solvency.get('debt_level')
        
        if debt_ratio is not None:
            if debt_level == 'low':
                messages.append(f'财务稳健（负债率{debt_ratio:.1f}%）')
            elif debt_level == 'medium':
                messages.append(f'负债适中（负债率{debt_ratio:.1f}%）')
            elif debt_level == 'high':
                messages.append(f'⚠️ 负债较高（负债率{debt_ratio:.1f}%）')
            elif debt_level == 'very_high':
                messages.append(f'⚠️ 负债过高（负债率{debt_ratio:.1f}%），财务压力大')
        
        # 综合判断
        if risk_score >= 80:
            status = 'green'
            summary = '财务状况优秀'
        elif risk_score >= 60:
            status = 'green'
            summary = '财务状况良好'
        elif risk_score >= 40:
            status = 'yellow'
            summary = '财务状况一般'
        elif risk_score >= 20:
            status = 'yellow'
            summary = '财务状况较差，注意风险'
        else:
            status = 'red'
            summary = '财务状况堪忧，风险较高'
        
        message = f'{summary}：{"，".join(messages)}'
        
        return status, message
    
    def _empty_report(self, code: str, name: str = None, is_st: bool = False) -> Dict:
        """返回空报告"""
        if is_st:
            status = 'red'
            message = '⚠️ 该股已被ST，存在退市风险，不建议买入'
        else:
            status = 'yellow'
            message = '无财务数据，无法评估财务风险'
        
        return {
            'code': code,
            'name': name or code,
            'status': status,
            'message': message,
            'is_st': is_st,
            'risk_score': 0.0,
            'profitability': {},
            'solvency': {},
            'report_date': None
        }
    
    def generate_financial_report(self, code: str) -> Dict:
        """
        生成财务风险报告（便捷方法）
        
        Args:
            code: 股票代码
            
        Returns:
            Dict: 财务风险分析报告
        """
        return self.analyze_financial_risk(code)


# 便捷函数
def analyze_financial_risk(code: str) -> Dict:
    """
    分析财务风险（便捷函数）
    
    Args:
        code: 股票代码
        
    Returns:
        Dict: 财务风险分析报告
    """
    analyzer = FinancialRiskAnalyzer()
    return analyzer.analyze_financial_risk(code)

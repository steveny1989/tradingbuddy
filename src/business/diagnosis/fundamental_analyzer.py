# -*- coding: utf-8 -*-
"""
基本面分析器 (Fundamental Analyzer)

分析股票的财务指标、盈利能力、财务健康状况，并与行业平均水平对比
"""
import sqlite3
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta


class FundamentalAnalyzer:
    """基本面分析器"""
    
    def __init__(self, db_path: str = 'data/stock_data.db', industry_db_path: str = 'data/a_share.db'):
        """
        初始化基本面分析器
        
        Args:
            db_path: 股票数据库路径
            industry_db_path: 行业数据库路径
        """
        self.db_path = db_path
        self.industry_db_path = industry_db_path
    
    def _get_connection(self, db_path: Optional[str] = None) -> sqlite3.Connection:
        """获取数据库连接"""
        path = db_path or self.db_path
        conn = sqlite3.Connection(path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def analyze(self, code: str) -> Dict:
        """
        对股票进行基本面分析
        
        Args:
            code: 股票代码 (如 '600519')
        
        Returns:
            基本面分析结果字典
        """
        # 获取财务指标
        financial_data = self._get_financial_indicators(code)
        if not financial_data:
            return self._create_empty_result(code, '无财务数据')
        
        # 获取利润表数据
        income_data = self._get_income_statement(code)
        
        # 获取资产负债表数据
        balance_data = self._get_balance_sheet(code)
        
        # 获取行业信息
        industry = self._get_industry(code)
        
        # 行业对比
        industry_comparison = {}
        if industry:
            industry_comparison = self._compare_with_industry(code, industry, financial_data)
        
        # 计算评分
        score = self._calculate_score(financial_data, income_data, balance_data, industry_comparison)
        
        # 生成状态和描述
        status = self._get_status_from_score(score)
        message = self._generate_message(score, financial_data, income_data, industry_comparison)
        
        # 构建详细数据
        details = {
            'pe': financial_data.get('pe_ratio'),
            'pb': financial_data.get('pb_ratio'),
            'roe': financial_data.get('roe'),
            'roa': financial_data.get('roa'),
            'net_margin': financial_data.get('net_margin'),
            'debt_ratio': financial_data.get('debt_to_asset_ratio'),
            'current_ratio': financial_data.get('current_ratio'),
            'industry': industry,
            'industry_comparison': industry_comparison
        }
        
        # 添加增长率数据
        if income_data:
            details['profit_growth_yoy'] = income_data.get('profit_growth_yoy')
            details['revenue_growth_yoy'] = income_data.get('revenue_growth_yoy')
        
        return {
            'score': score,
            'status': status,
            'message': message,
            'details': details
        }
    
    def _get_financial_indicators(self, code: str) -> Optional[Dict]:
        """
        获取最新的财务指标
        
        Args:
            code: 股票代码
        
        Returns:
            财务指标字典，如果没有数据则返回 None
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT *
                FROM financial_indicators
                WHERE code = ?
                ORDER BY report_date DESC
                LIMIT 1
            """, (code,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    def _get_income_statement(self, code: str, periods: int = 2) -> Optional[Dict]:
        """
        获取利润表数据并计算增长率
        
        Args:
            code: 股票代码
            periods: 获取最近几期数据
        
        Returns:
            利润表数据字典，包含增长率
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT *
                FROM income_statement
                WHERE code = ?
                ORDER BY report_date DESC
                LIMIT ?
            """, (code, periods))
            
            rows = cursor.fetchall()
            if not rows:
                return None
            
            current = dict(rows[0])
            
            # 计算同比增长率
            if len(rows) >= 2:
                previous = dict(rows[1])
                
                # 净利润增长率
                if current.get('net_profit') and previous.get('net_profit') and previous['net_profit'] != 0:
                    current['profit_growth_yoy'] = (
                        (current['net_profit'] - previous['net_profit']) / abs(previous['net_profit']) * 100
                    )
                
                # 营业收入增长率
                if current.get('operating_revenue') and previous.get('operating_revenue') and previous['operating_revenue'] != 0:
                    current['revenue_growth_yoy'] = (
                        (current['operating_revenue'] - previous['operating_revenue']) / abs(previous['operating_revenue']) * 100
                    )
            
            return current
        finally:
            conn.close()
    
    def _get_balance_sheet(self, code: str) -> Optional[Dict]:
        """
        获取资产负债表数据
        
        Args:
            code: 股票代码
        
        Returns:
            资产负债表数据字典
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                SELECT *
                FROM balance_sheet
                WHERE code = ?
                ORDER BY report_date DESC
                LIMIT 1
            """, (code,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    def _get_industry(self, code: str) -> Optional[str]:
        """
        获取股票所属行业
        
        Args:
            code: 股票代码
        
        Returns:
            行业名称
        """
        conn = self._get_connection(self.industry_db_path)
        try:
            cursor = conn.execute("""
                SELECT industry
                FROM industry_data
                WHERE code = ?
                LIMIT 1
            """, (code,))
            
            row = cursor.fetchone()
            if row and row['industry']:
                return row['industry']
            return None
        finally:
            conn.close()
    
    def _compare_with_industry(self, code: str, industry: str, financial_data: Dict) -> Dict:
        """
        与行业平均水平对比
        
        Args:
            code: 股票代码
            industry: 行业名称
            financial_data: 个股财务数据
        
        Returns:
            行业对比结果
        """
        # 获取同行业股票列表
        industry_stocks = self._get_industry_stocks(industry, exclude_code=code)
        
        if not industry_stocks:
            return {}
        
        # 获取行业平均指标
        industry_avg = self._calculate_industry_average(industry_stocks)
        
        if not industry_avg:
            return {}
        
        # 计算百分位排名
        comparison = {}
        
        # PE 对比
        if financial_data.get('pe_ratio') and industry_avg.get('pe_ratio'):
            comparison['pe_vs_industry'] = financial_data['pe_ratio'] - industry_avg['pe_ratio']
            comparison['pe_percentile'] = self._calculate_percentile(
                code, industry_stocks, 'pe_ratio', financial_data['pe_ratio']
            )
        
        # ROE 对比
        if financial_data.get('roe') and industry_avg.get('roe'):
            comparison['roe_vs_industry'] = financial_data['roe'] - industry_avg['roe']
            comparison['roe_percentile'] = self._calculate_percentile(
                code, industry_stocks, 'roe', financial_data['roe']
            )
        
        # 净利率对比
        if financial_data.get('net_margin') and industry_avg.get('net_margin'):
            comparison['net_margin_vs_industry'] = financial_data['net_margin'] - industry_avg['net_margin']
        
        comparison['industry_avg'] = industry_avg
        comparison['industry_stock_count'] = len(industry_stocks)
        
        return comparison
    
    def _get_industry_stocks(self, industry: str, exclude_code: Optional[str] = None) -> List[str]:
        """
        获取同行业股票列表
        
        Args:
            industry: 行业名称
            exclude_code: 要排除的股票代码
        
        Returns:
            股票代码列表
        """
        conn = self._get_connection(self.industry_db_path)
        try:
            if exclude_code:
                cursor = conn.execute("""
                    SELECT code
                    FROM industry_data
                    WHERE industry = ? AND code != ?
                    LIMIT 100
                """, (industry, exclude_code))
            else:
                cursor = conn.execute("""
                    SELECT code
                    FROM industry_data
                    WHERE industry = ?
                    LIMIT 100
                """, (industry,))
            
            return [row['code'] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def _calculate_industry_average(self, stock_codes: List[str]) -> Dict:
        """
        计算行业平均指标
        
        Args:
            stock_codes: 股票代码列表
        
        Returns:
            行业平均指标字典
        """
        if not stock_codes:
            return {}
        
        conn = self._get_connection()
        try:
            placeholders = ','.join('?' * len(stock_codes))
            cursor = conn.execute(f"""
                SELECT 
                    AVG(pe_ratio) as pe_ratio,
                    AVG(pb_ratio) as pb_ratio,
                    AVG(roe) as roe,
                    AVG(roa) as roa,
                    AVG(net_margin) as net_margin,
                    AVG(debt_to_asset_ratio) as debt_to_asset_ratio,
                    AVG(current_ratio) as current_ratio
                FROM (
                    SELECT code, pe_ratio, pb_ratio, roe, roa, net_margin, 
                           debt_to_asset_ratio, current_ratio,
                           ROW_NUMBER() OVER (PARTITION BY code ORDER BY report_date DESC) as rn
                    FROM financial_indicators
                    WHERE code IN ({placeholders})
                )
                WHERE rn = 1
            """, stock_codes)
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {}
        finally:
            conn.close()
    
    def _calculate_percentile(self, code: str, industry_stocks: List[str], 
                             metric: str, value: float) -> int:
        """
        计算个股在行业内的百分位排名
        
        Args:
            code: 股票代码
            industry_stocks: 行业股票列表
            metric: 指标名称
            value: 个股指标值
        
        Returns:
            百分位排名 (0-100)
        """
        if not industry_stocks or value is None:
            return 50
        
        conn = self._get_connection()
        try:
            # 获取所有行业股票的该指标值
            placeholders = ','.join('?' * len(industry_stocks))
            cursor = conn.execute(f"""
                SELECT {metric}
                FROM (
                    SELECT code, {metric},
                           ROW_NUMBER() OVER (PARTITION BY code ORDER BY report_date DESC) as rn
                    FROM financial_indicators
                    WHERE code IN ({placeholders}) AND {metric} IS NOT NULL
                )
                WHERE rn = 1
                ORDER BY {metric}
            """, industry_stocks)
            
            values = [row[metric] for row in cursor.fetchall() if row[metric] is not None]
            
            if not values:
                return 50
            
            # 计算百分位
            count_below = sum(1 for v in values if v < value)
            percentile = int((count_below / len(values)) * 100)
            
            return percentile
        finally:
            conn.close()
    
    def _calculate_score(self, financial_data: Dict, income_data: Optional[Dict],
                        balance_data: Optional[Dict], industry_comparison: Dict) -> int:
        """
        计算基本面综合评分
        
        评分规则:
        - ROE评分 (30分): >15%高分, <5%低分
        - 盈利增长评分 (25分): >10%高分, <0%低分
        - PE合理性评分 (20分): 与行业平均对比
        - 财务健康评分 (25分): 负债率、流动比率
        
        Args:
            financial_data: 财务指标数据
            income_data: 利润表数据
            balance_data: 资产负债表数据
            industry_comparison: 行业对比数据
        
        Returns:
            综合评分 (0-100)
        """
        score = 0
        
        # 1. ROE评分 (30分)
        roe = financial_data.get('roe')
        if roe is not None:
            if roe >= 15:
                score += 30
            elif roe >= 10:
                score += 25
            elif roe >= 5:
                score += 15
            elif roe >= 0:
                score += 5
            # ROE < 0 不加分
        
        # 2. 盈利增长评分 (25分)
        if income_data:
            profit_growth = income_data.get('profit_growth_yoy')
            if profit_growth is not None:
                if profit_growth >= 20:
                    score += 25
                elif profit_growth >= 10:
                    score += 20
                elif profit_growth >= 5:
                    score += 15
                elif profit_growth >= 0:
                    score += 10
                elif profit_growth >= -10:
                    score += 5
                # 增长率 < -10% 不加分
        
        # 3. PE合理性评分 (20分)
        pe = financial_data.get('pe_ratio')
        if pe is not None and pe > 0:
            if industry_comparison and 'pe_percentile' in industry_comparison:
                percentile = industry_comparison['pe_percentile']
                # PE在行业中等偏低为好 (30-60百分位)
                if 30 <= percentile <= 60:
                    score += 20
                elif 20 <= percentile < 30 or 60 < percentile <= 70:
                    score += 15
                elif 10 <= percentile < 20 or 70 < percentile <= 80:
                    score += 10
                else:
                    score += 5
            else:
                # 没有行业对比，根据绝对值判断
                if 10 <= pe <= 30:
                    score += 20
                elif 5 <= pe < 10 or 30 < pe <= 50:
                    score += 15
                elif pe < 5 or 50 < pe <= 80:
                    score += 10
                else:
                    score += 5
        
        # 4. 财务健康评分 (25分)
        debt_ratio = financial_data.get('debt_to_asset_ratio')
        current_ratio = financial_data.get('current_ratio')
        
        # 负债率评分 (12.5分)
        if debt_ratio is not None:
            if debt_ratio <= 30:
                score += 12.5
            elif debt_ratio <= 50:
                score += 10
            elif debt_ratio <= 70:
                score += 6
            else:
                score += 2
        
        # 流动比率评分 (12.5分)
        if current_ratio is not None:
            if current_ratio >= 2.0:
                score += 12.5
            elif current_ratio >= 1.5:
                score += 10
            elif current_ratio >= 1.0:
                score += 6
            else:
                score += 2
        
        return int(min(100, max(0, score)))
    
    def _get_status_from_score(self, score: int) -> str:
        """
        根据评分获取状态
        
        Args:
            score: 评分 (0-100)
        
        Returns:
            状态: green/yellow/red
        """
        if score >= 70:
            return 'green'
        elif score >= 50:
            return 'yellow'
        else:
            return 'red'
    
    def _generate_message(self, score: int, financial_data: Dict,
                         income_data: Optional[Dict], industry_comparison: Dict) -> str:
        """
        生成人话描述
        
        Args:
            score: 评分
            financial_data: 财务数据
            income_data: 利润表数据
            industry_comparison: 行业对比数据
        
        Returns:
            易懂的中文描述
        """
        messages = []
        
        # 整体评价
        if score >= 80:
            messages.append('基本面优秀')
        elif score >= 65:
            messages.append('基本面良好')
        elif score >= 50:
            messages.append('基本面一般')
        else:
            messages.append('基本面较弱')
        
        # ROE描述
        roe = financial_data.get('roe')
        if roe is not None:
            if roe >= 15:
                messages.append(f'盈利能力强(ROE {roe:.1f}%)')
            elif roe >= 10:
                messages.append(f'盈利能力较好(ROE {roe:.1f}%)')
            elif roe < 5:
                messages.append(f'盈利能力偏弱(ROE {roe:.1f}%)')
        
        # 增长描述
        if income_data and income_data.get('profit_growth_yoy') is not None:
            growth = income_data['profit_growth_yoy']
            if growth >= 10:
                messages.append(f'利润增长良好({growth:.1f}%)')
            elif growth < 0:
                messages.append(f'利润下滑({growth:.1f}%)')
        
        # 行业对比描述
        if industry_comparison and 'roe_percentile' in industry_comparison:
            percentile = industry_comparison['roe_percentile']
            if percentile >= 75:
                messages.append('行业内领先')
            elif percentile <= 25:
                messages.append('行业内落后')
        
        # 财务健康描述
        debt_ratio = financial_data.get('debt_to_asset_ratio')
        if debt_ratio is not None:
            if debt_ratio <= 30:
                messages.append('财务稳健')
            elif debt_ratio >= 70:
                messages.append('负债率偏高')
        
        return '；'.join(messages)
    
    def _create_empty_result(self, code: str, reason: str) -> Dict:
        """创建空结果"""
        return {
            'score': 0,
            'status': 'yellow',
            'message': f'基本面数据不足: {reason}',
            'details': {}
        }

"""
行业面分析模块
提供个股行业归属、行业涨跌幅排行、板块联动性分析
"""

import sqlite3
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SectorAnalyzer:
    """行业面分析器"""
    
    def __init__(self, db_path: str = "data/a_share.db"):
        self.db_path = db_path
    
    def get_stock_industry(self, code: str) -> Optional[Dict]:
        """
        获取个股行业信息
        
        Args:
            code: 股票代码 (如: 600519 或 sh.600519)
        
        Returns:
            {
                'code': '600519',
                'name': '贵州茅台',
                'industry': '食品饮料',
                'market': 'sh'
            }
        """
        # 处理代码格式
        if '.' in code:
            code = code.split('.')[1]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = """
        SELECT code, name, industry, market
        FROM industry_data
        WHERE code = ?
        """
        
        cursor.execute(query, (code,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'code': result[0],
                'name': result[1],
                'industry': result[2],
                'market': result[3]
            }
        
        return None
    
    def get_industry_performance(self, date: Optional[str] = None, top_n: int = 20) -> pd.DataFrame:
        """
        获取行业涨跌幅排行
        
        Args:
            date: 交易日期 (YYYY-MM-DD)，默认最新交易日
            top_n: 返回前N个行业
        
        Returns:
            DataFrame with columns: industry, avg_pct_chg, stock_count, total_amount, up_count, down_count
        """
        conn = sqlite3.connect(self.db_path)
        
        # 如果没有指定日期，获取最新交易日
        if date is None:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(date) FROM daily_data")
            date = cursor.fetchone()[0]
        
        query = """
        SELECT 
            i.industry,
            AVG(d.pct_chg) as avg_pct_chg,
            COUNT(*) as stock_count,
            SUM(d.amount) / 1e8 as total_amount_billion,
            SUM(CASE WHEN d.pct_chg > 0 THEN 1 ELSE 0 END) as up_count,
            SUM(CASE WHEN d.pct_chg < 0 THEN 1 ELSE 0 END) as down_count,
            SUM(CASE WHEN d.pct_chg >= 9.9 THEN 1 ELSE 0 END) as limit_up_count
        FROM industry_data i
        JOIN daily_data d ON i.full_code = d.code
        WHERE d.date = ?
        GROUP BY i.industry
        ORDER BY avg_pct_chg DESC
        LIMIT ?
        """
        
        df = pd.read_sql(query, conn, params=(date, top_n))
        conn.close()
        
        # 计算上涨比例
        df['up_ratio'] = (df['up_count'] / df['stock_count'] * 100).round(2)
        
        return df
    
    def get_industry_stocks(self, industry: str, date: Optional[str] = None, top_n: int = 10) -> pd.DataFrame:
        """
        获取某行业的股票列表（按涨跌幅排序）
        
        Args:
            industry: 行业名称
            date: 交易日期，默认最新交易日
            top_n: 返回前N只股票
        
        Returns:
            DataFrame with columns: code, name, close, pct_chg, volume, amount
        """
        conn = sqlite3.connect(self.db_path)
        
        if date is None:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(date) FROM daily_data")
            date = cursor.fetchone()[0]
        
        query = """
        SELECT 
            i.code,
            i.name,
            d.close,
            d.pct_chg,
            d.volume / 1e4 as volume_wan,
            d.amount / 1e8 as amount_billion
        FROM industry_data i
        JOIN daily_data d ON i.full_code = d.code
        WHERE i.industry = ? AND d.date = ?
        ORDER BY d.pct_chg DESC
        LIMIT ?
        """
        
        df = pd.read_sql(query, conn, params=(industry, date, top_n))
        conn.close()
        
        return df
    
    def analyze_sector_correlation(self, code: str, days: int = 30) -> Dict:
        """
        分析个股与行业的相关性（板块联动性）
        
        Args:
            code: 股票代码
            days: 分析天数
        
        Returns:
            {
                'industry': '食品饮料',
                'correlation': 0.85,
                'stock_performance': 2.5,
                'industry_performance': 1.8,
                'relative_strength': 'strong',  # strong/weak/neutral
                'message': '个股表现强于行业'
            }
        """
        # 获取个股行业
        industry_info = self.get_stock_industry(code)
        if not industry_info:
            return {'error': '未找到股票行业信息'}
        
        industry = industry_info['industry']
        full_code = f"{industry_info['market']}.{code}" if '.' not in code else code
        
        conn = sqlite3.connect(self.db_path)
        
        # 获取个股最近N天的涨跌幅
        query_stock = """
        SELECT date, pct_chg
        FROM daily_data
        WHERE code = ?
        ORDER BY date DESC
        LIMIT ?
        """
        df_stock = pd.read_sql(query_stock, conn, params=(full_code, days))
        
        # 获取行业最近N天的平均涨跌幅
        query_industry = """
        SELECT d.date, AVG(d.pct_chg) as avg_pct_chg
        FROM industry_data i
        JOIN daily_data d ON i.full_code = d.code
        WHERE i.industry = ?
        AND d.date IN (SELECT DISTINCT date FROM daily_data ORDER BY date DESC LIMIT ?)
        GROUP BY d.date
        ORDER BY d.date DESC
        """
        df_industry = pd.read_sql(query_industry, conn, params=(industry, days))
        conn.close()
        
        if len(df_stock) == 0 or len(df_industry) == 0:
            return {'error': '数据不足'}
        
        # 合并数据
        df_merged = pd.merge(df_stock, df_industry, on='date', how='inner')
        
        if len(df_merged) < 5:
            return {'error': '数据不足'}
        
        # 计算相关系数
        correlation = df_merged['pct_chg'].corr(df_merged['avg_pct_chg'])
        
        # 计算累计涨跌幅
        stock_performance = df_stock['pct_chg'].sum()
        industry_performance = df_industry['avg_pct_chg'].sum()
        
        # 判断相对强弱
        diff = stock_performance - industry_performance
        if diff > 5:
            relative_strength = 'strong'
            message = f"个股表现强于行业，跑赢{diff:.1f}个百分点"
        elif diff < -5:
            relative_strength = 'weak'
            message = f"个股表现弱于行业，跑输{abs(diff):.1f}个百分点"
        else:
            relative_strength = 'neutral'
            message = "个股表现与行业基本一致"
        
        return {
            'industry': industry,
            'correlation': round(correlation, 3),
            'stock_performance': round(stock_performance, 2),
            'industry_performance': round(industry_performance, 2),
            'relative_strength': relative_strength,
            'message': message,
            'days': len(df_merged)
        }
    
    def get_sector_recommendation(self, code: str, top_n: int = 5) -> Dict:
        """
        获取同行业股票推荐
        
        Args:
            code: 股票代码
            top_n: 推荐数量
        
        Returns:
            {
                'industry': '食品饮料',
                'recommendations': [
                    {'code': '000858', 'name': '五粮液', 'pct_chg': 2.5, 'reason': '行业龙头'},
                    ...
                ]
            }
        """
        industry_info = self.get_stock_industry(code)
        if not industry_info:
            return {'error': '未找到股票行业信息'}
        
        industry = industry_info['industry']
        
        # 获取同行业股票（排除自己）
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT 
            i.code,
            i.name,
            d.close,
            d.pct_chg,
            d.amount / 1e8 as amount_billion,
            m.total_cap / 1e8 as market_cap_billion
        FROM industry_data i
        JOIN daily_data d ON i.full_code = d.code
        LEFT JOIN market_cap_data m ON i.code = m.code
        WHERE i.industry = ? 
        AND i.code != ?
        AND d.date = (SELECT MAX(date) FROM daily_data)
        ORDER BY d.amount DESC
        LIMIT ?
        """
        
        df = pd.read_sql(query, conn, params=(industry, code.replace('sh.', '').replace('sz.', ''), top_n * 2))
        conn.close()
        
        if len(df) == 0:
            return {'industry': industry, 'recommendations': []}
        
        # 筛选推荐股票（成交额较大的）
        recommendations = []
        for _, row in df.head(top_n).iterrows():
            reason = []
            if row['market_cap_billion'] and row['market_cap_billion'] > 100:
                reason.append('大盘股')
            if row['amount_billion'] > 10:
                reason.append('成交活跃')
            if row['pct_chg'] > 3:
                reason.append('强势上涨')
            
            recommendations.append({
                'code': row['code'],
                'name': row['name'],
                'close': round(row['close'], 2) if pd.notna(row['close']) else None,
                'pct_chg': round(row['pct_chg'], 2) if pd.notna(row['pct_chg']) else None,
                'reason': '、'.join(reason) if reason else '同行业股票'
            })
        
        return {
            'industry': industry,
            'total_stocks': len(df),
            'recommendations': recommendations
        }
    
    def generate_sector_report(self, code: str) -> Dict:
        """
        生成完整的行业面分析报告
        
        Args:
            code: 股票代码
        
        Returns:
            完整的行业分析报告
        """
        # 1. 获取行业信息
        industry_info = self.get_stock_industry(code)
        if not industry_info:
            return {'error': '未找到股票行业信息'}
        
        # 2. 获取行业表现
        industry_perf = self.get_industry_performance()
        industry_rank = None
        if len(industry_perf) > 0:
            industry_row = industry_perf[industry_perf['industry'] == industry_info['industry']]
            if len(industry_row) > 0:
                industry_rank = industry_perf.index[industry_perf['industry'] == industry_info['industry']].tolist()[0] + 1
        
        # 3. 板块联动性分析
        correlation = self.analyze_sector_correlation(code)
        
        # 4. 同行业推荐
        recommendations = self.get_sector_recommendation(code)
        
        # 5. 生成人话描述
        status = 'yellow'
        message_parts = []
        
        # 行业排名
        if industry_rank:
            if industry_rank <= 5:
                status = 'green'
                message_parts.append(f"所属行业'{industry_info['industry']}'表现强势，排名第{industry_rank}")
            elif industry_rank <= 10:
                message_parts.append(f"所属行业'{industry_info['industry']}'表现中等，排名第{industry_rank}")
            else:
                status = 'red'
                message_parts.append(f"所属行业'{industry_info['industry']}'表现较弱，排名第{industry_rank}")
        
        # 个股相对强弱
        if 'relative_strength' in correlation:
            if correlation['relative_strength'] == 'strong':
                status = 'green' if status != 'red' else status
                message_parts.append(correlation['message'])
            elif correlation['relative_strength'] == 'weak':
                status = 'red'
                message_parts.append(correlation['message'])
        
        return {
            'status': status,
            'industry': industry_info['industry'],
            'industry_rank': industry_rank,
            'correlation': correlation,
            'recommendations': recommendations,
            'message': '；'.join(message_parts) if message_parts else f"所属行业：{industry_info['industry']}"
        }


if __name__ == "__main__":
    # 测试代码
    analyzer = SectorAnalyzer()
    
    # 测试1: 获取个股行业
    print("=== 测试1: 获取个股行业 ===")
    result = analyzer.get_stock_industry("600519")
    print(result)
    
    # 测试2: 获取行业涨跌幅排行
    print("\n=== 测试2: 行业涨跌幅排行 ===")
    df = analyzer.get_industry_performance(top_n=10)
    print(df.to_string())
    
    # 测试3: 板块联动性分析
    print("\n=== 测试3: 板块联动性分析 ===")
    result = analyzer.analyze_sector_correlation("600519", days=30)
    print(result)
    
    # 测试4: 同行业推荐
    print("\n=== 测试4: 同行业推荐 ===")
    result = analyzer.get_sector_recommendation("600519")
    print(result)
    
    # 测试5: 完整报告
    print("\n=== 测试5: 完整行业分析报告 ===")
    result = analyzer.generate_sector_report("600519")
    print(result)

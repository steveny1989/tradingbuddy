# -*- coding: utf-8 -*-
"""
大盘对比分析器 (Market Comparison Analyzer)

对比个股与大盘表现：
1. 计算个股收益率
2. 计算大盘指数收益率（上证指数、深证成指）
3. 计算相对表现（跑赢/跑输）
4. 计算Beta（相对大盘波动率）
5. 评分算法：0-100分
"""
import sqlite3
import pandas as pd
import numpy as np
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketComparisonAnalyzer:
    """大盘对比分析器"""
    
    def __init__(self, db_path: str = "data/a_share.db"):
        self.db_path = db_path
        # 大盘指数代码
        self.sh_index = 'sh.000001'  # 上证指数
        self.sz_index = 'sz.399001'  # 深证成指
    
    def analyze(self, code: str, days: int = 30) -> Dict:
        """
        大盘对比分析
        
        Args:
            code: 股票代码 (如: 600519 或 sh.600519)
            days: 分析天数（默认30天）
        
        Returns:
            {
                'score': 80,  # 0-100
                'status': 'green',  # green/yellow/red
                'message': '近30日跑赢大盘7.3%，表现强势',
                'details': {
                    'stock_return_30d': 15.5,
                    'sh_index_return_30d': 8.2,
                    'sz_index_return_30d': 10.1,
                    'outperformance_sh': 7.3,
                    'outperformance_sz': 5.4,
                    'beta': 1.2,
                    'relative_strength': 'strong'
                }
            }
        """
        # 处理代码格式
        full_code = code if '.' in code else self._get_full_code(code)
        if not full_code:
            return self._create_no_data_result(code)
        
        # 1. 获取个股收益率
        stock_return = self._calculate_return(full_code, days)
        if stock_return is None:
            return self._create_no_data_result(code)
        
        # 2. 获取大盘指数收益率
        sh_return = self._calculate_return(self.sh_index, days)
        sz_return = self._calculate_return(self.sz_index, days)
        
        # 3. 计算相对表现
        outperformance_sh = stock_return - sh_return if sh_return is not None else None
        outperformance_sz = stock_return - sz_return if sz_return is not None else None
        
        # 4. 计算Beta
        beta = self._calculate_beta(full_code, self.sh_index, days)
        
        # 5. 判断相对强弱
        relative_strength = self._get_relative_strength(outperformance_sh)
        
        # 6. 计算评分
        score = self._calculate_score(outperformance_sh, beta)
        
        # 7. 生成状态和描述
        status = self._get_status_from_score(score)
        message = self._generate_message(stock_return, sh_return, outperformance_sh, 
                                        relative_strength, days)
        
        # 8. 组装详细数据
        details = {
            'stock_return_30d': round(stock_return, 2) if stock_return is not None else None,
            'sh_index_return_30d': round(sh_return, 2) if sh_return is not None else None,
            'sz_index_return_30d': round(sz_return, 2) if sz_return is not None else None,
            'outperformance_sh': round(outperformance_sh, 2) if outperformance_sh is not None else None,
            'outperformance_sz': round(outperformance_sz, 2) if outperformance_sz is not None else None,
            'beta': round(beta, 2) if beta is not None else None,
            'relative_strength': relative_strength,
            'days': days
        }
        
        return {
            'score': score,
            'status': status,
            'message': message,
            'details': details
        }
    
    def _get_full_code(self, code: str) -> Optional[str]:
        """获取完整股票代码"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT full_code FROM stock_basic WHERE code = ?"
        cursor.execute(query, (code,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def _calculate_return(self, code: str, days: int) -> Optional[float]:
        """
        计算N日收益率
        
        Args:
            code: 完整股票代码 (如: sh.600519)
            days: 天数
        
        Returns:
            收益率 (%)
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT date, close
        FROM daily_data
        WHERE code = ?
        ORDER BY date DESC
        LIMIT ?
        """
        
        df = pd.read_sql(query, conn, params=(code, days + 10))
        conn.close()
        
        if len(df) < 2:
            return None
        
        # 获取最新价格和N天前价格
        latest_price = df.iloc[0]['close']
        
        # 找到N天前的价格（可能不是精确N天，取最接近的）
        if len(df) > days:
            old_price = df.iloc[days]['close']
        else:
            old_price = df.iloc[-1]['close']
        
        if old_price == 0 or pd.isna(old_price) or pd.isna(latest_price):
            return None
        
        return_rate = (latest_price - old_price) / old_price * 100
        return return_rate
    
    def _calculate_beta(self, stock_code: str, index_code: str, days: int) -> Optional[float]:
        """
        计算Beta（相对大盘波动率）
        
        Beta > 1: 波动大于大盘
        Beta = 1: 波动与大盘一致
        Beta < 1: 波动小于大盘
        """
        conn = sqlite3.connect(self.db_path)
        
        # 获取个股和指数的日收益率
        query = """
        SELECT date, close
        FROM daily_data
        WHERE code = ?
        ORDER BY date DESC
        LIMIT ?
        """
        
        df_stock = pd.read_sql(query, conn, params=(stock_code, days + 10))
        df_index = pd.read_sql(query, conn, params=(index_code, days + 10))
        conn.close()
        
        if len(df_stock) < 10 or len(df_index) < 10:
            return None
        
        # 计算日收益率
        df_stock = df_stock.sort_values('date')
        df_index = df_index.sort_values('date')
        
        df_stock['return'] = df_stock['close'].pct_change() * 100
        df_index['return'] = df_index['close'].pct_change() * 100
        
        # 合并数据
        df_merged = pd.merge(df_stock[['date', 'return']], 
                            df_index[['date', 'return']], 
                            on='date', 
                            suffixes=('_stock', '_index'))
        
        df_merged = df_merged.dropna()
        
        if len(df_merged) < 5:
            return None
        
        # 计算协方差和方差
        cov = df_merged['return_stock'].cov(df_merged['return_index'])
        var = df_merged['return_index'].var()
        
        if var == 0:
            return None
        
        beta = cov / var
        return beta
    
    def _get_relative_strength(self, outperformance: Optional[float]) -> str:
        """判断相对强弱"""
        if outperformance is None:
            return 'neutral'
        
        if outperformance > 5:
            return 'strong'
        elif outperformance < -5:
            return 'weak'
        else:
            return 'neutral'
    
    def _calculate_score(self, outperformance: Optional[float], beta: Optional[float]) -> int:
        """
        计算评分 (0-100)
        
        评分逻辑：
        - 跑赢大盘 >10% = 90-100分
        - 跑赢大盘 5-10% = 75-90分
        - 跑赢大盘 0-5% = 60-75分
        - 跑输大盘 0-5% = 45-60分
        - 跑输大盘 5-10% = 30-45分
        - 跑输大盘 >10% = 0-30分
        - Beta适中(0.8-1.2)加分
        """
        score = 50  # 基础分
        
        # 1. 相对表现评分 (最高80分)
        if outperformance is not None:
            if outperformance >= 10:
                score = 95
            elif outperformance >= 5:
                score = 80
            elif outperformance >= 0:
                score = 65
            elif outperformance >= -5:
                score = 50
            elif outperformance >= -10:
                score = 35
            else:
                score = 20
        
        # 2. Beta评分 (调整±10分)
        if beta is not None:
            if 0.8 <= beta <= 1.2:
                # Beta适中，加分
                score += 10
            elif beta > 1.5 or beta < 0.5:
                # Beta过高或过低，减分
                score -= 10
        
        return max(0, min(100, score))
    
    def _get_status_from_score(self, score: int) -> str:
        """根据评分获取状态"""
        if score >= 70:
            return 'green'
        elif score >= 50:
            return 'yellow'
        else:
            return 'red'
    
    def _generate_message(self, stock_return: Optional[float], index_return: Optional[float],
                         outperformance: Optional[float], relative_strength: str, days: int) -> str:
        """生成人话描述"""
        if stock_return is None or index_return is None or outperformance is None:
            return f"近{days}日数据不足，无法对比"
        
        messages = []
        
        # 1. 相对表现描述
        if relative_strength == 'strong':
            messages.append(f"近{days}日跑赢大盘{abs(outperformance):.1f}%，表现强势")
        elif relative_strength == 'weak':
            messages.append(f"近{days}日跑输大盘{abs(outperformance):.1f}%，表现疲软")
        else:
            if outperformance > 0:
                messages.append(f"近{days}日小幅跑赢大盘{outperformance:.1f}%")
            elif outperformance < 0:
                messages.append(f"近{days}日小幅跑输大盘{abs(outperformance):.1f}%")
            else:
                messages.append(f"近{days}日与大盘同步")
        
        # 2. 绝对收益描述
        if stock_return > 10:
            messages.append(f"个股涨幅{stock_return:.1f}%")
        elif stock_return < -10:
            messages.append(f"个股跌幅{abs(stock_return):.1f}%")
        
        return "，".join(messages)
    
    def _create_no_data_result(self, code: str) -> Dict:
        """创建无数据结果"""
        return {
            'score': 50,
            'status': 'yellow',
            'message': '暂无大盘对比数据',
            'details': {
                'stock_return_30d': None,
                'sh_index_return_30d': None,
                'sz_index_return_30d': None,
                'outperformance_sh': None,
                'outperformance_sz': None,
                'beta': None,
                'relative_strength': 'neutral',
                'days': 30
            }
        }


if __name__ == "__main__":
    # 测试代码
    analyzer = MarketComparisonAnalyzer()
    
    # 测试1: 贵州茅台
    print("=== 测试1: 贵州茅台 (600519) ===")
    result = analyzer.analyze("600519", days=30)
    print(f"评分: {result['score']}")
    print(f"状态: {result['status']}")
    print(f"描述: {result['message']}")
    print(f"详细数据: {result['details']}")
    
    # 测试2: 平安银行
    print("\n=== 测试2: 平安银行 (000001) ===")
    result = analyzer.analyze("000001", days=30)
    print(f"评分: {result['score']}")
    print(f"状态: {result['status']}")
    print(f"描述: {result['message']}")
    
    # 测试3: 不同时间周期
    print("\n=== 测试3: 贵州茅台 (60日对比) ===")
    result = analyzer.analyze("600519", days=60)
    print(f"评分: {result['score']}")
    print(f"描述: {result['message']}")

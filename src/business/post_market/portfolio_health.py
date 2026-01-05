# -*- coding: utf-8 -*-
"""
持仓健康检查器（增强版）

多维度分析：
1. 技术面：MA20偏离度、RSI、量比
2. 情绪面：涨跌停基因、股性分析、波动性
3. 财务面：ROE、资产负债率、财务风险评分
4. 行业面：行业归属、板块联动性、同行业推荐
5. 资金面：北向资金、主力资金流向

输出红绿灯系统：
- 🟢 绿灯 (green): 健康，可以持有
- 🟡 黄灯 (yellow): 警示，注意风险
- 🔴 红灯 (red): 危险，考虑止损
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict
from src.data.database_adapter import DatabaseAdapter
from src.business.post_market.models import PortfolioHealth
from src.business.post_market.sector_analysis import SectorAnalyzer
from src.business.post_market.capital_analysis import CapitalAnalyzer
from src.business.post_market.sentiment_analysis import SentimentAnalyzer
from src.business.post_market.financial_risk import FinancialRiskAnalyzer


class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_ma(df: pd.DataFrame, periods=[20, 50, 250]) -> pd.DataFrame:
        """计算移动平均线"""
        for period in periods:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period=14) -> pd.DataFrame:
        """计算RSI相对强弱指标"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        df['rsi'] = rsi
        return df
    
    @staticmethod
    def calculate_volume_ratio(df: pd.DataFrame, period=5) -> pd.DataFrame:
        """计算量比"""
        df['volume_ma'] = df['volume'].rolling(window=period).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma']
        return df
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """计算所有指标"""
        df = TechnicalIndicators.calculate_ma(df, [20, 50, 250])
        df = TechnicalIndicators.calculate_rsi(df, 14)
        df = TechnicalIndicators.calculate_volume_ratio(df, 5)
        return df


class PortfolioHealthChecker:
    """持仓健康检查器（增强版）"""
    
    def __init__(self):
        self.db = DatabaseAdapter()
        self.sector_analyzer = SectorAnalyzer()
        self.capital_analyzer = CapitalAnalyzer()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.financial_analyzer = FinancialRiskAnalyzer()
    
    def check_stock(self, code: str, cost_price: Optional[float] = None, 
                   include_sector: bool = True, include_capital: bool = True,
                   include_sentiment: bool = True, include_financial: bool = True) -> Dict:
        """
        检查单只股票的健康状态（增强版）
        
        Args:
            code: 股票代码 (如 'sh.600519')
            cost_price: 成本价格（可选）
            include_sector: 是否包含行业面分析
            include_capital: 是否包含资金面分析
            include_sentiment: 是否包含情绪面分析
            include_financial: 是否包含财务面分析
        
        Returns:
            Dict: 完整的健康分析报告
        """
        # 1. 技术面分析（原有功能）
        technical = self._check_technical(code, cost_price)
        
        # 2. 情绪面分析（新增）
        sentiment = None
        if include_sentiment:
            try:
                sentiment = self.sentiment_analyzer.analyze_sentiment(code)
            except Exception as e:
                print(f"情绪面分析失败: {e}")
        
        # 3. 财务面分析（新增）
        financial = None
        if include_financial:
            try:
                financial = self.financial_analyzer.analyze_financial_risk(code)
            except Exception as e:
                print(f"财务面分析失败: {e}")
        
        # 4. 行业面分析
        sector = None
        if include_sector:
            try:
                sector = self.sector_analyzer.generate_sector_report(code)
            except Exception as e:
                print(f"行业面分析失败: {e}")
        
        # 5. 资金面分析
        capital = None
        if include_capital:
            try:
                capital = self.capital_analyzer.generate_capital_report(code)
            except Exception as e:
                print(f"资金面分析失败: {e}")
        
        # 6. 综合判断
        overall_status, overall_message = self._综合判断(
            technical, sentiment, financial, sector, capital
        )
        
        return {
            'code': code,
            'name': technical.name,
            'overall_status': overall_status,
            'overall_message': overall_message,
            'technical': technical,
            'sentiment': sentiment,
            'financial': financial,
            'sector': sector,
            'capital': capital
        }
    
    def _check_technical(self, code: str, cost_price: Optional[float] = None) -> PortfolioHealth:
        """技术面分析（原有逻辑）"""
        # 1. 获取股票基本信息
        stock_info = self.db.get_stock_basic(code)
        if not stock_info:
            raise ValueError(f"找不到股票: {code}")
        
        name = stock_info.get('name', code)
        
        # 2. 获取历史数据（最近300天）
        df = self.db.get_daily_data(code)
        if df.empty:
            raise ValueError(f"无法获取 {code} 的历史数据")
        
        df = df.sort_values('date').tail(300).copy()
        
        # 3. 计算技术指标
        df = TechnicalIndicators.calculate_all(df)
        
        # 4. 获取最新数据
        latest = df.iloc[-1]
        
        # 5. 提取关键指标
        current_price = float(latest['close'])
        change_rate = float(latest.get('pctChg', 0.0))
        ma20 = float(latest['ma20']) if pd.notna(latest['ma20']) else current_price
        rsi = float(latest['rsi']) if pd.notna(latest['rsi']) else 50.0
        volume_ratio = float(latest['volume_ratio']) if pd.notna(latest['volume_ratio']) else 1.0
        
        # 6. 计算MA20偏离度
        ma20_deviation = (current_price - ma20) / ma20 * 100 if ma20 > 0 else 0.0
        
        # 7. 计算盈亏比例
        profit_rate = None
        if cost_price and cost_price > 0:
            profit_rate = (current_price - cost_price) / cost_price * 100
        
        # 8. 判断均线信号
        ma_signal = self._get_ma_signal(current_price, ma20, ma20_deviation)
        
        # 9. 判断成交量信号
        volume_signal = self._get_volume_signal(volume_ratio)
        
        # 10. 综合判断健康状态
        status, status_cn, recommendation = self._get_health_status(
            ma_signal, volume_signal, rsi, change_rate, ma20_deviation
        )
        
        # 11. 返回结果
        return PortfolioHealth(
            code=code,
            name=name,
            status=status,
            status_cn=status_cn,
            recommendation=recommendation,
            current_price=current_price,
            cost_price=cost_price,
            change_rate=change_rate,
            profit_rate=profit_rate,
            ma20=ma20,
            ma20_deviation=ma20_deviation,
            volume_ratio=volume_ratio,
            ma_signal=ma_signal,
            volume_signal=volume_signal
        )
    
    def _get_ma_signal(self, price: float, ma20: float, deviation: float) -> str:
        """
        判断均线信号
        
        Returns:
            'up': 趋势向上
            'flat': 趋势平稳
            'down': 趋势向下
        """
        if price > ma20 and deviation > 2:
            return 'up'
        elif price < ma20 and deviation < -2:
            return 'down'
        else:
            return 'flat'
    
    def _get_volume_signal(self, volume_ratio: float) -> str:
        """
        判断成交量信号
        
        Returns:
            'expand': 放量
            'normal': 正常
            'shrink': 缩量
        """
        if volume_ratio > 1.5:
            return 'expand'
        elif volume_ratio < 0.7:
            return 'shrink'
        else:
            return 'normal'
    
    def _get_health_status(
        self, 
        ma_signal: str, 
        volume_signal: str, 
        rsi: float, 
        change_rate: float,
        ma20_deviation: float
    ) -> tuple[str, str, str]:
        """
        综合判断健康状态
        
        Returns:
            (status, status_cn, recommendation)
        """
        # 🔴 红灯 (危险) - 满足任一条件
        if change_rate < -5:
            return (
                'red',
                '危险',
                f'今日大跌{abs(change_rate):.1f}%，建议止损离场'
            )
        
        if ma_signal == 'down' and rsi < 30:
            return (
                'red',
                '危险',
                f'破位下跌且超卖(RSI={rsi:.0f})，建议止损观望'
            )
        
        if ma_signal == 'down' and ma20_deviation < -10:
            return (
                'red',
                '危险',
                f'跌破均线{abs(ma20_deviation):.1f}%，趋势转弱，建议减仓'
            )
        
        # 🟢 绿灯 (健康) - 满足所有条件
        if ma_signal == 'up' and 30 < rsi < 70 and volume_signal in ['normal', 'expand']:
            if rsi > 60:
                return (
                    'green',
                    '健康',
                    f'趋势向上，RSI={rsi:.0f}，建议继续持有'
                )
            else:
                return (
                    'green',
                    '健康',
                    f'趋势向上，RSI={rsi:.0f}偏低，可以考虑加仓'
                )
        
        # 特殊情况：超卖反弹机会
        if rsi < 30 and change_rate > 0:
            return (
                'yellow',
                '警示',
                f'超卖反弹(RSI={rsi:.0f})，但趋势未明，谨慎观望'
            )
        
        # 🟡 黄灯 (警示) - 其他情况
        if ma_signal == 'flat':
            if volume_signal == 'shrink':
                return (
                    'yellow',
                    '警示',
                    f'横盘整理且缩量(量比={volume_ratio:.2f})，等待方向选择'
                )
            else:
                return (
                    'yellow',
                    '警示',
                    f'震荡整理中，建议观望，等待突破信号'
                )
        
        if ma_signal == 'up' and rsi > 70:
            return (
                'yellow',
                '警示',
                f'超买区域(RSI={rsi:.0f})，涨幅较大，注意回调风险'
            )
        
        if ma_signal == 'down':
            return (
                'yellow',
                '警示',
                f'趋势向下，RSI={rsi:.0f}，建议减仓或观望'
            )
        
        # 默认黄灯
        return (
            'yellow',
            '警示',
            f'市场信号不明确，建议谨慎操作'
        )
    
    def _综合判断(self, technical: PortfolioHealth, sentiment: Optional[Dict], 
                 financial: Optional[Dict], sector: Optional[Dict], 
                 capital: Optional[Dict]) -> tuple[str, str]:
        """
        综合技术面、情绪面、财务面、行业面、资金面，给出最终判断
        
        Returns:
            (status, message)
        """
        # 收集各维度状态
        statuses = [technical.status]
        messages = [f"技术面：{technical.recommendation}"]
        
        if sentiment and 'status' in sentiment:
            statuses.append(sentiment['status'])
            messages.append(f"情绪面：{sentiment['message']}")
        
        if financial and 'status' in financial:
            statuses.append(financial['status'])
            messages.append(f"财务面：{financial['message']}")
        
        if sector and 'status' in sector:
            statuses.append(sector['status'])
            messages.append(f"行业面：{sector['message']}")
        
        if capital and 'status' in capital:
            statuses.append(capital['status'])
            messages.append(f"资金面：{capital['message']}")
        
        # 综合判断逻辑
        red_count = statuses.count('red')
        green_count = statuses.count('green')
        
        if red_count >= 2:
            overall_status = 'red'
        elif green_count >= 2:
            overall_status = 'green'
        elif red_count >= 1:
            overall_status = 'yellow'
        else:
            overall_status = 'yellow'
        
        overall_message = '；'.join(messages)
        
        return overall_status, overall_message
    
    def check_portfolio(self, holdings: list[dict], include_sector: bool = True, 
                       include_capital: bool = True, include_sentiment: bool = True,
                       include_financial: bool = True) -> list[Dict]:
        """
        批量检查持仓健康（增强版）
        
        Args:
            holdings: 持仓列表，每个元素包含 {'code': 'sh.600519', 'cost_price': 1350.0}
            include_sector: 是否包含行业面分析
            include_capital: 是否包含资金面分析
            include_sentiment: 是否包含情绪面分析
            include_financial: 是否包含财务面分析
        
        Returns:
            List[Dict]: 持仓健康列表
        """
        results = []
        for holding in holdings:
            try:
                health = self.check_stock(
                    code=holding['code'],
                    cost_price=holding.get('cost_price'),
                    include_sector=include_sector,
                    include_capital=include_capital,
                    include_sentiment=include_sentiment,
                    include_financial=include_financial
                )
                results.append(health)
            except Exception as e:
                print(f"检查 {holding['code']} 失败: {e}")
                continue
        
        return results


# 便捷函数
def check_stock_health(code: str, cost_price: Optional[float] = None, 
                      include_sector: bool = True, include_capital: bool = True,
                      include_sentiment: bool = True, include_financial: bool = True) -> Dict:
    """
    检查单只股票的健康状态（便捷函数 - 增强版）
    
    Args:
        code: 股票代码
        cost_price: 成本价格（可选）
        include_sector: 是否包含行业面分析
        include_capital: 是否包含资金面分析
        include_sentiment: 是否包含情绪面分析
        include_financial: 是否包含财务面分析
    
    Returns:
        Dict: 完整的健康分析报告
    """
    checker = PortfolioHealthChecker()
    return checker.check_stock(code, cost_price, include_sector, include_capital,
                              include_sentiment, include_financial)


def check_portfolio_health(holdings: list[dict], include_sector: bool = True, 
                          include_capital: bool = True, include_sentiment: bool = True,
                          include_financial: bool = True) -> list[Dict]:
    """
    批量检查持仓健康（便捷函数 - 增强版）
    
    Args:
        holdings: 持仓列表
        include_sector: 是否包含行业面分析
        include_capital: 是否包含资金面分析
        include_sentiment: 是否包含情绪面分析
        include_financial: 是否包含财务面分析
    
    Returns:
        List[Dict]: 持仓健康列表
    """
    checker = PortfolioHealthChecker()
    return checker.check_portfolio(holdings, include_sector, include_capital,
                                  include_sentiment, include_financial)

# -*- coding: utf-8 -*-
"""
技术面分析器适配层 (Technical Analyzer Adapter)

封装现有的技术分析模块：
1. candlestick_patterns - K线形态识别
2. portfolio_health - 技术指标计算
3. 统一返回格式
4. 评分算法：0-100分
"""
import pandas as pd
from typing import Dict, Optional
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.data.database_adapter import DatabaseAdapter
from src.business.post_market.candlestick_patterns import PatternRecognizer
from src.business.post_market.portfolio_health import TechnicalIndicators

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """技术面分析器"""
    
    def __init__(self, db_path: str = "data/a_share.db"):
        """初始化技术分析器（使用新的适配器）"""
        self.db = DatabaseAdapter()
    
    def analyze(self, code: str) -> Dict:
        """
        技术面分析
        
        Args:
            code: 股票代码 (如: 600519 或 sh.600519)
        
        Returns:
            {
                'score': 75,  # 0-100
                'status': 'yellow',  # green/yellow/red
                'message': '短期震荡整理，等待方向选择',
                'details': {
                    'trend': '震荡',
                    'ma20_position': 'above',
                    'ma20_deviation': 2.5,
                    'rsi': 55.2,
                    'volume_ratio': 1.2,
                    'candlestick_pattern': {
                        'name': 'doji',
                        'name_cn': '十字星',
                        'signal': 'neutral',
                        'description': '...'
                    },
                    'support_level': 1650.0,
                    'resistance_level': 1750.0
                }
            }
        """
        # 处理代码格式
        full_code = code if '.' in code else self._get_full_code(code)
        if not full_code:
            return self._create_no_data_result(code)
        
        # 1. 获取历史数据
        df = self.db.get_daily_data(full_code)
        if df.empty or len(df) < 20:
            return self._create_no_data_result(code)
        
        df = df.sort_values('date').tail(300).copy()
        
        # 2. 计算技术指标
        df = TechnicalIndicators.calculate_all(df)
        
        # 3. 获取最新数据
        latest = df.iloc[-1]
        
        # 4. 提取关键指标
        current_price = float(latest['close'])
        change_rate = float(latest.get('pct_chg', 0.0))
        ma20 = float(latest['ma20']) if pd.notna(latest['ma20']) else current_price
        ma50 = float(latest['ma50']) if pd.notna(latest['ma50']) else None
        rsi = float(latest['rsi']) if pd.notna(latest['rsi']) else 50.0
        volume_ratio = float(latest['volume_ratio']) if pd.notna(latest['volume_ratio']) else 1.0
        
        # 5. 计算MA20偏离度
        ma20_deviation = (current_price - ma20) / ma20 * 100 if ma20 > 0 else 0.0
        
        # 6. 判断趋势
        trend = self._get_trend(current_price, ma20, ma50, ma20_deviation)
        
        # 7. 判断均线位置
        ma20_position = 'above' if current_price > ma20 else 'below' if current_price < ma20 else 'near'
        
        # 8. 识别K线形态
        pattern_result = PatternRecognizer.analyze_stock_pattern(df, trend_days=20)
        pattern_info = None
        if pattern_result and pattern_result.get('pattern'):
            pattern = pattern_result['pattern']
            pattern_info = {
                'name': pattern.pattern_name,
                'name_cn': pattern.pattern_name_cn,
                'signal': pattern.signal,
                'signal_cn': pattern.signal_cn,
                'confidence': pattern.confidence,
                'description': pattern.description,
                'emoji': pattern.emoji
            }
        
        # 9. 计算支撑位和阻力位
        support, resistance = self._calculate_support_resistance(df)
        
        # 10. 计算评分
        score = self._calculate_score(trend, rsi, volume_ratio, change_rate, 
                                      ma20_deviation, pattern_info)
        
        # 11. 生成状态和描述
        status = self._get_status_from_score(score)
        message = self._generate_message(trend, rsi, volume_ratio, ma20_deviation, 
                                        pattern_info, score)
        
        # 12. 组装详细数据
        details = {
            'trend': trend,
            'ma20_position': ma20_position,
            'ma20': round(ma20, 2),
            'ma20_deviation': round(ma20_deviation, 2),
            'ma50': round(ma50, 2) if ma50 else None,
            'rsi': round(rsi, 2),
            'volume_ratio': round(volume_ratio, 2),
            'candlestick_pattern': pattern_info,
            'support_level': round(support, 2) if support else None,
            'resistance_level': round(resistance, 2) if resistance else None,
            'current_price': round(current_price, 2),
            'change_rate': round(change_rate, 2)
        }
        
        return {
            'score': score,
            'status': status,
            'message': message,
            'details': details
        }
    
    def _get_full_code(self, code: str) -> Optional[str]:
        """获取完整股票代码"""
        # 如果已经是完整代码，直接返回
        if '.' in code:
            return code
        
        # 否则查询数据库
        stock_info = self.db.get_stock_basic(code)
        if stock_info and 'full_code' in stock_info:
            return stock_info['full_code']
        
        # 如果查询失败，尝试根据代码推断
        if code.startswith('6'):
            return f'sh.{code}'
        elif code.startswith(('0', '3')):
            return f'sz.{code}'
        
        return None
    
    def _get_trend(self, price: float, ma20: float, ma50: Optional[float], 
                   deviation: float) -> str:
        """
        判断趋势
        
        Returns:
            '上涨' / '下跌' / '震荡'
        """
        # 基于MA20偏离度和MA50位置判断
        if price > ma20 and deviation > 5:
            if ma50 and ma20 > ma50:
                return '上涨'
            else:
                return '震荡'
        elif price < ma20 and deviation < -5:
            if ma50 and ma20 < ma50:
                return '下跌'
            else:
                return '震荡'
        else:
            return '震荡'
    
    def _calculate_support_resistance(self, df: pd.DataFrame) -> tuple:
        """
        计算支撑位和阻力位
        
        简化算法：
        - 支撑位：最近20天的最低价
        - 阻力位：最近20天的最高价
        """
        recent = df.tail(20)
        support = recent['low'].min()
        resistance = recent['high'].max()
        return support, resistance
    
    def _calculate_score(self, trend: str, rsi: float, volume_ratio: float,
                        change_rate: float, ma20_deviation: float, 
                        pattern_info: Optional[Dict]) -> int:
        """
        计算技术面评分 (0-100)
        
        评分逻辑：
        - 趋势评分 (30分): 上涨=30, 震荡=20, 下跌=10
        - RSI评分 (25分): 30-70健康区间=25, 超买超卖=10
        - 成交量评分 (20分): 放量=20, 正常=15, 缩量=10
        - K线形态评分 (15分): 看涨=15, 中性=10, 看跌=5
        - 涨跌幅评分 (10分): 大涨=10, 小涨=8, 小跌=5, 大跌=0
        """
        score = 0
        
        # 1. 趋势评分 (30分)
        if trend == '上涨':
            score += 30
        elif trend == '震荡':
            score += 20
        else:  # 下跌
            score += 10
        
        # 2. RSI评分 (25分)
        if 30 <= rsi <= 70:
            score += 25
        elif 20 <= rsi <= 80:
            score += 20
        elif rsi < 20:
            # 超卖，可能反弹
            score += 15
        else:
            # 超买，注意风险
            score += 10
        
        # 3. 成交量评分 (20分)
        if volume_ratio > 1.5:
            # 放量
            if trend == '上涨':
                score += 20  # 放量上涨，好信号
            else:
                score += 15  # 放量下跌，注意风险
        elif volume_ratio > 0.7:
            # 正常
            score += 15
        else:
            # 缩量
            score += 10
        
        # 4. K线形态评分 (15分)
        if pattern_info:
            signal = pattern_info.get('signal')
            confidence = pattern_info.get('confidence')
            
            if signal == 'bullish':
                if confidence == 'high':
                    score += 15
                else:
                    score += 12
            elif signal == 'neutral':
                score += 10
            else:  # bearish
                if confidence == 'high':
                    score += 5
                else:
                    score += 8
        else:
            score += 10
        
        # 5. 涨跌幅评分 (10分)
        if change_rate > 5:
            score += 10
        elif change_rate > 0:
            score += 8
        elif change_rate > -3:
            score += 5
        else:
            score += 0
        
        return max(0, min(100, score))
    
    def _get_status_from_score(self, score: int) -> str:
        """根据评分获取状态"""
        if score >= 70:
            return 'green'
        elif score >= 50:
            return 'yellow'
        else:
            return 'red'
    
    def _generate_message(self, trend: str, rsi: float, volume_ratio: float,
                         ma20_deviation: float, pattern_info: Optional[Dict], 
                         score: int) -> str:
        """生成人话描述"""
        messages = []
        
        # 1. 趋势描述
        if trend == '上涨':
            messages.append(f"趋势向上")
        elif trend == '下跌':
            messages.append(f"趋势向下")
        else:
            messages.append(f"震荡整理")
        
        # 2. RSI描述
        if rsi > 70:
            messages.append(f"RSI超买({rsi:.0f})")
        elif rsi < 30:
            messages.append(f"RSI超卖({rsi:.0f})")
        
        # 3. 成交量描述
        if volume_ratio > 1.5:
            messages.append(f"放量(量比{volume_ratio:.1f})")
        elif volume_ratio < 0.7:
            messages.append(f"缩量(量比{volume_ratio:.1f})")
        
        # 4. K线形态描述
        if pattern_info:
            pattern_desc = pattern_info.get('name_cn', '')
            if pattern_desc:
                messages.append(f"出现{pattern_desc}")
        
        # 5. 综合建议
        if score >= 75:
            messages.append("技术面向好")
        elif score >= 50:
            messages.append("技术面中性")
        else:
            messages.append("技术面转弱")
        
        return "，".join(messages)
    
    def _create_no_data_result(self, code: str) -> Dict:
        """创建无数据结果"""
        return {
            'score': 50,
            'status': 'yellow',
            'message': '暂无技术分析数据',
            'details': {
                'trend': '未知',
                'ma20_position': 'unknown',
                'ma20': None,
                'ma20_deviation': None,
                'ma50': None,
                'rsi': None,
                'volume_ratio': None,
                'candlestick_pattern': None,
                'support_level': None,
                'resistance_level': None,
                'current_price': None,
                'change_rate': None
            }
        }


if __name__ == "__main__":
    # 测试代码
    analyzer = TechnicalAnalyzer()
    
    # 测试1: 贵州茅台
    print("=== 测试1: 贵州茅台 (600519) ===")
    result = analyzer.analyze("600519")
    print(f"评分: {result['score']}")
    print(f"状态: {result['status']}")
    print(f"描述: {result['message']}")
    print(f"详细数据: {result['details']}")
    
    # 测试2: 平安银行
    print("\n=== 测试2: 平安银行 (000001) ===")
    result = analyzer.analyze("000001")
    print(f"评分: {result['score']}")
    print(f"状态: {result['status']}")
    print(f"描述: {result['message']}")

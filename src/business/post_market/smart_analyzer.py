# -*- coding: utf-8 -*-
"""
智能分析器 - 改进版

改进点：
1. 先收集所有数据，再统一分析
2. 考虑行业特性（如银行股高负债是正常的）
3. 避免矛盾的建议
4. 给出更智能的综合判断
5. 集成K线形态识别
"""
import pandas as pd
import sqlite3
from typing import Dict, Optional
from dataclasses import dataclass
from src.data.database_adapter import DatabaseAdapter
from src.business.post_market.candlestick_patterns import PatternRecognizer


@dataclass
class StockData:
    """股票完整数据"""
    # 基本信息
    code: str
    name: str
    industry: Optional[str] = None
    
    # 技术面数据
    current_price: float = 0.0
    cost_price: Optional[float] = None
    change_rate: float = 0.0
    ma20: float = 0.0
    ma20_deviation: float = 0.0
    rsi: float = 50.0
    volume_ratio: float = 1.0
    
    # 布林线
    boll_upper: float = 0.0
    boll_middle: float = 0.0
    boll_lower: float = 0.0
    boll_position: float = 0.5  # 价格在布林带中的位置 (0-1)
    boll_width: float = 0.0     # 布林带宽度（波动率）
    
    # MACD
    macd_dif: float = 0.0
    macd_dea: float = 0.0
    macd_macd: float = 0.0      # MACD柱
    macd_signal: str = 'neutral'  # bullish/bearish/neutral
    
    # KDJ
    kdj_k: float = 50.0
    kdj_d: float = 50.0
    kdj_j: float = 50.0
    kdj_signal: str = 'neutral'  # overbought/oversold/neutral
    
    # 情绪面数据
    stock_character: str = 'unknown'  # stable/active/demon
    limit_up_days: int = 0
    max_consecutive_up: int = 0
    avg_amplitude: float = 0.0
    volatility_score: float = 0.0
    
    # 财务面数据
    is_st: bool = False
    roe: Optional[float] = None
    roe_level: str = 'unknown'
    net_margin: Optional[float] = None
    eps: Optional[float] = None
    debt_ratio: Optional[float] = None
    debt_level: str = 'unknown'
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    report_date: Optional[str] = None
    
    # 行业面数据
    industry_avg_roe: Optional[float] = None
    industry_avg_debt: Optional[float] = None
    
    # K线形态数据
    kline_pattern: Optional[str] = None
    kline_pattern_cn: Optional[str] = None
    kline_signal: Optional[str] = None
    kline_description: Optional[str] = None


class SmartAnalyzer:
    """智能分析器"""
    
    # 行业特性配置
    INDUSTRY_PROFILES = {
        '银行': {
            'normal_debt_ratio': (85, 95),  # 正常负债率范围
            'normal_roe': (5, 15),           # 正常ROE范围
            'high_debt_is_normal': True,     # 高负债是否正常
            'description': '银行业高负债是正常经营模式'
        },
        '保险': {
            'normal_debt_ratio': (80, 90),
            'normal_roe': (5, 15),
            'high_debt_is_normal': True,
            'description': '保险业高负债是正常经营模式'
        },
        '房地产': {
            'normal_debt_ratio': (60, 80),
            'normal_roe': (5, 15),
            'high_debt_is_normal': True,
            'description': '房地产业负债率较高是行业特点'
        },
        '白酒': {
            'normal_debt_ratio': (10, 30),
            'normal_roe': (15, 40),
            'high_debt_is_normal': False,
            'description': '白酒行业轻资产，低负债高ROE'
        },
        '食品饮料': {
            'normal_debt_ratio': (20, 40),
            'normal_roe': (10, 25),
            'high_debt_is_normal': False,
            'description': '食品饮料行业负债率适中'
        }
    }
    
    def __init__(self):
        self.db = DatabaseAdapter()
    
    def analyze(self, code: str, cost_price: Optional[float] = None) -> Dict:
        """
        智能分析（改进版）
        
        流程：
        1. 收集所有数据
        2. 识别行业特性
        3. 统一分析
        4. 生成智能建议
        """
        # Step 1: 收集所有数据
        data = self._collect_all_data(code, cost_price)
        
        # Step 2: 识别行业特性
        industry_profile = self._get_industry_profile(data.industry)
        
        # Step 3: 统一分析
        analysis = self._unified_analysis(data, industry_profile)
        
        return {
            'code': data.code,
            'name': data.name,
            'industry': data.industry,
            'data': data,
            'industry_profile': industry_profile,
            'analysis': analysis
        }
    
    def _collect_all_data(self, code: str, cost_price: Optional[float]) -> StockData:
        """收集所有数据"""
        data = StockData(code=code, name=code, cost_price=cost_price)
        
        # 1. 基本信息和行业
        stock_info = self.db.get_stock_basic(code)
        if stock_info:
            data.name = stock_info.get('name', code)
        
        # 获取行业信息
        data.industry = self._get_industry(code)
        
        # 检查ST状态
        data.is_st = self._check_st_status(data.name)
        
        # 2. 技术面数据
        self._collect_technical_data(data)
        
        # 3. 情绪面数据
        self._collect_sentiment_data(data)
        
        # 4. 财务面数据
        self._collect_financial_data(data)
        
        # 5. 行业对比数据
        if data.industry:
            self._collect_industry_comparison(data)
        
        # 6. K线形态数据
        self._collect_kline_pattern(data)
        
        return data
    
    def _get_industry(self, code: str) -> Optional[str]:
        """获取股票行业"""
        pure_code = code.split('.')[-1] if '.' in code else code
        
        try:
            conn = sqlite3.connect('data/a_share.db')
            query = "SELECT industry FROM industry_data WHERE code = ?"
            result = pd.read_sql_query(query, conn, params=(pure_code,))
            conn.close()
            
            if not result.empty:
                return result.iloc[0]['industry']
        except Exception as e:
            print(f"获取行业信息失败: {e}")
        
        return None
    
    def _check_st_status(self, name: str) -> bool:
        """检查ST状态"""
        st_keywords = ['ST', '*ST', 'S*ST', 'SST']
        return any(keyword in name for keyword in st_keywords)
    
    def _collect_technical_data(self, data: StockData):
        """收集技术面数据"""
        df = self.db.get_daily_data(data.code)
        if df.empty:
            return
        
        df = df.sort_values('date').tail(300).copy()
        
        # 计算技术指标
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['ma5'] = df['close'].rolling(window=5).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 量比
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma5']
        
        # 布林线 (BOLL)
        df['boll_middle'] = df['close'].rolling(window=20).mean()
        df['boll_std'] = df['close'].rolling(window=20).std()
        df['boll_upper'] = df['boll_middle'] + 2 * df['boll_std']
        df['boll_lower'] = df['boll_middle'] - 2 * df['boll_std']
        df['boll_width'] = (df['boll_upper'] - df['boll_lower']) / df['boll_middle'] * 100
        df['boll_position'] = (df['close'] - df['boll_lower']) / (df['boll_upper'] - df['boll_lower'])
        
        # MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd_dif'] = ema12 - ema26
        df['macd_dea'] = df['macd_dif'].ewm(span=9, adjust=False).mean()
        df['macd_macd'] = (df['macd_dif'] - df['macd_dea']) * 2
        
        # KDJ
        low_9 = df['low'].rolling(window=9).min()
        high_9 = df['high'].rolling(window=9).max()
        rsv = (df['close'] - low_9) / (high_9 - low_9) * 100
        df['kdj_k'] = rsv.ewm(com=2, adjust=False).mean()
        df['kdj_d'] = df['kdj_k'].ewm(com=2, adjust=False).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        
        latest = df.iloc[-1]
        
        # 基础数据
        data.current_price = float(latest['close'])
        data.ma20 = float(latest['ma20']) if pd.notna(latest['ma20']) else data.current_price
        data.ma20_deviation = (data.current_price - data.ma20) / data.ma20 * 100 if data.ma20 > 0 else 0
        data.rsi = float(latest['rsi']) if pd.notna(latest['rsi']) else 50.0
        data.volume_ratio = float(latest['volume_ratio']) if pd.notna(latest['volume_ratio']) else 1.0
        
        # 布林线数据
        data.boll_upper = float(latest['boll_upper']) if pd.notna(latest['boll_upper']) else data.current_price
        data.boll_middle = float(latest['boll_middle']) if pd.notna(latest['boll_middle']) else data.current_price
        data.boll_lower = float(latest['boll_lower']) if pd.notna(latest['boll_lower']) else data.current_price
        data.boll_position = float(latest['boll_position']) if pd.notna(latest['boll_position']) else 0.5
        data.boll_width = float(latest['boll_width']) if pd.notna(latest['boll_width']) else 0.0
        
        # MACD数据
        data.macd_dif = float(latest['macd_dif']) if pd.notna(latest['macd_dif']) else 0.0
        data.macd_dea = float(latest['macd_dea']) if pd.notna(latest['macd_dea']) else 0.0
        data.macd_macd = float(latest['macd_macd']) if pd.notna(latest['macd_macd']) else 0.0
        
        # MACD信号判断
        if len(df) >= 2:
            prev_macd = df.iloc[-2]['macd_macd']
            if data.macd_macd > 0 and prev_macd <= 0:
                data.macd_signal = 'golden_cross'  # 金叉
            elif data.macd_macd < 0 and prev_macd >= 0:
                data.macd_signal = 'death_cross'   # 死叉
            elif data.macd_macd > 0 and data.macd_dif > data.macd_dea:
                data.macd_signal = 'bullish'       # 多头
            elif data.macd_macd < 0 and data.macd_dif < data.macd_dea:
                data.macd_signal = 'bearish'       # 空头
            else:
                data.macd_signal = 'neutral'
        
        # KDJ数据
        data.kdj_k = float(latest['kdj_k']) if pd.notna(latest['kdj_k']) else 50.0
        data.kdj_d = float(latest['kdj_d']) if pd.notna(latest['kdj_d']) else 50.0
        data.kdj_j = float(latest['kdj_j']) if pd.notna(latest['kdj_j']) else 50.0
        
        # KDJ信号判断
        if data.kdj_k > 80 and data.kdj_d > 80:
            data.kdj_signal = 'overbought'  # 超买
        elif data.kdj_k < 20 and data.kdj_d < 20:
            data.kdj_signal = 'oversold'    # 超卖
        elif len(df) >= 2:
            prev_k = df.iloc[-2]['kdj_k']
            prev_d = df.iloc[-2]['kdj_d']
            if data.kdj_k > data.kdj_d and prev_k <= prev_d:
                data.kdj_signal = 'golden_cross'  # 金叉
            elif data.kdj_k < data.kdj_d and prev_k >= prev_d:
                data.kdj_signal = 'death_cross'   # 死叉
            else:
                data.kdj_signal = 'neutral'
        
        # 计算涨跌幅
        if len(df) > 1:
            prev_close = df.iloc[-2]['close']
            data.change_rate = (data.current_price - prev_close) / prev_close * 100
    
    def _collect_sentiment_data(self, data: StockData):
        """收集情绪面数据"""
        df = self.db.get_daily_data(data.code)
        if df.empty:
            return
        
        df = df.sort_values('date').tail(30).copy()
        
        # 计算涨跌幅
        df['pctChg'] = df['close'].pct_change() * 100
        
        # 涨跌停
        df['is_limit_up'] = df['pctChg'] >= 9.9
        data.limit_up_days = int(df['is_limit_up'].sum())
        
        # 最高连板
        max_consecutive = 0
        current_consecutive = 0
        for is_up in df['is_limit_up']:
            if is_up:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        data.max_consecutive_up = max_consecutive
        
        # 振幅
        amplitudes = ((df['high'] - df['low']) / df['low'] * 100).abs()
        data.avg_amplitude = float(amplitudes.mean())
        
        # 波动评分
        if data.avg_amplitude < 2:
            data.volatility_score = data.avg_amplitude / 2 * 20
        elif data.avg_amplitude < 4:
            data.volatility_score = 20 + (data.avg_amplitude - 2) / 2 * 30
        elif data.avg_amplitude < 6:
            data.volatility_score = 50 + (data.avg_amplitude - 4) / 2 * 30
        else:
            data.volatility_score = min(100, 80 + (data.avg_amplitude - 6) / 2 * 20)
        
        # 股性判断
        if data.limit_up_days >= 5 or data.max_consecutive_up >= 3 or data.avg_amplitude > 6:
            data.stock_character = 'demon'
        elif data.limit_up_days >= 2 or data.avg_amplitude > 3:
            data.stock_character = 'active'
        else:
            data.stock_character = 'stable'
    
    def _collect_financial_data(self, data: StockData):
        """收集财务面数据"""
        pure_code = data.code.split('.')[-1] if '.' in data.code else data.code
        
        try:
            conn = sqlite3.connect('data/a_share.db')
            query = """
            SELECT roe, net_margin, eps, debt_to_asset_ratio, 
                   current_ratio, quick_ratio, report_date
            FROM financial_indicators
            WHERE code = ?
            ORDER BY report_date DESC LIMIT 1
            """
            result = pd.read_sql_query(query, conn, params=(pure_code,))
            conn.close()
            
            if not result.empty:
                row = result.iloc[0]
                data.roe = float(row['roe']) if pd.notna(row['roe']) else None
                data.net_margin = float(row['net_margin']) if pd.notna(row['net_margin']) else None
                data.eps = float(row['eps']) if pd.notna(row['eps']) else None
                data.debt_ratio = float(row['debt_to_asset_ratio']) if pd.notna(row['debt_to_asset_ratio']) else None
                data.current_ratio = float(row['current_ratio']) if pd.notna(row['current_ratio']) else None
                data.quick_ratio = float(row['quick_ratio']) if pd.notna(row['quick_ratio']) else None
                data.report_date = row['report_date']
                
                # ROE等级
                if data.roe is not None:
                    if data.roe >= 20:
                        data.roe_level = 'excellent'
                    elif data.roe >= 15:
                        data.roe_level = 'good'
                    elif data.roe >= 10:
                        data.roe_level = 'fair'
                    elif data.roe >= 0:
                        data.roe_level = 'poor'
                    else:
                        data.roe_level = 'negative'
                
                # 负债等级
                if data.debt_ratio is not None:
                    if data.debt_ratio < 40:
                        data.debt_level = 'low'
                    elif data.debt_ratio < 60:
                        data.debt_level = 'medium'
                    elif data.debt_ratio < 70:
                        data.debt_level = 'high'
                    else:
                        data.debt_level = 'very_high'
        
        except Exception as e:
            print(f"获取财务数据失败: {e}")
    
    def _collect_industry_comparison(self, data: StockData):
        """收集行业对比数据"""
        if not data.industry:
            return
        
        try:
            conn = sqlite3.connect('data/a_share.db')
            
            # 获取同行业股票的平均ROE和负债率
            query = """
            SELECT AVG(fi.roe) as avg_roe, AVG(fi.debt_to_asset_ratio) as avg_debt
            FROM financial_indicators fi
            JOIN industry_data id ON fi.code = id.code
            WHERE id.industry = ?
              AND fi.report_date = (
                  SELECT MAX(report_date) FROM financial_indicators WHERE code = fi.code
              )
              AND fi.roe IS NOT NULL
              AND fi.debt_to_asset_ratio IS NOT NULL
            """
            
            result = pd.read_sql_query(query, conn, params=(data.industry,))
            conn.close()
            
            if not result.empty:
                data.industry_avg_roe = float(result.iloc[0]['avg_roe']) if pd.notna(result.iloc[0]['avg_roe']) else None
                data.industry_avg_debt = float(result.iloc[0]['avg_debt']) if pd.notna(result.iloc[0]['avg_debt']) else None
        
        except Exception as e:
            print(f"获取行业对比数据失败: {e}")
    
    def _analyze_kline_trend(self, df: pd.DataFrame) -> str:
        """分析K线走势（即使没有特殊形态）"""
        if len(df) < 5:
            return "数据不足，无法分析K线走势"
        
        # 获取最近的数据
        recent_5 = df.tail(5)
        recent_10 = df.tail(10)
        latest = df.iloc[-1]
        
        observations = []
        
        # 1. 最近5天的涨跌情况
        up_days = (recent_5['close'] > recent_5['open']).sum()
        down_days = (recent_5['close'] < recent_5['open']).sum()
        
        if up_days >= 4:
            observations.append(f"最近5天收了{up_days}根阳线，多方占优")
        elif down_days >= 4:
            observations.append(f"最近5天收了{down_days}根阴线，空方占优")
        elif up_days == down_days:
            observations.append("最近5天多空势均力敌，方向不明")
        
        # 2. 价格位置（相对于最近10天）
        recent_high = recent_10['high'].max()
        recent_low = recent_10['low'].min()
        current_price = latest['close']
        
        price_position = (current_price - recent_low) / (recent_high - recent_low) if recent_high > recent_low else 0.5
        
        if price_position > 0.8:
            observations.append(f"当前价格{current_price:.2f}接近近期高点{recent_high:.2f}，上方压力较大")
        elif price_position < 0.2:
            observations.append(f"当前价格{current_price:.2f}接近近期低点{recent_low:.2f}，下方支撑较强")
        else:
            observations.append(f"当前价格{current_price:.2f}在近期区间中部（高点{recent_high:.2f}，低点{recent_low:.2f}）")
        
        # 3. 成交量变化
        if 'volume' in df.columns and len(df) >= 5:
            recent_volume = recent_5['volume'].mean()
            prev_volume = df.iloc[-10:-5]['volume'].mean() if len(df) >= 10 else recent_volume
            
            if recent_volume > prev_volume * 1.3:
                observations.append("最近成交量明显放大，市场关注度提升")
            elif recent_volume < prev_volume * 0.7:
                observations.append("最近成交量萎缩，市场观望情绪浓厚")
        
        # 4. 今日表现
        today_change = latest.get('pct_chg', 0)
        if abs(today_change) > 3:
            if today_change > 0:
                observations.append(f"今日大涨{today_change:.1f}%，短期情绪较好")
            else:
                observations.append(f"今日大跌{abs(today_change):.1f}%，短期情绪较差")
        
        return "；".join(observations) if observations else "K线走势平稳，无明显特征"
    
    def _collect_kline_pattern(self, data: StockData):
        """收集K线形态数据"""
        df = self.db.get_daily_data(data.code)
        if df.empty or len(df) < 2:
            return
        
        df = df.sort_values('date').tail(30).copy()
        
        # 计算涨跌幅（如果没有）
        if 'pct_chg' not in df.columns:
            df['pct_chg'] = df['close'].pct_change() * 100
        
        # 识别K线形态
        result = PatternRecognizer.analyze_stock_pattern(df)
        
        if result and result.get('pattern'):
            pattern = result['pattern']
            data.kline_pattern = pattern.pattern_name
            data.kline_pattern_cn = pattern.pattern_name_cn
            data.kline_signal = pattern.signal
            data.kline_description = pattern.description
        else:
            # 即使没有特殊形态，也分析K线走势
            data.kline_description = self._analyze_kline_trend(df)
    
    def _get_industry_profile(self, industry: Optional[str]) -> Optional[Dict]:
        """获取行业特性配置"""
        if not industry:
            return None
        
        # 精确匹配
        if industry in self.INDUSTRY_PROFILES:
            return self.INDUSTRY_PROFILES[industry]
        
        # 模糊匹配
        for key in self.INDUSTRY_PROFILES:
            if key in industry or industry in key:
                return self.INDUSTRY_PROFILES[key]
        
        return None
    
    def _unified_analysis(self, data: StockData, industry_profile: Optional[Dict]) -> Dict:
        """统一分析（考虑行业特性和K线形态）"""
        
        # 1. 技术面分析
        technical_status, technical_msg = self._analyze_technical(data)
        
        # 2. 情绪面分析
        sentiment_status, sentiment_msg = self._analyze_sentiment(data)
        
        # 3. 财务面分析（考虑行业）
        financial_status, financial_msg = self._analyze_financial(data, industry_profile)
        
        # 4. K线形态分析
        kline_status, kline_msg = self._analyze_kline(data)
        
        # 5. 综合判断
        overall_status, overall_msg = self._综合判断_smart(
            data, technical_status, sentiment_status, financial_status, kline_status,
            technical_msg, sentiment_msg, financial_msg, kline_msg, industry_profile
        )
        
        return {
            'technical': {'status': technical_status, 'message': technical_msg},
            'sentiment': {'status': sentiment_status, 'message': sentiment_msg},
            'financial': {'status': financial_status, 'message': financial_msg},
            'kline': {'status': kline_status, 'message': kline_msg},
            'overall': {'status': overall_status, 'message': overall_msg}
        }
    
    def _calculate_signal_strength(self, data: StockData) -> int:
        """
        计算信号强度（改进版：信号分级）
        
        强信号（权重高）:
        - MACD金叉/死叉: ±3分
        - KDJ金叉/死叉: ±2分
        - 触及布林上轨/下轨: ±2分
        - RSI极度超买/超卖(>80/<20): ±2分
        
        中等信号（权重中）:
        - MACD多头/空头: ±1分
        - KDJ超买/超卖: ±1分
        - 接近布林上轨/下轨: ±1分
        - 站稳/跌破MA20: ±1分
        - RSI超买/超卖(>70/<30): ±1分
        """
        score = 0
        
        # MACD (最高±3分)
        if data.macd_signal == 'golden_cross':
            score += 3
        elif data.macd_signal == 'death_cross':
            score -= 3
        elif data.macd_signal == 'bullish':
            score += 1
        elif data.macd_signal == 'bearish':
            score -= 1
        
        # KDJ (最高±2分)
        if data.kdj_signal == 'golden_cross':
            score += 2
        elif data.kdj_signal == 'death_cross':
            score -= 2
        elif data.kdj_signal == 'oversold':
            score += 1
        elif data.kdj_signal == 'overbought':
            score -= 1
        
        # 布林线 (最高±2分)
        if data.boll_position > 0.95:
            score -= 2
        elif data.boll_position < 0.05:
            score += 2
        elif data.boll_position > 0.8:
            score -= 1
        elif data.boll_position < 0.2:
            score += 1
        
        # RSI (最高±2分)
        if data.rsi > 80:
            score -= 2
        elif data.rsi < 20:
            score += 2
        elif data.rsi > 70:
            score -= 1
        elif data.rsi < 30:
            score += 1
        
        # MA20 (最高±1分)
        if data.ma20_deviation > 5:
            score += 1
        elif data.ma20_deviation < -10:
            score -= 1
        
        # 量比 (最高±1分)
        if data.volume_ratio > 2:
            score += 1
        elif data.volume_ratio < 0.5:
            score -= 1
        
        return score
    
    def _verify_with_volume(self, signal_score: int, volume_ratio: float) -> tuple[int, str]:
        """量价配合验证"""
        verification = ""
        
        if signal_score > 0:  # 看涨信号
            if volume_ratio > 1.5:
                signal_score += 1
                verification = "放量上涨，信号有效"
            elif volume_ratio < 0.8:
                signal_score -= 1
                verification = "缩量上涨，信号减弱"
        
        elif signal_score < 0:  # 看跌信号
            if volume_ratio > 1.5:
                signal_score -= 1
                verification = "放量下跌，信号有效"
            elif volume_ratio < 0.8:
                signal_score += 1
                verification = "缩量下跌，可能是洗盘"
        
        return signal_score, verification
    
    def _verify_with_kline(self, signal_score: int, kline_signal: Optional[str]) -> tuple[int, str]:
        """K线形态验证"""
        verification = ""
        
        if not kline_signal:
            return signal_score, verification
        
        if signal_score > 0 and kline_signal == 'bullish':
            signal_score += 1
            verification = "K线+指标共振，强烈看涨"
        
        elif signal_score < 0 and kline_signal == 'bearish':
            signal_score -= 1
            verification = "K线+指标共振，强烈看跌"
        
        elif signal_score > 0 and kline_signal == 'bearish':
            signal_score = 0
            verification = "K线和指标矛盾，观望"
        
        elif signal_score < 0 and kline_signal == 'bullish':
            signal_score = 0
            verification = "K线和指标矛盾，观望"
        
        return signal_score, verification
    
    def _analyze_technical(self, data: StockData) -> tuple[str, str]:
        """技术面分析（高级版：信号共振+量价配合+K线验证）"""
        signals = []
        
        # Step 1: 计算基础信号强度
        base_score = self._calculate_signal_strength(data)
        
        # Step 2: 量价配合验证
        verified_score, volume_msg = self._verify_with_volume(base_score, data.volume_ratio)
        if volume_msg:
            signals.append(volume_msg)
        
        # Step 3: K线形态验证
        final_score, kline_msg = self._verify_with_kline(verified_score, data.kline_signal)
        if kline_msg:
            signals.append(kline_msg)
        
        # Step 4: 生成详细信号描述
        detail_signals = []
        
        # 价格趋势
        if data.change_rate < -5:
            detail_signals.append(f'今日大跌{abs(data.change_rate):.1f}%')
        
        if data.ma20_deviation > 5:
            detail_signals.append(f'远离MA20(+{data.ma20_deviation:.1f}%)')
        elif data.ma20_deviation < -10:
            detail_signals.append(f'跌破MA20({data.ma20_deviation:.1f}%)')
        elif data.ma20_deviation > 2:
            detail_signals.append(f'站稳MA20')
        elif abs(data.ma20_deviation) <= 2:
            detail_signals.append(f'围绕MA20震荡')
        
        # RSI
        if data.rsi > 80:
            detail_signals.append(f'RSI极度超买({data.rsi:.0f})')
        elif data.rsi > 70:
            detail_signals.append(f'RSI超买({data.rsi:.0f})')
        elif data.rsi < 20:
            detail_signals.append(f'RSI极度超卖({data.rsi:.0f})')
        elif data.rsi < 30:
            detail_signals.append(f'RSI超卖({data.rsi:.0f})')
        
        # 布林线
        if data.boll_position > 0.95:
            detail_signals.append(f'突破布林上轨')
        elif data.boll_position < 0.05:
            detail_signals.append(f'突破布林下轨')
        elif data.boll_position > 0.8:
            detail_signals.append(f'接近布林上轨')
        elif data.boll_position < 0.2:
            detail_signals.append(f'接近布林下轨')
        
        if data.boll_width < 5:
            detail_signals.append(f'布林带收窄({data.boll_width:.1f}%)，可能变盘')
        elif data.boll_width > 15:
            detail_signals.append(f'布林带扩张({data.boll_width:.1f}%)，波动加大')
        
        # MACD
        if data.macd_signal == 'golden_cross':
            detail_signals.append(f'⭐MACD金叉')
        elif data.macd_signal == 'death_cross':
            detail_signals.append(f'⚠️MACD死叉')
        elif data.macd_signal == 'bullish':
            detail_signals.append(f'MACD多头排列')
        elif data.macd_signal == 'bearish':
            detail_signals.append(f'MACD空头排列')
        
        # KDJ
        if data.kdj_signal == 'golden_cross':
            detail_signals.append(f'⭐KDJ金叉')
        elif data.kdj_signal == 'death_cross':
            detail_signals.append(f'⚠️KDJ死叉')
        elif data.kdj_signal == 'overbought':
            detail_signals.append(f'KDJ超买(K={data.kdj_k:.0f})')
        elif data.kdj_signal == 'oversold':
            detail_signals.append(f'KDJ超卖(K={data.kdj_k:.0f})')
        
        # 量比
        if data.volume_ratio > 2:
            detail_signals.append(f'放量({data.volume_ratio:.1f}倍)')
        elif data.volume_ratio < 0.5:
            detail_signals.append(f'缩量({data.volume_ratio:.1f}倍)')
        
        # Step 5: 综合判断
        if final_score >= 5:
            status = 'green'
            strength = '强烈看涨🟢🟢🟢'
        elif final_score >= 3:
            status = 'green'
            strength = '看涨🟢🟢'
        elif final_score >= 1:
            status = 'green'
            strength = '偏多🟢'
        elif final_score <= -5:
            status = 'red'
            strength = '强烈看跌🔴🔴🔴'
        elif final_score <= -3:
            status = 'red'
            strength = '看跌🔴🔴'
        elif final_score <= -1:
            status = 'red'
            strength = '偏空🔴'
        else:
            status = 'yellow'
            strength = '中性🟡'
        
        # 组合消息
        all_signals = signals + detail_signals
        message = f'{strength} (信号强度:{final_score}分) - ' + '；'.join(all_signals) if all_signals else f'{strength} (信号强度:{final_score}分)'
        
        return status, message
    
    def _analyze_sentiment(self, data: StockData) -> tuple[str, str]:
        """情绪面分析"""
        if data.stock_character == 'demon':
            return 'yellow', f'妖股体质，波动极大({data.avg_amplitude:.1f}%)，不适合新手'
        
        if data.stock_character == 'active':
            return 'green', f'股性活跃，适合波段操作'
        
        return 'green', f'股性稳健，波动平稳({data.avg_amplitude:.1f}%)'
    
    def _analyze_kline(self, data: StockData) -> tuple[str, str]:
        """K线形态分析"""
        if not data.kline_description:
            return 'yellow', '无K线数据'
        
        # 如果有特殊形态，根据信号判断
        if data.kline_pattern:
            if data.kline_signal == 'bullish':
                return 'green', f'{data.kline_pattern_cn}：{data.kline_description}'
            elif data.kline_signal == 'bearish':
                return 'red', f'{data.kline_pattern_cn}：{data.kline_description}'
            else:
                return 'yellow', f'{data.kline_pattern_cn}：{data.kline_description}'
        
        # 没有特殊形态，根据描述内容判断
        desc = data.kline_description.lower()
        
        # 看涨信号
        if any(word in desc for word in ['阳线', '多方占优', '放大', '大涨', '接近.*低点', '支撑']):
            if any(word in desc for word in ['大涨', '放大']):
                return 'green', data.kline_description
            return 'yellow', data.kline_description
        
        # 看跌信号
        if any(word in desc for word in ['阴线', '空方占优', '萎缩', '大跌', '接近.*高点', '压力']):
            if any(word in desc for word in ['大跌', '空方占优']):
                return 'red', data.kline_description
            return 'yellow', data.kline_description
        
        # 中性
        return 'yellow', data.kline_description
    
    def _analyze_financial(self, data: StockData, industry_profile: Optional[Dict]) -> tuple[str, str]:
        """财务面分析（考虑行业特性）"""
        
        # ST股票
        if data.is_st:
            return 'red', 'ST股票，存在退市风险'
        
        # 无财务数据
        if data.roe is None or data.debt_ratio is None:
            return 'yellow', '财务数据不足'
        
        # 考虑行业特性
        if industry_profile:
            return self._analyze_financial_with_industry(data, industry_profile)
        else:
            return self._analyze_financial_general(data)
    
    def _analyze_financial_with_industry(self, data: StockData, profile: Dict) -> tuple[str, str]:
        """考虑行业特性的财务分析"""
        
        normal_debt_min, normal_debt_max = profile['normal_debt_ratio']
        normal_roe_min, normal_roe_max = profile['normal_roe']
        high_debt_is_normal = profile['high_debt_is_normal']
        
        messages = []
        
        # ROE分析
        if data.roe < normal_roe_min:
            messages.append(f'ROE={data.roe:.1f}%偏低')
            roe_ok = False
        elif data.roe > normal_roe_max:
            messages.append(f'ROE={data.roe:.1f}%优秀')
            roe_ok = True
        else:
            messages.append(f'ROE={data.roe:.1f}%正常')
            roe_ok = True
        
        # 负债分析（考虑行业）
        if high_debt_is_normal:
            # 银行、保险等行业，高负债是正常的
            if normal_debt_min <= data.debt_ratio <= normal_debt_max:
                messages.append(f'负债率{data.debt_ratio:.1f}%符合行业特点')
                debt_ok = True
            elif data.debt_ratio < normal_debt_min:
                messages.append(f'负债率{data.debt_ratio:.1f}%偏低')
                debt_ok = True
            else:
                messages.append(f'负债率{data.debt_ratio:.1f}%偏高')
                debt_ok = False
        else:
            # 其他行业，低负债更好
            if data.debt_ratio < 40:
                messages.append(f'负债率{data.debt_ratio:.1f}%健康')
                debt_ok = True
            elif data.debt_ratio < 60:
                messages.append(f'负债率{data.debt_ratio:.1f}%适中')
                debt_ok = True
            else:
                messages.append(f'负债率{data.debt_ratio:.1f}%偏高')
                debt_ok = False
        
        # 综合判断
        if roe_ok and debt_ok:
            return 'green', f'{data.industry}：' + '，'.join(messages)
        elif not roe_ok and not debt_ok:
            return 'red', f'{data.industry}：' + '，'.join(messages)
        else:
            return 'yellow', f'{data.industry}：' + '，'.join(messages)
    
    def _analyze_financial_general(self, data: StockData) -> tuple[str, str]:
        """通用财务分析（无行业信息时）"""
        messages = []
        
        # ROE
        if data.roe >= 15:
            messages.append(f'ROE={data.roe:.1f}%优秀')
            roe_ok = True
        elif data.roe >= 10:
            messages.append(f'ROE={data.roe:.1f}%良好')
            roe_ok = True
        else:
            messages.append(f'ROE={data.roe:.1f}%偏低')
            roe_ok = False
        
        # 负债
        if data.debt_ratio < 40:
            messages.append(f'负债率{data.debt_ratio:.1f}%健康')
            debt_ok = True
        elif data.debt_ratio < 60:
            messages.append(f'负债率{data.debt_ratio:.1f}%适中')
            debt_ok = True
        else:
            messages.append(f'负债率{data.debt_ratio:.1f}%偏高')
            debt_ok = False
        
        if roe_ok and debt_ok:
            return 'green', '，'.join(messages)
        elif not roe_ok and not debt_ok:
            return 'red', '，'.join(messages)
        else:
            return 'yellow', '，'.join(messages)
    
    def _综合判断_smart(
        self, data: StockData,
        tech_status: str, sent_status: str, fin_status: str, kline_status: str,
        tech_msg: str, sent_msg: str, fin_msg: str, kline_msg: str,
        industry_profile: Optional[Dict]
    ) -> tuple[str, str]:
        """智能综合判断（包含K线形态）"""
        
        # 计算状态分数
        status_score = {
            'green': 1,
            'yellow': 0,
            'red': -1
        }
        
        total_score = (
            status_score[tech_status] +
            status_score[sent_status] +
            status_score[fin_status] +
            status_score[kline_status]
        )
        
        # 生成综合建议
        if data.is_st:
            return 'red', 'ST股票，风险极高，不建议持有'
        
        # K线形态有强烈信号时，优先考虑
        if kline_status == 'red' and data.kline_signal == 'bearish':
            return 'yellow', f'K线形态显示见顶信号（{data.kline_pattern_cn}），建议谨慎'
        
        if kline_status == 'green' and data.kline_signal == 'bullish' and total_score >= 1:
            return 'green', f'K线形态显示见底信号（{data.kline_pattern_cn}），可以关注'
        
        # 根据总分判断
        if total_score >= 2:
            # 至少2个绿灯
            if data.cost_price and data.current_price < data.cost_price:
                profit_rate = (data.current_price - data.cost_price) / data.cost_price * 100
                return 'green', f'综合健康，当前浮亏{abs(profit_rate):.1f}%，可继续持有等待反弹'
            else:
                return 'green', '综合健康，建议继续持有'
        
        elif total_score <= -2:
            # 至少2个红灯
            return 'red', '多个维度显示风险，建议减仓或止损'
        
        else:
            # 混合状态，需要更细致的判断
            if fin_status == 'red' and not (industry_profile and industry_profile.get('high_debt_is_normal')):
                return 'yellow', '财务状况较差，建议观望'
            
            if tech_status == 'red':
                return 'yellow', '技术面走弱，建议观望或减仓'
            
            return 'yellow', '综合表现一般，建议观望'


# 便捷函数
def smart_analyze(code: str, cost_price: Optional[float] = None) -> Dict:
    """智能分析（便捷函数）"""
    analyzer = SmartAnalyzer()
    return analyzer.analyze(code, cost_price)

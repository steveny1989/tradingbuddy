"""
个股诊断引擎

核心诊断引擎，协调各个评分器并生成最终报告。
"""

import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import logging

from .models import DiagnosisReport
from .exceptions import StockNotFoundError, DataInsufficientError
from .technical_scorer import TechnicalScorer
from .liquidity_scorer import LiquidityScorer
from .market_scorer import MarketEnvironmentScorer
from .risk_calculator import RiskCalculator
from .signal_evaluator import SignalLightEvaluator
from .plain_language_generator import PlainLanguageGenerator

logger = logging.getLogger(__name__)


class StockDiagnosisEngine:
    """个股诊断引擎"""
    
    def __init__(self, data_fetcher, financial_fetcher=None, cache=None):
        """
        初始化诊断引擎
        
        Args:
            data_fetcher: 数据获取器（用于获取股票日线数据）
            financial_fetcher: 财务数据获取器（可选）
            cache: 缓存管理器（可选）
        """
        self.data_fetcher = data_fetcher
        self.financial_fetcher = financial_fetcher
        self.cache = cache
        
        # 初始化各个组件
        self.technical_scorer = TechnicalScorer()
        self.liquidity_scorer = LiquidityScorer()
        self.market_scorer = MarketEnvironmentScorer(data_fetcher)
        self.risk_calculator = RiskCalculator(financial_fetcher)
        self.signal_evaluator = SignalLightEvaluator()
        self.plain_language_generator = PlainLanguageGenerator()
    
    def diagnose_stock(self, code: str, user_id: Optional[str] = None) -> DiagnosisReport:
        """
        诊断单只股票
        
        Args:
            code: 股票代码（支持 sh.600000 或 600000 格式）
            user_id: 用户 ID（用于记录历史）
            
        Returns:
            DiagnosisReport: 完整的诊断报告
            
        Raises:
            StockNotFoundError: 股票代码不存在
            DataInsufficientError: 数据不足以生成诊断
        """
        # 1. 标准化股票代码
        normalized_code = self._normalize_code(code)
        
        # 2. 检查缓存（5 分钟有效期）
        if self.cache:
            cached_report = self._get_from_cache(normalized_code)
            if cached_report:
                logger.info(f"从缓存获取诊断报告: {normalized_code}")
                return cached_report
        
        # 3. 获取股票数据
        stock_data = self._fetch_stock_data(normalized_code)
        
        # 4. 获取股票基本信息
        stock_info = self._get_stock_info(normalized_code)
        name = stock_info.get('name', normalized_code)
        
        # 5. 并行计算各维度评分
        logger.info(f"开始诊断股票: {normalized_code} ({name})")
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            technical_future = executor.submit(self.technical_scorer.score, stock_data)
            liquidity_future = executor.submit(self.liquidity_scorer.score, stock_data)
            market_future = executor.submit(self.market_scorer.score, stock_data, stock_info.get('sector'))
            risk_future = executor.submit(self.risk_calculator.calculate, stock_data, normalized_code, name)
        
        technical_score = technical_future.result()
        liquidity_score = liquidity_future.result()
        market_score = market_future.result()
        risk_info = risk_future.result()
        
        # 6. 计算综合评分
        overall_score = (
            technical_score.value * 0.6 +
            liquidity_score.value * 0.2 +
            market_score.value * 0.2
        )
        
        # 7. 生成信号灯
        signal_light = self.signal_evaluator.evaluate(
            overall_score, technical_score, liquidity_score, market_score, risk_info
        )
        
        # 8. 生成大白话诊断意见
        diagnosis_text = self.plain_language_generator.generate(
            stock_data, name, technical_score, liquidity_score, market_score, signal_light
        )
        
        # 9. 计算涨跌幅
        latest = stock_data.iloc[-1]
        if len(stock_data) >= 2:
            previous = stock_data.iloc[-2]
            change_pct = (latest['close'] - previous['close']) / previous['close'] * 100
        else:
            change_pct = 0.0
        
        # 10. 获取数据更新时间
        data_update_time = self._get_data_update_time(stock_data)
        
        # 11. 组装诊断报告
        report = DiagnosisReport(
            code=normalized_code,
            name=name,
            current_price=latest['close'],
            change_pct=change_pct,
            overall_score=overall_score,
            technical_score=technical_score,
            liquidity_score=liquidity_score,
            market_score=market_score,
            signal_light=signal_light,
            diagnosis_text=diagnosis_text,
            risk_info=risk_info,
            timestamp=datetime.now(),
            data_update_time=data_update_time
        )
        
        # 12. 缓存结果
        if self.cache:
            self._save_to_cache(normalized_code, report)
        
        # 13. 记录诊断历史
        if user_id:
            self._save_diagnosis_history(user_id, report)
        
        logger.info(f"诊断完成: {normalized_code}, 综合评分: {overall_score:.1f}, 信号灯: {signal_light.color}")
        
        return report
    
    def _normalize_code(self, code: str) -> str:
        """标准化股票代码"""
        code = code.strip().upper()
        
        # 如果已经有前缀，直接返回
        if code.startswith('SH.') or code.startswith('SZ.'):
            return code.lower()
        
        # 去掉可能的前缀
        code = re.sub(r'^(SH|SZ)\.?', '', code, flags=re.IGNORECASE)
        
        # 根据代码判断市场
        if code.startswith('6'):
            return f'sh.{code}'
        elif code.startswith(('0', '3')):
            return f'sz.{code}'
        else:
            # 默认上海
            return f'sh.{code}'
    
    def _fetch_stock_data(self, code: str):
        """获取股票数据"""
        # 获取最近 90 天的数据
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        stock_data = self.data_fetcher.get_daily_data(code, start_date=start_date, end_date=end_date)
        
        if stock_data is None or stock_data.empty:
            raise StockNotFoundError(code, f"未找到股票代码: {code}")
        
        if len(stock_data) < 60:
            raise DataInsufficientError(
                code, 
                required_days=60, 
                actual_days=len(stock_data),
                message=f"股票 {code} 数据不足: 需要至少 60 天，实际只有 {len(stock_data)} 天"
            )
        
        return stock_data
    
    def _get_stock_info(self, code: str) -> dict:
        """获取股票基本信息"""
        try:
            # 尝试从数据库获取股票基本信息
            info = self.data_fetcher.get_stock_basic(code)
            if info:
                return info
        except:
            pass
        
        # 如果获取失败，返回默认信息
        return {
            'code': code,
            'name': code,
            'sector': None
        }
    
    def _get_data_update_time(self, stock_data) -> Optional[datetime]:
        """获取数据更新时间"""
        try:
            latest_date = stock_data.iloc[-1]['date']
            if isinstance(latest_date, str):
                return datetime.strptime(latest_date, '%Y-%m-%d')
            return latest_date
        except:
            return None
    
    def _get_from_cache(self, code: str) -> Optional[DiagnosisReport]:
        """从缓存获取诊断报告"""
        try:
            cache_key = f"diagnosis:{code}"
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                # 检查缓存是否过期（5 分钟）
                if 'timestamp' in cached_data:
                    cached_time = cached_data['timestamp']
                    if isinstance(cached_time, str):
                        cached_time = datetime.fromisoformat(cached_time)
                    
                    if datetime.now() - cached_time < timedelta(minutes=5):
                        return cached_data.get('report')
            
            return None
        except Exception as e:
            logger.warning(f"从缓存获取失败: {e}")
            return None
    
    def _save_to_cache(self, code: str, report: DiagnosisReport):
        """保存诊断报告到缓存"""
        try:
            cache_key = f"diagnosis:{code}"
            cache_data = {
                'report': report,
                'timestamp': datetime.now()
            }
            self.cache.set(cache_key, cache_data, ttl=300)  # 5 分钟
        except Exception as e:
            logger.warning(f"保存到缓存失败: {e}")
    
    def _save_diagnosis_history(self, user_id: str, report: DiagnosisReport):
        """保存诊断历史"""
        # TODO: 实现历史记录保存
        pass

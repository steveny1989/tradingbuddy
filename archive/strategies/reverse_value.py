#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逆向价值选股策略（霍华德·马克斯投资哲学）
Reverse Value Strategy (Howard Marks Investment Philosophy)

核心理念：
1. 价值为本：不看价格，看价值（PE/PB百分位）
2. 买得好：寻找安全边际（低估值 + 稳定ROE）
3. 防守优先：避免永久损失（财务健康度过滤）
4. 逆向投资：在周期底部、市场恐慌时买入
5. 耐心等待：只在机会明确时出手

策略条件：
1. 估值维度：PE/PB处于历史低位（<20分位）
2. 质量维度：ROE稳定（>10%），资产负债率健康（<70%）
3. 周期维度：股价处于250日均线下方，但出现企稳信号
4. 逆向维度：市场情绪低迷，但该股已缩量企稳
5. 防守维度：剔除ST股、现金流为负、审计风险股票
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from src.business.strategies.base import FundamentalStrategy

logger = logging.getLogger(__name__)


class ReverseValueStrategy(FundamentalStrategy):
    """逆向价值选股策略"""
    
    def __init__(
        self, 
        db, 
        financial_fetcher=None,
        market_index_code: str = 'sh.000001',
        min_avg_turnover: float = 1e8
    ):
        """
        初始化策略
        
        Args:
            db: StockDatabase 实例
            financial_fetcher: 财务数据获取器
            market_index_code: 大盘指数代码
            min_avg_turnover: 最小日均成交额（默认1亿）
        """
        super().__init__(db)
        self.name = "逆向价值选股（霍华德·马克斯）"
        self.financial_fetcher = financial_fetcher
        self.market_index_code = market_index_code
        self.min_avg_turnover = min_avg_turnover
    
    def get_stock_pool(
        self, 
        min_cap: float = 50e8,
        max_cap: float = 500e8,  # 扩大到500亿，覆盖更多中盘股
        markets: List[str] = ['sh', 'sz']
    ) -> pd.DataFrame:
        """
        获取股票池（按市值筛选）
        
        Args:
            min_cap: 最小市值（元）
            max_cap: 最大市值（元）
            markets: 市场列表
            
        Returns:
            股票池 DataFrame
        """
        try:
            query = f"""
                SELECT 
                    m.full_code, 
                    m.code, 
                    COALESCE(s.name, m.name) as name,
                    m.total_cap, 
                    m.cap_category, 
                    m.market
                FROM market_cap_data m
                LEFT JOIN stock_basic s ON m.code = s.code
                WHERE m.total_cap >= {min_cap} 
                  AND m.total_cap <= {max_cap}
                  AND m.market IN ({','.join([f"'{m}'" for m in markets])})
            """
            pool = pd.read_sql(query, self.db.conn)
            logger.info(f"股票池: {len(pool)} 只股票 (市值 {min_cap/1e8:.0f}-{max_cap/1e8:.0f}亿)")
            return pool
        except Exception as e:
            logger.error(f"获取股票池失败: {e}")
            return pd.DataFrame()
    
    def check_defense_filter(self, code: str, name: str) -> tuple[bool, str]:
        """
        防守过滤器：避免永久损失（原则4, 16, 17）
        
        检查项：
        1. ST股票（高风险）
        2. 资产负债率 > 70%（财务风险）
        3. 现金流连续为负（经营风险）
        
        Args:
            code: 股票代码
            name: 股票名称
            
        Returns:
            (是否通过, 原因)
        """
        # 1. ST股检查
        if 'ST' in name or 'st' in name:
            return False, "ST股票，风险过高"
        
        # 2. 财务数据检查（如果有财务数据获取器）
        if self.financial_fetcher:
            try:
                # 获取最新资产负债表
                balance_sheet = self.financial_fetcher.get_balance_sheet(code, limit=1)
                if not balance_sheet.empty:
                    latest = balance_sheet.iloc[0]
                    
                    # 资产负债率检查
                    if 'total_liabilities' in latest and 'total_assets' in latest:
                        debt_ratio = (latest['total_liabilities'] / latest['total_assets']) * 100
                        if debt_ratio > 70:
                            return False, f"资产负债率过高 ({debt_ratio:.1f}%)"
                
                # 获取最近2年现金流量表
                cash_flow = self.financial_fetcher.get_cash_flow(code, limit=2)
                if len(cash_flow) >= 2:
                    # 检查经营活动现金流是否连续为负
                    if 'operating_cash_flow' in cash_flow.columns:
                        recent_cf = cash_flow['operating_cash_flow'].values
                        if all(cf < 0 for cf in recent_cf):
                            return False, "经营现金流连续为负"
            
            except Exception as e:
                logger.debug(f"财务数据检查失败 {code}: {e}")
        
        return True, "通过防守过滤"
    
    def check_valuation_filter(
        self, 
        code: str, 
        current_pe: float = None,
        current_pb: float = None,
        lookback_days: int = 1800  # 5年
    ) -> tuple[bool, Dict]:
        """
        估值过滤器：寻找价值低估（原则2, 3, 11）
        
        检查PE/PB是否处于历史低位（<20分位）
        
        Args:
            code: 股票代码
            current_pe: 当前PE（如果为None则从数据库获取）
            current_pb: 当前PB（如果为None则从数据库获取）
            lookback_days: 回溯天数
            
        Returns:
            (是否通过, 估值信息字典)
        """
        try:
            # 从日线数据中获取历史数据（使用get_daily_data方法）
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
            
            df = self.db.get_daily_data(code, start_date=start_date, end_date=end_date)
            
            if df.empty or len(df) < 250:  # 至少需要1年数据
                return False, {'reason': '历史数据不足'}
            
            # 检查是否有PE/PB列
            if 'pe_ttm' not in df.columns or 'pb' not in df.columns:
                # 尝试从market_snapshot表获取
                stock_code = code.split('.')[-1]
                query = f"""
                    SELECT date, pe_ttm, pb
                    FROM market_snapshot
                    WHERE code = ? AND date >= ? AND date <= ?
                      AND pe_ttm IS NOT NULL AND pb IS NOT NULL
                      AND pe_ttm > 0 AND pb > 0
                    ORDER BY date
                """
                df_val = pd.read_sql(query, self.db.conn, params=(stock_code, start_date, end_date))
                
                if df_val.empty or len(df_val) < 250:
                    return False, {'reason': '历史估值数据不足'}
                
                # 使用market_snapshot的数据
                df = df_val
            else:
                # 过滤有效的PE/PB数据
                df = df[(df['pe_ttm'].notna()) & (df['pb'].notna()) & (df['pe_ttm'] > 0) & (df['pb'] > 0)]
                
                if df.empty or len(df) < 250:
                    return False, {'reason': '有效估值数据不足'}
            
            # 获取当前估值
            if current_pe is None or current_pb is None:
                latest = df.iloc[-1]
                current_pe = latest['pe_ttm']
                current_pb = latest['pb']
            
            # 计算历史分位数
            pe_percentile = (df['pe_ttm'] < current_pe).sum() / len(df) * 100
            pb_percentile = (df['pb'] < current_pb).sum() / len(df) * 100
            
            # 判断是否低估（PE或PB任一指标<20分位）
            is_undervalued = pe_percentile < 20 or pb_percentile < 20
            
            valuation_info = {
                'current_pe': current_pe,
                'current_pb': current_pb,
                'pe_percentile': pe_percentile,
                'pb_percentile': pb_percentile,
                'is_undervalued': is_undervalued,
                'historical_days': len(df)
            }
            
            if is_undervalued:
                logger.debug(f"{code}: PE分位={pe_percentile:.1f}%, PB分位={pb_percentile:.1f}% - 低估")
            
            return is_undervalued, valuation_info
            
        except Exception as e:
            logger.debug(f"估值检查失败 {code}: {e}")
            return False, {'reason': f'估值检查失败: {e}'}
    
    def check_quality_filter(self, code: str) -> tuple[bool, Dict]:
        """
        质量过滤器：寻找优质公司（原则2）
        
        检查ROE是否稳定且>10%
        
        Args:
            code: 股票代码
            
        Returns:
            (是否通过, 质量信息字典)
        """
        if not self.financial_fetcher:
            return True, {'reason': '无财务数据，跳过质量检查'}
        
        try:
            # 获取最近4个季度的利润表
            income_stmt = self.financial_fetcher.get_income_statement(code, limit=4)
            balance_sheet = self.financial_fetcher.get_balance_sheet(code, limit=4)
            
            if income_stmt.empty or balance_sheet.empty:
                return False, {'reason': '财务数据不足'}
            
            # 计算ROE（净利润 / 股东权益）
            roes = []
            for i in range(min(len(income_stmt), len(balance_sheet))):
                net_profit = income_stmt.iloc[i].get('net_profit', 0)
                equity = balance_sheet.iloc[i].get('shareholders_equity', 1)
                
                if equity > 0:
                    roe = (net_profit / equity) * 100
                    roes.append(roe)
            
            if not roes:
                return False, {'reason': 'ROE计算失败'}
            
            # 检查ROE是否稳定且>10%
            avg_roe = np.mean(roes)
            roe_std = np.std(roes)
            
            is_quality = avg_roe > 10 and roe_std < 5  # 平均ROE>10%，波动<5%
            
            quality_info = {
                'avg_roe': avg_roe,
                'roe_std': roe_std,
                'recent_roes': roes,
                'is_quality': is_quality
            }
            
            if is_quality:
                logger.debug(f"{code}: ROE={avg_roe:.1f}% (波动={roe_std:.1f}%) - 优质")
            
            return is_quality, quality_info
            
        except Exception as e:
            logger.debug(f"质量检查失败 {code}: {e}")
            return False, {'reason': f'质量检查失败: {e}'}
    
    def check_cycle_filter(self, code: str, date: str = None) -> tuple[bool, Dict]:
        """
        周期过滤器：寻找周期底部（原则7, 8）
        
        检查股价是否处于250日均线下方，但出现企稳信号
        
        Args:
            code: 股票代码
            date: 检查日期
            
        Returns:
            (是否通过, 周期信息字典)
        """
        try:
            # 获取最近300天数据
            if date:
                end_date = date
                start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=400)).strftime('%Y-%m-%d')
            else:
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')
            
            df = self.db.get_daily_data(code, start_date=start_date, end_date=end_date)
            
            if df.empty or len(df) < 250:
                return False, {'reason': '数据不足'}
            
            df = df.sort_values('date')
            
            # 计算250日均线
            df['ma250'] = df['close'].rolling(window=250).mean()
            
            # 获取最近数据
            recent = df.tail(10)
            latest = recent.iloc[-1]
            
            if pd.isna(latest['ma250']):
                return False, {'reason': '均线数据不足'}
            
            # 检查是否在均线下方
            below_ma = latest['close'] < latest['ma250']
            
            # 检查是否出现企稳信号（最近3天不再创新低）
            recent_lows = recent.tail(3)['low'].values
            is_stabilizing = recent_lows[-1] >= recent_lows[0]
            
            # 计算乖离率
            deviation = (latest['close'] - latest['ma250']) / latest['ma250'] * 100
            
            # 判断是否在周期底部（在均线下方且已企稳）
            is_cycle_bottom = below_ma and is_stabilizing and deviation < -10  # 乖离率<-10%
            
            cycle_info = {
                'current_price': latest['close'],
                'ma250': latest['ma250'],
                'deviation': deviation,
                'below_ma': below_ma,
                'is_stabilizing': is_stabilizing,
                'is_cycle_bottom': is_cycle_bottom
            }
            
            if is_cycle_bottom:
                logger.debug(f"{code}: 乖离率={deviation:.1f}%, 已企稳 - 周期底部")
            
            return is_cycle_bottom, cycle_info
            
        except Exception as e:
            logger.debug(f"周期检查失败 {code}: {e}")
            return False, {'reason': f'周期检查失败: {e}'}
    
    def check_reverse_signal(self, code: str, date: str = None) -> tuple[bool, Dict]:
        """
        逆向信号检查：寻找缩量企稳（原则9, 10）
        
        检查是否出现"下跌后缩量企稳"信号
        
        Args:
            code: 股票代码
            date: 检查日期
            
        Returns:
            (是否通过, 逆向信号字典)
        """
        try:
            # 获取最近10天数据
            if date:
                df = self.db.get_daily_data(code, end_date=date)
                if df.empty or df['date'].max() != date:
                    return False, {'reason': '数据不足'}
                df = df.tail(10)
            else:
                df = self.db.get_daily_data(code)
                if df.empty:
                    return False, {'reason': '数据不足'}
                df = df.tail(10)
            
            if len(df) < 5:
                return False, {'reason': '数据不足'}
            
            df = df.sort_values('date')
            
            # 检查是否下跌（最新价 < 5天前价格）
            is_declining = df.iloc[-1]['close'] < df.iloc[-5]['close']
            
            # 检查是否缩量（最近3天成交量递减）
            recent_volumes = df.tail(3)['volume'].values
            is_shrinking = all(recent_volumes[i] > recent_volumes[i+1] for i in range(len(recent_volumes)-1))
            
            # 检查是否企稳（最近2天不再创新低）
            is_stabilizing = df.iloc[-1]['low'] >= df.iloc[-2]['low']
            
            # 逆向信号：下跌 + 缩量 + 企稳
            has_reverse_signal = is_declining and is_shrinking and is_stabilizing
            
            reverse_info = {
                'is_declining': is_declining,
                'is_shrinking': is_shrinking,
                'is_stabilizing': is_stabilizing,
                'has_reverse_signal': has_reverse_signal,
                'recent_volumes': recent_volumes.tolist()
            }
            
            if has_reverse_signal:
                logger.debug(f"{code}: 下跌缩量企稳 - 逆向信号")
            
            return has_reverse_signal, reverse_info
            
        except Exception as e:
            logger.debug(f"逆向信号检查失败 {code}: {e}")
            return False, {'reason': f'逆向信号检查失败: {e}'}
    
    def check_signal(
        self,
        code: str,
        date: str = None,
        skip_defense: bool = False,
        skip_valuation: bool = False,
        skip_quality: bool = False,
        skip_cycle: bool = False,
        skip_reverse: bool = False
    ) -> Optional[Dict]:
        """
        检查单只股票是否满足逆向价值策略
        
        完整检查流程：
        1. 防守过滤（避免永久损失）
        2. 估值过滤（寻找低估值）
        3. 质量过滤（寻找优质公司）
        4. 周期过滤（寻找周期底部）
        5. 逆向过滤（寻找逆向信号）
        
        Args:
            code: 股票代码
            date: 检查日期
            skip_*: 跳过某个检查（用于调试）
            
        Returns:
            信号字典，如果不满足条件返回None
        """
        try:
            # 获取股票名称
            stock_info = self.db.conn.execute(
                "SELECT name FROM stock_basic WHERE code = ?",
                (code.split('.')[-1],)
            ).fetchone()
            
            if not stock_info:
                return None
            
            name = stock_info[0]
            
            # 1. 防守过滤
            if not skip_defense:
                passed, reason = self.check_defense_filter(code, name)
                if not passed:
                    logger.debug(f"{code} {name}: 防守过滤未通过 - {reason}")
                    return None
            
            # 2. 估值过滤
            valuation_info = {}
            if not skip_valuation:
                passed, valuation_info = self.check_valuation_filter(code)
                if not passed:
                    return None
            
            # 3. 质量过滤
            quality_info = {}
            if not skip_quality:
                passed, quality_info = self.check_quality_filter(code)
                if not passed:
                    return None
            
            # 4. 周期过滤
            cycle_info = {}
            if not skip_cycle:
                passed, cycle_info = self.check_cycle_filter(code, date)
                if not passed:
                    return None
            
            # 5. 逆向过滤
            reverse_info = {}
            if not skip_reverse:
                passed, reverse_info = self.check_reverse_signal(code, date)
                if not passed:
                    return None
            
            # 构建信号
            signal = {
                'code': code,
                'name': name,
                'date': date or datetime.now().strftime('%Y-%m-%d'),
                'price': cycle_info.get('current_price', 0),
                'valuation': valuation_info,
                'quality': quality_info,
                'cycle': cycle_info,
                'reverse': reverse_info,
                'strategy': 'reverse_value'
            }
            
            logger.info(f"✅ {code} {name}: 符合逆向价值策略")
            
            return signal
            
        except Exception as e:
            logger.debug(f"检查 {code} 失败: {e}")
            return None
    
    def scan(
        self,
        date: str = None,
        min_cap: float = 50e8,
        max_cap: float = 500e8,
        max_stocks: int = None,
        check_liquidity: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        扫描股票池，找出符合逆向价值策略的股票
        
        Args:
            date: 扫描日期
            min_cap: 最小市值
            max_cap: 最大市值
            max_stocks: 最多扫描股票数
            check_liquidity: 是否检查流动性
            
        Returns:
            信号列表 DataFrame
        """
        # 获取股票池
        pool = self.get_stock_pool(min_cap, max_cap)
        
        if pool.empty:
            logger.warning("股票池为空")
            return pd.DataFrame()
        
        # ST股过滤
        pool = pool[~pool['name'].str.contains('ST|st', na=False)]
        logger.info(f"ST股过滤后: {len(pool)} 只股票")
        
        if max_stocks:
            pool = pool.head(max_stocks)
        
        logger.info(f"开始扫描 {len(pool)} 只股票...")
        
        signals = []
        scanned = 0
        
        for idx, row in pool.iterrows():
            code = row['full_code']
            scanned += 1
            
            # 流动性检查
            if check_liquidity:
                # 简单检查：日均成交额 > 1亿
                try:
                    df = self.db.get_daily_data(code)
                    if df.empty or len(df) < 5:
                        continue
                    
                    avg_amount = df.tail(5)['amount'].mean()
                    if avg_amount < self.min_avg_turnover:
                        continue
                except:
                    continue
            
            # 检查信号
            signal = self.check_signal(code=code, date=date)
            
            if signal:
                signal['market_cap'] = row['total_cap'] / 1e8
                signals.append(signal)
            
            if scanned % 50 == 0:
                logger.info(f"已扫描 {scanned}/{len(pool)}, 找到 {len(signals)} 个信号")
        
        logger.info(f"扫描完成: {len(signals)} 个信号")
        
        if not signals:
            return pd.DataFrame()
        
        df_signals = pd.DataFrame(signals)
        
        # 按估值分位数排序（越低越好）
        if 'valuation' in df_signals.columns:
            df_signals['pe_percentile'] = df_signals['valuation'].apply(
                lambda x: x.get('pe_percentile', 100) if isinstance(x, dict) else 100
            )
            df_signals = df_signals.sort_values('pe_percentile')
        
        return df_signals

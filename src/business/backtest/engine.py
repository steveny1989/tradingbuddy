#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测引擎
Backtesting Engine
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
import logging

from src.config.settings import BacktestConfig, DEFAULT_BACKTEST_CONFIG
from src.business.trading.cost_calculator import TradingCostCalculator

logger = logging.getLogger(__name__)


class BacktestEngine:
    """事件驱动的回测引擎"""
    
    def __init__(
        self,
        db,
        strategy,
        config: BacktestConfig = None,
        # 兼容旧参数（已废弃，建议使用config）
        initial_capital: float = None,
        commission_rate: float = None,
        slippage_rate: float = None,
        max_positions: int = None,
        position_size: float = None
    ):
        """
        初始化回测引擎
        
        Args:
            db: 数据库实例
            strategy: 策略实例
            config: 回测配置对象（推荐使用）
            
            以下参数已废弃，建议使用config参数：
            initial_capital: 初始资金
            commission_rate: 佣金率
            slippage_rate: 滑点率
            max_positions: 最大持仓数
            position_size: 单次买入比例
        """
        self.db = db
        self.strategy = strategy
        
        # 配置处理：优先使用config，其次使用传入参数，最后使用默认配置
        if config is None:
            config = DEFAULT_BACKTEST_CONFIG
            
            # 如果传入了旧参数，覆盖默认配置
            if initial_capital is not None:
                config.initial_capital = initial_capital
            if commission_rate is not None:
                config.commission_rate = commission_rate
            if slippage_rate is not None:
                config.slippage_rate = slippage_rate
            if max_positions is not None:
                config.max_positions = max_positions
            if position_size is not None:
                config.position_size = position_size
        
        self.config = config
        
        # 为了向后兼容，保留这些属性
        self.initial_capital = config.initial_capital
        self.commission_rate = config.commission_rate
        self.slippage_rate = config.slippage_rate
        self.max_positions = config.max_positions
        self.position_size = config.position_size
        
        # 创建成本计算器
        self.cost_calculator = TradingCostCalculator(config)
        
        # 回测状态
        self.cash = config.initial_capital
        self.positions = {}  # {code: {'shares': 100, 'cost': 10.5, 'date': '2024-01-01'}}
        self.trades = []     # 交易记录
        self.daily_values = []  # 每日净值
        
    def calculate_cost(self, price: float, shares: int, is_buy: bool = True) -> float:
        """
        计算交易成本（含佣金和滑点）
        
        Args:
            price: 价格
            shares: 股数
            is_buy: 是否买入
            
        Returns:
            实际成本（买入）或实际到手（卖出）
        """
        return self.cost_calculator.calculate_simple_cost(price, shares, is_buy)
    
    def buy(self, code: str, price: float, date: str, signal: Dict = None) -> bool:
        """
        买入股票
        
        Args:
            code: 股票代码
            price: 买入价格
            date: 买入日期
            signal: 信号信息
            
        Returns:
            是否成功买入
        """
        # 检查持仓数量
        if len(self.positions) >= self.max_positions:
            logger.debug(f"{date} {code}: 持仓已满")
            return False
        
        # 检查是否已持有
        if code in self.positions:
            logger.debug(f"{date} {code}: 已持有")
            return False
        
        # 计算买入金额
        buy_amount = self.cash * self.position_size
        
        # 计算股数（100股为1手）
        shares = int(buy_amount / price / 100) * 100
        
        if shares < 100:
            logger.debug(f"{date} {code}: 资金不足")
            return False
        
        # 计算实际成本
        cost = self.calculate_cost(price, shares, is_buy=True)
        
        if cost > self.cash:
            logger.debug(f"{date} {code}: 资金不足")
            return False
        
        # 执行买入
        self.cash -= cost
        self.positions[code] = {
            'shares': shares,
            'cost': price,
            'date': date,
            'signal': signal
        }
        
        # 记录交易
        self.trades.append({
            'date': date,
            'code': code,
            'action': 'buy',
            'price': price,
            'shares': shares,
            'amount': cost,
            'cash': self.cash,
            'signal': signal
        })
        
        logger.debug(f"{date} 买入 {code} {shares}股 @{price:.2f}, 成本{cost:.2f}")
        
        return True
    
    def sell(self, code: str, price: float, date: str, reason: str = '') -> bool:
        """
        卖出股票
        
        Args:
            code: 股票代码
            price: 卖出价格
            date: 卖出日期
            reason: 卖出原因
            
        Returns:
            是否成功卖出
        """
        if code not in self.positions:
            return False
        
        position = self.positions[code]
        shares = position['shares']
        cost_price = position['cost']
        
        # 计算卖出金额（使用统一的calculate_cost方法）
        proceeds = self.calculate_cost(price, shares, is_buy=False)
        
        # 执行卖出
        self.cash += proceeds
        
        # 计算收益
        cost_amount = shares * cost_price
        profit = proceeds - cost_amount
        profit_rate = profit / cost_amount
        
        # 记录交易
        self.trades.append({
            'date': date,
            'code': code,
            'action': 'sell',
            'price': price,
            'shares': shares,
            'amount': proceeds,
            'cost_price': cost_price,
            'profit': profit,
            'profit_rate': profit_rate,
            'cash': self.cash,
            'reason': reason,
            'hold_days': (pd.to_datetime(date) - pd.to_datetime(position['date'])).days
        })
        
        logger.debug(f"{date} 卖出 {code} {shares}股 @{price:.2f}, 收益{profit:.2f}({profit_rate:.2%}), 原因:{reason}")
        
        # 删除持仓
        del self.positions[code]
        
        return True
    
    def update_daily_value(self, date: str):
        """
        更新每日净值（仅在交易日更新）
        
        Args:
            date: 日期
        """
        # 计算持仓市值
        position_value = 0
        has_valid_data = False
        
        for code, position in self.positions.items():
            # 获取当日收盘价
            df = self.db.get_daily_data(code, start_date=date, end_date=date)
            if not df.empty:
                price = df['close'].iloc[0]
                position_value += price * position['shares']
                has_valid_data = True
            else:
                # 如果当天没有数据（停牌或非交易日），使用上一个交易日的价格
                # 从daily_values中获取上一次的价格
                if self.daily_values:
                    # 使用成本价作为保守估计
                    position_value += position['cost'] * position['shares']
                else:
                    position_value += position['cost'] * position['shares']
        
        # 只有当至少有一只股票有数据时才记录（说明是交易日）
        # 或者没有持仓时也记录（纯现金状态）
        if has_valid_data or len(self.positions) == 0:
            # 总资产
            total_value = self.cash + position_value
            
            self.daily_values.append({
                'date': date,
                'cash': self.cash,
                'position_value': position_value,
                'total_value': total_value,
                'position_count': len(self.positions)
            })
    
    def run(
        self,
        start_date: str,
        end_date: str,
        hold_days: int = 5,
        stop_loss: float = -0.10,
        take_profit: float = 0.15,
        scan_interval: int = 1,
        time_stop_days: int = 3
    ) -> Dict:
        """
        运行回测（稳健版）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            hold_days: 持有天数
            stop_loss: 止损线（-10%）
            take_profit: 止盈线（15%）
            scan_interval: 扫描间隔（天）
            time_stop_days: 时间止损天数（N天不反弹强制出局）
            
        Returns:
            回测结果
        """
        logger.info("="*80)
        logger.info(f"开始回测: {start_date} 至 {end_date}")
        logger.info(f"初始资金: {self.initial_capital:,.0f}")
        logger.info(f"持有天数: {hold_days}, 止损: {stop_loss:.1%}, 止盈: {take_profit:.1%}")
        logger.info(f"时间止损: {time_stop_days}天不反弹强制出局")
        logger.info("="*80)
        
        # 从指数数据获取真实交易日列表（避免周末和节假日）
        market_index_code = getattr(self.strategy, 'market_index_code', 'sh.000001')
        df_index = self.db.get_daily_data(market_index_code, start_date=start_date, end_date=end_date)
        
        if df_index.empty:
            logger.error("无法获取指数数据，回测终止")
            return {'total_trades': 0, 'message': '无法获取指数数据'}
        
        trade_dates = df_index['date'].tolist()
        logger.info(f"交易日数量: {len(trade_dates)} 天")
        
        scan_counter = 0
        
        for i, date in enumerate(trade_dates):
            # 检查持仓，执行止盈止损
            for code in list(self.positions.keys()):
                position = self.positions[code]
                
                # 获取当日价格
                df = self.db.get_daily_data(code, start_date=date, end_date=date)
                if df.empty:
                    continue
                
                current_price = df['close'].iloc[0]
                cost_price = position['cost']
                profit_rate = (current_price - cost_price) / cost_price
                hold_days_actual = (pd.to_datetime(date) - pd.to_datetime(position['date'])).days
                
                # 止损
                if profit_rate <= stop_loss:
                    self.sell(code, current_price, date, reason=f'止损({profit_rate:.2%})')
                    continue
                
                # 止盈
                if profit_rate >= take_profit:
                    self.sell(code, current_price, date, reason=f'止盈({profit_rate:.2%})')
                    continue
                
                # 时间止损：N天不反弹强制出局
                if time_stop_days > 0 and hold_days_actual >= time_stop_days:
                    # 检查是否有反弹（当前价格是否高于成本价）
                    if profit_rate < 0:
                        self.sell(code, current_price, date, reason=f'时间止损({hold_days_actual}天未反弹)')
                        continue
                
                # 持有天数到期
                if hold_days_actual >= hold_days:
                    self.sell(code, current_price, date, reason=f'到期({hold_days_actual}天)')
                    continue
            
            # 定期扫描新信号
            if scan_counter % scan_interval == 0:
                signals = self.strategy.scan(date=date, max_stocks=500)
                
                if not signals.empty:
                    logger.info(f"{date}: 发现 {len(signals)} 个信号")
                    
                    # 按信号强度排序（如果有相关字段）
                    if 'decline_rate' in signals.columns:
                        signals = signals.sort_values('decline_rate')
                    elif 'ma_distance' in signals.columns:
                        signals = signals.sort_values('ma_distance', ascending=False)
                    
                    for _, signal in signals.iterrows():
                        code = signal['code']
                        
                        # 获取下一个交易日的开盘价（模拟次日买入）
                        if i + 1 < len(trade_dates):
                            next_trading_date = trade_dates[i + 1]
                            df_next = self.db.get_daily_data(code, start_date=next_trading_date, end_date=next_trading_date)
                            
                            if df_next.empty:
                                continue
                            
                            buy_price = df_next['open'].iloc[0]
                            
                            # 尝试买入
                            if self.buy(code, buy_price, next_trading_date, signal=signal.to_dict()):
                                if len(self.positions) >= self.max_positions:
                                    break
            
            scan_counter += 1
            
            # 更新每日净值
            self.update_daily_value(date)
            
            # 进度提示
            if scan_counter % 30 == 0:
                logger.info(f"回测进度: {date}, 持仓: {len(self.positions)}, 现金: {self.cash:,.0f}")
        
        # 清仓
        logger.info("回测结束，清仓...")
        for code in list(self.positions.keys()):
            df = self.db.get_daily_data(code, start_date=end_date, end_date=end_date)
            if not df.empty:
                self.sell(code, df['close'].iloc[0], end_date, reason='回测结束')
        
        # 生成回测报告
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """生成回测报告"""
        df_trades = pd.DataFrame(self.trades)
        df_daily = pd.DataFrame(self.daily_values)
        
        # 基本统计
        total_trades = len(df_trades[df_trades['action'] == 'buy'])
        sell_trades = df_trades[df_trades['action'] == 'sell']
        
        if len(sell_trades) == 0:
            return {
                'total_trades': 0,
                'message': '没有完成的交易'
            }
        
        # 收益统计
        total_profit = sell_trades['profit'].sum()
        win_trades = sell_trades[sell_trades['profit'] > 0]
        loss_trades = sell_trades[sell_trades['profit'] <= 0]
        
        win_rate = len(win_trades) / len(sell_trades) if len(sell_trades) > 0 else 0
        avg_profit = sell_trades['profit'].mean()
        avg_profit_rate = sell_trades['profit_rate'].mean()
        
        # 最终净值
        final_value = df_daily['total_value'].iloc[-1] if not df_daily.empty else self.initial_capital
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # 最大回撤
        df_daily['peak'] = df_daily['total_value'].cummax()
        df_daily['drawdown'] = (df_daily['total_value'] - df_daily['peak']) / df_daily['peak']
        max_drawdown = df_daily['drawdown'].min()
        
        report = {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_profit': total_profit,
            'total_trades': total_trades,
            'completed_trades': len(sell_trades),
            'win_trades': len(win_trades),
            'loss_trades': len(loss_trades),
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_profit_rate': avg_profit_rate,
            'max_profit': sell_trades['profit'].max() if len(sell_trades) > 0 else 0,
            'max_loss': sell_trades['profit'].min() if len(sell_trades) > 0 else 0,
            'max_drawdown': max_drawdown,
            'avg_hold_days': sell_trades['hold_days'].mean() if len(sell_trades) > 0 else 0,
            'trades': df_trades,
            'daily_values': df_daily
        }
        
        return report

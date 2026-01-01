#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟盘交易系统（Paper Trading）
用真实数据模拟交易，不实际下单
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.config.settings import PaperTradingConfig, DEFAULT_PAPER_TRADING_CONFIG
from src.business.trading.cost_calculator import TradingCostCalculator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PaperTradingEngine:
    """模拟盘交易引擎"""
    
    def __init__(
        self,
        db,
        strategy,
        config: PaperTradingConfig = None,
        # 兼容旧参数（已废弃，建议使用config）
        initial_capital: float = None,
        max_positions: int = None,
        position_size: float = None,
        commission_rate: float = None,
        slippage_rate: float = None,
        data_dir: str = None
    ):
        """
        初始化模拟盘引擎
        
        Args:
            db: 数据库实例
            strategy: 策略实例
            config: 模拟盘配置对象（推荐使用）
            
            以下参数已废弃，建议使用config参数：
            initial_capital: 初始资金
            max_positions: 最大持仓数
            position_size: 单次买入比例
            commission_rate: 佣金率
            slippage_rate: 滑点率
            data_dir: 数据目录
        """
        self.db = db
        self.strategy = strategy
        
        # 配置处理：优先使用config，其次使用传入参数，最后使用默认配置
        if config is None:
            config = DEFAULT_PAPER_TRADING_CONFIG
            
            # 如果传入了旧参数，覆盖默认配置
            if initial_capital is not None:
                config.initial_capital = initial_capital
            if max_positions is not None:
                config.max_positions = max_positions
            if position_size is not None:
                config.position_size = position_size
            if commission_rate is not None:
                config.commission_rate = commission_rate
            if slippage_rate is not None:
                config.slippage_rate = slippage_rate
            if data_dir is not None:
                config.data_dir = data_dir
        
        self.config = config
        
        # 为了向后兼容，保留这些属性
        self.initial_capital = config.initial_capital
        self.max_positions = config.max_positions
        self.position_size = config.position_size
        self.commission_rate = config.commission_rate
        self.slippage_rate = config.slippage_rate
        
        # 创建成本计算器
        self.cost_calculator = TradingCostCalculator(config)
        
        # 创建数据目录
        self.data_dir = Path(config.data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 加载或初始化账户
        self.account_file = self.data_dir / "account.json"
        self.trades_file = self.data_dir / "trades.csv"
        self.positions_file = self.data_dir / "positions.csv"
        self.daily_file = self.data_dir / "daily_values.csv"
        
        self._load_account()
    
    def _load_account(self):
        """加载账户信息"""
        if self.account_file.exists():
            with open(self.account_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cash = data['cash']
                self.positions = data['positions']
                self.start_date = data['start_date']
                logger.info(f"加载已有账户: 现金={self.cash:,.0f}, 持仓={len(self.positions)}只")
        else:
            self.cash = self.initial_capital
            self.positions = {}
            self.start_date = datetime.now().strftime('%Y-%m-%d')
            self._save_account()
            logger.info(f"创建新账户: 初始资金={self.initial_capital:,.0f}")
    
    def _save_account(self):
        """保存账户信息"""
        data = {
            'cash': self.cash,
            'positions': self.positions,
            'start_date': self.start_date,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.account_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _calculate_cost(self, price: float, shares: int, is_buy: bool = True) -> float:
        """
        计算交易成本
        
        Args:
            price: 价格
            shares: 股数
            is_buy: 是否买入
            
        Returns:
            实际成本（买入）或实际到手（卖出）
        """
        return self.cost_calculator.calculate_simple_cost(price, shares, is_buy)
    
    def _log_trade(self, date: str, code: str, action: str, price: float, 
                   shares: int, amount: float, reason: str = ''):
        """记录交易"""
        trade = {
            'date': date,
            'time': datetime.now().strftime('%H:%M:%S'),
            'code': code,
            'action': action,
            'price': price,
            'shares': shares,
            'amount': amount,
            'cash': self.cash,
            'reason': reason
        }
        
        # 追加到CSV
        df = pd.DataFrame([trade])
        if self.trades_file.exists():
            df.to_csv(self.trades_file, mode='a', header=False, index=False)
        else:
            df.to_csv(self.trades_file, index=False)
        
        logger.info(f"{action.upper()} {code} {shares}股 @{price:.2f} 原因:{reason}")
    
    def _update_positions_file(self):
        """更新持仓文件"""
        if not self.positions:
            return
        
        positions_list = []
        for code, pos in self.positions.items():
            # 获取最新价格
            df = self.db.get_daily_data(code)
            if not df.empty:
                current_price = df['close'].iloc[-1]
                current_value = current_price * pos['shares']
                profit = current_value - pos['cost'] * pos['shares']
                profit_rate = profit / (pos['cost'] * pos['shares'])
                
                positions_list.append({
                    'code': code,
                    'name': pos.get('name', ''),
                    'shares': pos['shares'],
                    'cost': pos['cost'],
                    'current_price': current_price,
                    'current_value': current_value,
                    'profit': profit,
                    'profit_rate': profit_rate,
                    'buy_date': pos['date'],
                    'hold_days': (datetime.now() - datetime.strptime(pos['date'], '%Y-%m-%d')).days
                })
        
        if positions_list:
            df = pd.DataFrame(positions_list)
            df.to_csv(self.positions_file, index=False)
    
    def _update_daily_value(self, date: str):
        """更新每日净值"""
        position_value = 0
        for code, pos in self.positions.items():
            df = self.db.get_daily_data(code, start_date=date, end_date=date)
            if not df.empty:
                position_value += df['close'].iloc[0] * pos['shares']
            else:
                position_value += pos['cost'] * pos['shares']
        
        total_value = self.cash + position_value
        
        daily = {
            'date': date,
            'cash': self.cash,
            'position_value': position_value,
            'total_value': total_value,
            'position_count': len(self.positions),
            'return': (total_value - self.initial_capital) / self.initial_capital
        }
        
        df = pd.DataFrame([daily])
        if self.daily_file.exists():
            df.to_csv(self.daily_file, mode='a', header=False, index=False)
        else:
            df.to_csv(self.daily_file, index=False)
    
    def buy(self, code: str, price: float, date: str, signal: dict = None) -> bool:
        """买入股票"""
        if len(self.positions) >= self.max_positions:
            logger.debug(f"持仓已满，无法买入 {code}")
            return False
        
        if code in self.positions:
            logger.debug(f"已持有 {code}")
            return False
        
        # 计算买入金额
        buy_amount = self.cash * self.position_size
        shares = int(buy_amount / price / 100) * 100
        
        if shares < 100:
            logger.debug(f"资金不足，无法买入 {code}")
            return False
        
        cost = self._calculate_cost(price, shares, is_buy=True)
        
        if cost > self.cash:
            logger.debug(f"资金不足，无法买入 {code}")
            return False
        
        # 执行买入
        self.cash -= cost
        self.positions[code] = {
            'shares': shares,
            'cost': price,
            'date': date,
            'signal': signal,
            'name': signal.get('name', '') if signal else ''
        }
        
        self._log_trade(date, code, 'buy', price, shares, cost, 
                       reason=f"信号触发(跌幅{signal.get('decline_rate', 0):.2%})" if signal else '')
        self._save_account()
        self._update_positions_file()
        
        return True
    
    def sell(self, code: str, price: float, date: str, reason: str = '') -> bool:
        """卖出股票"""
        if code not in self.positions:
            return False
        
        pos = self.positions[code]
        shares = pos['shares']
        proceeds = self._calculate_cost(price, shares, is_buy=False)
        
        self.cash += proceeds
        
        self._log_trade(date, code, 'sell', price, shares, proceeds, reason=reason)
        
        del self.positions[code]
        self._save_account()
        self._update_positions_file()
        
        return True
    
    def check_and_sell(self, date: str, stop_loss: float = -0.10, 
                      take_profit: float = 0.15, max_hold_days: int = 5,
                      time_stop_days: int = 3):
        """检查并执行止盈止损"""
        for code in list(self.positions.keys()):
            pos = self.positions[code]
            
            # 获取当前价格
            df = self.db.get_daily_data(code, start_date=date, end_date=date)
            if df.empty:
                continue
            
            current_price = df['close'].iloc[0]
            profit_rate = (current_price - pos['cost']) / pos['cost']
            hold_days = (datetime.strptime(date, '%Y-%m-%d') - 
                        datetime.strptime(pos['date'], '%Y-%m-%d')).days
            
            # 止损
            if profit_rate <= stop_loss:
                self.sell(code, current_price, date, reason=f'止损({profit_rate:.2%})')
                continue
            
            # 止盈
            if profit_rate >= take_profit:
                self.sell(code, current_price, date, reason=f'止盈({profit_rate:.2%})')
                continue
            
            # 时间止损
            if time_stop_days > 0 and hold_days >= time_stop_days and profit_rate < 0:
                self.sell(code, current_price, date, reason=f'时间止损({hold_days}天未反弹)')
                continue
            
            # 持有天数到期
            if hold_days >= max_hold_days:
                self.sell(code, current_price, date, reason=f'到期({hold_days}天)')
                continue
    
    def scan_and_buy(self, date: str):
        """扫描信号并买入"""
        if len(self.positions) >= self.max_positions:
            logger.debug(f"{date}: 持仓已满")
            return
        
        # 扫描信号
        signals = self.strategy.scan(
            date=date,
            max_stocks=200,
            use_volume_stabilize=False,
            check_market=False,
            check_liquidity_filter=True
        )
        
        if signals.empty:
            logger.debug(f"{date}: 未发现信号")
            return
        
        logger.info(f"{date}: 发现 {len(signals)} 个信号")
        
        # 尝试买入
        for _, signal in signals.iterrows():
            if len(self.positions) >= self.max_positions:
                break
            
            code = signal['code']
            
            # 获取次日开盘价
            next_date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            df = self.db.get_daily_data(code, start_date=next_date, end_date=next_date)
            
            if df.empty:
                continue
            
            buy_price = df['open'].iloc[0]
            self.buy(code, buy_price, next_date, signal=signal.to_dict())
    
    def run_daily(self, date: str = None):
        """运行每日交易流程"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"\n{'='*80}")
        logger.info(f"模拟盘运行: {date}")
        logger.info(f"{'='*80}")
        
        # 1. 检查止盈止损
        self.check_and_sell(date)
        
        # 2. 扫描新信号
        self.scan_and_buy(date)
        
        # 3. 更新净值
        self._update_daily_value(date)
        
        # 4. 显示账户状态
        self.show_status()
    
    def show_status(self):
        """显示账户状态"""
        position_value = 0
        for code, pos in self.positions.items():
            df = self.db.get_daily_data(code)
            if not df.empty:
                current_price = df['close'].iloc[-1]
                position_value += current_price * pos['shares']
        
        total_value = self.cash + position_value
        total_return = (total_value - self.initial_capital) / self.initial_capital
        
        print(f"\n{'='*80}")
        print(f"账户状态")
        print(f"{'='*80}")
        print(f"初始资金:     {self.initial_capital:>12,.0f}")
        print(f"当前现金:     {self.cash:>12,.0f}")
        print(f"持仓市值:     {position_value:>12,.0f}")
        print(f"总资产:       {total_value:>12,.0f}")
        print(f"总收益:       {total_value - self.initial_capital:>12,.0f}")
        print(f"总收益率:     {total_return:>12.2%}")
        print(f"持仓数量:     {len(self.positions):>12}")
        
        if self.positions:
            print(f"\n当前持仓:")
            print(f"{'代码':<12} {'名称':<10} {'股数':>8} {'成本':>8} {'现价':>8} {'盈亏':>8} {'盈亏率':>8} {'持有天数':>8}")
            print("-"*80)
            
            for code, pos in self.positions.items():
                df = self.db.get_daily_data(code)
                if not df.empty:
                    current_price = df['close'].iloc[-1]
                    profit = (current_price - pos['cost']) * pos['shares']
                    profit_rate = (current_price - pos['cost']) / pos['cost']
                    hold_days = (datetime.now() - datetime.strptime(pos['date'], '%Y-%m-%d')).days
                    
                    print(f"{code:<12} {pos.get('name', ''):<10} {pos['shares']:>8} "
                          f"{pos['cost']:>8.2f} {current_price:>8.2f} {profit:>8.0f} "
                          f"{profit_rate:>8.2%} {hold_days:>8}")
        
        print(f"{'='*80}\n")
    
    def show_performance(self):
        """显示绩效报告"""
        if not self.daily_file.exists():
            print("暂无绩效数据")
            return
        
        df_daily = pd.read_csv(self.daily_file)
        
        if df_daily.empty:
            print("暂无绩效数据")
            return
        
        # 计算最大回撤
        df_daily['peak'] = df_daily['total_value'].cummax()
        df_daily['drawdown'] = (df_daily['total_value'] - df_daily['peak']) / df_daily['peak']
        max_drawdown = df_daily['drawdown'].min()
        
        # 读取交易记录
        trades_df = pd.read_csv(self.trades_file) if self.trades_file.exists() else pd.DataFrame()
        
        print(f"\n{'='*80}")
        print(f"绩效报告")
        print(f"{'='*80}")
        print(f"运行天数:     {len(df_daily):>12}")
        print(f"总收益率:     {df_daily['return'].iloc[-1]:>12.2%}")
        print(f"最大回撤:     {max_drawdown:>12.2%}")
        
        if not trades_df.empty:
            buy_trades = trades_df[trades_df['action'] == 'buy']
            sell_trades = trades_df[trades_df['action'] == 'sell']
            print(f"买入次数:     {len(buy_trades):>12}")
            print(f"卖出次数:     {len(sell_trades):>12}")
        
        print(f"{'='*80}\n")
        
        # 显示净值曲线
        print("净值曲线（最近10天）:")
        print(df_daily[['date', 'total_value', 'return']].tail(10).to_string(index=False))
    
    def reset(self):
        """重置账户（谨慎使用）"""
        confirm = input("确认要重置账户吗？这将清空所有数据！(yes/no): ")
        if confirm.lower() == 'yes':
            self.cash = self.initial_capital
            self.positions = {}
            self.start_date = datetime.now().strftime('%Y-%m-%d')
            self._save_account()
            
            # 清空文件
            for f in [self.trades_file, self.positions_file, self.daily_file]:
                if f.exists():
                    f.unlink()
            
            logger.info("账户已重置")
        else:
            logger.info("取消重置")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='模拟盘交易系统')
    parser.add_argument('command', choices=['run', 'status', 'performance', 'reset'],
                       help='命令: run=运行交易, status=查看状态, performance=查看绩效, reset=重置账户')
    parser.add_argument('--date', help='指定日期 (YYYY-MM-DD)', default=None)
    
    args = parser.parse_args()
    
    # 初始化
    db = StockDatabase("data/a_share.db")
    strategy = VolumeShrinkStrategy(db=db, min_avg_turnover=1e8)
    
    paper = PaperTradingEngine(
        db=db,
        strategy=strategy,
        initial_capital=100000,  # 10万
        max_positions=5,
        position_size=0.15
    )
    
    # 执行命令
    if args.command == 'run':
        paper.run_daily(date=args.date)
    elif args.command == 'status':
        paper.show_status()
    elif args.command == 'performance':
        paper.show_performance()
    elif args.command == 'reset':
        paper.reset()
    
    db.close()


if __name__ == "__main__":
    main()

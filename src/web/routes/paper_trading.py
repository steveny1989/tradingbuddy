"""
模拟盘API路由
"""
from flask import request
from . import api_bp
from src.data.database import StockDatabase
from src.app.paper_trading import PaperTradingEngine
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.web.utils.response import success_response, error_response
import logging
from pathlib import Path
import json
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

# 初始化数据库连接
db = StockDatabase()

# 全局模拟盘引擎实例（单例模式）
_paper_trading_engine = None


def get_paper_trading_engine():
    """获取模拟盘引擎实例（单例）"""
    global _paper_trading_engine
    
    if _paper_trading_engine is None:
        # 初始化策略
        strategy = VolumeShrinkStrategy(db=db, min_avg_turnover=1e8)
        
        # 初始化模拟盘引擎
        _paper_trading_engine = PaperTradingEngine(
            db=db,
            strategy=strategy,
            initial_capital=100000,  # 10万
            max_positions=5,
            position_size=0.15
        )
    
    return _paper_trading_engine


@api_bp.route('/paper-trading/status', methods=['GET'])
def get_paper_trading_status():
    """
    获取模拟盘状态
    
    Returns:
        {
            "success": true,
            "data": {
                "account": {
                    "initial_capital": float,
                    "cash": float,
                    "position_value": float,
                    "total_value": float,
                    "total_return": float,
                    "start_date": str
                },
                "positions": [
                    {
                        "code": str,
                        "name": str,
                        "shares": int,
                        "cost": float,
                        "current_price": float,
                        "current_value": float,
                        "profit": float,
                        "profit_rate": float,
                        "buy_date": str,
                        "hold_days": int
                    },
                    ...
                ],
                "today_trades": [
                    {
                        "time": str,
                        "code": str,
                        "action": str,
                        "price": float,
                        "shares": int,
                        "amount": float,
                        "reason": str
                    },
                    ...
                ]
            }
        }
    """
    try:
        engine = get_paper_trading_engine()
        
        # 计算持仓市值
        position_value = 0
        positions_list = []
        
        for code, pos in engine.positions.items():
            # 获取最新价格
            df = db.get_daily_data(code)
            if not df.empty:
                current_price = df['close'].iloc[-1]
                current_value = current_price * pos['shares']
                profit = current_value - pos['cost'] * pos['shares']
                profit_rate = profit / (pos['cost'] * pos['shares'])
                hold_days = (datetime.now() - datetime.strptime(pos['date'], '%Y-%m-%d')).days
                
                position_value += current_value
                
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
                    'hold_days': hold_days
                })
        
        # 计算总资产
        total_value = engine.cash + position_value
        total_return = (total_value - engine.initial_capital) / engine.initial_capital
        
        # 获取今日交易记录
        today_trades = []
        if engine.trades_file.exists():
            trades_df = pd.read_csv(engine.trades_file)
            today = datetime.now().strftime('%Y-%m-%d')
            today_trades_df = trades_df[trades_df['date'] == today]
            
            if not today_trades_df.empty:
                today_trades = today_trades_df.to_dict('records')
        
        # 构建响应
        response_data = {
            'account': {
                'initial_capital': engine.initial_capital,
                'cash': engine.cash,
                'position_value': position_value,
                'total_value': total_value,
                'total_return': total_return,
                'start_date': engine.start_date,
                'position_count': len(engine.positions)
            },
            'positions': positions_list,
            'today_trades': today_trades
        }
        
        return success_response(response_data)
        
    except Exception as e:
        logger.error(f"获取模拟盘状态失败: {e}", exc_info=True)
        return error_response('获取模拟盘状态失败', 'FETCH_ERROR', 500)


@api_bp.route('/paper-trading/performance', methods=['GET'])
def get_paper_trading_performance():
    """
    获取模拟盘绩效数据
    
    Returns:
        {
            "success": true,
            "data": {
                "metrics": {
                    "total_return": float,
                    "max_drawdown": float,
                    "running_days": int,
                    "total_trades": int,
                    "buy_count": int,
                    "sell_count": int
                },
                "daily_values": [
                    {
                        "date": str,
                        "cash": float,
                        "position_value": float,
                        "total_value": float,
                        "return": float
                    },
                    ...
                ]
            }
        }
    """
    try:
        engine = get_paper_trading_engine()
        
        # 读取每日净值数据
        daily_values = []
        max_drawdown = 0
        running_days = 0
        
        if engine.daily_file.exists():
            df_daily = pd.read_csv(engine.daily_file)
            
            if not df_daily.empty:
                # 计算最大回撤
                df_daily['peak'] = df_daily['total_value'].cummax()
                df_daily['drawdown'] = (df_daily['total_value'] - df_daily['peak']) / df_daily['peak']
                max_drawdown = df_daily['drawdown'].min()
                running_days = len(df_daily)
                
                # 转换为列表
                daily_values = df_daily[['date', 'cash', 'position_value', 'total_value', 'return']].to_dict('records')
        
        # 读取交易记录统计
        total_trades = 0
        buy_count = 0
        sell_count = 0
        
        if engine.trades_file.exists():
            trades_df = pd.read_csv(engine.trades_file)
            total_trades = len(trades_df)
            buy_count = len(trades_df[trades_df['action'] == 'buy'])
            sell_count = len(trades_df[trades_df['action'] == 'sell'])
        
        # 计算总收益率
        position_value = 0
        for code, pos in engine.positions.items():
            df = db.get_daily_data(code)
            if not df.empty:
                current_price = df['close'].iloc[-1]
                position_value += current_price * pos['shares']
        
        total_value = engine.cash + position_value
        total_return = (total_value - engine.initial_capital) / engine.initial_capital
        
        # 构建响应
        response_data = {
            'metrics': {
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'running_days': running_days,
                'total_trades': total_trades,
                'buy_count': buy_count,
                'sell_count': sell_count
            },
            'daily_values': daily_values
        }
        
        return success_response(response_data)
        
    except Exception as e:
        logger.error(f"获取模拟盘绩效失败: {e}", exc_info=True)
        return error_response('获取模拟盘绩效失败', 'FETCH_ERROR', 500)


@api_bp.route('/paper-trading/start', methods=['POST'])
def start_paper_trading():
    """
    启动模拟盘（运行每日交易流程）
    
    Request Body:
        {
            "date": str  # 可选，指定日期，默认为今天
        }
    
    Returns:
        {
            "success": true,
            "message": "模拟盘已启动"
        }
    """
    try:
        data = request.get_json() or {}
        date = data.get('date', None)
        
        engine = get_paper_trading_engine()
        engine.run_daily(date=date)
        
        return success_response({
            'message': '模拟盘交易流程已执行',
            'date': date or datetime.now().strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        logger.error(f"启动模拟盘失败: {e}", exc_info=True)
        return error_response('启动模拟盘失败', 'START_ERROR', 500)


@api_bp.route('/paper-trading/stop', methods=['POST'])
def stop_paper_trading():
    """
    停止模拟盘（暂不实现，预留接口）
    
    Returns:
        {
            "success": true,
            "message": "模拟盘已停止"
        }
    """
    try:
        # 目前模拟盘是手动触发的，没有后台运行，所以停止操作暂不需要
        return success_response({
            'message': '模拟盘已停止（当前为手动模式）'
        })
        
    except Exception as e:
        logger.error(f"停止模拟盘失败: {e}", exc_info=True)
        return error_response('停止模拟盘失败', 'STOP_ERROR', 500)


@api_bp.route('/paper-trading/reset', methods=['POST'])
def reset_paper_trading():
    """
    重置模拟盘账户
    
    Returns:
        {
            "success": true,
            "message": "模拟盘已重置"
        }
    """
    try:
        engine = get_paper_trading_engine()
        
        # 重置账户
        engine.cash = engine.initial_capital
        engine.positions = {}
        engine.start_date = datetime.now().strftime('%Y-%m-%d')
        engine._save_account()
        
        # 清空文件
        for f in [engine.trades_file, engine.positions_file, engine.daily_file]:
            if f.exists():
                f.unlink()
        
        logger.info("模拟盘账户已重置")
        
        return success_response({
            'message': '模拟盘账户已重置',
            'initial_capital': engine.initial_capital
        })
        
    except Exception as e:
        logger.error(f"重置模拟盘失败: {e}", exc_info=True)
        return error_response('重置模拟盘失败', 'RESET_ERROR', 500)

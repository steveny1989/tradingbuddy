"""
极简选股助手 API 路由
User-Friendly Stock Picker API Routes

为普通股民提供极简的选股体验，隐藏所有技术细节
"""
from flask import request, jsonify
from datetime import datetime
import pandas as pd
from . import api_bp
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.business.strategies.ma_crossover import MACrossoverStrategy
from src.web.utils.response import success_response, error_response
from src.web.cache_manager import get_cache, refresh_cache_async, init_cache
import logging

logger = logging.getLogger(__name__)

# 初始化数据库连接
db = StockDatabase()

# 金牌策略配置 - 为普通股民设计的三个核心策略
GOLDEN_STRATEGIES = {
    'low_volume_breakout': {
        'id': 'low_volume_breakout',
        'name': '低位放量突破',
        'simple_name': '低位放量突破',
        'description': '寻找连续下跌后突然放量的股票，可能是主力进场信号',
        'suitable_for': '适合短线操作，追求快速反弹',
        'risk_level': '中等',
        'strategy_class': VolumeShrinkStrategy,
        'strategy_params': {
            'min_avg_turnover': 1e8
        },
        'scan_params': {
            'min_cap': 50e8,
            'max_cap': 200e8,
            'min_decline': 0.10,
            'use_volume_stabilize': True,
            'check_market': True,
            'check_liquidity_filter': True
        }
    },
    'ma_golden_cross': {
        'id': 'ma_golden_cross',
        'name': '多头排列启动',
        'simple_name': '多头排列启动',
        'description': '短期均线上穿长期均线，趋势向上的信号',
        'suitable_for': '适合中线持有，跟随趋势',
        'risk_level': '较低',
        'strategy_class': MACrossoverStrategy,
        'strategy_params': {
            'short_window': 5,
            'long_window': 20,
            'volume_window': 5,
            'min_avg_turnover': 1e8
        },
        'scan_params': {
            'min_cap': 50e8,
            'max_cap': 200e8,
            'check_volume': True,
            'check_liquidity_filter': True
        }
    }
}


def make_error_friendly(error_message: str) -> str:
    """
    将技术错误消息转换为友好的用户消息
    
    Args:
        error_message: 原始错误消息
        
    Returns:
        友好的错误消息
    """
    # 技术术语到友好消息的映射
    error_mappings = {
        'database': '数据库连接失败，请稍后重试',
        'connection': '网络连接失败，请检查网络',
        'timeout': '请求超时，请稍后重试',
        'not found': '未找到相关数据',
        'invalid': '输入数据有误',
        'permission': '没有访问权限',
        'server error': '服务器繁忙，请稍后重试',
        'sql': '数据查询失败，请稍后重试',
        'empty': '暂无数据',
        'no data': '暂无数据'
    }
    
    # 转换为小写进行匹配
    error_lower = error_message.lower()
    
    # 查找匹配的映射
    for key, friendly_msg in error_mappings.items():
        if key in error_lower:
            return friendly_msg
    
    # 如果没有匹配，返回通用消息
    return '操作失败，请稍后重试'


def generate_plain_reason(strategy_id: str, signal_data: dict) -> str:
    """
    生成大白话选股理由
    
    Args:
        strategy_id: 策略ID
        signal_data: 信号数据
        
    Returns:
        大白话选股理由
    """
    if strategy_id == 'low_volume_breakout':
        # 低位放量突破策略
        decline_rate = abs(signal_data.get('decline_rate', 0)) * 100
        volume_ratio = signal_data.get('v0', 0) / signal_data.get('v1', 1) if signal_data.get('v1', 0) > 0 else 1
        
        reason = f"连续下跌{decline_rate:.1f}%后，今日成交量放大{volume_ratio:.1f}倍，可能有主力资金进场"
        return reason
        
    elif strategy_id == 'ma_golden_cross':
        # 多头排列启动策略
        volume_ratio = signal_data.get('volume_ratio', 1)
        
        reason = f"短期均线上穿长期均线，形成金叉，成交量放大{volume_ratio:.1f}倍，趋势向上"
        return reason
    
    return "符合策略条件"


def calculate_confidence_score(strategy_id: str, signal_data: dict) -> int:
    """
    计算信号强度分数（0-100）
    
    Args:
        strategy_id: 策略ID
        signal_data: 信号数据
        
    Returns:
        信号强度分数
    """
    score = 50  # 基础分数
    
    if strategy_id == 'low_volume_breakout':
        # 跌幅越大，分数越高（最多+20分）
        decline_rate = abs(signal_data.get('decline_rate', 0))
        score += min(decline_rate * 100, 20)
        
        # 放量越大，分数越高（最多+20分）
        volume_ratio = signal_data.get('v0', 0) / signal_data.get('v1', 1) if signal_data.get('v1', 0) > 0 else 1
        score += min((volume_ratio - 1) * 10, 20)
        
        # 有起跌转折，加10分
        if signal_data.get('reversal', False):
            score += 10
            
    elif strategy_id == 'ma_golden_cross':
        # 均线距离越大，分数越高（最多+20分）
        ma_distance = abs(signal_data.get('ma_distance', 0))
        score += min(ma_distance * 1000, 20)
        
        # 成交量放大越多，分数越高（最多+20分）
        volume_ratio = signal_data.get('volume_ratio', 1)
        score += min((volume_ratio - 1) * 10, 20)
    
    # 确保分数在0-100之间
    return max(0, min(100, int(score)))


def scan_daily_picks(strategy_id: str = None, max_picks: int = 10) -> list:
    """
    扫描今日精选股票
    
    Args:
        strategy_id: 策略ID（None表示使用所有策略）
        max_picks: 最多返回股票数
        
    Returns:
        精选股票列表
    """
    all_picks = []
    
    # 确定要使用的策略
    strategies_to_scan = [strategy_id] if strategy_id else list(GOLDEN_STRATEGIES.keys())
    
    for sid in strategies_to_scan:
        if sid not in GOLDEN_STRATEGIES:
            continue
            
        strategy_info = GOLDEN_STRATEGIES[sid]
        
        try:
            # 创建策略实例
            strategy_class = strategy_info['strategy_class']
            strategy_params = strategy_info['strategy_params']
            strategy = strategy_class(db, **strategy_params)
            
            # 执行扫描
            scan_params = strategy_info['scan_params'].copy()
            signals_df = strategy.scan(**scan_params)
            
            if signals_df.empty:
                continue
            
            # 转换为字典列表
            for _, row in signals_df.iterrows():
                signal_data = row.to_dict()
                
                # 计算信号强度
                confidence_score = calculate_confidence_score(sid, signal_data)
                
                # 生成选股理由
                reason = generate_plain_reason(sid, signal_data)
                
                pick = {
                    'code': signal_data.get('code', ''),
                    'name': signal_data.get('name', ''),
                    'price': float(signal_data.get('price', 0)),
                    'confidence_score': confidence_score,
                    'reason': reason,
                    'strategy_id': sid,
                    'strategy_name': strategy_info['simple_name'],
                    'date': signal_data.get('date', '')
                }
                
                all_picks.append(pick)
                
        except Exception as e:
            logger.error(f"扫描策略 {sid} 失败: {e}", exc_info=True)
            continue
    
    # 按信号强度排序
    all_picks.sort(key=lambda x: x['confidence_score'], reverse=True)
    
    # 过滤低于30分的信号
    all_picks = [p for p in all_picks if p['confidence_score'] >= 30]
    
    # 返回前N只
    return all_picks[:max_picks]


@api_bp.route('/picker/strategies', methods=['GET'])
def get_golden_strategies():
    """
    获取金牌策略列表
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "id": str,
                    "name": str,
                    "description": str,
                    "suitable_for": str,
                    "risk_level": str
                },
                ...
            ]
        }
    """
    try:
        strategies = []
        for strategy_id, strategy_info in GOLDEN_STRATEGIES.items():
            strategies.append({
                'id': strategy_info['id'],
                'name': strategy_info['simple_name'],
                'description': strategy_info['description'],
                'suitable_for': strategy_info['suitable_for'],
                'risk_level': strategy_info['risk_level']
            })
        
        return success_response(strategies)
        
    except Exception as e:
        logger.error(f"获取金牌策略列表失败: {e}", exc_info=True)
        friendly_error = make_error_friendly(str(e))
        return error_response(friendly_error, 'FETCH_ERROR', 500)


@api_bp.route('/picker/daily-picks', methods=['GET'])
def get_daily_picks():
    """
    获取今日精选股票（从缓存读取，毫秒级响应）
    
    Query Parameters:
        - strategy_id: 策略ID（可选，不传则使用所有策略）
        - limit: 返回数量（默认10）
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "code": str,
                    "name": str,
                    "price": float,
                    "confidence_score": int,
                    "reason": str,
                    "strategy_id": str,
                    "strategy_name": str,
                    "date": str
                },
                ...
            ]
        }
    """
    try:
        # 获取查询参数
        strategy_id = request.args.get('strategy_id')
        limit = int(request.args.get('limit', 10))
        
        # 限制最大返回数量
        limit = min(limit, 50)
        
        # 从缓存读取
        cache = get_cache()
        picks = cache.get_daily_picks()
        
        # 如果缓存为空，返回提示
        if not picks:
            return success_response([])
        
        # 按策略过滤
        if strategy_id:
            picks = [p for p in picks if p.get('strategy_id') == strategy_id]
        
        # 返回前N只
        return success_response(picks[:limit])
        
    except Exception as e:
        logger.error(f"获取今日精选失败: {e}", exc_info=True)
        friendly_error = make_error_friendly(str(e))
        return error_response(friendly_error, 'FETCH_ERROR', 500)


def get_picks_from_database(strategy_id: str = None, max_picks: int = 10) -> list:
    """
    从数据库读取最新的扫描结果，如果没有则返回空列表
    
    Args:
        strategy_id: 策略ID（None表示使用所有策略）
        max_picks: 最多返回股票数
        
    Returns:
        精选股票列表
    """
    try:
        # 先尝试从scan_results表读取（如果表存在）
        # 注意：当前scan_results表结构存储的是汇总信息，signals字段是JSON数组
        query = """
            SELECT strategy_name, scan_date, signals, signals_found
            FROM scan_results
            ORDER BY scan_date DESC
            LIMIT 1
        """
        
        try:
            row = db.conn.execute(query).fetchone()
            if row and row[2]:  # signals字段不为空
                import json
                strategy_name, scan_date, signals_json, signals_found = row
                signals = json.loads(signals_json)
                
                picks = []
                for signal in signals[:max_picks]:
                    # 从signal中提取信息
                    code = signal.get('code', '')
                    name = signal.get('name', '')
                    price = signal.get('price', 0)
                    signal_data = signal
                    
                    # 确定策略ID
                    sid = 'ma_golden_cross'  # 默认策略
                    
                    # 计算信号强度
                    confidence_score = calculate_confidence_score(sid, signal_data)
                    
                    # 生成选股理由
                    reason = generate_plain_reason(sid, signal_data)
                    
                    pick = {
                        'code': code,
                        'name': name,
                        'price': float(price) if price else 0.0,
                        'confidence_score': confidence_score,
                        'reason': reason,
                        'strategy_id': sid,
                        'strategy_name': '多头排列启动',
                        'date': scan_date
                    }
                    
                    picks.append(pick)
                
                # 按信号强度排序
                picks.sort(key=lambda x: x['confidence_score'], reverse=True)
                
                # 过滤低于30分的信号
                picks = [p for p in picks if p['confidence_score'] >= 30]
                
                return picks[:max_picks]
        except Exception as e:
            logger.warning(f"从scan_results读取失败: {e}")
        
        # 如果数据库没有数据，返回空列表（不再执行耗时的扫描）
        logger.info("数据库无缓存数据，返回空列表")
        return []
        
    except Exception as e:
        logger.error(f"获取精选股票失败: {e}", exc_info=True)
        return []


def calculate_signal(code: str) -> dict:
    """
    计算股票的信号状态（买入/卖出/观望）
    
    Args:
        code: 股票代码（支持 sz.000001 或 000001 格式）
        
    Returns:
        信号字典
    """
    try:
        # 确保代码有市场前缀（get_daily_data需要完整代码）
        # 如果没有前缀，需要从stock_basic表查询市场信息
        if '.' not in code:
            # 查询市场信息
            stock_info = db.conn.execute(
                "SELECT market FROM stock_basic WHERE code = ?",
                (code,)
            ).fetchone()
            if stock_info:
                market = stock_info[0]
                code = f"{market}.{code}"
            else:
                # 如果找不到，返回默认信号
                return {
                    'signal': 'hold',
                    'label': '观望',
                    'color': 'yellow'
                }
        
        # 获取最近数据
        df = db.get_daily_data(code)
        if df.empty or len(df) < 20:
            return {
                'signal': 'hold',
                'label': '观望',
                'color': 'yellow'
            }
        
        df = df.sort_values('date').tail(20)
        
        # 计算均线
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma20'] = df['close'].rolling(window=20).mean()
        
        latest = df.iloc[-1]
        
        # 简单的信号逻辑
        if latest['ma5'] > latest['ma20']:
            # 短期均线在长期均线上方 -> 买入信号
            return {
                'signal': 'buy',
                'label': '买入',
                'color': 'green'
            }
        elif latest['ma5'] < latest['ma20'] * 0.95:
            # 短期均线明显低于长期均线 -> 卖出信号
            return {
                'signal': 'sell',
                'label': '卖出',
                'color': 'red'
            }
        else:
            # 其他情况 -> 观望
            return {
                'signal': 'hold',
                'label': '观望',
                'color': 'yellow'
            }
            
    except Exception as e:
        logger.debug(f"计算信号失败 {code}: {e}")
        return {
            'signal': 'hold',
            'label': '观望',
            'color': 'yellow'
        }


def calculate_alerts(code: str, add_price: float, stop_loss_pct: float = -0.10, take_profit_pct: float = 0.20) -> dict:
    """
    计算止损止盈预警
    
    Args:
        code: 股票代码（支持 sz.000001 或 000001 格式）
        add_price: 添加时价格
        stop_loss_pct: 止损百分比（默认-10%）
        take_profit_pct: 止盈百分比（默认+20%）
        
    Returns:
        预警字典
    """
    try:
        # 确保代码有市场前缀（get_daily_data需要完整代码）
        # 如果没有前缀，需要从stock_basic表查询市场信息
        if '.' not in code:
            # 查询市场信息
            stock_info = db.conn.execute(
                "SELECT market FROM stock_basic WHERE code = ?",
                (code,)
            ).fetchone()
            if stock_info:
                market = stock_info[0]
                code = f"{market}.{code}"
            else:
                return None
        
        # 获取当前价格
        df = db.get_daily_data(code)
        if df.empty:
            return None
        
        current_price = float(df.iloc[-1]['close'])
        
        # 计算止损止盈价格
        stop_loss_price = add_price * (1 + stop_loss_pct)
        take_profit_price = add_price * (1 + take_profit_pct)
        
        # 计算当前盈亏百分比
        profit_pct = (current_price - add_price) / add_price
        
        # 检查是否触发预警
        if current_price <= stop_loss_price:
            return {
                'type': 'stop_loss',
                'message': f'建议止损卖出',
                'current_price': current_price,
                'target_price': stop_loss_price,
                'profit_pct': profit_pct
            }
        elif current_price >= take_profit_price:
            return {
                'type': 'take_profit',
                'message': f'建议止盈卖出',
                'current_price': current_price,
                'target_price': take_profit_price,
                'profit_pct': profit_pct
            }
        else:
            return None
            
    except Exception as e:
        logger.debug(f"计算预警失败 {code}: {e}")
        return None


@api_bp.route('/picker/watchlist', methods=['POST'])
def get_watchlist_data():
    """
    获取自选股数据
    
    Request Body:
        {
            "stocks": [
                {
                    "code": str,
                    "add_time": str,
                    "add_price": float,
                    "stop_loss": float,  // 止损百分比（如-0.10）
                    "take_profit": float  // 止盈百分比（如0.20）
                },
                ...
            ]
        }
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "code": str,
                    "name": str,
                    "current_price": float,
                    "change_pct": float,
                    "add_time": str,
                    "add_price": float,
                    "profit_pct": float,
                    "signal": {
                        "signal": str,
                        "label": str,
                        "color": str
                    },
                    "stop_loss": float,
                    "take_profit": float,
                    "alert": {
                        "type": str,
                        "message": str,
                        "current_price": float,
                        "target_price": float
                    } | null
                },
                ...
            ]
        }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data or 'stocks' not in data:
            return error_response('请求数据格式错误', 'INVALID_REQUEST', 400)
        
        stocks = data['stocks']
        result = []
        
        for stock in stocks:
            code = stock.get('code')
            add_time = stock.get('add_time')
            add_price = float(stock.get('add_price', 0))
            stop_loss_pct = float(stock.get('stop_loss', -0.10))
            take_profit_pct = float(stock.get('take_profit', 0.20))
            
            if not code:
                continue
            
            try:
                # 提取代码（不带前缀）用于查询stock_basic
                code_without_prefix = code.split('.')[1] if '.' in code else code
                
                # 获取股票基本信息和市场
                stock_info = db.conn.execute(
                    "SELECT name, market FROM stock_basic WHERE code = ?",
                    (code_without_prefix,)
                ).fetchone()
                
                if not stock_info:
                    logger.debug(f"股票 {code} 不存在")
                    continue
                
                name, market = stock_info
                
                # 构建完整代码（带市场前缀）用于查询日线数据
                full_code = code if '.' in code else f"{market}.{code_without_prefix}"
                
                # 获取当前价格
                df = db.get_daily_data(full_code)
                if df.empty:
                    # 没有数据时，返回基本信息
                    logger.debug(f"股票 {code} 没有日线数据")
                    result.append({
                        'code': code,
                        'name': name,
                        'current_price': add_price,  # 使用添加时价格
                        'change_pct': 0.0,
                        'add_time': add_time,
                        'add_price': add_price,
                        'profit_pct': 0.0,
                        'signal': {
                            'signal': 'hold',
                            'label': '观望',
                            'color': 'yellow'
                        },
                        'stop_loss': stop_loss_pct,
                        'take_profit': take_profit_pct,
                        'alert': None
                    })
                    continue
                
                latest = df.iloc[-1]
                current_price = float(latest['close'])
                
                # 计算涨跌幅
                if len(df) >= 2:
                    prev_close = float(df.iloc[-2]['close'])
                    change_pct = (current_price - prev_close) / prev_close
                else:
                    change_pct = 0.0
                
                # 计算盈亏
                profit_pct = (current_price - add_price) / add_price if add_price > 0 else 0.0
                
                # 计算信号
                signal = calculate_signal(code)
                
                # 计算预警
                alert = calculate_alerts(code, add_price, stop_loss_pct, take_profit_pct)
                
                result.append({
                    'code': code,
                    'name': name,
                    'current_price': current_price,
                    'change_pct': change_pct,
                    'add_time': add_time,
                    'add_price': add_price,
                    'profit_pct': profit_pct,
                    'signal': signal,
                    'stop_loss': stop_loss_pct,
                    'take_profit': take_profit_pct,
                    'alert': alert
                })
                
            except Exception as e:
                logger.error(f"处理自选股 {code} 失败: {e}")
                continue
        
        return success_response(result)
        
    except Exception as e:
        logger.error(f"获取自选股数据失败: {e}", exc_info=True)
        friendly_error = make_error_friendly(str(e))
        return error_response(friendly_error, 'FETCH_ERROR', 500)


def calculate_strategy_performance(strategy_id: str) -> dict:
    """
    计算策略历史表现
    
    Args:
        strategy_id: 策略ID
        
    Returns:
        策略表现数据字典
    """
    try:
        # 从回测结果表查询该策略的所有回测记录
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT 
                total_return, win_rate, max_drawdown, 
                total_trades, completed_trades, win_trades,
                avg_profit_rate, created_at
            FROM backtest_results
            WHERE strategy_id = ? AND status = 'completed'
            ORDER BY created_at DESC
            LIMIT 10
        """, (strategy_id,))
        
        results = cursor.fetchall()
        
        if not results:
            # 如果没有回测记录，返回默认值
            return {
                'win_rate': 0.0,
                'avg_return': 0.0,
                'max_drawdown': 0.0,
                'total_backtests': 0,
                'recent_performance': []
            }
        
        # 计算平均表现
        total_return_sum = sum(r[0] or 0 for r in results)
        win_rate_sum = sum(r[1] or 0 for r in results)
        max_drawdown_max = max(abs(r[2] or 0) for r in results)
        
        avg_return = total_return_sum / len(results)
        avg_win_rate = win_rate_sum / len(results)
        
        # 构建最近表现列表
        recent_performance = []
        for r in results[:5]:  # 只返回最近5次
            recent_performance.append({
                'return': r[0] or 0.0,
                'win_rate': r[1] or 0.0,
                'max_drawdown': r[2] or 0.0,
                'total_trades': r[3] or 0,
                'date': r[7]
            })
        
        return {
            'win_rate': avg_win_rate,
            'avg_return': avg_return,
            'max_drawdown': max_drawdown_max,
            'total_backtests': len(results),
            'recent_performance': recent_performance
        }
        
    except Exception as e:
        logger.error(f"计算策略表现失败 {strategy_id}: {e}")
        return {
            'win_rate': 0.0,
            'avg_return': 0.0,
            'max_drawdown': 0.0,
            'total_backtests': 0,
            'recent_performance': []
        }


@api_bp.route('/picker/strategies/<strategy_id>/performance', methods=['GET'])
def get_strategy_performance(strategy_id: str):
    """
    获取策略历史表现
    
    Path Parameters:
        - strategy_id: 策略ID
    
    Returns:
        {
            "success": true,
            "data": {
                "strategy_id": str,
                "strategy_name": str,
                "win_rate": float,
                "avg_return": float,
                "max_drawdown": float,
                "total_backtests": int,
                "recent_performance": [
                    {
                        "return": float,
                        "win_rate": float,
                        "max_drawdown": float,
                        "total_trades": int,
                        "date": str
                    },
                    ...
                ]
            }
        }
    """
    try:
        # 检查策略是否存在
        if strategy_id not in GOLDEN_STRATEGIES:
            return error_response('策略不存在', 'NOT_FOUND', 404)
        
        strategy_info = GOLDEN_STRATEGIES[strategy_id]
        
        # 计算策略表现
        performance = calculate_strategy_performance(strategy_id)
        
        # 构建响应
        result = {
            'strategy_id': strategy_id,
            'strategy_name': strategy_info['simple_name'],
            'description': strategy_info['description'],
            'win_rate': performance['win_rate'],
            'avg_return': performance['avg_return'],
            'max_drawdown': performance['max_drawdown'],
            'total_backtests': performance['total_backtests'],
            'recent_performance': performance['recent_performance']
        }
        
        return success_response(result)
        
    except Exception as e:
        logger.error(f"获取策略表现失败: {e}", exc_info=True)
        friendly_error = make_error_friendly(str(e))
        return error_response(friendly_error, 'FETCH_ERROR', 500)


@api_bp.route('/picker/sync', methods=['POST'])
def trigger_sync():
    """
    触发缓存刷新（后台异步执行）
    
    Returns:
        {
            "success": true,
            "data": {
                "status": "started",
                "message": "缓存刷新已开始"
            }
        }
    """
    try:
        cache = get_cache()
        
        # 检查是否正在更新
        if cache.is_updating():
            return success_response({
                'status': 'already_running',
                'message': '缓存正在刷新中，请稍后'
            })
        
        # 触发异步刷新
        refresh_cache_async(get_picks_from_database)
        
        return success_response({
            'status': 'started',
            'message': '缓存刷新已开始'
        })
        
    except Exception as e:
        logger.error(f"触发缓存刷新失败: {e}", exc_info=True)
        friendly_error = make_error_friendly(str(e))
        return error_response(friendly_error, 'SYNC_ERROR', 500)


@api_bp.route('/picker/sync/status', methods=['GET'])
def get_sync_status():
    """
    获取数据同步状态（从缓存读取）
    
    Returns:
        {
            "success": true,
            "data": {
                "last_update_time": str,
                "is_updating": bool,
                "total_picks": int
            }
        }
    """
    try:
        cache = get_cache()
        last_update = cache.get_last_update()
        is_updating = cache.is_updating()
        picks = cache.get_daily_picks()
        
        return success_response({
            'last_update_time': last_update.isoformat() if last_update else None,
            'is_updating': is_updating,
            'total_picks': len(picks)
        })
        
    except Exception as e:
        logger.error(f"获取同步状态失败: {e}", exc_info=True)
        return error_response('获取状态失败', 'FETCH_ERROR', 500)


@api_bp.route('/picker/stocks/<code>', methods=['GET'])
def get_picker_stock_detail(code: str):
    """
    获取股票详情
    
    Path Parameters:
        - code: 股票代码（支持 sz.000001 或 000001 格式）
    
    Returns:
        {
            "success": true,
            "data": {
                "code": str,
                "name": str,
                "price": float,
                "pct_change": float,
                "open": float,
                "high": float,
                "low": float,
                "volume": float,
                "market_cap": float,
                "pick_reason": {
                    "title": str,
                    "content": str,
                    "confidence_score": int
                } | null,
                "key_metrics": {
                    "pe_ratio": float,
                    "pb_ratio": float,
                    "roe": float,
                    "debt_ratio": float
                } | null
            }
        }
    """
    try:
        # 提取代码（不带前缀）
        code_without_prefix = code.split('.')[1] if '.' in code else code
        
        # 获取股票基本信息
        stock_info = db.conn.execute(
            "SELECT name, market FROM stock_basic WHERE code = ?",
            (code_without_prefix,)
        ).fetchone()
        
        if not stock_info:
            return error_response('股票不存在', 'NOT_FOUND', 404)
        
        name, market = stock_info
        
        # 构建完整代码
        full_code = code if '.' in code else f"{market}.{code_without_prefix}"
        
        # 获取日线数据
        df = db.get_daily_data(full_code)
        if df.empty:
            return error_response('暂无数据', 'NO_DATA', 404)
        
        # 获取最新数据
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else latest
        
        # 计算涨跌幅
        pct_change = (float(latest['close']) - float(prev['close'])) / float(prev['close']) if float(prev['close']) > 0 else 0.0
        
        # 获取市值（从market_cap_data表）
        market_cap = 0.0
        try:
            market_cap_info = db.conn.execute("""
                SELECT total_cap
                FROM market_cap_data
                WHERE code = ?
                ORDER BY date DESC
                LIMIT 1
            """, (code_without_prefix,)).fetchone()
            
            if market_cap_info and market_cap_info[0]:
                market_cap = float(market_cap_info[0])
        except Exception as e:
            logger.debug(f"获取市值失败: {e}")
        
        # 检查是否在今日精选中（从数据库读取，不重新扫描）
        pick_reason = None
        try:
            picks = get_picks_from_database(max_picks=50)
            for pick in picks:
                if pick['code'] == full_code or pick['code'] == code:
                    pick_reason = {
                        'title': pick['strategy_name'],
                        'content': pick['reason'],
                        'confidence_score': pick['confidence_score']
                    }
                    break
        except Exception as e:
            logger.debug(f"获取选股理由失败: {e}")
        
        # 获取财务指标
        key_metrics = None
        try:
            financial_data = db.conn.execute("""
                SELECT pe_ratio, pb_ratio, roe, debt_to_asset_ratio
                FROM financial_indicators
                WHERE code = ?
                ORDER BY report_date DESC
                LIMIT 1
            """, (code_without_prefix,)).fetchone()
            
            if financial_data:
                key_metrics = {
                    'pe_ratio': float(financial_data[0]) if financial_data[0] else 0.0,
                    'pb_ratio': float(financial_data[1]) if financial_data[1] else 0.0,
                    'roe': float(financial_data[2]) if financial_data[2] else 0.0,
                    'debt_ratio': float(financial_data[3]) if financial_data[3] else 0.0
                }
        except Exception as e:
            logger.debug(f"获取财务指标失败: {e}")
        
        # 构建响应
        result = {
            'code': full_code,
            'name': name,
            'price': float(latest['close']),
            'pct_change': pct_change,
            'open': float(latest['open']),
            'high': float(latest['high']),
            'low': float(latest['low']),
            'volume': float(latest['volume']),
            'market_cap': market_cap,
            'pick_reason': pick_reason,
            'key_metrics': key_metrics
        }
        
        return success_response(result)
        
    except Exception as e:
        logger.error(f"获取股票详情失败: {e}", exc_info=True)
        friendly_error = make_error_friendly(str(e))
        return error_response(friendly_error, 'FETCH_ERROR', 500)


def calculate_stock_rating(code: str, stock_data: dict, key_metrics: dict) -> dict:
    """
    计算股票综合评价
    
    Args:
        code: 股票代码
        stock_data: 股票基本数据（价格、成交量等）
        key_metrics: 关键财务指标
        
    Returns:
        评价字典，包含评分、优点、缺点、建议等
    """
    try:
        score = 50  # 基础分50分
        pros = []  # 优点列表
        cons = []  # 缺点列表
        
        # 1. 评估财务指标（40分）
        if key_metrics:
            # PE市盈率评估（10分）
            pe = key_metrics.get('pe_ratio', 0)
            if 0 < pe < 15:
                score += 10
                pros.append(f"估值较低（PE {pe:.1f}倍）")
            elif 15 <= pe < 30:
                score += 5
                pros.append(f"估值合理（PE {pe:.1f}倍）")
            elif pe >= 30:
                cons.append(f"估值偏高（PE {pe:.1f}倍）")
            
            # PB市净率评估（10分）
            pb = key_metrics.get('pb_ratio', 0)
            if 0 < pb < 1:
                score += 10
                pros.append(f"破净股（PB {pb:.2f}）")
            elif 1 <= pb < 3:
                score += 5
                pros.append(f"市净率健康（PB {pb:.2f}）")
            elif pb >= 3:
                cons.append(f"市净率偏高（PB {pb:.2f}）")
            
            # ROE净资产收益率评估（10分）
            roe = key_metrics.get('roe', 0)
            if roe > 15:  # ROE > 15%
                score += 10
                pros.append(f"盈利能力强（ROE {roe:.1f}%）")
            elif roe > 10:  # ROE > 10%
                score += 5
                pros.append(f"盈利能力一般（ROE {roe:.1f}%）")
            elif roe > 0:
                cons.append(f"盈利能力弱（ROE {roe:.1f}%）")
            else:
                cons.append("当前亏损")
            
            # 资产负债率评估（10分）
            debt = key_metrics.get('debt_ratio', 0)
            if debt < 30:  # 负债率 < 30%
                score += 10
                pros.append(f"负债健康（{debt:.1f}%）")
            elif debt < 50:  # 负债率 < 50%
                score += 5
                pros.append(f"负债适中（{debt:.1f}%）")
            elif debt < 70:  # 负债率 < 70%
                cons.append(f"负债偏高（{debt:.1f}%）")
            else:
                cons.append(f"负债很高（{debt:.1f}%）")
        
        # 2. 评估技术指标（30分）
        # 获取最近数据计算技术指标
        code_without_prefix = code.split('.')[1] if '.' in code else code
        stock_info = db.conn.execute(
            "SELECT market FROM stock_basic WHERE code = ?",
            (code_without_prefix,)
        ).fetchone()
        
        if stock_info:
            market = stock_info[0]
            full_code = code if '.' in code else f"{market}.{code_without_prefix}"
            df = db.get_daily_data(full_code)
            
            if not df.empty and len(df) >= 20:
                df = df.sort_values('date').tail(20)
                
                # 计算均线
                df['ma5'] = df['close'].rolling(window=5).mean()
                df['ma20'] = df['close'].rolling(window=20).mean()
                latest = df.iloc[-1]
                
                # 均线趋势（15分）
                if latest['ma5'] > latest['ma20']:
                    score += 15
                    pros.append("短期趋势向上（金叉）")
                elif latest['ma5'] < latest['ma20'] * 0.95:
                    cons.append("短期趋势向下（死叉）")
                else:
                    score += 5
                    pros.append("趋势震荡")
                
                # 成交量评估（15分）
                avg_volume = df['volume'].tail(5).mean()
                if avg_volume > 0:
                    volume_ratio = float(latest['volume']) / avg_volume
                    if volume_ratio > 1.5:
                        score += 15
                        pros.append(f"成交活跃（放量{volume_ratio:.1f}倍）")
                    elif volume_ratio > 0.8:
                        score += 8
                    else:
                        cons.append("成交量萎缩")
        
        # 3. 涨跌幅评估（20分）
        pct_change = stock_data.get('pct_change', 0)
        if -0.03 < pct_change < 0.03:
            score += 10
            pros.append("价格稳定")
        elif 0.03 <= pct_change < 0.07:
            score += 15
            pros.append(f"温和上涨（+{pct_change*100:.1f}%）")
        elif pct_change >= 0.07:
            score += 5
            cons.append(f"短期涨幅较大（+{pct_change*100:.1f}%）")
        elif pct_change < -0.05:
            cons.append(f"短期跌幅较大（{pct_change*100:.1f}%）")
        
        # 确保分数在0-100之间
        score = max(0, min(100, score))
        
        # 生成星级（1-5星）
        stars = max(1, min(5, int(score / 20) + 1))
        
        # 生成投资建议
        if score >= 80:
            suggestion = "综合表现优秀，适合中长线持有"
            risk_level = "较低"
        elif score >= 60:
            suggestion = "综合表现良好，可适量配置"
            risk_level = "中等"
        elif score >= 40:
            suggestion = "综合表现一般，建议观望"
            risk_level = "中等"
        else:
            suggestion = "综合表现较弱，谨慎参与"
            risk_level = "较高"
        
        return {
            'score': score,
            'stars': stars,
            'pros': pros[:5],  # 最多5个优点
            'cons': cons[:5],  # 最多5个缺点
            'suggestion': suggestion,
            'risk_level': risk_level
        }
        
    except Exception as e:
        logger.error(f"计算股票评价失败: {e}", exc_info=True)
        # 返回默认评价
        return {
            'score': 50,
            'stars': 3,
            'pros': [],
            'cons': [],
            'suggestion': '暂无足够数据进行评价',
            'risk_level': '未知'
        }


@api_bp.route('/picker/stocks/<code>/rating', methods=['GET'])
def get_stock_rating(code: str):
    """
    获取股票综合评价
    
    Path Parameters:
        - code: 股票代码（支持 sz.000001 或 000001 格式）
    
    Returns:
        {
            "success": true,
            "data": {
                "score": int,  // 综合评分 0-100
                "stars": int,  // 星级 1-5
                "pros": [str],  // 优点列表
                "cons": [str],  // 缺点列表
                "suggestion": str,  // 投资建议
                "risk_level": str  // 风险等级
            }
        }
    """
    try:
        # 提取代码（不带前缀）
        code_without_prefix = code.split('.')[1] if '.' in code else code
        
        # 获取股票基本信息
        stock_info = db.conn.execute(
            "SELECT name, market FROM stock_basic WHERE code = ?",
            (code_without_prefix,)
        ).fetchone()
        
        if not stock_info:
            return error_response('股票不存在', 'NOT_FOUND', 404)
        
        name, market = stock_info
        full_code = code if '.' in code else f"{market}.{code_without_prefix}"
        
        # 获取日线数据
        df = db.get_daily_data(full_code)
        if df.empty:
            return error_response('暂无数据', 'NO_DATA', 404)
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else latest
        
        # 构建股票数据
        stock_data = {
            'price': float(latest['close']),
            'pct_change': (float(latest['close']) - float(prev['close'])) / float(prev['close']) if float(prev['close']) > 0 else 0.0,
            'volume': float(latest['volume'])
        }
        
        # 获取财务指标（从真实数据库）
        key_metrics = None
        try:
            financial_data = db.conn.execute("""
                SELECT pe_ratio, pb_ratio, roe, debt_to_asset_ratio
                FROM financial_indicators
                WHERE code = ?
                ORDER BY report_date DESC
                LIMIT 1
            """, (code_without_prefix,)).fetchone()
            
            if financial_data:
                key_metrics = {
                    'pe_ratio': float(financial_data[0]) if financial_data[0] else 0.0,
                    'pb_ratio': float(financial_data[1]) if financial_data[1] else 0.0,
                    'roe': float(financial_data[2]) if financial_data[2] else 0.0,
                    'debt_ratio': float(financial_data[3]) if financial_data[3] else 0.0
                }
        except Exception as e:
            logger.debug(f"获取财务指标失败: {e}")
        
        # 计算评价
        rating = calculate_stock_rating(code, stock_data, key_metrics)
        
        return success_response(rating)
        
    except Exception as e:
        logger.error(f"获取股票评价失败: {e}", exc_info=True)
        friendly_error = make_error_friendly(str(e))
        return error_response(friendly_error, 'FETCH_ERROR', 500)


@api_bp.route('/picker/stocks/<code>/kline', methods=['GET'])
def get_picker_stock_kline(code: str):
    """
    获取股票K线数据
    
    Path Parameters:
        - code: 股票代码（支持 sz.000001 或 000001 格式）
    
    Query Parameters:
        - period: 时间周期，可选值: 1m(1个月), 3m(3个月), 6m(6个月), 1y(1年), 默认3m
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "date": str,
                    "open": float,
                    "high": float,
                    "low": float,
                    "close": float,
                    "volume": float
                },
                ...
            ]
        }
    """
    try:
        from datetime import datetime, timedelta
        
        # 获取时间周期参数
        period = request.args.get('period', '3m')
        
        # 计算起始日期
        end_date = datetime.now()
        if period == '1m':
            start_date = end_date - timedelta(days=30)
        elif period == '6m':
            start_date = end_date - timedelta(days=180)
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
        else:  # 默认3m
            start_date = end_date - timedelta(days=90)
        
        # 提取代码（不带前缀）
        code_without_prefix = code.split('.')[1] if '.' in code else code
        
        # 获取股票基本信息
        stock_info = db.conn.execute(
            "SELECT name, market FROM stock_basic WHERE code = ?",
            (code_without_prefix,)
        ).fetchone()
        
        if not stock_info:
            return error_response('股票不存在', 'NOT_FOUND', 404)
        
        name, market = stock_info
        
        # 构建完整代码
        full_code = code if '.' in code else f"{market}.{code_without_prefix}"
        
        # 获取日线数据
        df = db.get_daily_data(full_code)
        if df.empty:
            return error_response('暂无数据', 'NO_DATA', 404)
        
        # 过滤日期范围
        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'] >= start_date]
        df = df.sort_values('date')
        
        # 去重：如果有重复日期，保留最新的数据
        df = df.drop_duplicates(subset=['date'], keep='last')
        
        # 转换为前端需要的格式
        kline_data = []
        for _, row in df.iterrows():
            kline_data.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })
        
        return success_response(kline_data)
        
    except Exception as e:
        logger.error(f"获取K线数据失败: {e}", exc_info=True)
        friendly_error = make_error_friendly(str(e))
        return error_response(friendly_error, 'FETCH_ERROR', 500)

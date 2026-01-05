"""
策略管理API路由
"""
from flask import request, jsonify
from . import api_bp
from src.data.database_adapter import DatabaseAdapter
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.business.strategies.ma_crossover import MACrossoverStrategy
from src.web.utils.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# 初始化数据库连接（使用新的适配器）
db = DatabaseAdapter()

# 策略注册表 - 定义所有可用策略
STRATEGY_REGISTRY = {
    'volume_shrink': {
        'id': 'volume_shrink',
        'name': '缩量三连跌（稳健版）',
        'type': 'technical',
        'description': '寻找连续下跌后放量企稳的股票，适合短线反弹交易',
        'class': VolumeShrinkStrategy,
        'params': [
            {
                'name': 'min_cap',
                'label': '最小市值（亿元）',
                'type': 'number',
                'default': 50,
                'min': 10,
                'max': 1000,
                'description': '股票池最小市值筛选'
            },
            {
                'name': 'max_cap',
                'label': '最大市值（亿元）',
                'type': 'number',
                'default': 200,
                'min': 50,
                'max': 5000,
                'description': '股票池最大市值筛选'
            },
            {
                'name': 'min_decline',
                'label': '最小跌幅',
                'type': 'number',
                'default': 0.10,
                'min': 0.05,
                'max': 0.30,
                'description': '触发信号的最小跌幅（如0.10表示10%）'
            },
            {
                'name': 'use_volume_stabilize',
                'label': '使用放量企稳逻辑',
                'type': 'boolean',
                'default': True,
                'description': '启用后使用稳健版逻辑（放量企稳），否则使用激进版（缩量）'
            },
            {
                'name': 'check_market',
                'label': '检查市场环境',
                'type': 'boolean',
                'default': True,
                'description': '仅在大盘20日均线以上开仓'
            },
            {
                'name': 'min_avg_turnover',
                'label': '最小日均成交额（亿元）',
                'type': 'number',
                'default': 1.0,
                'min': 0.1,
                'max': 10.0,
                'description': '流动性过滤，剔除成交额过低的股票'
            }
        ],
        'default_config': {
            'min_cap': 50,
            'max_cap': 200,
            'min_decline': 0.10,
            'use_volume_stabilize': True,
            'check_market': True,
            'min_avg_turnover': 1.0
        }
    },
    'ma_crossover': {
        'id': 'ma_crossover',
        'name': '均线突破策略',
        'type': 'technical',
        'description': '基于短期均线上穿长期均线的金叉信号，适合趋势跟踪',
        'class': MACrossoverStrategy,
        'params': [
            {
                'name': 'min_cap',
                'label': '最小市值（亿元）',
                'type': 'number',
                'default': 50,
                'min': 10,
                'max': 1000,
                'description': '股票池最小市值筛选'
            },
            {
                'name': 'max_cap',
                'label': '最大市值（亿元）',
                'type': 'number',
                'default': 200,
                'min': 50,
                'max': 5000,
                'description': '股票池最大市值筛选'
            },
            {
                'name': 'short_window',
                'label': '短期均线周期',
                'type': 'number',
                'default': 5,
                'min': 3,
                'max': 20,
                'description': '短期移动平均线的天数'
            },
            {
                'name': 'long_window',
                'label': '长期均线周期',
                'type': 'number',
                'default': 20,
                'min': 10,
                'max': 60,
                'description': '长期移动平均线的天数'
            },
            {
                'name': 'volume_window',
                'label': '成交量均线周期',
                'type': 'number',
                'default': 5,
                'min': 3,
                'max': 20,
                'description': '成交量移动平均线的天数'
            },
            {
                'name': 'check_volume',
                'label': '检查成交量放大',
                'type': 'boolean',
                'default': True,
                'description': '要求金叉时成交量放大'
            },
            {
                'name': 'min_avg_turnover',
                'label': '最小日均成交额（亿元）',
                'type': 'number',
                'default': 1.0,
                'min': 0.1,
                'max': 10.0,
                'description': '流动性过滤，剔除成交额过低的股票'
            }
        ],
        'default_config': {
            'min_cap': 50,
            'max_cap': 200,
            'short_window': 5,
            'long_window': 20,
            'volume_window': 5,
            'check_volume': True,
            'min_avg_turnover': 1.0
        }
    }
}


@api_bp.route('/strategies', methods=['GET'])
def get_strategy_list():
    """
    获取策略列表
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "id": str,
                    "name": str,
                    "type": str,
                    "description": str,
                    "params": [...]
                },
                ...
            ]
        }
    """
    try:
        # 构建策略列表（不包含class字段）
        strategies = []
        for strategy_id, strategy_info in STRATEGY_REGISTRY.items():
            strategies.append({
                'id': strategy_info['id'],
                'name': strategy_info['name'],
                'type': strategy_info['type'],
                'description': strategy_info['description'],
                'params': strategy_info['params']
            })
        
        return success_response(strategies)
        
    except Exception as e:
        logger.error(f"获取策略列表失败: {e}", exc_info=True)
        return error_response('获取策略列表失败', 'FETCH_ERROR', 500)



@api_bp.route('/strategies/<strategy_id>', methods=['GET'])
def get_strategy_detail(strategy_id: str):
    """
    获取策略详情
    
    Path Parameters:
        - strategy_id: 策略ID
    
    Returns:
        {
            "success": true,
            "data": {
                "id": str,
                "name": str,
                "type": str,
                "description": str,
                "params": [...],
                "default_config": {...}
            }
        }
    """
    try:
        # 检查策略是否存在
        if strategy_id not in STRATEGY_REGISTRY:
            return error_response(
                f'策略 {strategy_id} 不存在',
                'STRATEGY_NOT_FOUND',
                404
            )
        
        strategy_info = STRATEGY_REGISTRY[strategy_id]
        
        # 构建响应（不包含class字段）
        strategy_detail = {
            'id': strategy_info['id'],
            'name': strategy_info['name'],
            'type': strategy_info['type'],
            'description': strategy_info['description'],
            'params': strategy_info['params'],
            'default_config': strategy_info['default_config']
        }
        
        return success_response(strategy_detail)
        
    except Exception as e:
        logger.error(f"获取策略详情失败: {e}", exc_info=True)
        return error_response('获取策略详情失败', 'FETCH_ERROR', 500)


@api_bp.route('/strategies/<strategy_id>/config', methods=['GET'])
def get_strategy_config(strategy_id: str):
    """
    获取策略配置
    
    Path Parameters:
        - strategy_id: 策略ID
    
    Returns:
        {
            "success": true,
            "data": {
                "config": {...}
            }
        }
    """
    try:
        # 检查策略是否存在
        if strategy_id not in STRATEGY_REGISTRY:
            return error_response(
                f'策略 {strategy_id} 不存在',
                'STRATEGY_NOT_FOUND',
                404
            )
        
        strategy_info = STRATEGY_REGISTRY[strategy_id]
        
        # 返回默认配置（实际应用中应该从数据库或配置文件读取用户自定义配置）
        config = strategy_info['default_config'].copy()
        
        return success_response({'config': config})
        
    except Exception as e:
        logger.error(f"获取策略配置失败: {e}", exc_info=True)
        return error_response('获取策略配置失败', 'FETCH_ERROR', 500)


@api_bp.route('/strategies/<strategy_id>/config', methods=['PUT'])
def update_strategy_config(strategy_id: str):
    """
    更新策略配置
    
    Path Parameters:
        - strategy_id: 策略ID
    
    Request Body:
        {
            "config": {
                "min_cap": 50,
                "max_cap": 200,
                ...
            }
        }
    
    Returns:
        {
            "success": true,
            "message": "配置更新成功"
        }
    """
    try:
        # 检查策略是否存在
        if strategy_id not in STRATEGY_REGISTRY:
            return error_response(
                f'策略 {strategy_id} 不存在',
                'STRATEGY_NOT_FOUND',
                404
            )
        
        # 获取请求数据
        data = request.get_json()
        if not data or 'config' not in data:
            return error_response(
                '请求数据格式错误，需要包含config字段',
                'INVALID_REQUEST',
                400
            )
        
        config = data['config']
        strategy_info = STRATEGY_REGISTRY[strategy_id]
        
        # 验证配置参数
        validation_errors = []
        for param in strategy_info['params']:
            param_name = param['name']
            
            # 如果配置中包含该参数，进行验证
            if param_name in config:
                value = config[param_name]
                param_type = param['type']
                
                # 类型验证
                if param_type == 'number':
                    if not isinstance(value, (int, float)):
                        validation_errors.append(f"{param['label']}必须是数字")
                        continue
                    
                    # 范围验证
                    if 'min' in param and value < param['min']:
                        validation_errors.append(
                            f"{param['label']}不能小于{param['min']}"
                        )
                    if 'max' in param and value > param['max']:
                        validation_errors.append(
                            f"{param['label']}不能大于{param['max']}"
                        )
                
                elif param_type == 'boolean':
                    if not isinstance(value, bool):
                        validation_errors.append(f"{param['label']}必须是布尔值")
                
                elif param_type == 'string':
                    if not isinstance(value, str):
                        validation_errors.append(f"{param['label']}必须是字符串")
                
                elif param_type == 'select':
                    if 'options' in param:
                        valid_values = [opt['value'] for opt in param['options']]
                        if value not in valid_values:
                            validation_errors.append(
                                f"{param['label']}必须是以下值之一: {', '.join(map(str, valid_values))}"
                            )
        
        # 如果有验证错误，返回错误信息
        if validation_errors:
            return error_response(
                '配置参数验证失败: ' + '; '.join(validation_errors),
                'VALIDATION_ERROR',
                400
            )
        
        # 实际应用中应该将配置保存到数据库或配置文件
        # 这里只是简单返回成功
        logger.info(f"策略 {strategy_id} 配置已更新: {config}")
        
        return success_response({
            'message': '配置更新成功',
            'config': config
        })
        
    except Exception as e:
        logger.error(f"更新策略配置失败: {e}", exc_info=True)
        return error_response('更新策略配置失败', 'UPDATE_ERROR', 500)


import uuid
import threading
from datetime import datetime
from src.business.backtest.engine import BacktestEngine
from src.config.settings import BacktestConfig

# 简单的任务存储（实际应用中应该使用Redis或数据库）
backtest_tasks = {}
backtest_tasks_lock = threading.Lock()


def run_backtest_task(task_id: str, strategy_id: str, config: dict):
    """
    在后台线程中运行回测任务
    
    Args:
        task_id: 任务ID
        strategy_id: 策略ID
        config: 回测配置
    """
    try:
        # 更新任务状态为运行中
        with backtest_tasks_lock:
            backtest_tasks[task_id]['status'] = 'running'
            backtest_tasks[task_id]['started_at'] = datetime.now().isoformat()
        
        # 获取策略类
        strategy_info = STRATEGY_REGISTRY[strategy_id]
        strategy_class = strategy_info['class']
        
        # 创建策略实例
        # 注意：策略构造函数只接受特定参数，其他参数在scan()时传入
        strategy_config = config.get('strategy_config', {})
        
        # 根据策略类型提取构造函数参数
        if strategy_id == 'volume_shrink':
            # VolumeShrinkStrategy只接受market_index_code和min_avg_turnover
            strategy_params = {
                'min_avg_turnover': strategy_config.get('min_avg_turnover', 1e8)
            }
        elif strategy_id == 'ma_crossover':
            # MACrossoverStrategy接受均线参数
            strategy_params = {
                'short_window': strategy_config.get('short_window', 5),
                'long_window': strategy_config.get('long_window', 20),
                'volume_window': strategy_config.get('volume_window', 5),
                'min_avg_turnover': strategy_config.get('min_avg_turnover', 1e8)
            }
        else:
            strategy_params = {}
        
        # 初始化策略
        strategy = strategy_class(db, **strategy_params)
        
        # 包装scan方法以传入配置参数
        original_scan = strategy.scan
        
        def wrapped_scan(date=None, max_stocks=None, **kwargs):
            # 合并策略配置和kwargs
            scan_params = strategy_config.copy()
            scan_params.update(kwargs)
            # 移除构造函数参数（已经在初始化时使用）
            for key in strategy_params.keys():
                scan_params.pop(key, None)
            
            # 转换市值单位：从亿元转换为元
            if 'min_cap' in scan_params:
                scan_params['min_cap'] = scan_params['min_cap'] * 1e8
            if 'max_cap' in scan_params:
                scan_params['max_cap'] = scan_params['max_cap'] * 1e8
            
            return original_scan(date=date, max_stocks=max_stocks, **scan_params)
        
        strategy.scan = wrapped_scan
        
        # 创建回测配置
        backtest_config = BacktestConfig(
            initial_capital=config.get('initial_capital', 1000000),
            commission_rate=config.get('commission_rate', 0.0003),
            slippage_rate=config.get('slippage_rate', 0.001),
            max_positions=config.get('max_positions', 5),
            position_size=config.get('position_size', 0.2)
        )
        
        # 创建回测引擎
        engine = BacktestEngine(db, strategy, config=backtest_config)
        
        # 运行回测
        result = engine.run(
            start_date=config['start_date'],
            end_date=config['end_date'],
            hold_days=config.get('hold_days', 5),
            stop_loss=config.get('stop_loss', -0.10),
            take_profit=config.get('take_profit', 0.15),
            scan_interval=config.get('scan_interval', 1),
            time_stop_days=config.get('time_stop_days', 3)
        )
        
        # 处理回测结果
        if 'trades' in result:
            result['trades'] = result['trades'].to_dict('records')
        if 'daily_values' in result:
            result['daily_values'] = result['daily_values'].to_dict('records')
        
        # 保存回测结果到数据库
        backtest_data = {
            'id': task_id,
            'strategy_id': strategy_id,
            'strategy_name': STRATEGY_REGISTRY[strategy_id]['name'],
            'config': config,
            'start_date': config['start_date'],
            'end_date': config['end_date'],
            'initial_capital': result.get('initial_capital'),
            'final_value': result.get('final_value'),
            'total_return': result.get('total_return'),
            'total_profit': result.get('total_profit'),
            'max_drawdown': result.get('max_drawdown'),
            'total_trades': result.get('total_trades'),
            'completed_trades': result.get('completed_trades'),
            'win_trades': result.get('win_trades'),
            'loss_trades': result.get('loss_trades'),
            'win_rate': result.get('win_rate'),
            'avg_profit': result.get('avg_profit'),
            'avg_profit_rate': result.get('avg_profit_rate'),
            'max_profit': result.get('max_profit'),
            'max_loss': result.get('max_loss'),
            'avg_hold_days': result.get('avg_hold_days'),
            'daily_values': result.get('daily_values', []),
            'trades': result.get('trades', []),
            'status': 'completed',
            'created_at': backtest_tasks[task_id]['created_at'],
            'completed_at': datetime.now().isoformat()
        }
        
        db.save_backtest_result(backtest_data)
        
        # 更新任务状态为完成
        with backtest_tasks_lock:
            backtest_tasks[task_id]['status'] = 'completed'
            backtest_tasks[task_id]['completed_at'] = datetime.now().isoformat()
            backtest_tasks[task_id]['result'] = result
        
        logger.info(f"回测任务 {task_id} 完成")
        
    except Exception as e:
        logger.error(f"回测任务 {task_id} 失败: {e}", exc_info=True)
        
        # 保存失败的回测记录到数据库
        with backtest_tasks_lock:
            task = backtest_tasks[task_id]
        
        backtest_data = {
            'id': task_id,
            'strategy_id': strategy_id,
            'strategy_name': STRATEGY_REGISTRY[strategy_id]['name'],
            'config': config,
            'start_date': config['start_date'],
            'end_date': config['end_date'],
            'initial_capital': config.get('initial_capital', 1000000),
            'status': 'failed',
            'created_at': task['created_at'],
            'completed_at': datetime.now().isoformat(),
            'error_message': str(e)
        }
        
        db.save_backtest_result(backtest_data)
        
        # 更新任务状态为失败
        with backtest_tasks_lock:
            backtest_tasks[task_id]['status'] = 'failed'
            backtest_tasks[task_id]['completed_at'] = datetime.now().isoformat()
            backtest_tasks[task_id]['error'] = str(e)


@api_bp.route('/strategies/<strategy_id>/backtest', methods=['POST'])
def run_backtest(strategy_id: str):
    """
    执行回测
    
    Path Parameters:
        - strategy_id: 策略ID
    
    Request Body:
        {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 1000000,
            "strategy_config": {
                "min_cap": 50,
                "max_cap": 200,
                ...
            },
            "hold_days": 5,
            "stop_loss": -0.10,
            "take_profit": 0.15
        }
    
    Returns:
        {
            "success": true,
            "data": {
                "task_id": str,
                "status": "pending"
            }
        }
    """
    try:
        # 检查策略是否存在
        if strategy_id not in STRATEGY_REGISTRY:
            return error_response(
                f'策略 {strategy_id} 不存在',
                'STRATEGY_NOT_FOUND',
                404
            )
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return error_response(
                '请求数据不能为空',
                'INVALID_REQUEST',
                400
            )
        
        # 验证必需参数
        required_fields = ['start_date', 'end_date']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return error_response(
                f'缺少必需参数: {", ".join(missing_fields)}',
                'MISSING_REQUIRED_FIELDS',
                400
            )
        
        # 验证日期格式
        from src.web.utils.validation import is_valid_date
        if not is_valid_date(data['start_date']):
            return error_response('开始日期格式无效', 'INVALID_DATE', 400)
        if not is_valid_date(data['end_date']):
            return error_response('结束日期格式无效', 'INVALID_DATE', 400)
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务记录
        task = {
            'task_id': task_id,
            'strategy_id': strategy_id,
            'strategy_name': STRATEGY_REGISTRY[strategy_id]['name'],
            'config': data,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'result': None,
            'error': None
        }
        
        with backtest_tasks_lock:
            backtest_tasks[task_id] = task
        
        # 在后台线程中运行回测
        thread = threading.Thread(
            target=run_backtest_task,
            args=(task_id, strategy_id, data)
        )
        thread.daemon = True
        thread.start()
        
        logger.info(f"回测任务 {task_id} 已创建并开始执行")
        
        return success_response({
            'task_id': task_id,
            'status': 'pending',
            'message': '回测任务已创建'
        })
        
    except Exception as e:
        logger.error(f"创建回测任务失败: {e}", exc_info=True)
        return error_response('创建回测任务失败', 'CREATE_TASK_ERROR', 500)


@api_bp.route('/strategies/backtest/<task_id>', methods=['GET'])
def get_backtest_status(task_id: str):
    """
    获取回测任务状态
    
    Path Parameters:
        - task_id: 任务ID
    
    Returns:
        {
            "success": true,
            "data": {
                "task_id": str,
                "status": "pending" | "running" | "completed" | "failed",
                "created_at": str,
                "started_at": str,
                "completed_at": str,
                "result": {...},  # 仅在completed状态时返回
                "error": str      # 仅在failed状态时返回
            }
        }
    """
    try:
        with backtest_tasks_lock:
            if task_id not in backtest_tasks:
                return error_response(
                    f'任务 {task_id} 不存在',
                    'TASK_NOT_FOUND',
                    404
                )
            
            task = backtest_tasks[task_id].copy()
        
        # 构建响应（移除敏感信息）
        response_data = {
            'task_id': task['task_id'],
            'strategy_id': task['strategy_id'],
            'strategy_name': task['strategy_name'],
            'status': task['status'],
            'created_at': task['created_at'],
            'started_at': task['started_at'],
            'completed_at': task['completed_at']
        }
        
        # 根据状态添加额外信息
        if task['status'] == 'completed' and task['result']:
            response_data['result'] = task['result']
        elif task['status'] == 'failed' and task['error']:
            response_data['error'] = task['error']
        
        return success_response(response_data)
        
    except Exception as e:
        logger.error(f"获取回测任务状态失败: {e}", exc_info=True)
        return error_response('获取回测任务状态失败', 'FETCH_ERROR', 500)

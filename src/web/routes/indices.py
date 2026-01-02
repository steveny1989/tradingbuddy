"""
指数数据API路由
"""
from flask import request
from . import api_bp
from src.data.database import StockDatabase
from src.web.utils.response import success_response, error_response
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# 初始化数据库连接
db = StockDatabase()

# 主要指数列表
MAJOR_INDICES = [
    # 国内指数
    {'code': 'sh.000001', 'name': '上证指数', 'table': 'daily_sh_000001', 'available': True},
    {'code': 'sz.399001', 'name': '深证成指', 'table': 'daily_sz_399001', 'available': True},
    {'code': 'sz.399006', 'name': '创业板指', 'table': 'daily_sz_399006', 'available': True},
    {'code': 'sh.000300', 'name': '沪深300', 'table': 'daily_sh_000300', 'available': True},
    
    # 香港指数
    {'code': 'hk.HSI', 'name': '恒生指数', 'table': 'daily_hk_HSI', 'available': True},
    {'code': 'hk.HSCEI', 'name': '国企指数', 'table': 'daily_hk_HSCEI', 'available': True},
    
    # 全球指数
    {'code': 'jp.N225', 'name': '日经225', 'table': 'daily_jp_N225', 'available': True},
    {'code': 'us.DJIA', 'name': '道琼斯', 'table': 'daily_us_DJIA', 'available': True},
    {'code': 'us.SPX', 'name': '标普500', 'table': 'daily_us_SPX', 'available': True},
    {'code': 'us.NDX', 'name': '纳斯达克', 'table': 'daily_us_NDX', 'available': True},
    {'code': 'uk.FTSE', 'name': '英国富时', 'table': 'daily_uk_FTSE', 'available': True},
]


@api_bp.route('/indices', methods=['GET'])
def get_indices():
    """
    获取主要指数的最新行情
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "code": str,
                    "name": str,
                    "close": float,
                    "change": float,
                    "pct_chg": float,
                    "open": float,
                    "high": float,
                    "low": float,
                    "volume": int,
                    "amount": float,
                    "date": str,
                    "available": bool
                },
                ...
            ]
        }
    """
    try:
        indices_data = []
        
        # 处理国内指数
        for index_info in MAJOR_INDICES:
            if not index_info['available'] or not index_info['table']:
                # 不可用的指数，返回占位数据
                indices_data.append({
                    'code': index_info['code'],
                    'name': index_info['name'],
                    'close': 0,
                    'change': 0,
                    'pct_chg': 0,
                    'open': 0,
                    'high': 0,
                    'low': 0,
                    'volume': 0,
                    'amount': 0,
                    'date': '',
                    'available': False
                })
                continue
            
            try:
                # 查询最新两天的数据（用于计算涨跌）
                query = f"""
                    SELECT date, open, close, high, low, volume, amount
                    FROM {index_info['table']}
                    ORDER BY date DESC
                    LIMIT 2
                """
                
                df = pd.read_sql(query, db.conn)
                
                if df.empty:
                    logger.warning(f"指数 {index_info['name']} 无数据")
                    continue
                
                # 最新数据
                latest = df.iloc[0]
                
                # 计算涨跌
                if len(df) > 1:
                    prev_close = df.iloc[1]['close']
                    change = latest['close'] - prev_close
                    pct_chg = (change / prev_close) * 100 if prev_close != 0 else 0
                else:
                    # 如果只有一天数据，用开盘价计算
                    change = latest['close'] - latest['open']
                    pct_chg = (change / latest['open']) * 100 if latest['open'] != 0 else 0
                
                indices_data.append({
                    'code': index_info['code'],
                    'name': index_info['name'],
                    'close': float(latest['close']),
                    'change': float(change),
                    'pct_chg': float(pct_chg),
                    'open': float(latest['open']),
                    'high': float(latest['high']),
                    'low': float(latest['low']),
                    'volume': int(latest['volume']) if latest['volume'] else 0,
                    'amount': float(latest['amount']) if latest['amount'] else 0,
                    'date': latest['date'],
                    'available': True
                })
                
            except Exception as e:
                logger.warning(f"获取指数 {index_info['name']} 数据失败: {e}")
                continue
        
        return success_response(indices_data)
        
    except Exception as e:
        logger.error(f"获取指数数据失败: {e}", exc_info=True)
        return error_response('获取指数数据失败', 'FETCH_ERROR', 500)


@api_bp.route('/indices/<code>', methods=['GET'])
def get_index_detail(code: str):
    """
    获取指定指数的详细信息
    
    Path Parameters:
        - code: 指数代码（如 "sh.000001"）
    
    Query Parameters:
        - start_date: 开始日期（YYYY-MM-DD）
        - end_date: 结束日期（YYYY-MM-DD）
    
    Returns:
        {
            "success": true,
            "data": {
                "code": str,
                "name": str,
                "daily_data": [...]
            }
        }
    """
    try:
        # 查找指数信息
        index_info = None
        for idx in MAJOR_INDICES:
            if idx['code'] == code:
                index_info = idx
                break
        
        if not index_info:
            return error_response(f'未找到指数 {code}', 'INDEX_NOT_FOUND', 404)
        
        # 获取日期参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询
        query = f"SELECT * FROM {index_info['table']}"
        conditions = []
        params = []
        
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY date ASC"
        
        df = pd.read_sql(query, db.conn, params=params)
        
        if df.empty:
            return error_response(
                f'未找到指数 {code} 的数据',
                'DATA_NOT_FOUND',
                404
            )
        
        # 转换为字典列表
        daily_data = df.to_dict('records')
        
        return success_response({
            'code': index_info['code'],
            'name': index_info['name'],
            'daily_data': daily_data
        })
        
    except Exception as e:
        logger.error(f"获取指数详情失败: {e}", exc_info=True)
        return error_response('获取指数详情失败', 'FETCH_ERROR', 500)

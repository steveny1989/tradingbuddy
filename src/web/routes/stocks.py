"""
股票数据API路由
"""
from flask import request
from . import api_bp
from src.data.database import StockDatabase
from src.web.utils.response import success_response, error_response, paginated_response
from src.web.utils.validation import (
    is_valid_stock_code,
    is_valid_date,
    validate_pagination,
    validate_market
)
from src.web.utils.errors import APIError
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# 初始化数据库连接
db = StockDatabase()


@api_bp.route('/stocks', methods=['GET'])
def get_stock_list():
    """
    获取股票列表
    
    Query Parameters:
        - market: 市场筛选 (sh/sz)
        - min_cap: 最小市值（亿元）
        - max_cap: 最大市值（亿元）
        - page: 页码（默认1）
        - page_size: 每页大小（默认50，最大1000）
    
    Returns:
        {
            "success": true,
            "data": [...],
            "pagination": {
                "total": int,
                "page": int,
                "page_size": int,
                "total_pages": int
            }
        }
    """
    try:
        # 获取查询参数
        market = request.args.get('market')
        min_cap = request.args.get('min_cap', type=float)
        max_cap = request.args.get('max_cap', type=float)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 50, type=int)
        
        # 验证参数
        market = validate_market(market)
        page, page_size = validate_pagination(page, page_size)
        
        # 获取股票列表
        df = db.get_stock_list()
        
        if df.empty:
            return paginated_response([], 0, page, page_size)
        
        # 应用市场筛选
        if market:
            df = df[df['market'] == market]
        
        # 应用市值筛选（需要从market_snapshot获取最新市值）
        if min_cap is not None or max_cap is not None:
            # 获取最新市值数据
            try:
                market_data = pd.read_sql(
                    """
                    SELECT code, total_cap 
                    FROM market_snapshot 
                    WHERE date = (SELECT MAX(date) FROM market_snapshot)
                    """,
                    db.conn
                )
                
                if not market_data.empty:
                    # 合并市值数据
                    df = df.merge(market_data, on='code', how='left')
                    
                    # 应用市值筛选（市值单位：亿元）
                    if min_cap is not None:
                        df = df[df['total_cap'] >= min_cap * 100000000]
                    if max_cap is not None:
                        df = df[df['total_cap'] <= max_cap * 100000000]
            except Exception as e:
                logger.warning(f"获取市值数据失败: {e}")
        
        # 计算总数
        total = len(df)
        
        # 应用分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        df_page = df.iloc[start_idx:end_idx]
        
        # 转换为字典列表
        stocks = df_page.to_dict('records')
        
        return paginated_response(stocks, total, page, page_size)
        
    except Exception as e:
        logger.error(f"获取股票列表失败: {e}", exc_info=True)
        return error_response('获取股票列表失败', 'FETCH_ERROR', 500)


@api_bp.route('/stocks/<code>', methods=['GET'])
def get_stock_detail(code: str):
    """
    获取股票详情
    
    Path Parameters:
        - code: 股票代码（如 "600000" 或 "sh.600000"）
    
    Returns:
        {
            "success": true,
            "data": {
                "code": str,
                "name": str,
                "market": str,
                "full_code": str,
                "industry": str,
                "market_cap": float,
                "list_date": str,
                ...
            }
        }
    """
    try:
        # 验证股票代码
        if not is_valid_stock_code(code):
            return error_response('股票代码格式无效', 'INVALID_CODE', 400)
        
        # 标准化代码格式（移除市场前缀）
        if '.' in code:
            code = code.split('.')[1]
        
        # 获取股票基本信息
        df = db.get_stock_list()
        
        if df.empty:
            return error_response('股票数据未初始化', 'DATA_NOT_READY', 503)
        
        stock_info = df[df['code'] == code]
        
        if stock_info.empty:
            return error_response(f'未找到股票 {code}', 'STOCK_NOT_FOUND', 404)
        
        # 转换为字典
        stock_dict = stock_info.iloc[0].to_dict()
        
        # 获取最新市值和行业信息
        try:
            # 获取最新市值
            market_data = pd.read_sql(
                """
                SELECT total_cap, float_cap, pe_ttm, pb, turnover
                FROM market_snapshot 
                WHERE code = ? AND date = (SELECT MAX(date) FROM market_snapshot WHERE code = ?)
                """,
                db.conn,
                params=[code, code]
            )
            
            if not market_data.empty:
                market_dict = market_data.iloc[0].to_dict()
                stock_dict.update(market_dict)
            
            # 获取行业信息（如果有单独的行业表）
            try:
                industry_data = pd.read_sql(
                    "SELECT industry FROM industry_data WHERE code = ?",
                    db.conn,
                    params=[code]
                )
                if not industry_data.empty:
                    stock_dict['industry'] = industry_data.iloc[0]['industry']
            except:
                pass
                
        except Exception as e:
            logger.warning(f"获取股票扩展信息失败: {e}")
        
        # 构建完整代码
        if 'market' in stock_dict and 'full_code' not in stock_dict:
            stock_dict['full_code'] = f"{stock_dict['market']}.{code}"
        
        return success_response(stock_dict)
        
    except Exception as e:
        logger.error(f"获取股票详情失败: {e}", exc_info=True)
        return error_response('获取股票详情失败', 'FETCH_ERROR', 500)


@api_bp.route('/stocks/<code>/daily', methods=['GET'])
def get_stock_daily_data(code: str):
    """
    获取股票日线数据
    
    Path Parameters:
        - code: 股票代码（如 "600000" 或 "sh.600000"）
    
    Query Parameters:
        - start_date: 开始日期（YYYY-MM-DD 或 YYYYMMDD）
        - end_date: 结束日期（YYYY-MM-DD 或 YYYYMMDD）
    
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
                    "volume": int,
                    "amount": float,
                    "pct_chg": float,
                    "turnover": float
                },
                ...
            ]
        }
    """
    try:
        # 验证股票代码
        if not is_valid_stock_code(code):
            return error_response('股票代码格式无效', 'INVALID_CODE', 400)
        
        # 标准化代码格式
        if '.' in code:
            market, stock_code = code.split('.')
            full_code = code
        else:
            stock_code = code
            # 尝试从数据库获取市场信息
            df_stocks = db.get_stock_list()
            if not df_stocks.empty:
                stock_row = df_stocks[df_stocks['code'] == stock_code]
                if not stock_row.empty:
                    market = stock_row.iloc[0]['market']
                    full_code = f"{market}.{stock_code}"
                else:
                    return error_response(f'未找到股票 {code}', 'STOCK_NOT_FOUND', 404)
            else:
                return error_response('股票数据未初始化', 'DATA_NOT_READY', 503)
        
        # 获取日期参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 验证日期格式
        if start_date and not is_valid_date(start_date):
            return error_response('开始日期格式无效', 'INVALID_DATE', 400)
        
        if end_date and not is_valid_date(end_date):
            return error_response('结束日期格式无效', 'INVALID_DATE', 400)
        
        # 标准化日期格式为 YYYY-MM-DD
        if start_date and len(start_date) == 8:
            start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        
        if end_date and len(end_date) == 8:
            end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        # 获取日线数据
        df = db.get_daily_data(full_code, start_date, end_date)
        
        if df.empty:
            return error_response(
                f'未找到股票 {code} 的数据',
                'DATA_NOT_FOUND',
                404
            )
        
        # 转换为字典列表
        data = df.to_dict('records')
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"获取日线数据失败: {e}", exc_info=True)
        return error_response('获取日线数据失败', 'FETCH_ERROR', 500)


@api_bp.route('/stocks/<code>/indicators', methods=['GET'])
def get_stock_indicators(code: str):
    """
    获取股票技术指标
    
    Path Parameters:
        - code: 股票代码（如 "600000" 或 "sh.600000"）
    
    Query Parameters:
        - indicators: 指标列表（逗号分隔，如 "ma5,ma10,ma20,ma60"）
        - start_date: 开始日期（YYYY-MM-DD 或 YYYYMMDD）
        - end_date: 结束日期（YYYY-MM-DD 或 YYYYMMDD）
    
    Returns:
        {
            "success": true,
            "data": [
                {
                    "date": str,
                    "ma5": float,
                    "ma10": float,
                    "ma20": float,
                    "ma60": float
                },
                ...
            ]
        }
    """
    try:
        # 验证股票代码
        if not is_valid_stock_code(code):
            return error_response('股票代码格式无效', 'INVALID_CODE', 400)
        
        # 标准化代码格式
        if '.' in code:
            market, stock_code = code.split('.')
            full_code = code
        else:
            stock_code = code
            # 尝试从数据库获取市场信息
            df_stocks = db.get_stock_list()
            if not df_stocks.empty:
                stock_row = df_stocks[df_stocks['code'] == stock_code]
                if not stock_row.empty:
                    market = stock_row.iloc[0]['market']
                    full_code = f"{market}.{stock_code}"
                else:
                    return error_response(f'未找到股票 {code}', 'STOCK_NOT_FOUND', 404)
            else:
                return error_response('股票数据未初始化', 'DATA_NOT_READY', 503)
        
        # 获取参数
        indicators_str = request.args.get('indicators', 'ma5,ma10,ma20,ma60')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 解析指标列表
        indicators = [ind.strip().lower() for ind in indicators_str.split(',')]
        
        # 验证指标
        valid_indicators = ['ma5', 'ma10', 'ma20', 'ma60']
        indicators = [ind for ind in indicators if ind in valid_indicators]
        
        if not indicators:
            return error_response('未指定有效的技术指标', 'INVALID_INDICATORS', 400)
        
        # 验证日期格式
        if start_date and not is_valid_date(start_date):
            return error_response('开始日期格式无效', 'INVALID_DATE', 400)
        
        if end_date and not is_valid_date(end_date):
            return error_response('结束日期格式无效', 'INVALID_DATE', 400)
        
        # 标准化日期格式
        if start_date and len(start_date) == 8:
            start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        
        if end_date and len(end_date) == 8:
            end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
        
        # 获取日线数据（需要额外的数据来计算MA）
        # 为了计算MA60，需要至少60天的数据
        max_period = max([int(ind[2:]) for ind in indicators])
        
        # 获取足够的历史数据
        df = db.get_daily_data(full_code)
        
        if df.empty:
            return error_response(
                f'未找到股票 {code} 的数据',
                'DATA_NOT_FOUND',
                404
            )
        
        # 确保数据按日期排序
        df = df.sort_values('date')
        
        # 计算移动平均线
        for indicator in indicators:
            period = int(indicator[2:])  # 提取周期数（如 ma5 -> 5）
            df[indicator] = df['close'].rolling(window=period, min_periods=1).mean()
        
        # 应用日期筛选
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]
        
        # 只返回日期和指标列
        columns = ['date'] + indicators
        df_result = df[columns]
        
        # 转换为字典列表
        data = df_result.to_dict('records')
        
        return success_response(data)
        
    except Exception as e:
        logger.error(f"获取技术指标失败: {e}", exc_info=True)
        return error_response('获取技术指标失败', 'FETCH_ERROR', 500)

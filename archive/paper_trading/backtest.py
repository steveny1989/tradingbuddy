"""
回测结果API路由
"""
from flask import request
from . import api_bp
from src.data.database import StockDatabase
from src.web.utils.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)

# 初始化数据库连接
db = StockDatabase()


@api_bp.route('/backtest', methods=['GET'])
def get_backtest_list():
    """
    获取回测历史列表
    
    Query Parameters:
        - page: 页码（默认1）
        - page_size: 每页数量（默认20）
        - strategy_id: 策略ID筛选（可选）
        - sort_by: 排序字段（默认created_at）
        - sort_order: 排序方向（asc/desc，默认desc）
    
    Returns:
        {
            "success": true,
            "data": {
                "items": [
                    {
                        "id": str,
                        "strategy_id": str,
                        "strategy_name": str,
                        "start_date": str,
                        "end_date": str,
                        "initial_capital": float,
                        "final_value": float,
                        "total_return": float,
                        "max_drawdown": float,
                        "total_trades": int,
                        "win_rate": float,
                        "created_at": str,
                        "status": str
                    },
                    ...
                ],
                "total": int,
                "page": int,
                "page_size": int,
                "total_pages": int
            }
        }
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        strategy_id = request.args.get('strategy_id', None, type=str)
        sort_by = request.args.get('sort_by', 'created_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)
        
        # 验证参数
        if page < 1:
            return error_response('页码必须大于0', 'INVALID_PAGE', 400)
        if page_size < 1 or page_size > 100:
            return error_response('每页数量必须在1-100之间', 'INVALID_PAGE_SIZE', 400)
        if sort_order not in ['asc', 'desc']:
            return error_response('排序方向必须是asc或desc', 'INVALID_SORT_ORDER', 400)
        
        # 允许的排序字段
        allowed_sort_fields = [
            'created_at', 'start_date', 'end_date', 'total_return',
            'max_drawdown', 'total_trades', 'win_rate'
        ]
        if sort_by not in allowed_sort_fields:
            return error_response(
                f'排序字段必须是以下之一: {", ".join(allowed_sort_fields)}',
                'INVALID_SORT_FIELD',
                400
            )
        
        # 获取回测列表
        backtest_list = db.get_backtest_list(
            page=page,
            page_size=page_size,
            strategy_id=strategy_id,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return success_response(backtest_list)
        
    except Exception as e:
        logger.error(f"获取回测列表失败: {e}", exc_info=True)
        return error_response('获取回测列表失败', 'FETCH_ERROR', 500)


@api_bp.route('/backtest/<backtest_id>', methods=['GET'])
def get_backtest_detail(backtest_id: str):
    """
    获取回测详情
    
    Path Parameters:
        - backtest_id: 回测ID
    
    Returns:
        {
            "success": true,
            "data": {
                "id": str,
                "strategy_id": str,
                "strategy_name": str,
                "config": {...},
                "start_date": str,
                "end_date": str,
                "initial_capital": float,
                "final_value": float,
                "total_return": float,
                "total_profit": float,
                "max_drawdown": float,
                "total_trades": int,
                "completed_trades": int,
                "win_trades": int,
                "loss_trades": int,
                "win_rate": float,
                "avg_profit": float,
                "avg_profit_rate": float,
                "max_profit": float,
                "max_loss": float,
                "avg_hold_days": float,
                "daily_values": [...],
                "trades": [...],
                "created_at": str,
                "completed_at": str,
                "status": str
            }
        }
    """
    try:
        # 获取回测详情
        backtest = db.get_backtest_detail(backtest_id)
        
        if not backtest:
            return error_response(
                f'回测记录 {backtest_id} 不存在',
                'BACKTEST_NOT_FOUND',
                404
            )
        
        return success_response(backtest)
        
    except Exception as e:
        logger.error(f"获取回测详情失败: {e}", exc_info=True)
        return error_response('获取回测详情失败', 'FETCH_ERROR', 500)


@api_bp.route('/backtest/<backtest_id>/export', methods=['GET'])
def export_backtest_trades(backtest_id: str):
    """
    导出回测交易记录为CSV
    
    Path Parameters:
        - backtest_id: 回测ID
    
    Returns:
        CSV文件下载
    """
    try:
        # 获取回测详情
        backtest = db.get_backtest_detail(backtest_id)
        
        if not backtest:
            return error_response(
                f'回测记录 {backtest_id} 不存在',
                'BACKTEST_NOT_FOUND',
                404
            )
        
        # 获取交易记录
        trades = backtest.get('trades', [])
        
        if not trades:
            return error_response(
                '该回测没有交易记录',
                'NO_TRADES',
                404
            )
        
        # 生成CSV内容
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        headers = [
            '日期', '股票代码', '操作', '价格', '数量', '金额',
            '成本价', '盈亏', '盈亏率', '持有天数', '原因'
        ]
        writer.writerow(headers)
        
        # 写入数据
        for trade in trades:
            row = [
                trade.get('date', ''),
                trade.get('code', ''),
                '买入' if trade.get('action') == 'buy' else '卖出',
                f"{trade.get('price', 0):.2f}",
                trade.get('shares', 0),
                f"{trade.get('amount', 0):.2f}",
                f"{trade.get('cost_price', 0):.2f}" if trade.get('action') == 'sell' else '',
                f"{trade.get('profit', 0):.2f}" if trade.get('action') == 'sell' else '',
                f"{trade.get('profit_rate', 0):.2%}" if trade.get('action') == 'sell' else '',
                trade.get('hold_days', '') if trade.get('action') == 'sell' else '',
                trade.get('reason', '')
            ]
            writer.writerow(row)
        
        # 创建响应
        from flask import make_response
        
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        response.headers['Content-Disposition'] = f'attachment; filename=backtest_{backtest_id}_trades.csv'
        
        return response
        
    except Exception as e:
        logger.error(f"导出交易记录失败: {e}", exc_info=True)
        return error_response('导出交易记录失败', 'EXPORT_ERROR', 500)

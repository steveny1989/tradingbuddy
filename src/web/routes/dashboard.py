"""
仪表板API路由
"""
from flask import jsonify
from . import api_bp
from src.data.database import StockDatabase
from src.web.utils.response import success_response, error_response
import logging
import os

logger = logging.getLogger(__name__)

# 初始化数据库连接
db = StockDatabase()


@api_bp.route('/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """
    获取仪表板摘要数据
    
    Returns:
        {
            "success": true,
            "data": {
                "database": {
                    "total_stocks": int,
                    "last_update": str,
                    "data_completeness": float
                },
                "paper_trading": {
                    "running": bool,
                    "total_value": float,
                    "daily_pnl": float
                },
                "recent_backtests": [...]
            }
        }
    """
    try:
        # 获取数据库状态
        df_stocks = db.get_stock_list()
        total_stocks = len(df_stocks) if not df_stocks.empty else 0
        
        # 获取最后更新时间
        last_update = "未知"
        data_completeness = 0.0
        
        try:
            # 尝试从数据库获取最新数据日期
            import pandas as pd
            latest_date_query = """
                SELECT MAX(date) as latest_date 
                FROM market_snapshot
            """
            result = pd.read_sql(latest_date_query, db.conn)
            if not result.empty and result.iloc[0]['latest_date']:
                last_update = result.iloc[0]['latest_date']
            
            # 计算数据完整性（有数据的股票数量 / 总股票数量）
            if total_stocks > 0:
                stocks_with_data = 0
                for _, stock in df_stocks.head(100).iterrows():  # 采样检查
                    full_code = f"{stock['market']}.{stock['code']}"
                    if db.table_exists(full_code):
                        stocks_with_data += 1
                data_completeness = stocks_with_data / min(100, total_stocks)
        except Exception as e:
            logger.warning(f"获取数据库详细状态失败: {e}")
        
        database_status = {
            "total_stocks": total_stocks,
            "last_update": last_update,
            "data_completeness": round(data_completeness, 2)
        }
        
        # 获取模拟盘状态（简化版本，实际应该从模拟盘系统获取）
        paper_trading_status = {
            "running": False,
            "total_value": 0.0,
            "daily_pnl": 0.0
        }
        
        # 检查模拟盘数据文件是否存在
        paper_trading_dir = "paper_trading"
        if os.path.exists(paper_trading_dir):
            account_file = os.path.join(paper_trading_dir, "account.json")
            if os.path.exists(account_file):
                try:
                    import json
                    with open(account_file, 'r') as f:
                        account_data = json.load(f)
                        paper_trading_status = {
                            "running": True,
                            "total_value": account_data.get('total_value', 0.0),
                            "daily_pnl": account_data.get('daily_pnl', 0.0)
                        }
                except Exception as e:
                    logger.warning(f"读取模拟盘数据失败: {e}")
        
        # 获取最近回测结果（简化版本，实际应该从数据库获取）
        recent_backtests = []
        
        # 尝试从数据库获取回测记录
        try:
            import pandas as pd
            backtest_query = """
                SELECT id, strategy_name, metrics, created_at
                FROM backtest_results
                ORDER BY created_at DESC
                LIMIT 5
            """
            df_backtests = pd.read_sql(backtest_query, db.conn)
            
            if not df_backtests.empty:
                import json
                for _, row in df_backtests.iterrows():
                    try:
                        metrics = json.loads(row['metrics']) if isinstance(row['metrics'], str) else row['metrics']
                        recent_backtests.append({
                            "id": row['id'],
                            "strategy_name": row['strategy_name'],
                            "total_return": metrics.get('total_return', 0.0),
                            "max_drawdown": metrics.get('max_drawdown', 0.0),
                            "created_at": row['created_at']
                        })
                    except:
                        continue
        except Exception as e:
            logger.warning(f"获取回测记录失败: {e}")
        
        summary = {
            "database": database_status,
            "paper_trading": paper_trading_status,
            "recent_backtests": recent_backtests
        }
        
        return success_response(summary)
        
    except Exception as e:
        logger.error(f"获取仪表板摘要失败: {e}", exc_info=True)
        return error_response('获取仪表板摘要失败', 'FETCH_ERROR', 500)

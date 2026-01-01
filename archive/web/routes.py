"""
API路由定义
"""
from flask import Blueprint, jsonify, request
from database import DatabaseManager
from drive_handler import DriveHandler
from strategy import StockStrategy
import os

api = Blueprint('api', __name__)
db_manager = DatabaseManager()


@api.route('/api/databases', methods=['GET'])
def list_databases():
    """获取所有数据库列表"""
    try:
        databases = db_manager.list_databases()
        return jsonify({
            'success': True,
            'data': databases
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/databases/<db_name>/tables', methods=['GET'])
def get_tables(db_name):
    """获取指定数据库的所有表"""
    try:
        tables = db_manager.get_tables(db_name)
        return jsonify({
            'success': True,
            'data': tables
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/databases/<db_name>/tables/<table_name>/info', methods=['GET'])
def get_table_info(db_name, table_name):
    """获取表结构信息"""
    try:
        info = db_manager.get_table_info(db_name, table_name)
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/databases/<db_name>/tables/<table_name>/data', methods=['GET'])
def get_table_data(db_name, table_name):
    """获取表数据"""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        result = db_manager.get_table_data(db_name, table_name, limit, offset)
        return jsonify({
            'success': True,
            'data': result['data'],
            'total': result['total'],
            'limit': result['limit'],
            'offset': result['offset']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/databases/<db_name>/query', methods=['POST'])
def execute_query(db_name):
    """执行SQL查询"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': '查询语句不能为空'
            }), 400
        
        result = db_manager.execute_query(db_name, query)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'data': result['data'],
            'columns': result['columns'],
            'row_count': result['row_count']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/drive/files', methods=['GET'])
def list_drive_files():
    """列出Google Drive中的数据库文件"""
    try:
        folder_id = request.args.get('folder_id') or os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        handler = DriveHandler()
        files = handler.list_files(folder_id)
        return jsonify({
            'success': True,
            'data': files
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/drive/download', methods=['POST'])
def download_from_drive():
    """从Google Drive下载数据库文件"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        folder_id = data.get('folder_id') or os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        
        if not file_id:
            # 如果未指定文件ID，下载所有数据库文件
            handler = DriveHandler()
            files = handler.download_all_databases(folder_id)
            return jsonify({
                'success': True,
                'message': f'成功下载 {len(files)} 个文件',
                'data': files
            })
        else:
            # 下载指定文件
            handler = DriveHandler()
            # 获取文件信息
            file_info = handler.service.files().get(fileId=file_id).execute()
            file_path = handler.download_file(file_id, file_info['name'])
            
            return jsonify({
                'success': True,
                'message': '下载成功',
                'data': {
                    'name': file_info['name'],
                    'path': file_path
                }
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/databases/<db_name>/strategy/reversal', methods=['POST'])
def run_reversal_strategy(db_name):
    """执行起跌转折+缩量三连跌策略"""
    try:
        data = request.get_json() or {}
        min_cap = float(data.get('min_cap', 5e9))  # 默认50亿
        max_cap = float(data.get('max_cap', 20e9))  # 默认200亿
        min_drop_rate = float(data.get('min_drop_rate', 0.07))  # 默认7%
        
        strategy = StockStrategy(db_manager, db_name)
        pool = strategy.get_universe_pool(min_cap, max_cap)
        results = strategy.reversal_strategy(pool, min_drop_rate)
        
        return jsonify({
            'success': True,
            'data': results.to_dict('records') if not results.empty else [],
            'count': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/databases/<db_name>/strategy/bottom', methods=['POST'])
def run_bottom_strategy(db_name):
    """执行长线底部策略"""
    try:
        data = request.get_json() or {}
        min_cap = float(data.get('min_cap', 5e9))
        max_cap = float(data.get('max_cap', 20e9))
        max_drop_from_high = float(data.get('max_drop_from_high', 0.40))
        max_rise_from_low = float(data.get('max_rise_from_low', 1.20))
        
        strategy = StockStrategy(db_manager, db_name)
        pool = strategy.get_universe_pool(min_cap, max_cap)
        results = strategy.long_term_bottom_strategy(
            pool,
            max_drop_from_high=max_drop_from_high,
            max_rise_from_low=max_rise_from_low
        )
        
        return jsonify({
            'success': True,
            'data': results.to_dict('records') if not results.empty else [],
            'count': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api.route('/api/databases/<db_name>/strategy/combined', methods=['POST'])
def run_combined_strategy(db_name):
    """执行组合策略：长线底部+缩量三连跌"""
    try:
        data = request.get_json() or {}
        min_cap = float(data.get('min_cap', 5e9))
        max_cap = float(data.get('max_cap', 20e9))
        min_drop_rate = float(data.get('min_drop_rate', 0.07))
        max_drop_from_high = float(data.get('max_drop_from_high', 0.40))
        max_rise_from_low = float(data.get('max_rise_from_low', 1.20))
        check_support = data.get('check_support', True)
        
        strategy = StockStrategy(db_manager, db_name)
        pool = strategy.get_universe_pool(min_cap, max_cap)
        results = strategy.combined_strategy(
            pool,
            min_drop_rate=min_drop_rate,
            max_drop_from_high=max_drop_from_high,
            max_rise_from_low=max_rise_from_low,
            check_support=check_support
        )
        
        return jsonify({
            'success': True,
            'data': results.to_dict('records') if not results.empty else [],
            'count': len(results)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


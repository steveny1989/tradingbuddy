# -*- coding: utf-8 -*-
"""
股票诊断 API 路由

提供股票综合诊断的 REST API 接口
"""
from flask import Blueprint, jsonify, request
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.business.diagnosis.diagnosis_engine import StockDiagnosisEngine

logger = logging.getLogger(__name__)

# 创建 Blueprint
diagnosis_bp = Blueprint('diagnosis', __name__, url_prefix='/api/diagnosis')

# 初始化诊断引擎（全局单例）
diagnosis_engine = None


def get_diagnosis_engine():
    """获取诊断引擎实例（懒加载）"""
    global diagnosis_engine
    if diagnosis_engine is None:
        diagnosis_engine = StockDiagnosisEngine()
    return diagnosis_engine


@diagnosis_bp.route('/<code>', methods=['GET'])
def get_stock_diagnosis(code: str):
    """
    获取单只股票的综合诊断
    
    GET /api/diagnosis/{code}
    
    Query Parameters:
        - use_cache: 是否使用缓存（默认true）
    
    Returns:
        {
            "code": "600519",
            "name": "贵州茅台",
            "overall_score": 85,
            "overall_rating": "优秀",
            "overall_status": "green",
            "dimensions": {...},
            "strengths": [...],
            "weaknesses": [...],
            "suggestions": [...],
            "summary": "...",
            "updated_at": "2026-01-04 10:30:00"
        }
    """
    try:
        # 获取查询参数
        use_cache = request.args.get('use_cache', 'true').lower() == 'true'
        
        # 执行诊断
        engine = get_diagnosis_engine()
        report = engine.diagnose(code, use_cache=use_cache)
        
        # 返回JSON
        return jsonify(report.to_dict()), 200
        
    except ValueError as e:
        logger.error(f"诊断失败 - 参数错误: {e}")
        return jsonify({
            'error': 'invalid_parameter',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"诊断失败 - 服务器错误: {e}")
        return jsonify({
            'error': 'internal_error',
            'message': '服务器内部错误'
        }), 500


@diagnosis_bp.route('/batch', methods=['POST'])
def batch_stock_diagnosis():
    """
    批量获取股票诊断
    
    POST /api/diagnosis/batch
    
    Request Body:
        {
            "codes": ["600519", "000001", "000858"],
            "use_cache": true,
            "max_workers": 5
        }
    
    Returns:
        {
            "total": 3,
            "success": 3,
            "failed": 0,
            "reports": [...]
        }
    """
    try:
        # 解析请求体
        data = request.get_json()
        if not data or 'codes' not in data:
            return jsonify({
                'error': 'invalid_request',
                'message': '请求体必须包含 codes 字段'
            }), 400
        
        codes = data['codes']
        use_cache = data.get('use_cache', True)
        max_workers = data.get('max_workers', 5)
        
        # 验证参数
        if not isinstance(codes, list):
            return jsonify({
                'error': 'invalid_parameter',
                'message': 'codes 必须是数组'
            }), 400
        
        if len(codes) == 0:
            return jsonify({
                'error': 'invalid_parameter',
                'message': 'codes 不能为空'
            }), 400
        
        if len(codes) > 50:
            return jsonify({
                'error': 'invalid_parameter',
                'message': 'codes 最多支持50只股票'
            }), 400
        
        # 执行批量诊断
        engine = get_diagnosis_engine()
        reports = engine.diagnose_batch(codes, use_cache=use_cache, max_workers=max_workers)
        
        # 统计结果
        total = len(codes)
        success = len(reports)
        failed = total - success
        
        # 返回JSON
        return jsonify({
            'total': total,
            'success': success,
            'failed': failed,
            'reports': [report.to_dict() for report in reports]
        }), 200
        
    except ValueError as e:
        logger.error(f"批量诊断失败 - 参数错误: {e}")
        return jsonify({
            'error': 'invalid_parameter',
            'message': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"批量诊断失败 - 服务器错误: {e}")
        return jsonify({
            'error': 'internal_error',
            'message': '服务器内部错误'
        }), 500


@diagnosis_bp.route('/cache/clear', methods=['POST'])
def clear_diagnosis_cache():
    """
    清除诊断缓存
    
    POST /api/diagnosis/cache/clear
    
    Request Body (可选):
        {
            "code": "600519"  # 如果不提供，清除所有缓存
        }
    
    Returns:
        {
            "message": "缓存已清除"
        }
    """
    try:
        data = request.get_json() or {}
        code = data.get('code')
        
        engine = get_diagnosis_engine()
        engine.clear_cache(code)
        
        if code:
            message = f"已清除 {code} 的缓存"
        else:
            message = "已清除所有缓存"
        
        return jsonify({
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        return jsonify({
            'error': 'internal_error',
            'message': '服务器内部错误'
        }), 500


@diagnosis_bp.route('/health', methods=['GET'])
def health_check():
    """
    健康检查
    
    GET /api/diagnosis/health
    
    Returns:
        {
            "status": "ok",
            "engine": "initialized"
        }
    """
    try:
        engine = get_diagnosis_engine()
        return jsonify({
            'status': 'ok',
            'engine': 'initialized' if engine else 'not_initialized'
        }), 200
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# 错误处理
@diagnosis_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'not_found',
        'message': '资源不存在'
    }), 404


@diagnosis_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'internal_error',
        'message': '服务器内部错误'
    }), 500

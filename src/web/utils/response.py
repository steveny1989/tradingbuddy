"""
API响应辅助函数
"""
from flask import jsonify
from typing import Any, Optional


def success_response(data: Any = None, message: str = None) -> tuple:
    """
    成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        
    Returns:
        (response, status_code)
    """
    response = {'success': True}
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return jsonify(response), 200


def error_response(
    message: str,
    error_code: Optional[str] = None,
    status: int = 400
) -> tuple:
    """
    错误响应
    
    Args:
        message: 错误消息
        error_code: 错误代码
        status: HTTP状态码
        
    Returns:
        (response, status_code)
    """
    response = {
        'success': False,
        'error': message
    }
    
    if error_code:
        response['error_code'] = error_code
    
    return jsonify(response), status


def paginated_response(
    data: list,
    total: int,
    page: int,
    page_size: int
) -> tuple:
    """
    分页响应
    
    Args:
        data: 数据列表
        total: 总数
        page: 当前页码
        page_size: 每页大小
        
    Returns:
        (response, status_code)
    """
    return jsonify({
        'success': True,
        'data': data,
        'pagination': {
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    }), 200

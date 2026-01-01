"""
测试路由 - 用于验证API基础功能
"""
from flask import request
from src.web.routes import api_bp
from src.web.utils.response import success_response, error_response
from src.web.utils.errors import ValidationError, NotFoundError, DatabaseError


@api_bp.route('/test', methods=['GET'])
def test_endpoint():
    """测试端点 - 验证API正常工作"""
    return success_response({
        'message': 'API is working!',
        'version': '1.0.0'
    })


@api_bp.route('/test/error/<error_type>', methods=['GET'])
def test_error(error_type):
    """测试错误处理"""
    if error_type == 'validation':
        raise ValidationError('这是一个验证错误示例')
    elif error_type == 'notfound':
        raise NotFoundError('这是一个资源未找到错误示例')
    elif error_type == 'database':
        raise DatabaseError('这是一个数据库错误示例')
    elif error_type == 'exception':
        raise Exception('这是一个未处理的异常示例')
    else:
        return success_response({'error_type': error_type})


@api_bp.route('/test/validation', methods=['POST'])
def test_validation():
    """测试参数验证"""
    data = request.get_json()
    
    if not data:
        raise ValidationError('请求体不能为空')
    
    required_fields = ['name', 'value']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f'缺少必需参数: {field}')
    
    return success_response({
        'message': '验证通过',
        'data': data
    })

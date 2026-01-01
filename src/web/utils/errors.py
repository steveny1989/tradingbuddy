"""
自定义错误类和错误码定义
"""


class APIError(Exception):
    """API错误基类"""
    
    def __init__(self, message: str, error_code: str = None, status_code: int = 400):
        self.message = message
        self.error_code = error_code or 'API_ERROR'
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIError):
    """参数验证错误"""
    
    def __init__(self, message: str):
        super().__init__(message, 'VALIDATION_ERROR', 400)


class NotFoundError(APIError):
    """资源未找到错误"""
    
    def __init__(self, message: str = '资源未找到'):
        super().__init__(message, 'NOT_FOUND', 404)


class DatabaseError(APIError):
    """数据库错误"""
    
    def __init__(self, message: str = '数据库操作失败'):
        super().__init__(message, 'DATABASE_ERROR', 500)


class BusinessError(APIError):
    """业务逻辑错误"""
    
    def __init__(self, message: str, error_code: str = 'BUSINESS_ERROR'):
        super().__init__(message, error_code, 400)


# 错误码常量
class ErrorCode:
    """标准错误码"""
    
    # 通用错误
    INTERNAL_ERROR = 'INTERNAL_ERROR'
    INVALID_REQUEST = 'INVALID_REQUEST'
    NOT_FOUND = 'NOT_FOUND'
    
    # 验证错误
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    INVALID_PARAMETER = 'INVALID_PARAMETER'
    MISSING_PARAMETER = 'MISSING_PARAMETER'
    INVALID_DATE_FORMAT = 'INVALID_DATE_FORMAT'
    INVALID_STOCK_CODE = 'INVALID_STOCK_CODE'
    
    # 数据错误
    DATABASE_ERROR = 'DATABASE_ERROR'
    DATA_NOT_FOUND = 'DATA_NOT_FOUND'
    DATA_SYNC_ERROR = 'DATA_SYNC_ERROR'
    
    # 业务错误
    STRATEGY_NOT_FOUND = 'STRATEGY_NOT_FOUND'
    BACKTEST_ERROR = 'BACKTEST_ERROR'
    PAPER_TRADING_ERROR = 'PAPER_TRADING_ERROR'

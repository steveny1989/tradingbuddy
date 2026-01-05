"""
诊断模块的异常类定义
"""


class StockNotFoundError(Exception):
    """股票代码不存在"""
    def __init__(self, code: str, message: str = None):
        self.code = code
        self.message = message or f"未找到股票代码: {code}"
        super().__init__(self.message)


class DataInsufficientError(Exception):
    """数据不足以生成诊断"""
    def __init__(self, code: str, required_days: int, actual_days: int, message: str = None):
        self.code = code
        self.required_days = required_days
        self.actual_days = actual_days
        self.message = message or f"股票 {code} 数据不足: 需要 {required_days} 天，实际只有 {actual_days} 天"
        super().__init__(self.message)


class TooManyStocksError(Exception):
    """对比股票数量超过限制"""
    def __init__(self, count: int, max_count: int = 5, message: str = None):
        self.count = count
        self.max_count = max_count
        self.message = message or f"对比股票数量超过限制: 最多支持 {max_count} 只，实际提供了 {count} 只"
        super().__init__(self.message)


class DataStaleError(Warning):
    """数据过期警告"""
    def __init__(self, hours_old: float, message: str = None):
        self.hours_old = hours_old
        self.message = message or f"数据已过期 {hours_old:.1f} 小时"
        super().__init__(self.message)

"""
API路由模块
"""
from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 导入各个路由模块
from . import test  # 测试路由
from . import stocks  # 股票数据路由
from . import dashboard  # 仪表板路由
from . import strategies  # 策略管理路由
from . import backtest  # 回测结果路由

# 后续任务中会添加更多路由
# from . import paper_trading
# from . import data_management

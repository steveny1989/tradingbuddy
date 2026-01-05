# -*- coding: utf-8 -*-
"""配置文件"""
from datetime import datetime, timedelta
from dataclasses import dataclass

# ==================== 数据库配置 ====================

# V2 三层数据架构路径
DB_PATHS = {
    "raw": "data/raw",           # 原始数据层
    "cleaned": "data/cleaned",   # 清洗数据层
    "aggregated": "data/aggregated",  # 聚合数据层
    "legacy": "data/a_share.db"  # V1 遗留数据库（兼容旧代码）
}

# V1 兼容配置（逐步废弃）
DB_PATH = "data/a_share.db"  # 保留用于向后兼容

# 数据采集配置
START_DATE = "20230101"  # 建议采集2-3年数据
END_DATE = datetime.now().strftime('%Y%m%d')

# 采集控制
BATCH_SIZE = 100  # 每批次处理数量
SLEEP_INTERVAL = 0.5  # 请求间隔（秒）
MAX_RETRIES = 3  # 最大重试次数

# 数据字段映射
AKSHARE_COLUMNS = {
    '日期': 'date',
    '开盘': 'open',
    '收盘': 'close',
    '最高': 'high',
    '最低': 'low',
    '成交量': 'volume',
    '成交额': 'amount',
    '振幅': 'amplitude',
    '涨跌幅': 'pct_chg',
    '涨跌额': 'change',
    '换手率': 'turnover'
}

# 市场信息字段
MARKET_INFO_COLUMNS = {
    '代码': 'code',
    '名称': 'name',
    '最新价': 'price',
    '涨跌幅': 'pct_chg',
    '涨跌额': 'change',
    '成交量': 'volume',
    '成交额': 'amount',
    '振幅': 'amplitude',
    '最高': 'high',
    '最低': 'low',
    '今开': 'open',
    '昨收': 'pre_close',
    '量比': 'volume_ratio',
    '换手率': 'turnover',
    '市盈率-动态': 'pe_ttm',
    '市净率': 'pb',
    '总市值': 'total_cap',
    '流通市值': 'float_cap',
    '涨速': 'rise_speed',
    '5分钟涨跌': 'pct_5min',
    '60日涨跌幅': 'pct_60d',
    '年初至今涨跌幅': 'pct_ytd'
}

# ==================== 交易配置 ====================

@dataclass
class TradingConfig:
    """交易配置基类"""
    commission_rate: float = 0.0003      # 佣金率 0.03%
    slippage_rate: float = 0.001         # 滑点率 0.1%
    stamp_tax_rate: float = 0.001        # 印花税率 0.1%（仅卖出）
    min_commission: float = 5.0          # 最低佣金 5元


@dataclass
class BacktestConfig(TradingConfig):
    """回测配置"""
    initial_capital: float = 1000000     # 初始资金 100万
    max_positions: int = 10              # 最大持仓数
    position_size: float = 0.1           # 单次买入比例 10%
    
    # 止损止盈配置
    stop_loss: float = -0.10             # 止损线 -10%
    take_profit: float = 0.20            # 止盈线 +20%
    max_hold_days: int = 60              # 最大持仓天数


@dataclass
class PaperTradingConfig(TradingConfig):
    """模拟盘配置"""
    initial_capital: float = 100000      # 初始资金 10万
    max_positions: int = 5               # 最大持仓数
    position_size: float = 0.15          # 单次买入比例 15%
    data_dir: str = "paper_trading_data" # 数据目录
    
    # 止损止盈配置
    stop_loss: float = -0.08             # 止损线 -8%
    take_profit: float = 0.15            # 止盈线 +15%
    max_hold_days: int = 30              # 最大持仓天数


# 默认配置实例
DEFAULT_BACKTEST_CONFIG = BacktestConfig()
DEFAULT_PAPER_TRADING_CONFIG = PaperTradingConfig()

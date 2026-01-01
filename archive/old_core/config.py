# -*- coding: utf-8 -*-
"""配置文件"""
from datetime import datetime, timedelta

# 数据库配置
DB_PATH = "data/a_share.db"

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

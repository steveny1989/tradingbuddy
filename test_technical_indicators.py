#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试技术指标计算
验证我们可以计算哪些技术指标
"""
import pandas as pd
import numpy as np
from src.data.database import StockDatabase

def calculate_ma(df, periods=[20, 50, 250]):
    """计算移动平均线"""
    for period in periods:
        df[f'ma{period}'] = df['close'].rolling(window=period).mean()
    return df

def calculate_rsi(df, period=14):
    """计算RSI相对强弱指标"""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    df['rsi'] = rsi
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    df['macd'] = ema_fast - ema_slow
    df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    return df

def calculate_bollinger_bands(df, period=20, std_dev=2):
    """计算布林带"""
    df['bb_middle'] = df['close'].rolling(window=period).mean()
    rolling_std = df['close'].rolling(window=period).std()
    df['bb_upper'] = df['bb_middle'] + (rolling_std * std_dev)
    df['bb_lower'] = df['bb_middle'] - (rolling_std * std_dev)
    return df

def calculate_volume_ma(df, period=5):
    """计算成交量均线"""
    df['volume_ma'] = df['volume'].rolling(window=period).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    return df

def calculate_atr(df, period=14):
    """计算ATR平均真实波幅"""
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['atr'] = true_range.rolling(window=period).mean()
    return df

def analyze_stock(code='sh.600519', days=300):
    """分析单只股票的技术指标"""
    print(f"\n{'='*80}")
    print(f"技术指标分析: {code}")
    print(f"{'='*80}\n")
    
    # 获取数据
    db = StockDatabase()
    df = db.get_daily_data(code)
    
    if df.empty:
        print(f"❌ 无法获取 {code} 的数据")
        return
    
    # 按日期排序，取最近N天
    df = df.sort_values('date').tail(days).copy()
    
    print(f"✅ 数据加载成功: {len(df)} 天")
    print(f"   日期范围: {df['date'].min()} 至 {df['date'].max()}")
    print(f"   最新价格: {df['close'].iloc[-1]:.2f}")
    
    # 计算各种技术指标
    print(f"\n{'='*80}")
    print("计算技术指标...")
    print(f"{'='*80}\n")
    
    # 1. 移动平均线
    df = calculate_ma(df, [5, 10, 20, 50, 250])
    print("✅ 移动平均线 (MA5, MA10, MA20, MA50, MA250)")
    
    # 2. RSI
    df = calculate_rsi(df, 14)
    print("✅ RSI相对强弱指标 (14日)")
    
    # 3. MACD
    df = calculate_macd(df)
    print("✅ MACD指标 (12, 26, 9)")
    
    # 4. 布林带
    df = calculate_bollinger_bands(df, 20, 2)
    print("✅ 布林带 (20日, 2倍标准差)")
    
    # 5. 成交量指标
    df = calculate_volume_ma(df, 5)
    print("✅ 成交量均线和量比")
    
    # 6. ATR
    df = calculate_atr(df, 14)
    print("✅ ATR平均真实波幅 (14日)")
    
    # 显示最新数据
    print(f"\n{'='*80}")
    print("最新技术指标 (最近5天)")
    print(f"{'='*80}\n")
    
    latest = df.tail(5)
    
    # 格式化输出
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.float_format', lambda x: f'{x:.2f}')
    
    columns_to_show = [
        'date', 'close', 
        'ma5', 'ma20', 'ma50', 'ma250',
        'rsi', 'macd', 'macd_signal',
        'bb_upper', 'bb_middle', 'bb_lower',
        'volume_ratio', 'atr'
    ]
    
    print(latest[columns_to_show].to_string(index=False))
    
    # 技术分析总结
    print(f"\n{'='*80}")
    print("技术分析总结")
    print(f"{'='*80}\n")
    
    latest_row = df.iloc[-1]
    
    # 1. 均线分析
    print("📊 均线分析:")
    price = latest_row['close']
    ma20 = latest_row['ma20']
    ma50 = latest_row['ma50']
    ma250 = latest_row['ma250']
    
    if pd.notna(ma20):
        ma20_dev = (price - ma20) / ma20 * 100
        print(f"   当前价: {price:.2f}")
        print(f"   MA20: {ma20:.2f} (偏离: {ma20_dev:+.2f}%)")
        if price > ma20:
            print(f"   ✅ 价格在20日均线上方 - 短期趋势向上")
        else:
            print(f"   ⚠️ 价格在20日均线下方 - 短期趋势向下")
    
    if pd.notna(ma50):
        print(f"   MA50: {ma50:.2f}")
        if price > ma50:
            print(f"   ✅ 价格在50日均线上方 - 中期趋势向上")
    
    if pd.notna(ma250):
        print(f"   MA250: {ma250:.2f}")
        if price > ma250:
            print(f"   ✅ 价格在250日均线上方 - 长期趋势向上")
    
    # 2. RSI分析
    print(f"\n📈 RSI分析:")
    rsi = latest_row['rsi']
    if pd.notna(rsi):
        print(f"   RSI(14): {rsi:.2f}")
        if rsi > 70:
            print(f"   ⚠️ 超买区域 (>70) - 可能回调")
        elif rsi < 30:
            print(f"   ✅ 超卖区域 (<30) - 可能反弹")
        else:
            print(f"   ✅ 正常区域 (30-70)")
    
    # 3. MACD分析
    print(f"\n📉 MACD分析:")
    macd = latest_row['macd']
    macd_signal = latest_row['macd_signal']
    macd_hist = latest_row['macd_hist']
    if pd.notna(macd):
        print(f"   MACD: {macd:.2f}")
        print(f"   Signal: {macd_signal:.2f}")
        print(f"   Histogram: {macd_hist:.2f}")
        if macd > macd_signal:
            print(f"   ✅ MACD在信号线上方 - 多头信号")
        else:
            print(f"   ⚠️ MACD在信号线下方 - 空头信号")
    
    # 4. 布林带分析
    print(f"\n📊 布林带分析:")
    bb_upper = latest_row['bb_upper']
    bb_middle = latest_row['bb_middle']
    bb_lower = latest_row['bb_lower']
    if pd.notna(bb_upper):
        print(f"   上轨: {bb_upper:.2f}")
        print(f"   中轨: {bb_middle:.2f}")
        print(f"   下轨: {bb_lower:.2f}")
        bb_position = (price - bb_lower) / (bb_upper - bb_lower) * 100
        print(f"   位置: {bb_position:.1f}% (0%=下轨, 100%=上轨)")
        if price > bb_upper:
            print(f"   ⚠️ 价格突破上轨 - 超买")
        elif price < bb_lower:
            print(f"   ✅ 价格跌破下轨 - 超卖")
    
    # 5. 成交量分析
    print(f"\n📊 成交量分析:")
    volume_ratio = latest_row['volume_ratio']
    if pd.notna(volume_ratio):
        print(f"   量比: {volume_ratio:.2f}")
        if volume_ratio > 1.5:
            print(f"   ✅ 放量 (>1.5) - 资金活跃")
        elif volume_ratio < 0.7:
            print(f"   ⚠️ 缩量 (<0.7) - 资金观望")
        else:
            print(f"   ✅ 正常量能")
    
    print(f"\n{'='*80}\n")
    
    return df


if __name__ == '__main__':
    # 测试贵州茅台
    df = analyze_stock('sh.600519', days=300)
    
    # 可以测试其他股票
    # analyze_stock('sz.000858', days=300)  # 五粮液
    # analyze_stock('sh.600036', days=300)  # 招商银行

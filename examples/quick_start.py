# -*- coding: utf-8 -*-
"""快速启动脚本 - 用于测试和演示"""
import os
import logging
from src.data.database import StockDatabase
from src.data.fetcher import DataFetcher

# 配置简单日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def quick_start():
    """快速启动 - 下载少量数据用于测试"""
    
    print("="*60)
    print("🚀 A股数据采集系统 - 快速启动")
    print("="*60)
    print("\n这个脚本会下载前100只股票的数据用于测试")
    print("完整下载请使用: python main.py download\n")
    
    # 创建必要的目录
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # 初始化
    db = StockDatabase("data/a_share.db")
    fetcher = DataFetcher(db)
    
    try:
        # 第一步：获取股票列表
        print("\n📋 步骤1: 获取股票列表...")
        stock_list = fetcher.fetch_stock_list()
        print(f"✅ 获取成功: {len(stock_list)} 只股票")
        
        # 第二步：下载前100只股票的数据（测试用）
        print("\n📊 步骤2: 下载前100只股票数据（测试）...")
        print("数据范围: 2024-01-01 至今")
        
        test_stocks = stock_list.head(100)
        success = 0
        
        from tqdm import tqdm
        for idx, row in tqdm(test_stocks.iterrows(), total=len(test_stocks)):
            code = row['code']
            full_code = row.get('full_code', f"{row['market']}.{code}")
            
            df = fetcher.fetch_history(code, start_date="20240101")
            
            if df is not None and not df.empty:
                db.save_daily_data(full_code, df)
                success += 1
        
        print(f"\n✅ 下载完成: {success}/100")
        
        # 第三步：显示统计
        print("\n📈 步骤3: 数据库统计")
        stats = db.get_statistics()
        print(f"  总股票数: {stats['total_stocks']}")
        print(f"  已下载: {stats['downloaded_stocks']}")
        print(f"  总记录数: {stats['total_records']}")
        
        # 第四步：简单查询示例
        print("\n📉 步骤4: 数据查询示例")
        if success > 0:
            first_stock = test_stocks.iloc[0]
            code = first_stock.get('full_code', f"{first_stock['market']}.{first_stock['code']}")
            df = db.get_daily_data(code)
            
            if not df.empty:
                print(f"\n{first_stock['name']} ({code}) 最近5天数据:")
                print(df[['date', 'open', 'high', 'low', 'close', 'volume']].tail())
        
        print("\n" + "="*60)
        print("✨ 快速启动完成！")
        print("="*60)
        print("\n下一步:")
        print("  1. 查看示例: python example_usage.py")
        print("  2. 下载全市场: python main.py download")
        print("  3. 查看状态: python main.py status")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ 启动失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    quick_start()

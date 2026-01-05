#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量迁移工具

将所有使用 StockDatabase 的文件迁移到 DatabaseAdapter
"""
import os
import re
from pathlib import Path

# 需要迁移的文件列表（核心业务模块）
FILES_TO_MIGRATE = [
    # Web API 路由（已完成）
    'src/web/routes/stocks.py',
    'src/web/routes/strategies.py',
    'src/web/routes/dashboard.py',
    'src/web/routes/indices.py',
    
    # 诊断系统
    'src/business/diagnosis/technical_analyzer.py',
    
    # 后市分析
    'src/business/post_market/portfolio_health.py',
]

def migrate_file(filepath: str):
    """迁移单个文件"""
    if not os.path.exists(filepath):
        print(f"⚠️  文件不存在: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 替换导入语句
    content = content.replace(
        'from src.data.database import StockDatabase',
        'from src.data.database_adapter import DatabaseAdapter'
    )
    
    # 替换实例化
    content = re.sub(
        r'StockDatabase\([^)]*\)',
        'DatabaseAdapter()',
        content
    )
    
    # 替换类型注解
    content = content.replace(': StockDatabase', ': DatabaseAdapter')
    content = content.replace('StockDatabase()', 'DatabaseAdapter()')
    
    # 如果有修改，保存文件
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已迁移: {filepath}")
        return True
    else:
        print(f"⏭️  无需迁移: {filepath}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("批量迁移到 DatabaseAdapter")
    print("="*60)
    
    migrated = 0
    skipped = 0
    
    for filepath in FILES_TO_MIGRATE:
        if migrate_file(filepath):
            migrated += 1
        else:
            skipped += 1
    
    print("\n" + "="*60)
    print(f"迁移完成: {migrated} 个文件已迁移, {skipped} 个文件跳过")
    print("="*60)

if __name__ == "__main__":
    main()

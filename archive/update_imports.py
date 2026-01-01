#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新导入路径"""
import os
import re
from pathlib import Path

# 导入路径映射
IMPORT_MAPPINGS = {
    'from core.database import': 'from src.data.database import',
    'from core.data_fetcher import': 'from src.data.fetcher import',
    'from core.config import': 'from src.config.settings import',
    'from strategy.base import': 'from src.business.strategies.base import',
    'from strategy.backtest_engine import': 'from src.business.backtest.engine import',
    'from strategy.volume_shrink_strategy import': 'from src.business.strategies.volume_shrink import',
    'from strategy.ma_crossover_strategy import': 'from src.business.strategies.ma_crossover import',
    'from strategy import': 'from src.business.strategies import',
    'import core.database': 'import src.data.database',
    'import strategy.': 'import src.business.strategies.',
}

def update_file(filepath):
    """更新单个文件的导入"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 应用所有映射
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # 如果有变化，写回文件
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 更新: {filepath}")
            return True
        return False
    except Exception as e:
        print(f"❌ 错误 {filepath}: {e}")
        return False

def main():
    """主函数"""
    print("="*80)
    print("更新导入路径")
    print("="*80)
    
    # 需要更新的目录
    directories = ['src', 'tests', 'tools', 'examples']
    
    updated_count = 0
    
    for directory in directories:
        if not Path(directory).exists():
            continue
            
        print(f"\n处理目录: {directory}/")
        print("-"*80)
        
        # 遍历所有Python文件
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    if update_file(filepath):
                        updated_count += 1
    
    print("\n" + "="*80)
    print(f"完成！共更新 {updated_count} 个文件")
    print("="*80)

if __name__ == "__main__":
    main()

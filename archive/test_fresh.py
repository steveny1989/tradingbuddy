#!/usr/bin/env python3
import sys
sys.dont_write_bytecode = True  # 禁止生成.pyc文件

# 清除所有相关模块
for mod in list(sys.modules.keys()):
    if 'strategy' in mod or 'core' in mod:
        del sys.modules[mod]

from strategy.backtest_engine import BacktestEngine
import inspect

# 检查run方法的源代码
source = inspect.getsource(BacktestEngine.run)
print("检查run方法源代码:")
print("="*80)
if 'TEST:' in source:
    print("✓ 找到TEST语句")
else:
    print("✗ 没有找到TEST语句")

if 'df_index' in source:
    print("✓ 找到df_index (使用指数数据获取交易日)")
else:
    print("✗ 没有找到df_index")

if 'pd.date_range' in source:
    print("✗ 还在使用pd.date_range (旧代码)")
else:
    print("✓ 不使用pd.date_range")

print("\n前1000个字符:")
print(source[:1000])

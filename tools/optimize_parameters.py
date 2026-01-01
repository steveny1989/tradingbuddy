#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""参数优化工具 - 网格搜索最优参数"""
import logging
import pandas as pd
from itertools import product
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.business.backtest.engine import BacktestEngine

logging.basicConfig(
    level=logging.WARNING,  # 只显示警告和错误，减少输出
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_backtest_with_params(db, strategy, **params):
    """运行回测并返回结果"""
    backtest = BacktestEngine(
        db=db,
        strategy=strategy,
        initial_capital=1000000,
        max_positions=params.get('max_positions', 10),
        position_size=params.get('position_size', 0.1)
    )
    
    result = backtest.run(
        start_date='2024-10-01',
        end_date='2024-12-31',
        hold_days=params.get('hold_days', 5),
        stop_loss=params.get('stop_loss', -0.10),
        take_profit=params.get('take_profit', 0.15),
        scan_interval=1,
        time_stop_days=params.get('time_stop_days', 3)
    )
    
    return result

def main():
    print("="*80)
    print("参数优化 - 网格搜索")
    print("="*80)
    print("\n警告：这可能需要较长时间（10-30分钟），请耐心等待...\n")
    
    db = StockDatabase("data/a_share.db")
    strategy = VolumeShrinkStrategy(db=db, min_avg_turnover=1e8)
    
    # 定义参数网格
    param_grid = {
        'hold_days': [3, 5, 7],
        'stop_loss': [-0.08, -0.10, -0.12],
        'take_profit': [0.10, 0.15, 0.20],
        'time_stop_days': [2, 3, 5],
        'position_size': [0.08, 0.10, 0.12]
    }
    
    # 生成所有参数组合
    keys = param_grid.keys()
    values = param_grid.values()
    combinations = list(product(*values))
    
    print(f"总共需要测试 {len(combinations)} 种参数组合\n")
    
    results = []
    
    for i, combo in enumerate(combinations, 1):
        params = dict(zip(keys, combo))
        
        print(f"[{i}/{len(combinations)}] 测试参数: "
              f"持有={params['hold_days']}天, "
              f"止损={params['stop_loss']:.0%}, "
              f"止盈={params['take_profit']:.0%}, "
              f"时间止损={params['time_stop_days']}天, "
              f"仓位={params['position_size']:.0%}")
        
        try:
            result = run_backtest_with_params(db, strategy, **params)
            
            if result['total_trades'] > 0:
                results.append({
                    'hold_days': params['hold_days'],
                    'stop_loss': params['stop_loss'],
                    'take_profit': params['take_profit'],
                    'time_stop_days': params['time_stop_days'],
                    'position_size': params['position_size'],
                    'total_return': result['total_return'],
                    'max_drawdown': result['max_drawdown'],
                    'win_rate': result['win_rate'],
                    'total_trades': result['total_trades'],
                    'avg_profit_rate': result['avg_profit_rate'],
                    'sharpe_ratio': result['total_return'] / abs(result['max_drawdown']) if result['max_drawdown'] != 0 else 0
                })
                
                print(f"  结果: 收益={result['total_return']:.2%}, "
                      f"回撤={result['max_drawdown']:.2%}, "
                      f"胜率={result['win_rate']:.2%}, "
                      f"交易={result['total_trades']}笔")
            else:
                print(f"  结果: 无交易")
        
        except Exception as e:
            print(f"  错误: {e}")
            continue
    
    # 转换为DataFrame
    df_results = pd.DataFrame(results)
    
    if df_results.empty:
        print("\n没有有效的回测结果")
        db.close()
        return
    
    # 保存完整结果
    df_results.to_csv('optimization_results.csv', index=False)
    print(f"\n完整结果已保存到: optimization_results.csv")
    
    # 分析结果
    print("\n" + "="*80)
    print("优化结果分析")
    print("="*80)
    
    # 按不同指标排序
    print("\n【Top 5 - 按总收益率排序】")
    top_return = df_results.nlargest(5, 'total_return')
    print(top_return[['hold_days', 'stop_loss', 'take_profit', 'time_stop_days', 
                      'total_return', 'max_drawdown', 'win_rate']].to_string(index=False))
    
    print("\n【Top 5 - 按最小回撤排序】")
    top_drawdown = df_results.nsmallest(5, 'max_drawdown', key=abs)
    print(top_drawdown[['hold_days', 'stop_loss', 'take_profit', 'time_stop_days', 
                        'total_return', 'max_drawdown', 'win_rate']].to_string(index=False))
    
    print("\n【Top 5 - 按夏普比率排序】")
    top_sharpe = df_results.nlargest(5, 'sharpe_ratio')
    print(top_sharpe[['hold_days', 'stop_loss', 'take_profit', 'time_stop_days', 
                      'total_return', 'max_drawdown', 'sharpe_ratio']].to_string(index=False))
    
    print("\n【Top 5 - 按胜率排序】")
    top_winrate = df_results.nlargest(5, 'win_rate')
    print(top_winrate[['hold_days', 'stop_loss', 'take_profit', 'time_stop_days', 
                       'total_return', 'max_drawdown', 'win_rate']].to_string(index=False))
    
    # 推荐配置
    print("\n" + "="*80)
    print("推荐配置")
    print("="*80)
    
    # 综合评分：收益率 * 0.4 + (1 - abs(回撤)) * 0.3 + 胜率 * 0.3
    df_results['score'] = (
        df_results['total_return'] * 0.4 + 
        (1 - df_results['max_drawdown'].abs()) * 0.3 + 
        df_results['win_rate'] * 0.3
    )
    
    best = df_results.nlargest(1, 'score').iloc[0]
    
    print(f"\n最佳综合配置:")
    print(f"  持有天数: {best['hold_days']:.0f} 天")
    print(f"  止损线: {best['stop_loss']:.1%}")
    print(f"  止盈线: {best['take_profit']:.1%}")
    print(f"  时间止损: {best['time_stop_days']:.0f} 天")
    print(f"  仓位大小: {best['position_size']:.1%}")
    print(f"\n预期表现:")
    print(f"  总收益率: {best['total_return']:.2%}")
    print(f"  最大回撤: {best['max_drawdown']:.2%}")
    print(f"  胜率: {best['win_rate']:.2%}")
    print(f"  交易次数: {best['total_trades']:.0f}")
    print(f"  夏普比率: {best['sharpe_ratio']:.2f}")
    
    # 参数影响分析
    print("\n" + "="*80)
    print("参数影响分析")
    print("="*80)
    
    print("\n持有天数影响:")
    print(df_results.groupby('hold_days')[['total_return', 'max_drawdown', 'win_rate']].mean())
    
    print("\n止损线影响:")
    print(df_results.groupby('stop_loss')[['total_return', 'max_drawdown', 'win_rate']].mean())
    
    print("\n止盈线影响:")
    print(df_results.groupby('take_profit')[['total_return', 'max_drawdown', 'win_rate']].mean())
    
    print("\n时间止损影响:")
    print(df_results.groupby('time_stop_days')[['total_return', 'max_drawdown', 'win_rate']].mean())
    
    db.close()
    print("\n" + "="*80)
    print("优化完成")
    print("="*80)

if __name__ == "__main__":
    main()

/**
 * 极简选股助手主页面
 * 
 * 为普通股民提供极简的选股体验，只显示3个核心模块：
 * 1. 今日精选股票
 * 2. 我的自选监控
 * 3. 策略历史表现
 */
import React, { useState, useEffect } from 'react';
import { Card, Space, Typography } from 'antd';
import { OneSyncButton, DailyPicksCard, WatchlistCard, StrategyPerformanceCard } from '../components/picker';
import type { SyncStatus } from '../components/picker/OneSyncButton';
import type { DailyPick } from '../components/picker/DailyPicksCard';
import type { WatchlistItem } from '../components/picker/WatchlistCard';
import type { StrategyPerformance } from '../components/picker/StrategyPerformanceCard';
import './SimplePicker.css';

const { Title } = Typography;

/**
 * 极简选股助手主页面组件
 */
const SimplePicker: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [syncStatus, setSyncStatus] = useState<SyncStatus>({
    syncing: false,
    progress: 0,
    lastUpdate: undefined,
  });
  const [dailyPicks, setDailyPicks] = useState<DailyPick[]>([]);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [strategies, setStrategies] = useState<StrategyPerformance[]>([]);

  useEffect(() => {
    // 加载数据
    loadSyncStatus();
    loadDailyPicks();
    loadWatchlist();
    loadStrategies();
    setLoading(false);
  }, []);

  // 加载同步状态
  const loadSyncStatus = async () => {
    try {
      // 调用 API 获取同步状态
      const response = await fetch('http://localhost:5001/api/picker/sync/status');
      const result = await response.json();
      
      if (result.success && result.data) {
        setSyncStatus({
          syncing: false,
          progress: 0,
          lastUpdate: result.data.last_update_time,
          totalStocks: result.data.total_stocks,
          syncedStocks: result.data.synced_stocks,
        });
      }
    } catch (error) {
      console.error('加载同步状态失败:', error);
    }
  };

  // 加载今日精选
  const loadDailyPicks = async () => {
    try {
      // 调用 API 获取今日精选
      const response = await fetch('http://localhost:5001/api/picker/daily-picks');
      const result = await response.json();
      
      if (result.success && result.data) {
        // 转换 API 数据格式为前端格式
        const picks: DailyPick[] = result.data.map((item: any) => {
          // 计算信号强度
          let signal_strength: 'strong' | 'medium' | 'weak' = 'medium';
          if (item.confidence_score >= 70) {
            signal_strength = 'strong';
          } else if (item.confidence_score < 50) {
            signal_strength = 'weak';
          }
          
          // 计算涨跌幅（暂时设为0，因为API没有返回）
          const pct_change = 0;
          
          return {
            code: item.code,
            name: item.name,
            price: item.price,
            pct_change: pct_change,
            confidence_score: item.confidence_score,
            signal_strength: signal_strength,
            reason: item.reason,
          };
        });
        
        setDailyPicks(picks);
      } else {
        console.error('API 返回格式错误:', result);
      }
    } catch (error) {
      console.error('加载今日精选失败:', error);
    }
  };

  // 加载自选股
  const loadWatchlist = async () => {
    try {
      // TODO: 从 localStorage 读取自选股代码，然后调用 API 获取数据
      // const codes = JSON.parse(localStorage.getItem('watchlist') || '[]');
      // const response = await fetch(`/api/picker/watchlist?codes=${codes.join(',')}`);
      // const data = await response.json();
      // setWatchlist(data.watchlist);
      
      // 临时模拟数据
      const mockWatchlist: WatchlistItem[] = [
        {
          code: '600000.SH',
          name: '浦发银行',
          price: 8.52,
          pct_change: 0.0235,
          signal: 'buy',
          added_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
          added_price: 8.20,
          stop_loss: 7.38,  // -10%
          take_profit: 9.84,  // +20%
        },
        {
          code: '601318.SH',
          name: '中国平安',
          price: 45.67,
          pct_change: 0.0156,
          signal: 'hold',
          added_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          added_price: 46.00,
          stop_loss: 41.40,  // -10%
          take_profit: 55.20,  // +20%
        },
        {
          code: '600519.SH',
          name: '贵州茅台',
          price: 1678.90,
          pct_change: 0.0123,
          signal: 'hold',
          added_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
          added_price: 1700.00,
          stop_loss: 1530.00,  // -10%
          take_profit: 2040.00,  // +20%
          alert: {
            type: 'stop_loss',
            message: '建议止损卖出',
            current_price: 1678.90,
            target_price: 1530.00,
          },
        },
      ];
      
      setWatchlist(mockWatchlist);
    } catch (error) {
      console.error('加载自选股失败:', error);
    }
  };

  // 从自选股移除
  const handleRemoveFromWatchlist = (code: string) => {
    setWatchlist(prev => prev.filter(item => item.code !== code));
    // TODO: 更新 localStorage
    // const codes = watchlist.filter(item => item.code !== code).map(item => item.code);
    // localStorage.setItem('watchlist', JSON.stringify(codes));
  };

  // 加载策略表现
  const loadStrategies = async () => {
    try {
      // TODO: 调用 API 获取策略表现
      // const response = await fetch('/api/picker/strategies');
      // const data = await response.json();
      // setStrategies(data.strategies);
      
      // 临时模拟数据
      const mockStrategies: StrategyPerformance[] = [
        {
          id: 'low-volume-breakout',
          name: '低位放量突破',
          description: '股价在低位缩量后突然放量上涨，可能有资金进场',
          suitable_for: '稳健型',
          win_rate: 68.5,
          avg_return: 12.3,
          max_drawdown: -8.5,
          equity_curve: [
            { date: '2024-01-01', value: 100000 },
            { date: '2024-01-15', value: 102500 },
            { date: '2024-02-01', value: 105800 },
            { date: '2024-02-15', value: 104200 },
            { date: '2024-03-01', value: 108900 },
            { date: '2024-03-15', value: 111500 },
            { date: '2024-04-01', value: 110200 },
            { date: '2024-04-15', value: 113800 },
            { date: '2024-05-01', value: 116500 },
            { date: '2024-05-15', value: 115200 },
            { date: '2024-06-01', value: 119800 },
            { date: '2024-06-15', value: 122300 },
          ],
          recent_picks: [
            { code: '600000.SH', name: '浦发银行', pick_date: '2024-06-10', pick_price: 8.20, result: 'success', return: 0.039 },
            { code: '601318.SH', name: '中国平安', pick_date: '2024-06-08', pick_price: 44.50, result: 'success', return: 0.026 },
            { code: '600519.SH', name: '贵州茅台', pick_date: '2024-06-05', pick_price: 1650.00, result: 'failure', return: -0.012 },
            { code: '000858.SZ', name: '五粮液', pick_date: '2024-06-03', pick_price: 155.00, result: 'success', return: 0.011 },
            { code: '601166.SH', name: '兴业银行', pick_date: '2024-06-01', pick_price: 18.20, result: 'success', return: 0.014 },
          ],
        },
        {
          id: 'ma-golden-cross',
          name: '多头排列启动',
          description: '短期均线上穿长期均线，趋势可能转强',
          suitable_for: '激进型',
          win_rate: 72.3,
          avg_return: 15.8,
          max_drawdown: -12.3,
          equity_curve: [
            { date: '2024-01-01', value: 100000 },
            { date: '2024-01-15', value: 103200 },
            { date: '2024-02-01', value: 107500 },
            { date: '2024-02-15', value: 105800 },
            { date: '2024-03-01', value: 111200 },
            { date: '2024-03-15', value: 114800 },
            { date: '2024-04-01', value: 112500 },
            { date: '2024-04-15', value: 117900 },
            { date: '2024-05-01', value: 121500 },
            { date: '2024-05-15', value: 119800 },
            { date: '2024-06-01', value: 125200 },
            { date: '2024-06-15', value: 128900 },
          ],
          recent_picks: [
            { code: '600036.SH', name: '招商银行', pick_date: '2024-06-12', pick_price: 34.00, result: 'success', return: 0.016 },
            { code: '000002.SZ', name: '万科A', pick_date: '2024-06-10', pick_price: 9.80, result: 'success', return: 0.007 },
            { code: '601398.SH', name: '工商银行', pick_date: '2024-06-08', pick_price: 5.40, result: 'success', return: 0.006 },
            { code: '601288.SH', name: '农业银行', pick_date: '2024-06-05', pick_price: 3.62, result: 'success', return: 0.008 },
            { code: '000001.SZ', name: '平安银行', pick_date: '2024-06-03', pick_price: 12.10, result: 'success', return: 0.020 },
          ],
        },
        {
          id: 'pullback-support',
          name: '回踩支撑买入',
          description: '股价回调到重要支撑位后企稳，可能反弹',
          suitable_for: '稳健型',
          win_rate: 65.2,
          avg_return: 10.5,
          max_drawdown: -7.2,
          equity_curve: [
            { date: '2024-01-01', value: 100000 },
            { date: '2024-01-15', value: 101800 },
            { date: '2024-02-01', value: 104200 },
            { date: '2024-02-15', value: 103500 },
            { date: '2024-03-01', value: 106800 },
            { date: '2024-03-15', value: 108900 },
            { date: '2024-04-01', value: 107500 },
            { date: '2024-04-15', value: 110200 },
            { date: '2024-05-01', value: 112500 },
            { date: '2024-05-15', value: 111800 },
            { date: '2024-06-01', value: 114900 },
            { date: '2024-06-15', value: 117200 },
          ],
          recent_picks: [
            { code: '600519.SH', name: '贵州茅台', pick_date: '2024-06-11', pick_price: 1680.00, result: 'failure', return: -0.001 },
            { code: '000858.SZ', name: '五粮液', pick_date: '2024-06-09', pick_price: 156.00, result: 'success', return: 0.005 },
            { code: '601166.SH', name: '兴业银行', pick_date: '2024-06-07', pick_price: 18.30, result: 'success', return: 0.008 },
            { code: '600036.SH', name: '招商银行', pick_date: '2024-06-04', pick_price: 34.20, result: 'success', return: 0.011 },
            { code: '000002.SZ', name: '万科A', pick_date: '2024-06-02', pick_price: 9.85, result: 'success', return: 0.002 },
          ],
        },
      ];
      
      setStrategies(mockStrategies);
    } catch (error) {
      console.error('加载策略表现失败:', error);
    }
  };

  // 处理同步操作
  const handleSync = async () => {
    try {
      setSyncStatus(prev => ({ ...prev, syncing: true, progress: 0, error: undefined }));
      
      // TODO: 调用同步 API
      // const response = await fetch('/api/picker/sync', { method: 'POST' });
      // const data = await response.json();
      // const taskId = data.task_id;
      
      // 模拟同步进度
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 500));
        setSyncStatus(prev => ({
          ...prev,
          progress: i,
          currentStock: i < 100 ? `60000${Math.floor(i / 10)}.SH` : undefined,
          syncedStocks: Math.floor(i * 50 / 100),
          totalStocks: 5000,
        }));
      }
      
      // 同步完成
      setSyncStatus(prev => ({
        ...prev,
        syncing: false,
        progress: 100,
        lastUpdate: new Date().toISOString(),
        currentStock: undefined,
      }));
      
      // 刷新数据
      await loadSyncStatus();
      await loadDailyPicks();
    } catch (error) {
      console.error('同步失败:', error);
      setSyncStatus(prev => ({
        ...prev,
        syncing: false,
        error: '网络不稳定，请稍后重试',
      }));
    }
  };

  return (
    <div className="simple-picker">
      <div className="simple-picker-header">
        <Title level={2}>极简选股助手</Title>
        <p className="subtitle">懂你的选股直觉</p>
      </div>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 一键同步按钮 */}
        <Card className="sync-card">
          <OneSyncButton onSync={handleSync} syncStatus={syncStatus} />
        </Card>

        {/* 今日精选模块 */}
        <Card 
          title="今日精选股票" 
          className="daily-picks-card"
        >
          <DailyPicksCard 
            picks={dailyPicks} 
            loading={loading}
          />
        </Card>

        {/* 我的自选监控模块 */}
        <Card 
          title="我的自选监控" 
          className="watchlist-card"
        >
          <WatchlistCard 
            watchlist={watchlist}
            loading={loading}
            onRemove={handleRemoveFromWatchlist}
          />
        </Card>

        {/* 策略历史表现模块 */}
        <Card 
          title="策略历史表现" 
          className="strategy-performance-card"
        >
          <StrategyPerformanceCard 
            strategies={strategies}
            loading={loading}
          />
        </Card>
      </Space>
    </div>
  );
};

export default SimplePicker;

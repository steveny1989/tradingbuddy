/**
 * 极简选股助手主页面 - 首席级视觉版本
 * Premium UI Version with Glassmorphism and Animations
 */
import React, { useState, useEffect } from 'react';
import { Typography } from 'antd';
import { DataParticles, EnergyOrb, StockSignalBox, StrategyCard } from '../components/premium';
import type { SyncStatus } from '../components/picker/OneSyncButton';
import type { DailyPick } from '../components/picker/DailyPicksCard';
import type { WatchlistItem } from '../components/picker/WatchlistCard';
import '../styles/premium.css';
import './SimplePicker.css';

const { Title } = Typography;

const SimplePicker: React.FC = () => {
  const [syncStatus, setSyncStatus] = useState<SyncStatus>({
    syncing: false,
    progress: 0,
    lastUpdate: undefined,
  });
  const [dailyPicks, setDailyPicks] = useState<DailyPick[]>([]);
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);

  useEffect(() => {
    loadSyncStatus();
    loadDailyPicks();
    loadWatchlist();
  }, []);

  // 加载同步状态
  const loadSyncStatus = async () => {
    try {
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
      console.log('开始加载今日精选...');
      const response = await fetch('http://localhost:5001/api/picker/daily-picks');
      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      const result = await response.json();
      console.log('API返回结果:', result);
      
      if (result.success && result.data) {
        const picks: DailyPick[] = result.data.map((item: any) => {
          let signal_strength: 'strong' | 'medium' | 'weak' = 'medium';
          if (item.confidence_score >= 70) {
            signal_strength = 'strong';
          } else if (item.confidence_score < 50) {
            signal_strength = 'weak';
          }
          
          return {
            code: item.code,
            name: item.name,
            price: item.price || 0,  // 添加默认值防止undefined
            pct_change: item.pct_change || 0,
            confidence_score: item.confidence_score || 0,
            signal_strength: signal_strength,
            reason: item.reason || '符合策略条件',
          };
        });
        
        console.log('处理后的picks:', picks);
        console.log('picks数量:', picks.length);
        setDailyPicks(picks);
      } else {
        console.warn('API返回success=false或data为空:', result);
      }
    } catch (error) {
      console.error('加载今日精选失败:', error);
      console.error('错误详情:', error instanceof Error ? error.message : String(error));
    }
  };

  // 加载自选股
  const loadWatchlist = async () => {
    try {
      // TODO: 实现真实的自选股功能
      // 目前返回空列表，用户需要从今日精选中添加股票到自选
      setWatchlist([]);
    } catch (error) {
      console.error('加载自选股失败:', error);
    }
  };

  // 处理同步操作
  const handleSync = async () => {
    try {
      setSyncStatus(prev => ({ ...prev, syncing: true, progress: 0 }));
      
      // 模拟同步进度
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 300));
        setSyncStatus(prev => ({ ...prev, progress: i }));
      }
      
      setSyncStatus(prev => ({
        ...prev,
        syncing: false,
        progress: 100,
        lastUpdate: new Date().toISOString(),
      }));
      
      // 2秒后恢复idle状态
      setTimeout(() => {
        setSyncStatus(prev => ({ ...prev, progress: 0 }));
      }, 2000);
      
      // 刷新数据
      await loadSyncStatus();
      await loadDailyPicks();
    } catch (error) {
      console.error('同步失败:', error);
      setSyncStatus(prev => ({ ...prev, syncing: false }));
    }
  };

  // 获取能量球状态
  const getOrbStatus = (): 'idle' | 'syncing' | 'completed' => {
    if (syncStatus.syncing) return 'syncing';
    if (syncStatus.progress === 100) return 'completed';
    return 'idle';
  };

  return (
    <div style={{ position: 'relative', minHeight: '100vh' }}>
      {/* 数据流颗粒背景 */}
      <DataParticles />

      {/* 主内容区 */}
      <div style={{ position: 'relative', zIndex: 1, padding: '20px', maxWidth: '1400px', margin: '0 auto' }}>
        {/* 头部 */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: 40 
        }}>
          <div>
            <Title level={2} style={{ color: '#fff', margin: 0 }}>
              极简选股助手
            </Title>
            <p style={{ color: '#9ca3af', margin: '8px 0 0 0' }}>
              懂你的选股直觉
            </p>
          </div>

          {/* 能量球同步 */}
          <EnergyOrb
            status={getOrbStatus()}
            progress={syncStatus.progress}
            onClick={handleSync}
          />
        </div>

        {/* 今日精选 - 神盾雷达 */}
        <div className="glass-card" style={{ padding: 24, marginBottom: 24 }}>
          <Title level={3} style={{ color: '#fff', marginBottom: 20 }}>
            🎯 今日精选 - 神盾雷达 ({dailyPicks.length}只)
          </Title>
          
          {dailyPicks.length === 0 ? (
            <div style={{ color: '#9ca3af', textAlign: 'center', padding: 40 }}>
              暂无精选股票，请点击右上角同步按钮获取最新数据
            </div>
          ) : (
            <div className="card-carousel">
              {dailyPicks.map((pick) => (
                <StrategyCard
                  key={pick.code}
                  code={pick.code}
                  name={pick.name}
                  price={pick.price}
                  confidenceScore={pick.confidence_score}
                  strategyName="多头排列启动"
                  reason={pick.reason}
                />
              ))}
            </div>
          )}
        </div>

        {/* 自选股监控 - 信号方块 */}
        <div className="glass-card" style={{ padding: 24 }}>
          <Title level={3} style={{ color: '#fff', marginBottom: 20 }}>
            🚦 自选股监控 - 实时战况
          </Title>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: 16,
          }}>
            {watchlist.map((item) => {
              // 计算盈亏
              const profitPct = (item.price - item.added_price) / item.added_price;
              
              // 判断信号
              let signal: 'buy' | 'sell' | 'hold' | 'stop_loss' = item.signal as any;
              if (item.alert?.type === 'stop_loss') {
                signal = 'stop_loss';
              }
              
              return (
                <StockSignalBox
                  key={item.code}
                  code={item.code}
                  name={item.name}
                  price={item.price}
                  pctChange={item.pct_change}
                  signal={signal}
                  profitPct={profitPct}
                  alert={item.alert}
                />
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimplePicker;

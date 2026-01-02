/**
 * 指数行情栏组件 - 支持滚动播放
 */
import { useEffect, useState } from 'react';
import { Card, Space } from 'antd';
import { RiseOutlined, FallOutlined } from '@ant-design/icons';
import { getIndices, type IndexData } from '../../services/indices';
import './IndexBar.css';

export function IndexBar() {
  const [indices, setIndices] = useState<IndexData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIndices();
    // 每30秒刷新一次
    const interval = setInterval(loadIndices, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadIndices = async () => {
    try {
      const data = await getIndices();
      setIndices(data);
    } catch (error) {
      console.error('加载指数数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 过滤出可用的指数
  const availableIndices = indices.filter(index => index.available);

  return (
    <Card loading={loading} bodyStyle={{ padding: '12px 0', overflow: 'hidden' }}>
      <div className="index-bar-container">
        <div className="index-bar-scroll">
          {/* 渲染两次以实现无缝滚动 */}
          {[...availableIndices, ...availableIndices].map((index, idx) => {
            const isUp = index.pct_chg > 0;
            const isDown = index.pct_chg < 0;
            const color = isUp ? '#cf1322' : isDown ? '#3f8600' : '#666';
            
            return (
              <div key={`${index.code}-${idx}`} className="index-item">
                <Space direction="vertical" size={0}>
                  <div style={{ fontSize: '12px', color: '#999', whiteSpace: 'nowrap' }}>
                    {index.name}
                  </div>
                  <Space size={8} align="center">
                    <span style={{ 
                      fontSize: '16px', 
                      fontWeight: 'bold', 
                      color, 
                      fontFamily: 'monospace',
                      whiteSpace: 'nowrap'
                    }}>
                      {index.close.toFixed(2)}
                    </span>
                    <Space size={4}>
                      {isUp && <RiseOutlined style={{ color, fontSize: '12px' }} />}
                      {isDown && <FallOutlined style={{ color, fontSize: '12px' }} />}
                      <span style={{ fontSize: '12px', color, fontWeight: 500, whiteSpace: 'nowrap' }}>
                        {isUp ? '+' : ''}{index.pct_chg.toFixed(2)}%
                      </span>
                    </Space>
                  </Space>
                </Space>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}

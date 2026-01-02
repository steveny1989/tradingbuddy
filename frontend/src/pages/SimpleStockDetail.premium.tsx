/**
 * 极简股票详情页 - 首席级视觉版本
 * Premium Stock Detail Page
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Typography, Tag, Spin, message } from 'antd';
import { ArrowLeftOutlined, StarOutlined, StarFilled } from '@ant-design/icons';
import { motion } from 'framer-motion';
import { DataParticles } from '../components/premium';
import { formatPrice, formatPercentage } from '../utils/picker';
import '../styles/premium.css';
import './SimpleStockDetail.css';

const { Title, Text } = Typography;

interface StockInfo {
  code: string;
  name: string;
  price: number;
  pct_change: number;
  open: number;
  high: number;
  low: number;
  volume: number;
  market_cap: number;
}

interface PickReason {
  title: string;
  content: string;
  confidence_score: number;
}

interface KeyMetrics {
  pe_ratio: number;
  pb_ratio: number;
  roe: number;
  debt_ratio: number;
}

const SimpleStockDetail: React.FC = () => {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stockInfo, setStockInfo] = useState<StockInfo | null>(null);
  const [pickReason, setPickReason] = useState<PickReason | null>(null);
  const [keyMetrics, setKeyMetrics] = useState<KeyMetrics | null>(null);
  const [isInWatchlist, setIsInWatchlist] = useState(false);

  useEffect(() => {
    if (code) {
      loadStockDetail(code);
      checkWatchlistStatus(code);
    }
  }, [code]);

  const loadStockDetail = async (stockCode: string) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:5001/api/picker/stocks/${stockCode}`);
      const result = await response.json();
      
      if (result.success && result.data) {
        const data = result.data;
        
        setStockInfo({
          code: data.code,
          name: data.name,
          price: data.price,
          pct_change: data.pct_change,
          open: data.open,
          high: data.high,
          low: data.low,
          volume: data.volume,
          market_cap: data.market_cap,
        });
        
        if (data.pick_reason) {
          setPickReason({
            title: data.pick_reason.title,
            content: data.pick_reason.content,
            confidence_score: data.pick_reason.confidence_score,
          });
        } else {
          setPickReason({
            title: '技术分析',
            content: '该股票当前未在今日精选列表中。您可以通过查看关键指标和K线图来分析该股票的投资价值。',
            confidence_score: 50,
          });
        }
        
        if (data.key_metrics) {
          setKeyMetrics(data.key_metrics);
        } else {
          setKeyMetrics({
            pe_ratio: 0,
            pb_ratio: 0,
            roe: 0,
            debt_ratio: 0,
          });
        }
      } else {
        message.error(result.message || '加载失败，请稍后重试');
      }
    } catch (error) {
      console.error('加载股票详情失败:', error);
      message.error('加载失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const checkWatchlistStatus = (stockCode: string) => {
    try {
      const watchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
      setIsInWatchlist(watchlist.includes(stockCode));
    } catch (error) {
      console.error('检查自选股状态失败:', error);
    }
  };

  const toggleWatchlist = () => {
    if (!code) return;
    
    try {
      const watchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
      
      if (isInWatchlist) {
        const newWatchlist = watchlist.filter((c: string) => c !== code);
        localStorage.setItem('watchlist', JSON.stringify(newWatchlist));
        setIsInWatchlist(false);
        message.success('已从自选股移除');
      } else {
        watchlist.push(code);
        localStorage.setItem('watchlist', JSON.stringify(watchlist));
        setIsInWatchlist(true);
        message.success('已加入自选股');
      }
    } catch (error) {
      console.error('操作自选股失败:', error);
      message.error('操作失败，请稍后重试');
    }
  };

  const goBack = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <div style={{ position: 'relative', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <DataParticles />
        <Spin size="large" tip="加载中..." style={{ color: '#fff' }} />
      </div>
    );
  }

  if (!stockInfo) {
    return (
      <div style={{ position: 'relative', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 16 }}>
        <DataParticles />
        <Text style={{ color: '#fff' }}>股票信息加载失败</Text>
        <Button onClick={goBack}>返回</Button>
      </div>
    );
  }

  const priceColor = stockInfo.pct_change >= 0 ? '#ef4444' : '#10b981'; // 红涨绿跌

  return (
    <div style={{ position: 'relative', minHeight: '100vh' }}>
      <DataParticles />
      
      <div style={{ position: 'relative', zIndex: 1, padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
        {/* 顶部导航 */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 24 }}>
          <Button 
            type="text" 
            icon={<ArrowLeftOutlined />} 
            onClick={goBack}
            style={{ color: '#fff' }}
          >
            返回
          </Button>
          <Button
            type={isInWatchlist ? 'primary' : 'default'}
            icon={isInWatchlist ? <StarFilled /> : <StarOutlined />}
            onClick={toggleWatchlist}
          >
            {isInWatchlist ? '已加自选' : '加入自选'}
          </Button>
        </div>

        {/* 股票基本信息 */}
        <motion.div
          className="glass-card"
          style={{ padding: 32, marginBottom: 24 }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32 }}>
            <div>
              <Title level={2} style={{ color: '#fff', margin: 0, marginBottom: 8 }}>
                {stockInfo.name}
              </Title>
              <Text style={{ color: '#9ca3af', fontSize: 16 }}>{stockInfo.code}</Text>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 36, fontWeight: 'bold', color: priceColor, marginBottom: 4 }}>
                ¥{formatPrice(stockInfo.price)}
              </div>
              <div style={{ fontSize: 20, color: priceColor }}>
                {formatPercentage(stockInfo.pct_change)}
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24 }}>
            <div>
              <Text style={{ color: '#9ca3af', display: 'block', marginBottom: 8 }}>今开</Text>
              <Text style={{ color: '#fff', fontSize: 18, fontWeight: 600 }}>¥{formatPrice(stockInfo.open)}</Text>
            </div>
            <div>
              <Text style={{ color: '#9ca3af', display: 'block', marginBottom: 8 }}>最高</Text>
              <Text style={{ color: '#ef4444', fontSize: 18, fontWeight: 600 }}>¥{formatPrice(stockInfo.high)}</Text>
            </div>
            <div>
              <Text style={{ color: '#9ca3af', display: 'block', marginBottom: 8 }}>最低</Text>
              <Text style={{ color: '#10b981', fontSize: 18, fontWeight: 600 }}>¥{formatPrice(stockInfo.low)}</Text>
            </div>
            <div>
              <Text style={{ color: '#9ca3af', display: 'block', marginBottom: 8 }}>成交量</Text>
              <Text style={{ color: '#fff', fontSize: 18, fontWeight: 600 }}>{(stockInfo.volume / 100000000).toFixed(2)}亿</Text>
            </div>
          </div>
        </motion.div>

        {/* K线图占位 */}
        <motion.div
          className="glass-card"
          style={{ padding: 24, marginBottom: 24 }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <Title level={4} style={{ color: '#fff', marginBottom: 20 }}>
            📈 价格走势（最近3个月）
          </Title>
          <div style={{ 
            height: 300, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            background: 'rgba(59, 130, 246, 0.05)',
            borderRadius: 12,
            border: '1px dashed rgba(59, 130, 246, 0.3)'
          }}>
            <div style={{ textAlign: 'center' }}>
              <Text style={{ color: '#9ca3af', display: 'block', marginBottom: 8 }}>K线图功能开发中...</Text>
              <Text style={{ color: '#6b7280', fontSize: 12 }}>
                将显示最近3个月的K线图，并标注买入/卖出信号点
              </Text>
            </div>
          </div>
        </motion.div>

        {/* 选股理由 */}
        {pickReason && (
          <motion.div
            className="glass-card"
            style={{ padding: 24, marginBottom: 24 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.2 }}
          >
            <Title level={4} style={{ color: '#fff', marginBottom: 20 }}>
              💡 为什么推荐这只股票？
            </Title>
            <div style={{ marginBottom: 16 }}>
              <Tag color="blue" style={{ fontSize: 14, padding: '4px 12px' }}>{pickReason.title}</Tag>
              <Tag color="green" style={{ fontSize: 14, padding: '4px 12px', marginLeft: 8 }}>
                信心指数: {pickReason.confidence_score}分
              </Tag>
            </div>
            <Text style={{ color: '#d1d5db', fontSize: 16, lineHeight: 1.8, display: 'block', marginBottom: 16 }}>
              {pickReason.content}
            </Text>
            <Text style={{ color: '#6b7280', fontSize: 12 }}>
              💡 提示：以上分析基于技术指标，仅供参考，不构成投资建议
            </Text>
          </motion.div>
        )}

        {/* 关键指标 */}
        {keyMetrics && (
          <motion.div
            className="glass-card"
            style={{ padding: 24 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.3 }}
          >
            <Title level={4} style={{ color: '#fff', marginBottom: 20 }}>
              📊 关键指标
            </Title>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24, marginBottom: 16 }}>
              <div style={{ 
                padding: 20, 
                background: 'rgba(59, 130, 246, 0.1)', 
                borderRadius: 12,
                border: '1px solid rgba(59, 130, 246, 0.2)'
              }}>
                <Text style={{ color: '#9ca3af', display: 'block', marginBottom: 8 }}>市盈率 (PE)</Text>
                <Text style={{ color: '#fff', fontSize: 24, fontWeight: 'bold', display: 'block', marginBottom: 4 }}>
                  {keyMetrics.pe_ratio.toFixed(2)}
                </Text>
                <Text style={{ color: '#6b7280', fontSize: 12 }}>
                  {keyMetrics.pe_ratio < 15 ? '估值较低' : keyMetrics.pe_ratio < 30 ? '估值合理' : '估值较高'}
                </Text>
              </div>
              <div style={{ 
                padding: 20, 
                background: 'rgba(16, 185, 129, 0.1)', 
                borderRadius: 12,
                border: '1px solid rgba(16, 185, 129, 0.2)'
              }}>
                <Text style={{ color: '#9ca3af', display: 'block', marginBottom: 8 }}>市净率 (PB)</Text>
                <Text style={{ color: '#fff', fontSize: 24, fontWeight: 'bold', display: 'block', marginBottom: 4 }}>
                  {keyMetrics.pb_ratio.toFixed(2)}
                </Text>
                <Text style={{ color: '#6b7280', fontSize: 12 }}>
                  {keyMetrics.pb_ratio < 1 ? '破净' : keyMetrics.pb_ratio < 3 ? '正常' : '偏高'}
                </Text>
              </div>
              <div style={{ 
                padding: 20, 
                background: 'rgba(245, 158, 11, 0.1)', 
                borderRadius: 12,
                border: '1px solid rgba(245, 158, 11, 0.2)'
              }}>
                <Text style={{ color: '#9ca3af', display: 'block', marginBottom: 8 }}>净资产收益率 (ROE)</Text>
                <Text style={{ color: '#fff', fontSize: 24, fontWeight: 'bold', display: 'block', marginBottom: 4 }}>
                  {formatPercentage(keyMetrics.roe)}
                </Text>
                <Text style={{ color: '#6b7280', fontSize: 12 }}>
                  {keyMetrics.roe > 0.15 ? '盈利能力强' : keyMetrics.roe > 0.10 ? '盈利能力一般' : '盈利能力弱'}
                </Text>
              </div>
              <div style={{ 
                padding: 20, 
                background: 'rgba(239, 68, 68, 0.1)', 
                borderRadius: 12,
                border: '1px solid rgba(239, 68, 68, 0.2)'
              }}>
                <Text style={{ color: '#9ca3af', display: 'block', marginBottom: 8 }}>资产负债率</Text>
                <Text style={{ color: '#fff', fontSize: 24, fontWeight: 'bold', display: 'block', marginBottom: 4 }}>
                  {formatPercentage(keyMetrics.debt_ratio)}
                </Text>
                <Text style={{ color: '#6b7280', fontSize: 12 }}>
                  {keyMetrics.debt_ratio < 0.5 ? '负债健康' : keyMetrics.debt_ratio < 0.7 ? '负债适中' : '负债偏高'}
                </Text>
              </div>
            </div>
            <Text style={{ color: '#6b7280', fontSize: 12 }}>
              💡 指标说明：市盈率和市净率越低通常越便宜，ROE越高盈利能力越强，资产负债率越低财务越健康
            </Text>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default SimpleStockDetail;

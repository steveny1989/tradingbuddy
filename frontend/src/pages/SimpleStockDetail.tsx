/**
 * 极简股票详情页
 * 
 * 为普通股民提供简洁的股票详情展示：
 * - 股票基本信息（名称、代码、价格、涨跌幅）
 * - K线图（最近3个月）
 * - 大白话选股理由
 * - 关键指标
 * - 加入自选按钮
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Space, Typography, Tag, Spin, message } from 'antd';
import { ArrowLeftOutlined, StarOutlined, StarFilled } from '@ant-design/icons';
import { formatPrice, formatPercentage, getPriceChangeColor } from '../utils/picker';
import './SimpleStockDetail.css';

const { Title, Text } = Typography;

/**
 * 股票基本信息
 */
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

/**
 * 选股理由
 */
interface PickReason {
  title: string;
  content: string;
  confidence_score: number;
}

/**
 * 关键指标
 */
interface KeyMetrics {
  pe_ratio: number;
  pb_ratio: number;
  roe: number;
  debt_ratio: number;
}

/**
 * 极简股票详情页组件
 */
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

  // 加载股票详情
  const loadStockDetail = async (stockCode: string) => {
    try {
      setLoading(true);
      
      // 调用 API 获取股票详情
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
        
        // 设置选股理由
        if (data.pick_reason) {
          setPickReason({
            title: data.pick_reason.title,
            content: data.pick_reason.content,
            confidence_score: data.pick_reason.confidence_score,
          });
        } else {
          // 如果不在今日精选中，提供默认理由
          setPickReason({
            title: '技术分析',
            content: '该股票当前未在今日精选列表中。您可以通过查看关键指标和K线图来分析该股票的投资价值。',
            confidence_score: 50,
          });
        }
        
        // 设置关键指标
        if (data.key_metrics) {
          setKeyMetrics(data.key_metrics);
        } else {
          // 如果没有财务数据，使用默认值
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

  // 获取股票名称（临时函数）
  const getStockName = (stockCode: string): string => {
    const nameMap: Record<string, string> = {
      '600000.SH': '浦发银行',
      '000001.SZ': '平安银行',
      '601318.SH': '中国平安',
      '600519.SH': '贵州茅台',
      '000858.SZ': '五粮液',
      '601166.SH': '兴业银行',
      '600036.SH': '招商银行',
      '000002.SZ': '万科A',
      '601398.SH': '工商银行',
      '601288.SH': '农业银行',
    };
    return nameMap[stockCode] || '未知股票';
  };

  // 检查是否在自选股中
  const checkWatchlistStatus = (stockCode: string) => {
    try {
      const watchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
      setIsInWatchlist(watchlist.includes(stockCode));
    } catch (error) {
      console.error('检查自选股状态失败:', error);
    }
  };

  // 切换自选股状态
  const toggleWatchlist = () => {
    if (!code) return;
    
    try {
      const watchlist = JSON.parse(localStorage.getItem('watchlist') || '[]');
      
      if (isInWatchlist) {
        // 移除
        const newWatchlist = watchlist.filter((c: string) => c !== code);
        localStorage.setItem('watchlist', JSON.stringify(newWatchlist));
        setIsInWatchlist(false);
        message.success('已从自选股移除');
      } else {
        // 添加
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

  // 返回上一页
  const goBack = () => {
    navigate(-1);
  };

  if (loading) {
    return (
      <div className="simple-stock-detail loading">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (!stockInfo) {
    return (
      <div className="simple-stock-detail error">
        <Text>股票信息加载失败</Text>
        <Button onClick={goBack}>返回</Button>
      </div>
    );
  }

  const priceColor = getPriceChangeColor(stockInfo.pct_change);

  return (
    <div className="simple-stock-detail">
      {/* 顶部导航栏 */}
      <div className="detail-header">
        <Button 
          type="text" 
          icon={<ArrowLeftOutlined />} 
          onClick={goBack}
          className="back-button"
        >
          返回
        </Button>
        <Button
          type={isInWatchlist ? 'primary' : 'default'}
          icon={isInWatchlist ? <StarFilled /> : <StarOutlined />}
          onClick={toggleWatchlist}
          className="watchlist-button"
        >
          {isInWatchlist ? '已加自选' : '加入自选'}
        </Button>
      </div>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 股票基本信息卡片 */}
        <Card className="stock-info-card">
          <div className="stock-header">
            <div className="stock-title">
              <Title level={3} style={{ margin: 0 }}>{stockInfo.name}</Title>
              <Text type="secondary">{stockInfo.code}</Text>
            </div>
            <div className="stock-price">
              <div className="price" style={{ color: priceColor }}>
                ¥{formatPrice(stockInfo.price)}
              </div>
              <div className="change" style={{ color: priceColor }}>
                {formatPercentage(stockInfo.pct_change)}
              </div>
            </div>
          </div>

          <div className="stock-metrics">
            <div className="metric-item">
              <Text type="secondary">今开</Text>
              <Text strong>¥{formatPrice(stockInfo.open)}</Text>
            </div>
            <div className="metric-item">
              <Text type="secondary">最高</Text>
              <Text strong style={{ color: '#ff4d4f' }}>¥{formatPrice(stockInfo.high)}</Text>
            </div>
            <div className="metric-item">
              <Text type="secondary">最低</Text>
              <Text strong style={{ color: '#52c41a' }}>¥{formatPrice(stockInfo.low)}</Text>
            </div>
            <div className="metric-item">
              <Text type="secondary">成交量</Text>
              <Text strong>{(stockInfo.volume / 100000000).toFixed(2)}亿</Text>
            </div>
          </div>
        </Card>

        {/* K线图占位 */}
        <Card title="价格走势（最近3个月）" className="chart-card">
          <div className="chart-placeholder">
            <Text type="secondary">K线图功能开发中...</Text>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 8 }}>
              将显示最近3个月的K线图，并标注买入/卖出信号点
            </Text>
          </div>
        </Card>

        {/* 选股理由卡片 */}
        {pickReason && (
          <Card title="为什么推荐这只股票？" className="reason-card">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div className="reason-header">
                <Tag color="blue" style={{ fontSize: 14 }}>{pickReason.title}</Tag>
                <Tag color="green">信心指数: {pickReason.confidence_score}分</Tag>
              </div>
              <Text className="reason-content">{pickReason.content}</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                💡 提示：以上分析基于技术指标，仅供参考，不构成投资建议
              </Text>
            </Space>
          </Card>
        )}

        {/* 关键指标卡片 */}
        {keyMetrics && (
          <Card title="关键指标" className="metrics-card">
            <div className="metrics-grid">
              <div className="metric-box">
                <Text type="secondary">市盈率 (PE)</Text>
                <Text strong style={{ fontSize: 20 }}>{keyMetrics.pe_ratio.toFixed(2)}</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {keyMetrics.pe_ratio < 15 ? '估值较低' : keyMetrics.pe_ratio < 30 ? '估值合理' : '估值较高'}
                </Text>
              </div>
              <div className="metric-box">
                <Text type="secondary">市净率 (PB)</Text>
                <Text strong style={{ fontSize: 20 }}>{keyMetrics.pb_ratio.toFixed(2)}</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {keyMetrics.pb_ratio < 1 ? '破净' : keyMetrics.pb_ratio < 3 ? '正常' : '偏高'}
                </Text>
              </div>
              <div className="metric-box">
                <Text type="secondary">净资产收益率 (ROE)</Text>
                <Text strong style={{ fontSize: 20 }}>{formatPercentage(keyMetrics.roe)}</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {keyMetrics.roe > 0.15 ? '盈利能力强' : keyMetrics.roe > 0.10 ? '盈利能力一般' : '盈利能力弱'}
                </Text>
              </div>
              <div className="metric-box">
                <Text type="secondary">资产负债率</Text>
                <Text strong style={{ fontSize: 20 }}>{formatPercentage(keyMetrics.debt_ratio)}</Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {keyMetrics.debt_ratio < 0.5 ? '负债健康' : keyMetrics.debt_ratio < 0.7 ? '负债适中' : '负债偏高'}
                </Text>
              </div>
            </div>
            <Text type="secondary" style={{ fontSize: 12, display: 'block', marginTop: 16 }}>
              💡 指标说明：市盈率和市净率越低通常越便宜，ROE越高盈利能力越强，资产负债率越低财务越健康
            </Text>
          </Card>
        )}
      </Space>
    </div>
  );
};

export default SimpleStockDetail;

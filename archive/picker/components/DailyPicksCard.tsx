/**
 * 今日精选卡片组件
 * 
 * 显示今日精选的前10只股票，用颜色标识信号强度
 */
import React from 'react';
import { Table, Tag, Space, Typography, Empty, Badge } from 'antd';
import { RightOutlined, TrophyOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { 
  getSignalColor, 
  calculateSignalStrength,
  formatPrice, 
  formatPercentage,
  getPriceChangeColor,
} from '../../utils/picker';
import { formatStockCode } from '../../utils/stockCode';
import './DailyPicksCard.css';
  filterTechnicalTerms 
} from '../../utils/picker';
import type { SignalStrength } from '../../utils/picker';
import './DailyPicksCard.css';

const { Text } = Typography;

/**
 * 今日精选股票数据接口
 */
export interface DailyPick {
  code: string;
  name: string;
  price: number;
  pct_change: number;
  confidence_score: number;   // 0-100
  reason: string;             // 大白话选股理由
  signal_strength: SignalStrength;
}

/**
 * DailyPicksCard 组件属性
 */
export interface DailyPicksCardProps {
  picks: DailyPick[];
  loading?: boolean;
  onStockClick?: (code: string) => void;
}

/**
 * 今日精选卡片组件
 * 
 * 功能：
 * - 显示前10只股票
 * - 用颜色标识信号强度
 * - 显示股票代码、名称、价格、信号强度
 * - 点击股票跳转到详情页
 * - 显示大白话选股理由
 */
const DailyPicksCard: React.FC<DailyPicksCardProps> = ({ 
  picks, 
  loading = false,
  onStockClick 
}) => {
  const navigate = useNavigate();

  // 处理股票点击
  const handleStockClick = (code: string) => {
    if (onStockClick) {
      onStockClick(code);
    } else {
      // 跳转到极简股票详情页
      navigate(`/picker/stocks/${code}`);
    }
  };

  // 渲染信号强度标签
  const renderSignalStrength = (strength: SignalStrength, score: number) => {
    const color = getSignalColor(strength);
    const labels = {
      strong: '强',
      medium: '中',
      weak: '弱',
    };

    return (
      <Space direction="vertical" size={0} align="center">
        <Badge 
          color={color} 
          text={
            <Text strong style={{ color }}>
              {labels[strength]}
            </Text>
          }
        />
        <Text type="secondary" style={{ fontSize: 12 }}>
          {score}分
        </Text>
      </Space>
    );
  };

  // 渲染价格和涨跌幅
  const renderPrice = (price: number, pctChange: number) => {
    const color = getPriceChangeColor(pctChange);
    
    return (
      <Space direction="vertical" size={0} align="end">
        <Text strong style={{ fontSize: 16 }}>
          {formatPrice(price, 2, false)}
        </Text>
        <Text style={{ color, fontSize: 12 }}>
          {formatPercentage(pctChange)}
        </Text>
      </Space>
    );
  };

  // 渲染选股理由
  const renderReason = (reason: string) => {
    // 过滤技术术语
    const friendlyReason = filterTechnicalTerms(reason);
    
    return (
      <Text 
        type="secondary" 
        className="pick-reason"
        ellipsis={{ tooltip: friendlyReason }}
      >
        {friendlyReason}
      </Text>
    );
  };

  // 表格列定义
  const columns = [
    {
      title: '排名',
      key: 'rank',
      width: 60,
      align: 'center' as const,
      render: (_: any, __: any, index: number) => (
        <div className="rank-badge">
          {index < 3 ? (
            <TrophyOutlined style={{ 
              color: index === 0 ? '#FFD700' : index === 1 ? '#C0C0C0' : '#CD7F32',
              fontSize: 20 
            }} />
          ) : (
            <Text type="secondary">{index + 1}</Text>
          )}
        </div>
      ),
    },
    {
      title: '股票',
      key: 'stock',
      width: 180,
      render: (record: DailyPick) => (
        <Space direction="vertical" size={0}>
          <Text strong className="stock-name">{record.name}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>{formatStockCode(record.code)}</Text>
        </Space>
      ),
    },
    {
      title: '价格',
      key: 'price',
      width: 100,
      align: 'right' as const,
      render: (record: DailyPick) => renderPrice(record.price, record.pct_change),
    },
    {
      title: '信号强度',
      key: 'signal',
      width: 100,
      align: 'center' as const,
      render: (record: DailyPick) => renderSignalStrength(
        record.signal_strength, 
        record.confidence_score
      ),
    },
    {
      title: '选股理由',
      key: 'reason',
      ellipsis: true,
      render: (record: DailyPick) => renderReason(record.reason),
    },
    {
      title: '',
      key: 'action',
      width: 50,
      align: 'center' as const,
      render: (record: DailyPick) => (
        <RightOutlined className="action-icon" />
      ),
    },
  ];

  // 空状态
  if (!loading && picks.length === 0) {
    return (
      <Empty
        description="暂无今日精选"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      />
    );
  }

  // 只显示前10只股票
  const displayPicks = picks.slice(0, 10);

  return (
    <div className="daily-picks-card">
      <Table
        columns={columns}
        dataSource={displayPicks}
        loading={loading}
        rowKey="code"
        pagination={false}
        onRow={(record) => ({
          onClick: () => handleStockClick(record.code),
          className: 'clickable-row',
        })}
        className="picks-table"
      />
      
      {picks.length > 10 && (
        <div className="more-picks-hint">
          <Text type="secondary">
            还有 {picks.length - 10} 只股票未显示
          </Text>
        </div>
      )}
    </div>
  );
};

export default DailyPicksCard;

/**
 * 自选股监控卡片组件
 * 
 * 显示用户的自选股列表，包含信号灯、止损止盈预警等功能
 */
import React from 'react';
import { Table, Space, Typography, Button, Progress, Alert, Empty, Popconfirm } from 'antd';
import { DeleteOutlined, WarningOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import SignalLight from './SignalLight';
import { 
  formatPrice, 
  formatPercentage,
  getPriceChangeColor,
  formatRelativeTime 
} from '../../utils/picker';
import type { SignalType } from '../../utils/picker';
import './WatchlistCard.css';

const { Text } = Typography;

/**
 * 预警信息接口
 */
export interface Alert {
  type: 'stop_loss' | 'take_profit';
  message: string;
  current_price: number;
  target_price: number;
}

/**
 * 自选股数据接口
 */
export interface WatchlistItem {
  code: string;
  name: string;
  current_price: number;  // API返回的字段名
  change_pct: number;     // API返回的字段名
  signal: SignalType;
  add_time: string;       // API返回的字段名
  add_price: number;
  stop_loss: number;      // 止损百分比（如-0.10）
  take_profit: number;    // 止盈百分比（如0.20）
  profit_pct: number;     // API返回的持仓盈亏百分比
  alert?: Alert;
}

/**
 * WatchlistCard 组件属性
 */
export interface WatchlistCardProps {
  watchlist: WatchlistItem[];
  loading?: boolean;
  onRemove?: (code: string) => void;
  onStockClick?: (code: string) => void;
}

/**
 * 自选股监控卡片组件
 * 
 * 功能：
 * - 显示自选股列表
 * - 显示当前价格、涨跌幅、信号灯
 * - 显示添加时间和添加时价格
 * - 显示止损止盈进度条
 * - 支持移除股票
 * - 显示止损止盈预警
 */
const WatchlistCard: React.FC<WatchlistCardProps> = ({ 
  watchlist, 
  loading = false,
  onRemove,
  onStockClick 
}) => {
  const navigate = useNavigate();

  // 处理股票点击
  const handleStockClick = (code: string) => {
    if (onStockClick) {
      onStockClick(code);
    } else {
      navigate(`/picker/stocks/${code}`);
    }
  };

  // 处理移除股票
  const handleRemove = (code: string) => {
    if (onRemove) {
      onRemove(code);
    }
  };

  // 渲染价格信息
  const renderPrice = (record: WatchlistItem) => {
    const color = getPriceChangeColor(record.change_pct);
    const pnlColor = getPriceChangeColor(record.profit_pct);
    
    return (
      <Space direction="vertical" size={0} align="end">
        <Text strong style={{ fontSize: 16 }}>
          {formatPrice(record.current_price, 2, false)}
        </Text>
        <Text style={{ color, fontSize: 12 }}>
          {formatPercentage(record.change_pct)}
        </Text>
        <Text style={{ color: pnlColor, fontSize: 11 }}>
          持仓: {formatPercentage(record.profit_pct)}
        </Text>
      </Space>
    );
  };

  // 渲染止损止盈进度条
  const renderStopLossProgress = (record: WatchlistItem) => {
    const pnl = record.profit_pct;  // 使用API返回的盈亏百分比
    const stopLossPct = record.stop_loss;  // 已经是百分比
    const takeProfitPct = record.take_profit;  // 已经是百分比
    
    // 计算止损和止盈的实际价格
    const stopLossPrice = record.add_price * (1 + stopLossPct);
    const takeProfitPrice = record.add_price * (1 + takeProfitPct);
    
    // 计算进度条位置 (0-100)
    // 止损线在0，止盈线在100，当前价格在中间
    let progress = 0;
    let status: 'success' | 'exception' | 'normal' = 'normal';
    
    if (pnl <= stopLossPct) {
      progress = 0;
      status = 'exception';
    } else if (pnl >= takeProfitPct) {
      progress = 100;
      status = 'success';
    } else {
      // 在止损和止盈之间
      progress = ((pnl - stopLossPct) / (takeProfitPct - stopLossPct)) * 100;
    }
    
    return (
      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        <Progress 
          percent={progress} 
          status={status}
          showInfo={false}
          strokeColor={{
            '0%': '#ff4d4f',
            '50%': '#faad14',
            '100%': '#52c41a',
          }}
        />
        <Space size="small" style={{ width: '100%', justifyContent: 'space-between' }}>
          <Text type="secondary" style={{ fontSize: 11 }}>
            止损: {formatPrice(stopLossPrice, 2, false)}
          </Text>
          <Text type="secondary" style={{ fontSize: 11 }}>
            止盈: {formatPrice(takeProfitPrice, 2, false)}
          </Text>
        </Space>
      </Space>
    );
  };

  // 渲染预警信息
  const renderAlert = (alert: Alert) => {
    const isStopLoss = alert.type === 'stop_loss';
    
    return (
      <Alert
        message={isStopLoss ? '止损预警' : '止盈提示'}
        description={
          <Space direction="vertical" size={0}>
            <Text>{alert.message}</Text>
            <Text type="secondary" style={{ fontSize: 12 }}>
              当前价: {formatPrice(alert.current_price, 2)} | 
              目标价: {formatPrice(alert.target_price, 2)}
            </Text>
          </Space>
        }
        type={isStopLoss ? 'error' : 'success'}
        showIcon
        icon={isStopLoss ? <WarningOutlined /> : <CheckCircleOutlined />}
        closable
        style={{ marginTop: 8 }}
      />
    );
  };

  // 表格列定义
  const columns = [
    {
      title: '股票',
      key: 'stock',
      width: 150,
      render: (record: WatchlistItem) => (
        <Space direction="vertical" size={0}>
          <Text strong className="stock-name">{record.name}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>{record.code}</Text>
          <Text type="secondary" style={{ fontSize: 11 }}>
            {formatRelativeTime(record.add_time)}加入
          </Text>
        </Space>
      ),
    },
    {
      title: '价格',
      key: 'price',
      width: 120,
      align: 'right' as const,
      render: (record: WatchlistItem) => renderPrice(record),
    },
    {
      title: '信号',
      key: 'signal',
      width: 100,
      align: 'center' as const,
      render: (record: WatchlistItem) => (
        <SignalLight signal={record.signal} showLabel={true} />
      ),
    },
    {
      title: '止损止盈',
      key: 'stopLoss',
      width: 200,
      render: (record: WatchlistItem) => renderStopLossProgress(record),
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      align: 'center' as const,
      render: (record: WatchlistItem) => (
        <Popconfirm
          title="确定移除该股票？"
          onConfirm={() => handleRemove(record.code)}
          okText="确定"
          cancelText="取消"
        >
          <Button 
            type="text" 
            danger 
            icon={<DeleteOutlined />}
            size="small"
          >
            移除
          </Button>
        </Popconfirm>
      ),
    },
  ];

  // 空状态
  if (!loading && watchlist.length === 0) {
    return (
      <Empty
        description="暂无自选股"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      >
        <Text type="secondary">
          在"今日精选"中点击股票，即可加入自选
        </Text>
      </Empty>
    );
  }

  return (
    <div className="watchlist-card">
      <Table
        columns={columns}
        dataSource={watchlist}
        loading={loading}
        rowKey="code"
        pagination={false}
        onRow={(record) => ({
          onClick: () => handleStockClick(record.code),
          className: 'clickable-row',
        })}
        expandable={{
          expandedRowRender: (record) => 
            record.alert ? renderAlert(record.alert) : null,
          rowExpandable: (record) => !!record.alert,
          expandIcon: () => null,
          defaultExpandAllRows: true,
        }}
        className="watchlist-table"
      />
    </div>
  );
};

export default WatchlistCard;

/**
 * 最近回测卡片组件 - 专业交易站风格
 */
import React from 'react';
import { Card, Table, Tag, Button, Space } from 'antd';
import { LineChartOutlined, TrophyOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { TRADING_COLORS } from '../../theme/tradingTheme';
import type { BacktestSummary } from '../../services/dashboard';
import type { ColumnsType } from 'antd/es/table';

interface RecentBacktestCardProps {
  data: BacktestSummary[];
  loading?: boolean;
}

const RecentBacktestCard: React.FC<RecentBacktestCardProps> = ({ data, loading = false }) => {
  const navigate = useNavigate();

  const columns: ColumnsType<BacktestSummary> = [
    {
      title: '策略名称',
      dataIndex: 'strategy_name',
      key: 'strategy_name',
      width: '25%',
      render: (text: string) => (
        <span style={{ fontWeight: 500 }}>{text}</span>
      ),
    },
    {
      title: '总收益率',
      dataIndex: 'total_return',
      key: 'total_return',
      width: '15%',
      align: 'right',
      render: (value: number) => {
        const isPositive = value >= 0;
        return (
          <Space size={4}>
            <span style={{ 
              color: isPositive ? TRADING_COLORS.UP : TRADING_COLORS.DOWN,
              fontFamily: 'monospace',
              fontWeight: 'bold',
              fontSize: '14px'
            }}>
              {isPositive ? '+' : ''}{(value * 100).toFixed(2)}%
            </span>
          </Space>
        );
      },
      sorter: (a, b) => a.total_return - b.total_return,
    },
    {
      title: '最大回撤',
      dataIndex: 'max_drawdown',
      key: 'max_drawdown',
      width: '15%',
      align: 'right',
      render: (value: number) => (
        <span style={{ 
          color: TRADING_COLORS.DOWN,
          fontFamily: 'monospace',
          fontSize: '13px'
        }}>
          {(value * 100).toFixed(2)}%
        </span>
      ),
      sorter: (a, b) => a.max_drawdown - b.max_drawdown,
    },
    {
      title: '夏普比率',
      dataIndex: 'sharpe_ratio',
      key: 'sharpe_ratio',
      width: '12%',
      align: 'right',
      render: (value: number) => {
        if (!value) return <span style={{ color: '#8c8c8c' }}>-</span>;
        const color = value > 2 ? TRADING_COLORS.UP : 
                     value > 1 ? TRADING_COLORS.STABLE : 
                     TRADING_COLORS.DOWN;
        return (
          <span style={{ 
            color,
            fontFamily: 'monospace',
            fontSize: '13px'
          }}>
            {value.toFixed(2)}
          </span>
        );
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: '18%',
      render: (value: string) => (
        <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
          {value.split(' ')[0]}
        </span>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: '15%',
      align: 'center',
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          onClick={() => navigate(`/backtest/${record.id}`)}
        >
          查看详情
        </Button>
      ),
    },
  ];

  // 找出最佳策略
  const bestStrategy = data.length > 0 
    ? data.reduce((best, current) => 
        current.total_return > best.total_return ? current : best
      )
    : null;

  return (
    <Card
      title={
        <Space>
          <LineChartOutlined />
          <span>回测记录</span>
          {bestStrategy && (
            <Tag icon={<TrophyOutlined />} color="gold">
              最佳: {bestStrategy.strategy_name} ({(bestStrategy.total_return * 100).toFixed(2)}%)
            </Tag>
          )}
        </Space>
      }
      loading={loading}
      bordered={false}
      extra={
        <Button type="link" onClick={() => navigate('/backtest')}>
          查看全部
        </Button>
      }
    >
      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        pagination={false}
        size="small"
        locale={{ emptyText: '暂无回测记录，开始你的第一次回测吧！' }}
      />
    </Card>
  );
};

export default RecentBacktestCard;

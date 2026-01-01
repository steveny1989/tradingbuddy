/**
 * 最近回测卡片组件
 */
import React from 'react';
import { Card, Table, Tag, Button } from 'antd';
import { LineChartOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
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
      width: '30%',
    },
    {
      title: '总收益率',
      dataIndex: 'total_return',
      key: 'total_return',
      width: '20%',
      render: (value: number) => {
        const isPositive = value >= 0;
        return (
          <Tag color={isPositive ? 'green' : 'red'}>
            {isPositive ? '+' : ''}
            {(value * 100).toFixed(2)}%
          </Tag>
        );
      },
    },
    {
      title: '最大回撤',
      dataIndex: 'max_drawdown',
      key: 'max_drawdown',
      width: '20%',
      render: (value: number) => (
        <span style={{ color: '#cf1322' }}>{(value * 100).toFixed(2)}%</span>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: '20%',
      render: (value: string) => value.split(' ')[0],
    },
    {
      title: '操作',
      key: 'action',
      width: '10%',
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          onClick={() => navigate(`/backtest/${record.id}`)}
        >
          查看
        </Button>
      ),
    },
  ];

  return (
    <Card
      title={
        <span>
          <LineChartOutlined style={{ marginRight: 8 }} />
          最近回测
        </span>
      }
      loading={loading}
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
        locale={{ emptyText: '暂无回测记录' }}
      />
    </Card>
  );
};

export default RecentBacktestCard;

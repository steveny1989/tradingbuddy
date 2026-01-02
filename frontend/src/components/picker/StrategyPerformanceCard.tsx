/**
 * 策略表现卡片组件
 * 
 * 显示金牌策略的历史表现数据
 */
import React, { useState } from 'react';
import { Card, Row, Col, Statistic, Tag, Space, Typography, Collapse, Table, Empty } from 'antd';
import { TrophyOutlined, RiseOutlined, FallOutlined, LineChartOutlined } from '@ant-design/icons';
import { Line } from '@ant-design/charts';
import { formatPercentage, getPriceChangeColor } from '../../utils/picker';
import './StrategyPerformanceCard.css';

const { Text, Title } = Typography;
const { Panel } = Collapse;

/**
 * 资金曲线数据点
 */
export interface EquityPoint {
  date: string;
  value: number;
}

/**
 * 历史选股记录
 */
export interface HistoricalPick {
  code: string;
  name: string;
  pick_date: string;
  pick_price: number;
  result: 'success' | 'failure';
  return: number;  // 收益率
}

/**
 * 策略表现数据
 */
export interface StrategyPerformance {
  id: string;
  name: string;
  description: string;
  suitable_for: string;
  win_rate: number;           // 胜率 (%)
  avg_return: number;         // 平均收益率 (%)
  max_drawdown: number;       // 最大回撤 (%)
  equity_curve: EquityPoint[];
  recent_picks: HistoricalPick[];
}

/**
 * StrategyPerformanceCard 组件属性
 */
export interface StrategyPerformanceCardProps {
  strategies: StrategyPerformance[];
  loading?: boolean;
  onStrategyClick?: (id: string) => void;
}

/**
 * 策略表现卡片组件
 * 
 * 功能：
 * - 显示金牌策略列表
 * - 显示胜率、平均收益率、最大回撤
 * - 用图表展示资金曲线
 * - 点击策略显示历史选股记录
 */
const StrategyPerformanceCard: React.FC<StrategyPerformanceCardProps> = ({ 
  strategies, 
  loading = false,
  onStrategyClick 
}) => {
  const [activeStrategy, setActiveStrategy] = useState<string | string[]>([]);

  // 处理策略展开/收起
  const handleStrategyChange = (key: string | string[]) => {
    setActiveStrategy(key);
    if (onStrategyClick && typeof key === 'string') {
      onStrategyClick(key);
    }
  };

  // 渲染策略统计数据
  const renderStrategyStats = (strategy: StrategyPerformance) => {
    const winRateColor = strategy.win_rate >= 60 ? '#52c41a' : strategy.win_rate >= 50 ? '#faad14' : '#ff4d4f';
    const avgReturnColor = getPriceChangeColor(strategy.avg_return / 100);
    const drawdownColor = '#ff4d4f';

    return (
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Card size="small" className="stat-card">
            <Statistic
              title="近30天胜率"
              value={strategy.win_rate}
              precision={1}
              suffix="%"
              valueStyle={{ color: winRateColor, fontSize: 24 }}
              prefix={<TrophyOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small" className="stat-card">
            <Statistic
              title="平均收益率"
              value={strategy.avg_return}
              precision={2}
              suffix="%"
              valueStyle={{ color: avgReturnColor, fontSize: 24 }}
              prefix={strategy.avg_return >= 0 ? <RiseOutlined /> : <FallOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small" className="stat-card">
            <Statistic
              title="最大回撤"
              value={Math.abs(strategy.max_drawdown)}
              precision={2}
              suffix="%"
              valueStyle={{ color: drawdownColor, fontSize: 24 }}
              prefix={<FallOutlined />}
            />
          </Card>
        </Col>
      </Row>
    );
  };

  // 渲染资金曲线图表
  const renderEquityCurve = (equityCurve: EquityPoint[]) => {
    if (!equityCurve || equityCurve.length === 0) {
      return <Empty description="暂无数据" image={Empty.PRESENTED_IMAGE_SIMPLE} />;
    }

    const config = {
      data: equityCurve,
      xField: 'date',
      yField: 'value',
      smooth: true,
      animation: {
        appear: {
          animation: 'path-in',
          duration: 1000,
        },
      },
      areaStyle: {
        fill: 'l(270) 0:#ffffff 0.5:#7ec2f3 1:#1890ff',
        fillOpacity: 0.3,
      },
      line: {
        color: '#1890ff',
        size: 2,
      },
      point: {
        size: 3,
        shape: 'circle',
      },
      tooltip: {
        formatter: (datum: EquityPoint) => {
          return {
            name: '账户价值',
            value: `¥${datum.value.toFixed(2)}`,
          };
        },
      },
      xAxis: {
        label: {
          formatter: (text: string) => {
            // 简化日期显示
            return text.substring(5);  // 只显示月-日
          },
        },
      },
      yAxis: {
        label: {
          formatter: (text: string) => {
            return `¥${text}`;
          },
        },
      },
    };

    return (
      <div className="equity-curve-container">
        <div className="chart-header">
          <LineChartOutlined style={{ marginRight: 8 }} />
          <Text strong>资金曲线</Text>
          <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
            （如果按这个策略操作，账户价值如何变化）
          </Text>
        </div>
        <Line {...config} height={250} />
      </div>
    );
  };

  // 渲染历史选股记录
  const renderHistoricalPicks = (picks: HistoricalPick[]) => {
    const columns = [
      {
        title: '股票',
        key: 'stock',
        width: 150,
        render: (record: HistoricalPick) => (
          <Space direction="vertical" size={0}>
            <Text strong>{record.name}</Text>
            <Text type="secondary" style={{ fontSize: 12 }}>{record.code}</Text>
          </Space>
        ),
      },
      {
        title: '选股日期',
        dataIndex: 'pick_date',
        key: 'pick_date',
        width: 120,
        render: (date: string) => (
          <Text>{date.substring(0, 10)}</Text>
        ),
      },
      {
        title: '选股价格',
        dataIndex: 'pick_price',
        key: 'pick_price',
        width: 100,
        align: 'right' as const,
        render: (price: number) => (
          <Text>¥{price.toFixed(2)}</Text>
        ),
      },
      {
        title: '收益率',
        dataIndex: 'return',
        key: 'return',
        width: 100,
        align: 'right' as const,
        render: (returnValue: number) => {
          const color = getPriceChangeColor(returnValue);
          return (
            <Text style={{ color }}>
              {formatPercentage(returnValue)}
            </Text>
          );
        },
      },
      {
        title: '结果',
        dataIndex: 'result',
        key: 'result',
        width: 80,
        align: 'center' as const,
        render: (result: 'success' | 'failure') => (
          <Tag color={result === 'success' ? 'success' : 'error'}>
            {result === 'success' ? '成功' : '失败'}
          </Tag>
        ),
      },
    ];

    return (
      <div className="historical-picks-container">
        <Table
          columns={columns}
          dataSource={picks}
          rowKey={(record) => `${record.code}-${record.pick_date}`}
          pagination={{ pageSize: 5, size: 'small' }}
          size="small"
        />
        <div className="data-source-note">
          <Text type="secondary" style={{ fontSize: 12 }}>
            数据来源：基于2024年1月至今的回测数据
          </Text>
        </div>
      </div>
    );
  };

  // 空状态
  if (!loading && strategies.length === 0) {
    return (
      <Empty
        description="暂无策略数据"
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      />
    );
  };

  return (
    <div className="strategy-performance-card">
      <Collapse 
        activeKey={activeStrategy}
        onChange={handleStrategyChange}
        accordion
        className="strategy-collapse"
      >
        {strategies.map((strategy) => (
          <Panel
            key={strategy.id}
            header={
              <div className="strategy-header">
                <Space>
                  <TrophyOutlined style={{ color: '#faad14', fontSize: 18 }} />
                  <div>
                    <Text strong style={{ fontSize: 16 }}>{strategy.name}</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: 12 }}>
                      {strategy.description}
                    </Text>
                  </div>
                </Space>
                <Tag color="blue">{strategy.suitable_for}</Tag>
              </div>
            }
          >
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              {/* 统计数据 */}
              {renderStrategyStats(strategy)}

              {/* 资金曲线 */}
              {renderEquityCurve(strategy.equity_curve)}

              {/* 历史选股记录 */}
              <div>
                <Title level={5}>历史选股记录</Title>
                {renderHistoricalPicks(strategy.recent_picks)}
              </div>
            </Space>
          </Panel>
        ))}
      </Collapse>
    </div>
  );
};

export default StrategyPerformanceCard;

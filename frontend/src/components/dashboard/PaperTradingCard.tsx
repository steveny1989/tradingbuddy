/**
 * 模拟盘概览卡片组件
 */
import React from 'react';
import { Card, Statistic, Row, Col, Badge, Button } from 'antd';
import { MonitorOutlined, DollarOutlined, RiseOutlined, FallOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import type { PaperTradingStatus } from '../../services/dashboard';

interface PaperTradingCardProps {
  data: PaperTradingStatus;
  loading?: boolean;
}

const PaperTradingCard: React.FC<PaperTradingCardProps> = ({ data, loading = false }) => {
  const navigate = useNavigate();
  const isProfitable = data.daily_pnl >= 0;

  return (
    <Card
      title={
        <span>
          <MonitorOutlined style={{ marginRight: 8 }} />
          模拟盘概览
          <Badge
            status={data.running ? 'processing' : 'default'}
            text={data.running ? '运行中' : '已停止'}
            style={{ marginLeft: 16 }}
          />
        </span>
      }
      loading={loading}
      extra={
        <Button type="link" onClick={() => navigate('/paper-trading')}>
          查看详情
        </Button>
      }
    >
      <Row gutter={16}>
        <Col span={12}>
          <Statistic
            title={
              <span>
                <DollarOutlined style={{ marginRight: 4 }} />
                账户总值
              </span>
            }
            value={data.total_value}
            precision={2}
            suffix="元"
            valueStyle={{ color: '#1890ff' }}
          />
        </Col>
        <Col span={12}>
          <Statistic
            title={
              <span>
                {isProfitable ? (
                  <RiseOutlined style={{ marginRight: 4 }} />
                ) : (
                  <FallOutlined style={{ marginRight: 4 }} />
                )}
                当日盈亏
              </span>
            }
            value={data.daily_pnl}
            precision={2}
            suffix="元"
            valueStyle={{ color: isProfitable ? '#3f8600' : '#cf1322' }}
            prefix={isProfitable ? '+' : ''}
          />
        </Col>
      </Row>
    </Card>
  );
};

export default PaperTradingCard;

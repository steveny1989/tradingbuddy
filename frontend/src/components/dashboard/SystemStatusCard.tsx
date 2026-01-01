/**
 * 系统状态卡片组件
 */
import React from 'react';
import { Card, Statistic, Row, Col, Progress } from 'antd';
import { DatabaseOutlined, ClockCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import type { DatabaseStatus } from '../../services/dashboard';

interface SystemStatusCardProps {
  data: DatabaseStatus;
  loading?: boolean;
}

const SystemStatusCard: React.FC<SystemStatusCardProps> = ({ data, loading = false }) => {
  const completenessPercent = Math.round(data.data_completeness * 100);

  return (
    <Card
      title={
        <span>
          <DatabaseOutlined style={{ marginRight: 8 }} />
          数据库状态
        </span>
      }
      loading={loading}
    >
      <Row gutter={16}>
        <Col span={8}>
          <Statistic
            title="股票总数"
            value={data.total_stocks}
            suffix="只"
            valueStyle={{ color: '#1890ff' }}
          />
        </Col>
        <Col span={8}>
          <Statistic
            title={
              <span>
                <ClockCircleOutlined style={{ marginRight: 4 }} />
                最后更新
              </span>
            }
            value={data.last_update}
            valueStyle={{ fontSize: '16px' }}
          />
        </Col>
        <Col span={8}>
          <div>
            <div style={{ marginBottom: 8, color: 'rgba(0, 0, 0, 0.45)' }}>
              <CheckCircleOutlined style={{ marginRight: 4 }} />
              数据完整性
            </div>
            <Progress
              percent={completenessPercent}
              status={completenessPercent >= 80 ? 'success' : completenessPercent >= 50 ? 'normal' : 'exception'}
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
            />
          </div>
        </Col>
      </Row>
    </Card>
  );
};

export default SystemStatusCard;

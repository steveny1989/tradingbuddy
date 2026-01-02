/**
 * 系统状态卡片组件 - 专业交易站风格
 */
import React from 'react';
import { Card, Statistic, Row, Col, Progress, Space, Tag } from 'antd';
import { 
  DatabaseOutlined, 
  ClockCircleOutlined, 
  CheckCircleOutlined,
  SyncOutlined 
} from '@ant-design/icons';
import type { DatabaseStatus } from '../../services/dashboard';

interface SystemStatusCardProps {
  data: DatabaseStatus;
  loading?: boolean;
}

const SystemStatusCard: React.FC<SystemStatusCardProps> = ({ data, loading = false }) => {
  const completenessPercent = Math.round(data.data_completeness * 100);
  
  // 判断数据新鲜度（假设超过1天为过期）
  const isDataFresh = () => {
    if (!data.last_update || data.last_update === '未知') return false;
    try {
      const lastUpdate = new Date(data.last_update);
      const now = new Date();
      const diffHours = (now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60);
      return diffHours < 24;
    } catch {
      return false;
    }
  };

  return (
    <Card
      title={
        <Space>
          <DatabaseOutlined />
          <span>数据引擎</span>
          <Tag 
            icon={<SyncOutlined spin={loading} />} 
            color={isDataFresh() ? 'success' : 'warning'}
          >
            {isDataFresh() ? '实时' : '需更新'}
          </Tag>
        </Space>
      }
      loading={loading}
      bordered={false}
    >
      <Row gutter={16}>
        <Col span={8}>
          <Statistic
            title="股票池"
            value={data.total_stocks}
            suffix="只"
            valueStyle={{ 
              color: '#177ddc',
              fontFamily: 'monospace',
              fontWeight: 'bold'
            }}
          />
        </Col>
        <Col span={8}>
          <Statistic
            title={
              <Space size={4}>
                <ClockCircleOutlined />
                <span>最后同步</span>
              </Space>
            }
            value={data.last_update}
            valueStyle={{ 
              fontSize: '14px',
              fontFamily: 'monospace'
            }}
          />
        </Col>
        <Col span={8}>
          <div>
            <div style={{ marginBottom: 8, fontSize: 14, opacity: 0.65 }}>
              <CheckCircleOutlined style={{ marginRight: 4 }} />
              数据完整性
            </div>
            <Progress
              percent={completenessPercent}
              status={
                completenessPercent >= 90 ? 'success' : 
                completenessPercent >= 70 ? 'normal' : 
                'exception'
              }
              strokeColor={{
                '0%': '#cf1322',
                '50%': '#faad14',
                '100%': '#3f8600',
              }}
              format={(percent) => (
                <span style={{ fontFamily: 'monospace', fontWeight: 'bold' }}>
                  {percent}%
                </span>
              )}
            />
          </div>
        </Col>
      </Row>
    </Card>
  );
};

export default SystemStatusCard;

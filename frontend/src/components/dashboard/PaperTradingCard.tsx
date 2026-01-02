/**
 * 模拟盘概览卡片组件 - 专业交易站风格
 */
import React from 'react';
import { Card, Statistic, Row, Col, Badge, Button, Space, Divider } from 'antd';
import { 
  MonitorOutlined, 
  DollarOutlined, 
  RiseOutlined, 
  FallOutlined,
  ThunderboltOutlined 
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { TRADING_COLORS } from '../../theme/tradingTheme';
import type { PaperTradingStatus } from '../../services/dashboard';

interface PaperTradingCardProps {
  data: PaperTradingStatus;
  loading?: boolean;
}

const PaperTradingCard: React.FC<PaperTradingCardProps> = ({ data, loading = false }) => {
  const navigate = useNavigate();
  const isProfitable = data.daily_pnl >= 0;
  
  // 计算收益率
  const returnRate = data.total_value > 0 
    ? ((data.daily_pnl / data.total_value) * 100) 
    : 0;

  return (
    <Card
      title={
        <Space>
          <MonitorOutlined />
          <span>模拟交易</span>
          <Badge
            status={data.running ? 'processing' : 'default'}
            text={data.running ? '运行中' : '已停止'}
          />
        </Space>
      }
      loading={loading}
      bordered={false}
      extra={
        <Button type="link" onClick={() => navigate('/paper-trading')}>
          进入交易台
        </Button>
      }
    >
      <Row gutter={16}>
        <Col span={12}>
          <Statistic
            title={
              <Space size={4}>
                <DollarOutlined />
                <span>账户总值</span>
              </Space>
            }
            value={data.total_value}
            precision={2}
            suffix="元"
            valueStyle={{ 
              color: '#177ddc',
              fontFamily: 'monospace',
              fontWeight: 'bold',
              fontSize: '24px'
            }}
          />
        </Col>
        <Col span={12}>
          <Statistic
            title={
              <Space size={4}>
                {isProfitable ? (
                  <RiseOutlined style={{ color: TRADING_COLORS.UP }} />
                ) : (
                  <FallOutlined style={{ color: TRADING_COLORS.DOWN }} />
                )}
                <span>当日盈亏</span>
              </Space>
            }
            value={data.daily_pnl}
            precision={2}
            suffix="元"
            valueStyle={{ 
              color: isProfitable ? TRADING_COLORS.UP : TRADING_COLORS.DOWN,
              fontFamily: 'monospace',
              fontWeight: 'bold',
              fontSize: '20px'
            }}
            prefix={isProfitable ? '+' : ''}
          />
        </Col>
      </Row>
      
      <Divider style={{ margin: '16px 0' }} />
      
      <Row gutter={16}>
        <Col span={12}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 12, opacity: 0.65, marginBottom: 4 }}>
              <ThunderboltOutlined /> 日收益率
            </div>
            <div style={{ 
              fontSize: 18, 
              fontWeight: 'bold',
              fontFamily: 'monospace',
              color: isProfitable ? TRADING_COLORS.UP : TRADING_COLORS.DOWN
            }}>
              {isProfitable ? '+' : ''}{returnRate.toFixed(2)}%
            </div>
          </div>
        </Col>
        <Col span={12}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 12, opacity: 0.65, marginBottom: 4 }}>
              运行状态
            </div>
            <div style={{ 
              fontSize: 18, 
              fontWeight: 'bold',
              color: data.running ? '#3f8600' : '#8c8c8c'
            }}>
              {data.running ? '实时监控' : '待启动'}
            </div>
          </div>
        </Col>
      </Row>
    </Card>
  );
};

export default PaperTradingCard;

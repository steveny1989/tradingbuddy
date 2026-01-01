/**
 * 仪表板页面
 */
import { useEffect, useState } from 'react';
import { Typography, Row, Col, Space } from 'antd';
import { SystemStatusCard, PaperTradingCard, RecentBacktestCard } from '../components/dashboard';
import { getDashboardSummary, type DashboardSummary } from '../services/dashboard';
import { LoadingSpinner } from '../components/common';

const { Title } = Typography;

function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const summary = await getDashboardSummary();
      setData(summary);
    } catch (error) {
      console.error('加载仪表板数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !data) {
    return <LoadingSpinner tip="加载仪表板数据..." />;
  }

  // 如果没有数据，显示默认值
  const defaultData: DashboardSummary = {
    database: {
      total_stocks: 0,
      last_update: '未知',
      data_completeness: 0,
    },
    paper_trading: {
      running: false,
      total_value: 0,
      daily_pnl: 0,
    },
    recent_backtests: [],
  };

  const displayData = data || defaultData;

  return (
    <div>
      <Title level={2}>仪表板</Title>
      
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <SystemStatusCard data={displayData.database} loading={loading} />
          </Col>
          <Col xs={24} lg={12}>
            <PaperTradingCard data={displayData.paper_trading} loading={loading} />
          </Col>
        </Row>

        <Row>
          <Col span={24}>
            <RecentBacktestCard data={displayData.recent_backtests} loading={loading} />
          </Col>
        </Row>
      </Space>
    </div>
  );
}

export default Dashboard;

/**
 * 仪表板页面 - 专业交易站风格
 */
import { useEffect, useState } from 'react';
import { Typography, Row, Col, Space, Card, Statistic, Progress } from 'antd';
import { 
  RiseOutlined, 
  FallOutlined, 
  FireOutlined,
  ThunderboltOutlined,
  DashboardOutlined 
} from '@ant-design/icons';
import { SystemStatusCard, PaperTradingCard, RecentBacktestCard } from '../components/dashboard';
import { getDashboardSummary, type DashboardSummary } from '../services/dashboard';
import { getStockList } from '../services/stocks';
import { LoadingSpinner } from '../components/common';
import { TRADING_COLORS } from '../theme/tradingTheme';

const { Title } = Typography;

function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [marketStats, setMarketStats] = useState({
    gainers: 0,
    losers: 0,
    avgChange: 0,
    volume: 0,
  });

  useEffect(() => {
    loadData();
    loadMarketStats();
    
    // 每30秒刷新一次市场数据
    const interval = setInterval(() => {
      loadMarketStats();
    }, 30000);
    
    return () => clearInterval(interval);
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

  const loadMarketStats = async () => {
    try {
      const response = await getStockList({ page: 1, page_size: 5000 });
      const stocks = response.data;
      
      const gainers = stocks.filter(s => s.pct_chg && s.pct_chg > 0).length;
      const losers = stocks.filter(s => s.pct_chg && s.pct_chg < 0).length;
      const validStocks = stocks.filter(s => s.pct_chg !== null && s.pct_chg !== undefined);
      const avgChange = validStocks.length > 0
        ? validStocks.reduce((sum, s) => sum + (s.pct_chg || 0), 0) / validStocks.length
        : 0;
      
      setMarketStats({
        gainers,
        losers,
        avgChange,
        volume: stocks.length,
      });
    } catch (error) {
      console.error('加载市场统计失败:', error);
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
  
  // 计算市场情绪指标（0-100）
  const marketSentiment = marketStats.gainers + marketStats.losers > 0
    ? (marketStats.gainers / (marketStats.gainers + marketStats.losers)) * 100
    : 50;

  return (
    <div>
      <Space align="center" style={{ marginBottom: 24 }}>
        <DashboardOutlined style={{ fontSize: 28, color: TRADING_COLORS.UP }} />
        <Title level={2} style={{ margin: 0 }}>交易控制台</Title>
      </Space>
      
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 市场概览 - 新增 */}
        <Card 
          title={
            <Space>
              <FireOutlined style={{ color: TRADING_COLORS.UP }} />
              <span>市场概览</span>
            </Space>
          }
          bordered={false}
        >
          <Row gutter={[16, 16]}>
            <Col xs={12} sm={6}>
              <Statistic
                title="上涨"
                value={marketStats.gainers}
                suffix="只"
                prefix={<RiseOutlined />}
                valueStyle={{ color: TRADING_COLORS.UP, fontFamily: 'monospace' }}
              />
            </Col>
            <Col xs={12} sm={6}>
              <Statistic
                title="下跌"
                value={marketStats.losers}
                suffix="只"
                prefix={<FallOutlined />}
                valueStyle={{ color: TRADING_COLORS.DOWN, fontFamily: 'monospace' }}
              />
            </Col>
            <Col xs={12} sm={6}>
              <Statistic
                title="平均涨跌"
                value={marketStats.avgChange}
                precision={2}
                suffix="%"
                prefix={marketStats.avgChange > 0 ? '+' : ''}
                valueStyle={{ 
                  color: marketStats.avgChange > 0 ? TRADING_COLORS.UP : 
                         marketStats.avgChange < 0 ? TRADING_COLORS.DOWN : 
                         TRADING_COLORS.STABLE,
                  fontFamily: 'monospace',
                  fontWeight: 'bold'
                }}
              />
            </Col>
            <Col xs={12} sm={6}>
              <div>
                <div style={{ marginBottom: 8, fontSize: 14, opacity: 0.65 }}>
                  <ThunderboltOutlined style={{ marginRight: 4 }} />
                  市场情绪
                </div>
                <Progress
                  percent={marketSentiment}
                  strokeColor={{
                    '0%': TRADING_COLORS.DOWN,
                    '50%': TRADING_COLORS.STABLE,
                    '100%': TRADING_COLORS.UP,
                  }}
                  format={(percent) => `${percent?.toFixed(0)}%`}
                  status="active"
                />
              </div>
            </Col>
          </Row>
        </Card>

        {/* 系统状态和模拟盘 */}
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={12}>
            <SystemStatusCard data={displayData.database} loading={loading} />
          </Col>
          <Col xs={24} lg={12}>
            <PaperTradingCard data={displayData.paper_trading} loading={loading} />
          </Col>
        </Row>

        {/* 最近回测 */}
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

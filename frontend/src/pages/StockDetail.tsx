/**
 * 股票详情页面
 */
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Typography, Card, Row, Col, Space, Button, Descriptions, Spin } from 'antd';
import { ArrowLeftOutlined, StarOutlined, StarFilled } from '@ant-design/icons';
import { KLineChart } from '../components/stocks';
import { getStockDetail, getStockDaily, type Stock, type DailyData } from '../services/stocks';
import { LoadingSpinner } from '../components/common';

const { Title } = Typography;

const FAVORITES_KEY = 'stock_favorites';

function StockDetail() {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const [stock, setStock] = useState<Stock | null>(null);
  const [dailyData, setDailyData] = useState<DailyData[]>([]);
  const [loading, setLoading] = useState(true);
  const [chartLoading, setChartLoading] = useState(false);
  const [timeRange, setTimeRange] = useState<string>('6M'); // 默认6个月
  const [isFavorite, setIsFavorite] = useState(false);

  useEffect(() => {
    if (code) {
      loadStockDetail();
      loadDailyData();
      checkFavorite();
    }
  }, [code]);

  useEffect(() => {
    if (code) {
      loadDailyData();
    }
  }, [timeRange]);

  const checkFavorite = () => {
    if (!code) return;
    const savedFavorites = localStorage.getItem(FAVORITES_KEY);
    if (savedFavorites) {
      const favorites = new Set(JSON.parse(savedFavorites));
      setIsFavorite(favorites.has(code));
    }
  };

  const toggleFavorite = () => {
    if (!code) return;
    
    const savedFavorites = localStorage.getItem(FAVORITES_KEY);
    const favorites = savedFavorites ? new Set(JSON.parse(savedFavorites)) : new Set();
    
    if (favorites.has(code)) {
      favorites.delete(code);
      setIsFavorite(false);
    } else {
      favorites.add(code);
      setIsFavorite(true);
    }
    
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(Array.from(favorites)));
  };

  const loadStockDetail = async () => {
    if (!code) return;
    
    try {
      setLoading(true);
      const data = await getStockDetail(code);
      setStock(data);
    } catch (error) {
      console.error('加载股票详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadDailyData = async () => {
    if (!code) return;
    
    try {
      setChartLoading(true);
      
      // 计算日期范围
      const endDate = new Date();
      const startDate = new Date();
      
      switch (timeRange) {
        case '1M':
          startDate.setMonth(endDate.getMonth() - 1);
          break;
        case '3M':
          startDate.setMonth(endDate.getMonth() - 3);
          break;
        case '6M':
          startDate.setMonth(endDate.getMonth() - 6);
          break;
        case '1Y':
          startDate.setFullYear(endDate.getFullYear() - 1);
          break;
        case 'ALL':
          startDate.setFullYear(2000, 0, 1); // 从2000年开始
          break;
      }

      const data = await getStockDaily(code, {
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
      });
      
      setDailyData(data);
    } catch (error) {
      console.error('加载日线数据失败:', error);
    } finally {
      setChartLoading(false);
    }
  };

  const handleTimeRangeChange = (range: string) => {
    setTimeRange(range);
  };

  if (loading && !stock) {
    return <LoadingSpinner tip="加载股票详情..." />;
  }

  if (!stock) {
    return (
      <div>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/stocks')}>
          返回列表
        </Button>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Typography.Text type="secondary">股票不存在</Typography.Text>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/stocks')}>
            返回列表
          </Button>
          <Button
            icon={isFavorite ? <StarFilled /> : <StarOutlined />}
            onClick={toggleFavorite}
            type={isFavorite ? 'primary' : 'default'}
          >
            {isFavorite ? '已加自选' : '加入自选'}
          </Button>
        </div>

        <div>
          <Title level={2}>
            {stock.name} ({stock.code})
          </Title>
        </div>

        {/* 基本信息卡片 */}
        <Card title="基本信息" loading={loading}>
          <Descriptions column={{ xs: 1, sm: 2, md: 3 }}>
            <Descriptions.Item label="股票代码">{stock.code}</Descriptions.Item>
            <Descriptions.Item label="股票名称">{stock.name}</Descriptions.Item>
            <Descriptions.Item label="市场">{stock.market === 'sh' ? '上海' : '深圳'}</Descriptions.Item>
            <Descriptions.Item label="完整代码">{stock.full_code}</Descriptions.Item>
            {stock.industry && (
              <Descriptions.Item label="行业">{stock.industry}</Descriptions.Item>
            )}
            {stock.total_cap && (
              <Descriptions.Item label="总市值">
                {(stock.total_cap / 100000000).toFixed(2)} 亿元
              </Descriptions.Item>
            )}
            {stock.float_cap && (
              <Descriptions.Item label="流通市值">
                {(stock.float_cap / 100000000).toFixed(2)} 亿元
              </Descriptions.Item>
            )}
            {stock.pe_ttm && (
              <Descriptions.Item label="市盈率(TTM)">{stock.pe_ttm.toFixed(2)}</Descriptions.Item>
            )}
            {stock.pb && (
              <Descriptions.Item label="市净率">{stock.pb.toFixed(2)}</Descriptions.Item>
            )}
            {stock.list_date && (
              <Descriptions.Item label="上市日期">{stock.list_date}</Descriptions.Item>
            )}
          </Descriptions>
        </Card>

        {/* K线图卡片 */}
        <Card title="K线图">
          <Spin spinning={chartLoading} tip="加载图表数据...">
            <div style={{ minHeight: '600px' }}>
              <KLineChart
                data={dailyData}
                timeRange={timeRange}
                onTimeRangeChange={handleTimeRangeChange}
              />
            </div>
          </Spin>
        </Card>
      </Space>
    </div>
  );
}

export default StockDetail;

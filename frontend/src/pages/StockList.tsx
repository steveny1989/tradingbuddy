/**
 * 股票列表页面
 */
import { useEffect, useState } from 'react';
import { Typography, Space, Tabs, Input, Row, Col, Statistic, Card } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { StockTable, IndexBar } from '../components/stocks';
import { getStockList, type Stock, type StockListParams } from '../services/stocks';
import { TRADING_COLORS } from '../theme/tradingTheme';
import type { TablePaginationConfig } from 'antd/es/table';

const { Title } = Typography;
const { Search } = Input;

// 自选股管理（使用localStorage）
const FAVORITES_KEY = 'stock_favorites';

function StockList() {
  const navigate = useNavigate();
  const [allStocks, setAllStocks] = useState<Stock[]>([]);
  const [displayStocks, setDisplayStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [favorites, setFavorites] = useState<Set<string>>(new Set());
  const [activeTab, setActiveTab] = useState<string>('all');
  const [pagination, setPagination] = useState<TablePaginationConfig>({
    current: 1,
    pageSize: 50,
    total: 0,
    showSizeChanger: true,
    showTotal: (total) => `共 ${total} 只股票`,
    pageSizeOptions: ['20', '50', '100', '200'],
  });

  // 加载自选股
  useEffect(() => {
    const savedFavorites = localStorage.getItem(FAVORITES_KEY);
    if (savedFavorites) {
      setFavorites(new Set(JSON.parse(savedFavorites)));
    }
  }, []);

  useEffect(() => {
    loadStocks();
  }, [pagination.current, pagination.pageSize]);

  useEffect(() => {
    filterAndDisplayStocks();
  }, [allStocks, searchQuery, activeTab, favorites]);

  const loadStocks = async () => {
    try {
      setLoading(true);
      
      const params: StockListParams = {
        page: pagination.current,
        page_size: pagination.pageSize,
      };

      const response = await getStockList(params);
      
      // 确保响应数据有效
      if (response && response.data && response.pagination) {
        setAllStocks(response.data);
        
        setPagination((prev) => ({
          ...prev,
          total: response.pagination.total,
        }));
      } else {
        console.error('API 返回数据格式错误:', response);
        setAllStocks([]);
        setPagination((prev) => ({
          ...prev,
          total: 0,
        }));
      }
    } catch (error) {
      console.error('加载股票列表失败:', error);
      setAllStocks([]);
      setPagination((prev) => ({
        ...prev,
        total: 0,
      }));
    } finally {
      setLoading(false);
    }
  };

  const filterAndDisplayStocks = () => {
    let filtered = [...allStocks];

    // 自选股过滤
    if (activeTab === 'favorites') {
      filtered = filtered.filter((stock) => favorites.has(stock.code));
    }

    // 搜索过滤
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (stock) =>
          stock.code.toLowerCase().includes(query) ||
          stock.name.toLowerCase().includes(query) ||
          (stock.industry && stock.industry.toLowerCase().includes(query))
      );
    }

    setDisplayStocks(filtered);
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
  };

  const handleTableChange = (newPagination: TablePaginationConfig) => {
    setPagination(newPagination);
  };

  const handleRowClick = (stock: Stock) => {
    navigate(`/stocks/${stock.code}`);
  };

  const handleToggleFavorite = (code: string) => {
    setFavorites((prev) => {
      const newFavorites = new Set(prev);
      if (newFavorites.has(code)) {
        newFavorites.delete(code);
      } else {
        newFavorites.add(code);
      }
      // 保存到localStorage
      localStorage.setItem(FAVORITES_KEY, JSON.stringify(Array.from(newFavorites)));
      return newFavorites;
    });
  };

  const handleTabChange = (key: string) => {
    setActiveTab(key);
    setSearchQuery(''); // 切换标签时清空搜索
  };

  // 计算统计数据
  const avgPctChg = allStocks.length > 0
    ? allStocks.reduce((sum, s) => sum + (s.pct_chg || 0), 0) / allStocks.filter(s => s.pct_chg !== null && s.pct_chg !== undefined).length
    : 0;
  
  const stats = {
    favorites: favorites.size,
    gainers: allStocks.filter(s => s.pct_chg && s.pct_chg > 0).length,
    losers: allStocks.filter(s => s.pct_chg && s.pct_chg < 0).length,
    avgChange: avgPctChg,
  };

  return (
    <div>
      <Title level={2}>股票浏览</Title>

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 指数行情 */}
        <IndexBar />

        {/* 统计卡片 */}
        <Row gutter={16}>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="我的自选"
                value={stats.favorites}
                suffix="只"
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="上涨"
                value={stats.gainers}
                suffix="只"
                valueStyle={{ color: TRADING_COLORS.UP }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="下跌"
                value={stats.losers}
                suffix="只"
                valueStyle={{ color: TRADING_COLORS.DOWN }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card>
              <Statistic
                title="平均涨跌"
                value={stats.avgChange}
                precision={2}
                suffix="%"
                valueStyle={{ color: stats.avgChange > 0 ? TRADING_COLORS.UP : stats.avgChange < 0 ? TRADING_COLORS.DOWN : TRADING_COLORS.STABLE }}
                prefix={stats.avgChange > 0 ? '+' : ''}
              />
            </Card>
          </Col>
        </Row>

        {/* 搜索框 */}
        <Search
          placeholder="搜索股票代码、名称或行业..."
          allowClear
          enterButton={<SearchOutlined />}
          size="large"
          onSearch={handleSearch}
          onChange={(e) => handleSearch(e.target.value)}
          style={{ maxWidth: 600 }}
        />

        {/* 标签页 */}
        <Tabs
          activeKey={activeTab}
          onChange={handleTabChange}
          items={[
            {
              key: 'all',
              label: `全部股票`,
            },
            {
              key: 'favorites',
              label: `我的自选 (${stats.favorites})`,
            },
          ]}
        />

        {/* 股票表格 */}
        <StockTable
          data={displayStocks}
          loading={loading}
          pagination={activeTab === 'all' ? pagination : false}
          favorites={favorites}
          onRowClick={handleRowClick}
          onChange={handleTableChange}
          onToggleFavorite={handleToggleFavorite}
        />
      </Space>
    </div>
  );
}

export default StockList;

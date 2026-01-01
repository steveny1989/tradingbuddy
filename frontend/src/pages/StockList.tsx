/**
 * 股票列表页面
 */
import { useEffect, useState } from 'react';
import { Typography, Space } from 'antd';
import { useNavigate } from 'react-router-dom';
import { StockTable, SearchBar, FilterPanel, type FilterValues } from '../components/stocks';
import { getStockList, type Stock, type StockListParams } from '../services/stocks';
import type { TablePaginationConfig } from 'antd/es/table';

const { Title } = Typography;

function StockList() {
  const navigate = useNavigate();
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterValues, setFilterValues] = useState<FilterValues>({});
  const [pagination, setPagination] = useState<TablePaginationConfig>({
    current: 1,
    pageSize: 50,
    total: 0,
    showSizeChanger: true,
    showTotal: (total) => `共 ${total} 只股票`,
    pageSizeOptions: ['20', '50', '100', '200'],
  });

  useEffect(() => {
    loadStocks();
  }, [pagination.current, pagination.pageSize, filterValues]);

  const loadStocks = async () => {
    try {
      setLoading(true);
      
      const params: StockListParams = {
        page: pagination.current,
        page_size: pagination.pageSize,
        ...filterValues,
      };

      const response = await getStockList(params);
      
      let filteredData = response.data;
      
      // 客户端搜索过滤
      if (searchQuery) {
        filteredData = filteredData.filter(
          (stock) =>
            stock.code.includes(searchQuery) ||
            stock.name.includes(searchQuery)
        );
      }

      setStocks(filteredData);
      setPagination((prev) => ({
        ...prev,
        total: response.pagination.total,
      }));
    } catch (error) {
      console.error('加载股票列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    // 重新加载数据
    loadStocks();
  };

  const handleFilter = (values: FilterValues) => {
    setFilterValues(values);
    setPagination((prev) => ({ ...prev, current: 1 }));
  };

  const handleResetFilter = () => {
    setFilterValues({});
    setPagination((prev) => ({ ...prev, current: 1 }));
  };

  const handleTableChange = (newPagination: TablePaginationConfig) => {
    setPagination(newPagination);
  };

  const handleRowClick = (stock: Stock) => {
    navigate(`/stocks/${stock.code}`);
  };

  return (
    <div>
      <Title level={2}>股票浏览</Title>

      <Space direction="vertical" size="middle" style={{ width: '100%' }}>
        <SearchBar onSearch={handleSearch} />
        
        <FilterPanel onFilter={handleFilter} onReset={handleResetFilter} />

        <StockTable
          data={stocks}
          loading={loading}
          pagination={pagination}
          onRowClick={handleRowClick}
          onChange={handleTableChange}
        />
      </Space>
    </div>
  );
}

export default StockList;

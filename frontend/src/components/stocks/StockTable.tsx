/**
 * 股票列表表格组件
 */
import React from 'react';
import { Table, Tag } from 'antd';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import type { Stock } from '../../services/stocks';

interface StockTableProps {
  data: Stock[];
  loading: boolean;
  pagination: TablePaginationConfig;
  onRowClick: (stock: Stock) => void;
  onChange: (pagination: TablePaginationConfig) => void;
}

const StockTable: React.FC<StockTableProps> = ({
  data,
  loading,
  pagination,
  onRowClick,
  onChange,
}) => {
  const columns: ColumnsType<Stock> = [
    {
      title: '股票代码',
      dataIndex: 'code',
      key: 'code',
      width: '15%',
      sorter: (a, b) => a.code.localeCompare(b.code),
    },
    {
      title: '股票名称',
      dataIndex: 'name',
      key: 'name',
      width: '20%',
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      title: '市场',
      dataIndex: 'market',
      key: 'market',
      width: '10%',
      render: (market: string) => (
        <Tag color={market === 'sh' ? 'blue' : 'green'}>
          {market === 'sh' ? '上海' : '深圳'}
        </Tag>
      ),
      filters: [
        { text: '上海', value: 'sh' },
        { text: '深圳', value: 'sz' },
      ],
      onFilter: (value, record) => record.market === value,
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      width: '20%',
      ellipsis: true,
    },
    {
      title: '市值（亿）',
      dataIndex: 'market_cap',
      key: 'market_cap',
      width: '15%',
      render: (value: number) => {
        if (!value) return '-';
        return (value / 100000000).toFixed(2);
      },
      sorter: (a, b) => (a.market_cap || 0) - (b.market_cap || 0),
    },
    {
      title: '上市日期',
      dataIndex: 'list_date',
      key: 'list_date',
      width: '15%',
      sorter: (a, b) => (a.list_date || '').localeCompare(b.list_date || ''),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={data}
      rowKey="code"
      loading={loading}
      pagination={pagination}
      onChange={onChange}
      onRow={(record) => ({
        onClick: () => onRowClick(record),
        style: { cursor: 'pointer' },
      })}
      size="middle"
    />
  );
};

export default StockTable;

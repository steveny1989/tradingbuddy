/**
 * 股票列表表格组件
 */
import React from 'react';
import { Table, Tag, Button, Space, Tooltip } from 'antd';
import { StarOutlined, StarFilled, RiseOutlined, FallOutlined } from '@ant-design/icons';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import type { Stock } from '../../services/stocks';

interface StockTableProps {
  data: Stock[];
  loading: boolean;
  pagination: TablePaginationConfig | false;
  favorites: Set<string>;
  onRowClick: (stock: Stock) => void;
  onChange: (pagination: TablePaginationConfig) => void;
  onToggleFavorite: (code: string) => void;
}

const StockTable: React.FC<StockTableProps> = ({
  data,
  loading,
  pagination,
  favorites,
  onRowClick,
  onChange,
  onToggleFavorite,
}) => {
  const columns: ColumnsType<Stock> = [
    {
      title: '自选',
      key: 'favorite',
      width: 60,
      align: 'center',
      fixed: 'left',
      render: (_, record) => (
        <Button
          type="text"
          icon={favorites.has(record.code) ? <StarFilled style={{ color: '#faad14' }} /> : <StarOutlined />}
          onClick={(e) => {
            e.stopPropagation();
            onToggleFavorite(record.code);
          }}
        />
      ),
    },
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      width: 100,
      fixed: 'left',
      render: (code: string) => <span style={{ fontFamily: 'monospace', fontWeight: 500 }}>{code}</span>,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
      fixed: 'left',
      ellipsis: true,
      render: (name: string) => <span style={{ fontWeight: 500 }}>{name}</span>,
    },
    {
      title: '涨跌幅',
      dataIndex: 'pct_chg',
      key: 'pct_chg',
      width: 100,
      align: 'right',
      render: (value: number) => {
        if (value === null || value === undefined) return <span style={{ color: '#999' }}>-</span>;
        const color = value > 0 ? '#cf1322' : value < 0 ? '#3f8600' : '#666';
        const icon = value > 0 ? <RiseOutlined /> : value < 0 ? <FallOutlined /> : null;
        const prefix = value > 0 ? '+' : '';
        return (
          <Space size={4}>
            {icon}
            <span style={{ color, fontWeight: 'bold', fontSize: '14px' }}>
              {prefix}{value.toFixed(2)}%
            </span>
          </Space>
        );
      },
      sorter: (a, b) => ((a as any).pct_chg || 0) - ((b as any).pct_chg || 0),
      showSorterTooltip: { title: '点击排序' },
    },
    {
      title: '市值',
      dataIndex: 'total_cap',
      key: 'total_cap',
      width: 120,
      align: 'right',
      render: (value: number) => {
        if (!value) return <span style={{ color: '#999' }}>-</span>;
        const yi = value / 100000000;
        let displayValue: string;
        let unit: string;
        
        if (yi >= 1000) {
          displayValue = (yi / 1000).toFixed(2);
          unit = '万亿';
        } else {
          displayValue = yi.toFixed(2);
          unit = '亿';
        }
        
        return (
          <Tooltip title={`${yi.toFixed(2)}亿元`}>
            <span style={{ fontFamily: 'monospace' }}>
              {displayValue}<span style={{ fontSize: '12px', color: '#999' }}>{unit}</span>
            </span>
          </Tooltip>
        );
      },
      sorter: (a, b) => ((a as any).total_cap || 0) - ((b as any).total_cap || 0),
      showSorterTooltip: { title: '点击排序' },
    },
    {
      title: '市盈率',
      dataIndex: 'pe_ttm',
      key: 'pe_ttm',
      width: 90,
      align: 'right',
      render: (value: number) => {
        if (!value) return <span style={{ color: '#999' }}>-</span>;
        const color = value < 15 ? '#3f8600' : value < 30 ? '#666' : '#cf1322';
        return <span style={{ color, fontFamily: 'monospace' }}>{value.toFixed(2)}</span>;
      },
      sorter: (a, b) => ((a as any).pe_ttm || 0) - ((b as any).pe_ttm || 0),
    },
    {
      title: '市净率',
      dataIndex: 'pb',
      key: 'pb',
      width: 90,
      align: 'right',
      render: (value: number) => {
        if (!value) return <span style={{ color: '#999' }}>-</span>;
        const color = value < 1 ? '#3f8600' : value < 3 ? '#666' : '#cf1322';
        return <span style={{ color, fontFamily: 'monospace' }}>{value.toFixed(2)}</span>;
      },
      sorter: (a, b) => ((a as any).pb || 0) - ((b as any).pb || 0),
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      width: 120,
      ellipsis: true,
      render: (industry: string) => {
        if (!industry) return <span style={{ color: '#999' }}>-</span>;
        return <Tag color="blue">{industry}</Tag>;
      },
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
      scroll={{ x: 1000 }}
      rowClassName={(record) => 
        favorites.has(record.code) ? 'favorite-row' : ''
      }
    />
  );
};

export default StockTable;

/**
 * 股票列表表格组件
 */
import React, { useState, useEffect } from 'react';
import { Table, Tag, Button, Space, Tooltip } from 'antd';
import { StarOutlined, StarFilled, RiseOutlined, FallOutlined } from '@ant-design/icons';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import type { Stock } from '../../services/stocks';
import { TRADING_COLORS } from '../../theme/tradingTheme';
import { Sparkline } from './Sparkline';

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
  // 跟踪正在移除的自选股（用于淡出动画）
  const [removingFavorites, setRemovingFavorites] = useState<Set<string>>(new Set());

  const handleToggleFavorite = (code: string) => {
    // 如果是取消自选，先添加淡出动画
    if (favorites.has(code)) {
      setRemovingFavorites(new Set([...removingFavorites, code]));
      // 300ms 后执行实际的取消操作
      setTimeout(() => {
        onToggleFavorite(code);
        setRemovingFavorites((prev) => {
          const next = new Set(prev);
          next.delete(code);
          return next;
        });
      }, 300);
    } else {
      // 添加自选立即执行
      onToggleFavorite(code);
    }
  };
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
            handleToggleFavorite(record.code);
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
      title: '走势',
      key: 'sparkline',
      width: 100,
      align: 'center',
      render: (_, record) => (
        <Sparkline 
          data={record.sparkline || []} 
          width={80} 
          height={30}
          showArea={true}
        />
      ),
    },
    {
      title: '涨跌幅',
      dataIndex: 'pct_chg',
      key: 'pct_chg',
      width: 100,
      align: 'right',
      render: (value: number) => {
        if (value === null || value === undefined) return <span style={{ color: '#999' }}>-</span>;
        const color = value > 0 ? TRADING_COLORS.UP : value < 0 ? TRADING_COLORS.DOWN : TRADING_COLORS.STABLE;
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
        const color = value < 15 ? TRADING_COLORS.DOWN : value < 30 ? TRADING_COLORS.STABLE : TRADING_COLORS.UP;
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
        const color = value < 1 ? TRADING_COLORS.DOWN : value < 3 ? TRADING_COLORS.STABLE : TRADING_COLORS.UP;
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
      rowClassName={(record) => {
        const isFavorite = favorites.has(record.code);
        const isRemoving = removingFavorites.has(record.code);
        
        if (isRemoving) {
          return 'favorite-row favorite-row-removing';
        }
        return isFavorite ? 'favorite-row' : '';
      }}
    />
  );
};

export default StockTable;

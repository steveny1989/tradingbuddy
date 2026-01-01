/**
 * 股票搜索栏组件
 */
import React, { useState } from 'react';
import { Input, Space } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

const { Search } = Input;

interface SearchBarProps {
  onSearch: (value: string) => void;
  placeholder?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = '搜索股票代码或名称...',
}) => {
  const [value, setValue] = useState('');

  const handleSearch = (searchValue: string) => {
    onSearch(searchValue.trim());
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setValue(newValue);
    
    // 实时搜索（可选）
    if (newValue.trim() === '') {
      onSearch('');
    }
  };

  return (
    <Space style={{ width: '100%', marginBottom: 16 }}>
      <Search
        placeholder={placeholder}
        allowClear
        enterButton={<SearchOutlined />}
        size="large"
        value={value}
        onChange={handleChange}
        onSearch={handleSearch}
        style={{ width: 400 }}
      />
    </Space>
  );
};

export default SearchBar;

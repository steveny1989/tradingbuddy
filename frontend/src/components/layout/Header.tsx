/**
 * 顶部导航栏组件
 */
import React from 'react';
import { Layout, Typography, Space, Badge } from 'antd';
import { DatabaseOutlined, ApiOutlined } from '@ant-design/icons';

const { Header: AntHeader } = Layout;
const { Title } = Typography;

interface HeaderProps {
  title?: string;
}

const Header: React.FC<HeaderProps> = ({ title = 'TradingBuddy' }) => {
  return (
    <AntHeader
      style={{
        background: '#fff',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid #f0f0f0',
        height: '64px',
      }}
    >
      <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
        {title}
      </Title>

      <Space size="large">
        <Space>
          <DatabaseOutlined style={{ fontSize: '16px', color: '#52c41a' }} />
          <span style={{ fontSize: '14px', color: '#666' }}>数据库已连接</span>
        </Space>
        <Space>
          <ApiOutlined style={{ fontSize: '16px', color: '#1890ff' }} />
          <Badge status="success" text="API正常" />
        </Space>
      </Space>
    </AntHeader>
  );
};

export default Header;

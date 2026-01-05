/**
 * 一键同步按钮组件
 * 
 * 提供一键数据同步功能，显示同步进度和状态
 */
import React, { useState, useEffect } from 'react';
import { Button, Progress, Space, Typography, Alert, Spin } from 'antd';
import { SyncOutlined, CheckCircleOutlined, WarningOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { getUpdateWarningLevel, formatRelativeTime } from '../../utils/picker';
import './OneSyncButton.css';

const { Text } = Typography;

/**
 * 同步状态接口
 */
export interface SyncStatus {
  syncing: boolean;
  progress: number;           // 0-100
  currentStock?: string;      // 当前正在同步的股票
  lastUpdate?: string;        // 最后更新时间（ISO字符串）
  error?: string;             // 错误信息
  totalStocks?: number;       // 总股票数
  syncedStocks?: number;      // 已同步股票数
}

/**
 * OneSyncButton 组件属性
 */
export interface OneSyncButtonProps {
  onSync: () => Promise<void>;
  syncStatus: SyncStatus;
}

/**
 * 一键同步按钮组件
 * 
 * 功能：
 * - 点击触发数据同步
 * - 显示同步进度条
 * - 显示当前同步状态
 * - 根据最后更新时间显示警告
 */
const OneSyncButton: React.FC<OneSyncButtonProps> = ({ onSync, syncStatus }) => {
  const [loading, setLoading] = useState(false);

  // 计算警告级别
  const warningLevel = syncStatus.lastUpdate 
    ? getUpdateWarningLevel(syncStatus.lastUpdate)
    : 'none';

  // 处理同步按钮点击
  const handleSync = async () => {
    setLoading(true);
    try {
      await onSync();
    } catch (error) {
      console.error('同步失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 渲染警告信息
  const renderWarning = () => {
    if (!syncStatus.lastUpdate) {
      return (
        <Alert
          message="数据未初始化"
          description="请点击同步按钮获取最新数据"
          type="warning"
          showIcon
          icon={<WarningOutlined />}
        />
      );
    }

    if (warningLevel === 'red') {
      return (
        <Alert
          message="数据已过期"
          description={`最后更新：${formatRelativeTime(syncStatus.lastUpdate)}，建议立即同步`}
          type="error"
          showIcon
          icon={<CloseCircleOutlined />}
        />
      );
    }

    if (warningLevel === 'yellow') {
      return (
        <Alert
          message="数据需要更新"
          description={`最后更新：${formatRelativeTime(syncStatus.lastUpdate)}`}
          type="warning"
          showIcon
          icon={<WarningOutlined />}
        />
      );
    }

    return (
      <Alert
        message="数据已是最新"
        description={`最后更新：${formatRelativeTime(syncStatus.lastUpdate)}`}
        type="success"
        showIcon
        icon={<CheckCircleOutlined />}
      />
    );
  };

  // 渲染同步进度
  const renderProgress = () => {
    if (!syncStatus.syncing) {
      return null;
    }

    return (
      <div className="sync-progress">
        <Space direction="vertical" style={{ width: '100%' }} size="small">
          <div className="progress-header">
            <Spin size="small" />
            <Text strong>正在同步数据...</Text>
          </div>
          
          <Progress 
            percent={syncStatus.progress} 
            status="active"
            strokeColor={{
              '0%': '#667eea',
              '100%': '#764ba2',
            }}
          />
          
          {syncStatus.currentStock && (
            <Text type="secondary" className="current-stock">
              当前：{syncStatus.currentStock}
            </Text>
          )}
          
          {syncStatus.totalStocks && syncStatus.syncedStocks !== undefined && (
            <Text type="secondary" className="sync-stats">
              已同步 {syncStatus.syncedStocks} / {syncStatus.totalStocks} 只股票
            </Text>
          )}
        </Space>
      </div>
    );
  };

  // 渲染错误信息
  const renderError = () => {
    if (!syncStatus.error) {
      return null;
    }

    return (
      <Alert
        message="同步失败"
        description={syncStatus.error}
        type="error"
        showIcon
        closable
      />
    );
  };

  return (
    <div className="one-sync-button-container">
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* 警告信息 */}
        {renderWarning()}

        {/* 同步按钮 */}
        <div className="sync-button-wrapper">
          <Button
            type="primary"
            size="large"
            icon={<SyncOutlined spin={syncStatus.syncing} />}
            onClick={handleSync}
            loading={loading || syncStatus.syncing}
            disabled={syncStatus.syncing}
            block
            className="sync-button"
          >
            {syncStatus.syncing ? '同步中...' : '一键同步数据'}
          </Button>
        </div>

        {/* 同步进度 */}
        {renderProgress()}

        {/* 错误信息 */}
        {renderError()}
      </Space>
    </div>
  );
};

export default OneSyncButton;

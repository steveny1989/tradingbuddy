/**
 * 能量球同步组件
 * Energy Orb Sync Component
 */
import React from 'react';
import { motion } from 'framer-motion';
import { SyncOutlined, CheckOutlined } from '@ant-design/icons';

interface EnergyOrbProps {
  status: 'idle' | 'syncing' | 'completed';
  progress?: number;
  onClick?: () => void;
}

const EnergyOrb: React.FC<EnergyOrbProps> = ({ status, progress = 0, onClick }) => {
  const getIcon = () => {
    switch (status) {
      case 'syncing':
        return <SyncOutlined style={{ fontSize: 24, color: '#fff' }} spin />;
      case 'completed':
        return <CheckOutlined style={{ fontSize: 24, color: '#fff' }} />;
      default:
        return <SyncOutlined style={{ fontSize: 24, color: '#fff' }} />;
    }
  };

  const getLabel = () => {
    switch (status) {
      case 'syncing':
        return `${progress}%`;
      case 'completed':
        return '完成';
      default:
        return '同步';
    }
  };

  return (
    <motion.div
      className={`energy-orb ${status}`}
      onClick={onClick}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 4,
      }}
    >
      {getIcon()}
      <div style={{ 
        fontSize: 12, 
        color: '#fff', 
        fontWeight: 500,
        textAlign: 'center'
      }}>
        {getLabel()}
      </div>
    </motion.div>
  );
};

export default EnergyOrb;

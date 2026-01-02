/**
 * 股票信号方块组件
 * Stock Signal Box Component
 */
import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

interface StockSignalBoxProps {
  code: string;
  name: string;
  price: number;
  pctChange: number;
  signal: 'buy' | 'sell' | 'hold' | 'stop_loss';
  profitPct?: number;
  alert?: {
    type: 'stop_loss' | 'take_profit';
    message: string;
  };
}

const StockSignalBox: React.FC<StockSignalBoxProps> = ({
  code,
  name,
  price,
  pctChange,
  signal,
  profitPct = 0,
  alert,
}) => {
  const navigate = useNavigate();

  const getSignalLabel = () => {
    switch (signal) {
      case 'buy':
        return '买入';
      case 'sell':
        return '卖出';
      case 'stop_loss':
        return '止损!';
      default:
        return '观望';
    }
  };

  const getSignalColor = () => {
    switch (signal) {
      case 'buy':
        return '#10b981'; // 绿色
      case 'sell':
      case 'stop_loss':
        return '#ef4444'; // 红色
      default:
        return '#f59e0b'; // 黄色
    }
  };

  const getPriceColor = () => {
    return pctChange >= 0 ? '#ef4444' : '#10b981'; // 红涨绿跌
  };

  const getProfitColor = () => {
    return profitPct >= 0 ? '#ef4444' : '#10b981'; // 红涨绿跌
  };

  const handleClick = () => {
    navigate(`/picker/stocks/${code}`);
  };

  return (
    <motion.div
      className={`stock-signal-box signal-${signal === 'stop_loss' ? 'stop-loss' : signal}`}
      onClick={handleClick}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      style={{
        position: 'relative',
      }}
    >
      {/* 预警标记 */}
      {alert && (
        <div
          style={{
            position: 'absolute',
            top: -8,
            right: -8,
            width: 20,
            height: 20,
            borderRadius: '50%',
            background: alert.type === 'stop_loss' ? '#ef4444' : '#10b981',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 12,
            color: '#fff',
            fontWeight: 'bold',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
          }}
        >
          !
        </div>
      )}

      {/* 股票名称 */}
      <div
        style={{
          fontSize: 16,
          fontWeight: 600,
          color: '#fff',
          marginBottom: 8,
          textAlign: 'center',
        }}
      >
        {name}
      </div>

      {/* 价格和涨跌幅 */}
      <div
        style={{
          fontSize: 20,
          fontWeight: 'bold',
          color: getPriceColor(),
          textAlign: 'center',
          marginBottom: 4,
        }}
      >
        ¥{(price || 0).toFixed(2)}
      </div>

      <div
        style={{
          fontSize: 14,
          color: getPriceColor(),
          textAlign: 'center',
          marginBottom: 12,
        }}
      >
        {(pctChange || 0) >= 0 ? '+' : ''}{((pctChange || 0) * 100).toFixed(2)}%
      </div>

      {/* 盈亏显示 */}
      {profitPct !== 0 && (
        <div
          style={{
            fontSize: 12,
            color: getProfitColor(),
            textAlign: 'center',
            marginBottom: 8,
          }}
        >
          持仓: {profitPct >= 0 ? '+' : ''}{(profitPct * 100).toFixed(2)}%
        </div>
      )}

      {/* 信号标签 */}
      <div
        style={{
          padding: '6px 12px',
          borderRadius: 8,
          background: getSignalColor(),
          color: '#fff',
          fontSize: 14,
          fontWeight: 600,
          textAlign: 'center',
        }}
      >
        {getSignalLabel()}
      </div>

      {/* 预警消息 */}
      {alert && (
        <div
          style={{
            marginTop: 8,
            padding: 8,
            borderRadius: 6,
            background: alert.type === 'stop_loss' 
              ? 'rgba(239, 68, 68, 0.2)' 
              : 'rgba(16, 185, 129, 0.2)',
            fontSize: 12,
            color: '#fff',
            textAlign: 'center',
          }}
        >
          {alert.message}
        </div>
      )}
    </motion.div>
  );
};

export default StockSignalBox;

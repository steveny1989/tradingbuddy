/**
 * 策略卡片组件
 * Strategy Card Component
 */
import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

interface StrategyCardProps {
  code: string;
  name: string;
  price: number;
  confidenceScore: number;
  strategyName: string;
  reason: string;
  onAddToWatchlist?: (stock: { code: string; name: string; price: number }) => void;
  isInWatchlist?: boolean;
}

const StrategyCard: React.FC<StrategyCardProps> = ({
  code,
  name,
  price,
  confidenceScore,
  strategyName,
  reason,
  onAddToWatchlist,
  isInWatchlist = false,
}) => {
  const navigate = useNavigate();

  const getConfidenceColor = () => {
    if (confidenceScore >= 70) return '#10b981'; // 绿色
    if (confidenceScore >= 50) return '#f59e0b'; // 黄色
    return '#6b7280'; // 灰色
  };

  const handleClick = () => {
    navigate(`/picker/stocks/${code}`);
  };

  const handleAddToWatchlist = (e: React.MouseEvent) => {
    console.log('StrategyCard handleAddToWatchlist 被调用');
    console.log('isInWatchlist:', isInWatchlist);
    console.log('onAddToWatchlist:', onAddToWatchlist);
    console.log('stock info:', { code, name, price });
    e.preventDefault();
    e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击
    if (onAddToWatchlist && !isInWatchlist) {
      console.log('调用 onAddToWatchlist 回调');
      onAddToWatchlist({ code, name, price });
    } else {
      console.log('未调用回调，原因:', { 
        hasCallback: !!onAddToWatchlist, 
        isInWatchlist 
      });
    }
  };

  return (
    <motion.div
      className="strategy-card"
      onClick={handleClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.98 }}
    >
      {/* 信心指数 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          marginBottom: 12,
        }}
      >
        <span style={{ fontSize: 24 }}>🎯</span>
        <span
          style={{
            fontSize: 28,
            fontWeight: 'bold',
            color: getConfidenceColor(),
          }}
        >
          {confidenceScore}分
        </span>
      </div>

      {/* 股票名称和价格 */}
      <div style={{ marginBottom: 12 }}>
        <div
          style={{
            fontSize: 18,
            fontWeight: 600,
            color: '#fff',
            marginBottom: 4,
          }}
        >
          {name}
        </div>
        <div
          style={{
            fontSize: 16,
            color: '#9ca3af',
          }}
        >
          ¥{price.toFixed(2)}
        </div>
      </div>

      {/* 策略标签和加入自选按钮 */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 12,
        }}
      >
        <div
          style={{
            display: 'inline-block',
            padding: '6px 12px',
            borderRadius: 8,
            background: 'rgba(59, 130, 246, 0.2)',
            border: '1px solid rgba(59, 130, 246, 0.5)',
            color: '#60a5fa',
            fontSize: 14,
            fontWeight: 600,
          }}
        >
          {strategyName}
        </div>
        
        {/* 加入自选按钮 */}
        <button
          onClick={handleAddToWatchlist}
          disabled={isInWatchlist}
          style={{
            position: 'relative',
            zIndex: 10,
            padding: '6px 12px',
            borderRadius: 8,
            background: isInWatchlist 
              ? 'rgba(107, 114, 128, 0.2)' 
              : 'rgba(16, 185, 129, 0.2)',
            border: isInWatchlist 
              ? '1px solid rgba(107, 114, 128, 0.5)' 
              : '1px solid rgba(16, 185, 129, 0.5)',
            color: isInWatchlist ? '#6b7280' : '#10b981',
            fontSize: 12,
            fontWeight: 600,
            cursor: isInWatchlist ? 'not-allowed' : 'pointer',
            outline: 'none',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            if (!isInWatchlist) {
              e.currentTarget.style.transform = 'scale(1.05)';
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)';
          }}
        >
          {isInWatchlist ? '✓ 已加入' : '+ 加入自选'}
        </button>
      </div>

      {/* 大白话理由 */}
      <div
        style={{
          fontSize: 14,
          color: '#d1d5db',
          lineHeight: 1.6,
          marginTop: 12,
        }}
      >
        {reason}
      </div>

      {/* K线图占位（未来实现） */}
      <div
        style={{
          marginTop: 16,
          height: 60,
          borderRadius: 8,
          background: 'rgba(59, 130, 246, 0.05)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#6b7280',
          fontSize: 12,
        }}
      >
        K线图
      </div>
    </motion.div>
  );
};

export default StrategyCard;

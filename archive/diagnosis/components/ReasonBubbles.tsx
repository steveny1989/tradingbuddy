/**
 * 诊断理由气泡链组件
 * Reason Bubbles - 把文字理由变成可视化气泡标签
 */
import React from 'react';
import { motion } from 'framer-motion';
import './ReasonBubbles.css';

interface ReasonBubblesProps {
  reasons: string[];
  type?: 'technical' | 'liquidity' | 'market';
}

const ReasonBubbles: React.FC<ReasonBubblesProps> = ({ reasons, type = 'technical' }) => {
  // 根据理由内容自动匹配图标
  const getReasonIcon = (reason: string): string => {
    // 技术面相关
    if (reason.includes('均线') || reason.includes('MA')) return '📈';
    if (reason.includes('成交量') || reason.includes('放量')) return '📊';
    if (reason.includes('MACD')) return '🔄';
    if (reason.includes('RSI')) return '⚡';
    if (reason.includes('突破') || reason.includes('上涨')) return '🚀';
    if (reason.includes('下跌') || reason.includes('回调')) return '📉';
    
    // 流动性相关
    if (reason.includes('流动性') || reason.includes('换手')) return '💧';
    if (reason.includes('活跃')) return '🔥';
    if (reason.includes('冷清') || reason.includes('低迷')) return '❄️';
    
    // 市场环境相关
    if (reason.includes('大盘') || reason.includes('指数')) return '🌍';
    if (reason.includes('行业') || reason.includes('板块')) return '🏢';
    if (reason.includes('市场')) return '📍';
    
    // 默认图标
    return '✓';
  };

  // 根据理由内容判断是正面还是负面
  const getReasonSentiment = (reason: string): 'positive' | 'negative' | 'neutral' => {
    const positiveKeywords = ['上涨', '突破', '放量', '活跃', '强势', '金叉', '多头', '支撑'];
    const negativeKeywords = ['下跌', '回调', '缩量', '冷清', '弱势', '死叉', '空头', '压力'];
    
    const hasPositive = positiveKeywords.some(keyword => reason.includes(keyword));
    const hasNegative = negativeKeywords.some(keyword => reason.includes(keyword));
    
    if (hasPositive && !hasNegative) return 'positive';
    if (hasNegative && !hasPositive) return 'negative';
    return 'neutral';
  };

  // 容器动画变体
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  // 气泡动画变体
  const bubbleVariants = {
    hidden: { 
      opacity: 0, 
      scale: 0.8,
      y: 20,
    },
    visible: { 
      opacity: 1, 
      scale: 1,
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 200,
        damping: 15,
      },
    },
  };

  return (
    <motion.div
      className="reason-bubbles"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {reasons.map((reason, index) => {
        const icon = getReasonIcon(reason);
        const sentiment = getReasonSentiment(reason);
        
        return (
          <motion.div
            key={index}
            className={`reason-bubble ${sentiment}`}
            variants={bubbleVariants}
            whileHover={{ 
              scale: 1.05,
              boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)',
            }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="bubble-icon">{icon}</span>
            <span className="bubble-text">{reason}</span>
            
            {/* 情绪指示器 */}
            <div className={`sentiment-indicator ${sentiment}`}>
              {sentiment === 'positive' && '✓'}
              {sentiment === 'negative' && '✗'}
              {sentiment === 'neutral' && '•'}
            </div>
          </motion.div>
        );
      })}
    </motion.div>
  );
};

export default ReasonBubbles;

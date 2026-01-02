/**
 * 股票评价卡片组件
 * Stock Rating Card Component
 */
import React from 'react';
import { motion } from 'framer-motion';

interface StockRatingProps {
  score: number;
  stars: number;
  pros: string[];
  cons: string[];
  suggestion: string;
  riskLevel: string;
}

const StockRatingCard: React.FC<StockRatingProps> = ({
  score,
  stars,
  pros,
  cons,
  suggestion,
  riskLevel,
}) => {
  // 根据分数获取颜色
  const getScoreColor = () => {
    if (score >= 80) return '#10b981'; // 绿色
    if (score >= 60) return '#f59e0b'; // 黄色
    if (score >= 40) return '#f97316'; // 橙色
    return '#ef4444'; // 红色
  };

  // 根据风险等级获取颜色
  const getRiskColor = () => {
    if (riskLevel === '较低') return '#10b981';
    if (riskLevel === '中等') return '#f59e0b';
    return '#ef4444';
  };

  // 渲染星星
  const renderStars = () => {
    return Array.from({ length: 5 }, (_, i) => (
      <span
        key={i}
        style={{
          fontSize: 24,
          color: i < stars ? '#fbbf24' : '#4b5563',
          marginRight: 4,
        }}
      >
        {i < stars ? '⭐' : '☆'}
      </span>
    ));
  };

  return (
    <motion.div
      className="glass-card"
      style={{ padding: 24 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* 标题 */}
      <div style={{ marginBottom: 20 }}>
        <h3 style={{ color: '#fff', fontSize: 20, fontWeight: 600, margin: 0 }}>
          🎯 综合评价
        </h3>
      </div>

      {/* 评分和星级 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: 24,
          padding: 20,
          background: 'rgba(59, 130, 246, 0.1)',
          borderRadius: 12,
          border: '1px solid rgba(59, 130, 246, 0.2)',
        }}
      >
        <div>
          <div style={{ marginBottom: 8 }}>{renderStars()}</div>
          <div style={{ color: '#9ca3af', fontSize: 14 }}>综合评分</div>
        </div>
        <div
          style={{
            fontSize: 48,
            fontWeight: 'bold',
            color: getScoreColor(),
          }}
        >
          {score}
          <span style={{ fontSize: 24, color: '#9ca3af' }}>分</span>
        </div>
      </div>

      {/* 优点 */}
      {pros.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <div
            style={{
              color: '#10b981',
              fontSize: 16,
              fontWeight: 600,
              marginBottom: 12,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <span>✅</span>
            <span>优点</span>
          </div>
          <div style={{ paddingLeft: 28 }}>
            {pros.map((pro, index) => (
              <div
                key={index}
                style={{
                  color: '#d1d5db',
                  fontSize: 14,
                  lineHeight: 1.8,
                  marginBottom: 8,
                }}
              >
                • {pro}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 缺点/注意事项 */}
      {cons.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <div
            style={{
              color: '#f59e0b',
              fontSize: 16,
              fontWeight: 600,
              marginBottom: 12,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}
          >
            <span>⚠️</span>
            <span>注意</span>
          </div>
          <div style={{ paddingLeft: 28 }}>
            {cons.map((con, index) => (
              <div
                key={index}
                style={{
                  color: '#d1d5db',
                  fontSize: 14,
                  lineHeight: 1.8,
                  marginBottom: 8,
                }}
              >
                • {con}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 投资建议 */}
      <div
        style={{
          padding: 16,
          background: 'rgba(99, 102, 241, 0.1)',
          borderRadius: 12,
          border: '1px solid rgba(99, 102, 241, 0.2)',
          marginBottom: 16,
        }}
      >
        <div
          style={{
            color: '#818cf8',
            fontSize: 14,
            fontWeight: 600,
            marginBottom: 8,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <span>💡</span>
          <span>建议</span>
        </div>
        <div style={{ color: '#d1d5db', fontSize: 14, lineHeight: 1.6 }}>
          {suggestion}
        </div>
      </div>

      {/* 风险等级 */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <span style={{ color: '#9ca3af', fontSize: 14 }}>🎚️ 风险等级</span>
        <span
          style={{
            color: getRiskColor(),
            fontSize: 16,
            fontWeight: 600,
          }}
        >
          {riskLevel}
        </span>
      </div>

      {/* 免责声明 */}
      <div
        style={{
          marginTop: 16,
          padding: 12,
          background: 'rgba(107, 114, 128, 0.1)',
          borderRadius: 8,
          border: '1px solid rgba(107, 114, 128, 0.2)',
        }}
      >
        <div style={{ color: '#6b7280', fontSize: 12, lineHeight: 1.6 }}>
          ⚠️ 以上评价基于技术和财务指标分析，仅供参考，不构成投资建议。投资有风险，入市需谨慎。
        </div>
      </div>
    </motion.div>
  );
};

export default StockRatingCard;

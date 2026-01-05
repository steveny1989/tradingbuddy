/**
 * AI 决策总结卡片
 * AI Decision Summary Card - 金字招牌组件
 */
import React from 'react';
import { motion } from 'framer-motion';
import './AIDecisionCard.css';

interface AIDecisionCardProps {
  overallScore: number;
  signalLight: {
    color: string;
    label: string;
    confidence: number;
    reason: string;
  };
  diagnosisText: string;
  stockName: string;
}

const AIDecisionCard: React.FC<AIDecisionCardProps> = ({
  overallScore,
  signalLight,
  diagnosisText,
  stockName,
}) => {
  // 根据评分获取阶段描述
  const getPhaseDescription = (score: number): string => {
    if (score >= 80) return '黄金布局期';
    if (score >= 60) return '观察窗口期';
    if (score >= 40) return '谨慎观望期';
    return '高风险区域';
  };

  // 根据信号灯颜色获取建议
  const getRecommendation = (color: string): string => {
    switch (color) {
      case 'GREEN':
        return '基本面非常硬朗，技术面刚抬头，建议加入自选重点观察';
      case 'YELLOW':
        return '目前处于调整期，建议等待更明确的信号再做决策';
      case 'RED':
        return '当前风险较高，建议观望或考虑止损离场';
      default:
        return '请谨慎评估风险后再做决策';
    }
  };

  // 获取信号灯 emoji
  const getSignalEmoji = (color: string): string => {
    switch (color) {
      case 'GREEN': return '🟢';
      case 'YELLOW': return '🟡';
      case 'RED': return '🔴';
      default: return '⚪';
    }
  };

  // 提取诊断意见的第一段作为简短总结
  const getShortSummary = (text: string): string => {
    const firstParagraph = text.split('\n\n')[0];
    return firstParagraph.length > 100 
      ? firstParagraph.substring(0, 100) + '...' 
      : firstParagraph;
  };

  return (
    <motion.div
      className="ai-decision-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* 呼吸光晕效果 */}
      <div className="breathing-glow"></div>

      {/* 卡片内容 */}
      <div className="card-content">
        {/* 左侧：AI 决策核心 */}
        <div className="decision-core">
          <div className="ai-badge">
            <span className="ai-icon">🤖</span>
            <span className="ai-label">AI 诊断</span>
          </div>

          <div className="phase-info">
            <div className="phase-label">本股目前处于</div>
            <div className="phase-value">{getPhaseDescription(overallScore)}</div>
          </div>

          <div className="confidence-meter">
            <div className="confidence-label">
              <span>信心指数</span>
              <span className="confidence-score">{Math.round(signalLight.confidence)} 分</span>
            </div>
            <div className="confidence-bar">
              <motion.div
                className="confidence-fill"
                initial={{ width: 0 }}
                animate={{ width: `${signalLight.confidence}%` }}
                transition={{ duration: 1, delay: 0.3 }}
              />
            </div>
          </div>
        </div>

        {/* 右侧：信号灯和建议 */}
        <div className="decision-details">
          <div className="signal-status">
            <span className="signal-emoji">{getSignalEmoji(signalLight.color)}</span>
            <span className="signal-text">{signalLight.label}</span>
          </div>

          <div className="recommendation">
            <div className="recommendation-icon">💡</div>
            <div className="recommendation-text">
              {getRecommendation(signalLight.color)}
            </div>
          </div>

          <div className="quick-summary">
            {getShortSummary(diagnosisText)}
          </div>
        </div>
      </div>

      {/* 底部装饰线 */}
      <div className="card-footer">
        <div className="footer-line"></div>
        <div className="footer-text">
          基于 {stockName} 的多维度量化分析
        </div>
      </div>
    </motion.div>
  );
};

export default AIDecisionCard;

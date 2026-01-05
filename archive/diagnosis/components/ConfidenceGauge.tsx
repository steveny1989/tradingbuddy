import React from 'react';
import './ConfidenceGauge.css';

interface ConfidenceGaugeProps {
  score: number; // 0-100
  conclusion: string;
  level: 'low' | 'medium' | 'high';
}

export const ConfidenceGauge: React.FC<ConfidenceGaugeProps> = ({ score, conclusion, level }) => {
  // 计算指针角度 (0-180度)
  const angle = (score / 100) * 180;
  
  // 根据分数确定颜色
  const getColor = () => {
    if (score >= 70) return '#fbbf24'; // 金色
    if (score >= 40) return '#60a5fa'; // 蓝色
    return '#94a3b8'; // 灰色
  };

  const getLevelText = () => {
    if (score >= 70) return '黄金布局期';
    if (score >= 40) return '观察期';
    return '谨慎期';
  };

  return (
    <div className="confidence-gauge">
      <div className="gauge-container">
        <svg viewBox="0 0 200 120" className="gauge-svg">
          {/* 背景弧线 */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="20"
            strokeLinecap="round"
          />
          
          {/* 分段彩色弧线 */}
          <path
            d="M 20 100 A 80 80 0 0 1 73 36"
            fill="none"
            stroke="rgba(148, 163, 184, 0.5)"
            strokeWidth="20"
            strokeLinecap="round"
          />
          <path
            d="M 73 36 A 80 80 0 0 1 127 36"
            fill="none"
            stroke="rgba(96, 165, 250, 0.5)"
            strokeWidth="20"
            strokeLinecap="round"
          />
          <path
            d="M 127 36 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="rgba(251, 191, 36, 0.5)"
            strokeWidth="20"
            strokeLinecap="round"
          />
          
          {/* 指针 */}
          <g transform={`rotate(${angle - 90} 100 100)`}>
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="30"
              stroke={getColor()}
              strokeWidth="3"
              strokeLinecap="round"
              className="gauge-needle"
            />
            <circle cx="100" cy="100" r="6" fill={getColor()} />
          </g>
        </svg>
        
        <div className="gauge-score">
          <span className="score-value" style={{ color: getColor() }}>{score}</span>
          <span className="score-label">信心指数</span>
        </div>
      </div>
      
      <div className="gauge-conclusion">
        <div className="conclusion-badge" style={{ borderColor: getColor(), color: getColor() }}>
          {getLevelText()}
        </div>
        <p className="conclusion-text">{conclusion}</p>
      </div>
    </div>
  );
};

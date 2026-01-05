import React from 'react';
import './ValueIndicator.css';

interface ValueIndicatorProps {
  title: string;
  value: number | string;
  status: 'excellent' | 'good' | 'normal' | 'poor';
  statusText: string;
  position: number; // 0-100, 在行业中的位置
  unit?: string;
}

export const ValueIndicator: React.FC<ValueIndicatorProps> = ({
  title,
  value,
  status,
  statusText,
  position,
  unit = ''
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'excellent': return '#10b981'; // 绿色
      case 'good': return '#fbbf24'; // 金色
      case 'normal': return '#60a5fa'; // 蓝色
      case 'poor': return '#ef4444'; // 红色
      default: return '#94a3b8';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'excellent': return '🏆';
      case 'good': return '✨';
      case 'normal': return '📊';
      case 'poor': return '⚠️';
      default: return '📈';
    }
  };

  return (
    <div className="value-indicator">
      <div className="indicator-header">
        <span className="indicator-title">{title}</span>
        <div className="indicator-badge" style={{ backgroundColor: getStatusColor() }}>
          <span className="badge-icon">{getStatusIcon()}</span>
          <span className="badge-text">{statusText}</span>
        </div>
      </div>
      
      <div className="indicator-value">
        <span className="value-number">{value}</span>
        {unit && <span className="value-unit">{unit}</span>}
      </div>
      
      <div className="indicator-bar">
        <div className="bar-track">
          <div 
            className="bar-fill"
            style={{ 
              width: `${position}%`,
              background: `linear-gradient(90deg, ${getStatusColor()}, ${getStatusColor()}88)`
            }}
          />
          <div 
            className="bar-marker"
            style={{ 
              left: `${position}%`,
              backgroundColor: getStatusColor()
            }}
          >
            <div className="marker-pulse" style={{ backgroundColor: getStatusColor() }} />
          </div>
        </div>
        <div className="bar-labels">
          <span>行业低位</span>
          <span>行业高位</span>
        </div>
      </div>
      
      <div className="indicator-insight">
        💡 <span>在同行业中排名前 {100 - position}%</span>
      </div>
    </div>
  );
};

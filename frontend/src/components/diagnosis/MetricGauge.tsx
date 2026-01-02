/**
 * 指标仪表盘组件
 * Metric Gauge - 把冰冷数字变成情绪表盘
 */
import React from 'react';
import { motion } from 'framer-motion';
import './MetricGauge.css';

interface MetricGaugeProps {
  title: string;
  value: number;
  unit?: string;
  min?: number;
  max?: number;
  thresholds?: {
    low: number;    // 低于此值为绿色（便宜/好）
    high: number;   // 高于此值为红色（贵/差）
  };
  comparison?: string; // 对比描述，如 "比90%同行便宜"
  icon?: string;
  reverse?: boolean; // 是否反转颜色逻辑（如 ROE 越高越好）
}

const MetricGauge: React.FC<MetricGaugeProps> = ({
  title,
  value,
  unit = '',
  min = 0,
  max = 100,
  thresholds = { low: 33, high: 66 },
  comparison,
  icon = '📊',
  reverse = false,
}) => {
  // 计算百分比位置
  const percentage = Math.min(Math.max(((value - min) / (max - min)) * 100, 0), 100);

  // 获取颜色
  const getColor = () => {
    const normalizedValue = (value - min) / (max - min) * 100;
    
    if (reverse) {
      // 反转逻辑：值越高越好（如 ROE）
      if (normalizedValue >= thresholds.high) return '#10b981'; // 绿色
      if (normalizedValue >= thresholds.low) return '#f59e0b';  // 黄色
      return '#ef4444'; // 红色
    } else {
      // 正常逻辑：值越低越好（如 PE）
      if (normalizedValue <= thresholds.low) return '#10b981'; // 绿色
      if (normalizedValue <= thresholds.high) return '#f59e0b'; // 黄色
      return '#ef4444'; // 红色
    }
  };

  // 获取状态文本
  const getStatus = () => {
    const normalizedValue = (value - min) / (max - min) * 100;
    
    if (reverse) {
      if (normalizedValue >= thresholds.high) return '优秀';
      if (normalizedValue >= thresholds.low) return '良好';
      return '偏弱';
    } else {
      if (normalizedValue <= thresholds.low) return '低估';
      if (normalizedValue <= thresholds.high) return '合理';
      return '高估';
    }
  };

  const color = getColor();
  const status = getStatus();

  return (
    <div className="metric-gauge">
      <div className="gauge-header">
        <span className="gauge-icon">{icon}</span>
        <span className="gauge-title">{title}</span>
      </div>

      {/* 彩虹刻度尺 */}
      <div className="gauge-track">
        <div className="gauge-gradient">
          {reverse ? (
            // 反转：红-黄-绿
            <>
              <div className="gradient-section red"></div>
              <div className="gradient-section yellow"></div>
              <div className="gradient-section green"></div>
            </>
          ) : (
            // 正常：绿-黄-红
            <>
              <div className="gradient-section green"></div>
              <div className="gradient-section yellow"></div>
              <div className="gradient-section red"></div>
            </>
          )}
        </div>

        {/* 指针 */}
        <motion.div
          className="gauge-pointer"
          style={{ left: `${percentage}%`, borderTopColor: color }}
          initial={{ left: '0%', opacity: 0 }}
          animate={{ left: `${percentage}%`, opacity: 1 }}
          transition={{ duration: 1, delay: 0.2, ease: 'easeOut' }}
        >
          <div className="pointer-dot" style={{ background: color }}></div>
        </motion.div>

        {/* 刻度标记 */}
        <div className="gauge-marks">
          <span className="mark" style={{ left: '0%' }}>{min}</span>
          <span className="mark" style={{ left: '50%' }}>中</span>
          <span className="mark" style={{ left: '100%' }}>{max}</span>
        </div>
      </div>

      {/* 数值显示 */}
      <div className="gauge-value-section">
        <div className="gauge-value">
          <span className="value-number" style={{ color }}>{value.toFixed(2)}</span>
          {unit && <span className="value-unit">{unit}</span>}
        </div>
        <div className="gauge-status" style={{ color }}>
          {status}
        </div>
      </div>

      {/* 对比描述 */}
      {comparison && (
        <motion.div
          className="gauge-comparison"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <span className="comparison-icon">💡</span>
          <span className="comparison-text">{comparison}</span>
        </motion.div>
      )}
    </div>
  );
};

export default MetricGauge;

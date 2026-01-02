/**
 * Sparkline 微缩走势图组件
 * 使用 SVG 渲染，轻量高效
 */
import React, { useMemo } from 'react';
import { TRADING_COLORS } from '../../theme/tradingTheme';

interface SparklineProps {
  data: number[];  // 价格数据数组
  width?: number;
  height?: number;
  strokeWidth?: number;
  showArea?: boolean;  // 是否显示面积图
}

export const Sparkline: React.FC<SparklineProps> = ({
  data,
  width = 80,
  height = 30,
  strokeWidth = 1.5,
  showArea = true,
}) => {
  const { path, areaPath, color, trend } = useMemo(() => {
    if (!data || data.length < 2) {
      return { path: '', areaPath: '', color: TRADING_COLORS.STABLE, trend: 0 };
    }

    // 计算趋势（首尾对比）
    const firstPrice = data[0];
    const lastPrice = data[data.length - 1];
    const trendValue = ((lastPrice - firstPrice) / firstPrice) * 100;
    const lineColor = trendValue > 0 ? TRADING_COLORS.UP : 
                      trendValue < 0 ? TRADING_COLORS.DOWN : 
                      TRADING_COLORS.STABLE;

    // 找出最大最小值用于归一化
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1; // 避免除以0

    // 计算每个点的坐标
    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width;
      const y = height - ((value - min) / range) * height;
      return { x, y };
    });

    // 生成 SVG path
    const linePath = points
      .map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x},${point.y}`)
      .join(' ');

    // 生成面积图 path（如果需要）
    let area = '';
    if (showArea) {
      area = `${linePath} L ${width},${height} L 0,${height} Z`;
    }

    return {
      path: linePath,
      areaPath: area,
      color: lineColor,
      trend: trendValue,
    };
  }, [data, width, height, showArea]);

  if (!data || data.length < 2) {
    return (
      <div style={{ width, height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <span style={{ fontSize: 10, color: '#666' }}>-</span>
      </div>
    );
  }

  return (
    <svg
      width={width}
      height={height}
      style={{ display: 'block' }}
      viewBox={`0 0 ${width} ${height}`}
    >
      {/* 面积图 */}
      {showArea && areaPath && (
        <path
          d={areaPath}
          fill={color}
          fillOpacity={0.1}
        />
      )}
      
      {/* 折线图 */}
      <path
        d={path}
        fill="none"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

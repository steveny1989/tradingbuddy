/**
 * 五维雷达图组件
 * Five-Dimensional Radar Chart - 展现股票的"综合人格"
 */
import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import './RadarChart.css';

interface RadarChartProps {
  technicalScore: number;  // 技术面评分 -> 势头
  liquidityScore: number;  // 流动性评分 -> 活跃
  marketScore: number;     // 市场环境评分 -> 安全
  // 这些需要从后端获取或计算
  valueScore?: number;     // 价值评分（PE、PB等）
  growthScore?: number;    // 成长评分（ROE、营收增长等）
}

const RadarChart: React.FC<RadarChartProps> = ({
  technicalScore,
  liquidityScore,
  marketScore,
  valueScore = 50,  // 默认值，后续从后端获取
  growthScore = 50, // 默认值，后续从后端获取
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // 初始化图表
    chartInstance.current = echarts.init(chartRef.current);

    // 配置雷达图
    const option: echarts.EChartsOption = {
      backgroundColor: 'transparent',
      radar: {
        indicator: [
          { name: '价值', max: 100 },
          { name: '成长', max: 100 },
          { name: '安全', max: 100 },
          { name: '活跃', max: 100 },
          { name: '势头', max: 100 },
        ],
        shape: 'polygon',
        center: ['50%', '50%'],
        radius: '70%',
        splitNumber: 4,
        name: {
          textStyle: {
            color: 'rgba(255, 255, 255, 0.8)',
            fontSize: 14,
            fontWeight: 500,
          },
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(255, 255, 255, 0.1)',
            width: 1,
          },
        },
        splitArea: {
          show: true,
          areaStyle: {
            color: [
              'rgba(59, 130, 246, 0.05)',
              'rgba(59, 130, 246, 0.1)',
              'rgba(59, 130, 246, 0.05)',
              'rgba(59, 130, 246, 0.1)',
            ],
          },
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(255, 255, 255, 0.2)',
            width: 1,
          },
        },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: [
                valueScore,
                growthScore,
                marketScore,
                liquidityScore,
                technicalScore,
              ],
              name: '综合评分',
              symbol: 'circle',
              symbolSize: 6,
              lineStyle: {
                color: '#fbbf24',
                width: 2,
                shadowColor: 'rgba(251, 191, 36, 0.5)',
                shadowBlur: 10,
              },
              areaStyle: {
                color: {
                  type: 'radial',
                  x: 0.5,
                  y: 0.5,
                  r: 0.5,
                  colorStops: [
                    {
                      offset: 0,
                      color: 'rgba(251, 191, 36, 0.4)',
                    },
                    {
                      offset: 1,
                      color: 'rgba(251, 191, 36, 0.1)',
                    },
                  ],
                },
                shadowColor: 'rgba(251, 191, 36, 0.3)',
                shadowBlur: 20,
              },
              itemStyle: {
                color: '#fbbf24',
                borderColor: '#fff',
                borderWidth: 2,
                shadowColor: 'rgba(251, 191, 36, 0.8)',
                shadowBlur: 10,
              },
            },
          ],
          animationDuration: 1500,
          animationEasing: 'cubicOut',
        },
      ],
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: 'rgba(251, 191, 36, 0.5)',
        borderWidth: 1,
        textStyle: {
          color: '#fff',
          fontSize: 12,
        },
        formatter: (params: any) => {
          const data = params.value;
          const names = ['价值', '成长', '安全', '活跃', '势头'];
          let result = '<div style="padding: 8px;">';
          result += '<div style="font-weight: bold; margin-bottom: 8px;">综合评分</div>';
          names.forEach((name, index) => {
            result += `<div style="margin: 4px 0;">
              ${name}: <span style="color: #fbbf24; font-weight: bold;">${data[index].toFixed(1)}</span> 分
            </div>`;
          });
          result += '</div>';
          return result;
        },
      },
    };

    chartInstance.current.setOption(option);

    // 响应式调整
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chartInstance.current?.dispose();
    };
  }, [technicalScore, liquidityScore, marketScore, valueScore, growthScore]);

  // 计算是否是"六边形战士"
  const isHexagonWarrior = () => {
    const scores = [valueScore, growthScore, marketScore, liquidityScore, technicalScore];
    const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
    const minScore = Math.min(...scores);
    // 平均分 >= 70 且最低分 >= 60
    return avgScore >= 70 && minScore >= 60;
  };

  return (
    <div className="radar-chart-container">
      <div className="radar-chart-header">
        <h3>五维雷达图</h3>
        {isHexagonWarrior() && (
          <div className="hexagon-badge">
            <span className="badge-icon">🏆</span>
            <span className="badge-text">六边形战士</span>
          </div>
        )}
      </div>
      <div ref={chartRef} className="radar-chart" />
      <div className="radar-chart-legend">
        <div className="legend-item">
          <span className="legend-dot" style={{ background: '#fbbf24' }}></span>
          <span className="legend-text">综合评分</span>
        </div>
      </div>
    </div>
  );
};

export default RadarChart;

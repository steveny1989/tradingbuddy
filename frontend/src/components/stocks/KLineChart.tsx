/**
 * K线图组件 - 使用ECharts渲染K线图和技术指标
 */
import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import { Button, Space } from 'antd';
import type { DailyData } from '../../services/stocks';

interface KLineChartProps {
  data: DailyData[];
  timeRange: string;
  onTimeRangeChange: (range: string) => void;
}

export function KLineChart({ data, timeRange, onTimeRangeChange }: KLineChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // 初始化图表
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    // 准备数据
    const dates = data.map((d) => d.date);
    const klineData = data.map((d) => [d.open, d.close, d.low, d.high]);
    const volumes = data.map((d) => d.volume);

    // 计算移动平均线
    const ma5 = calculateMA(5, data);
    const ma10 = calculateMA(10, data);
    const ma20 = calculateMA(20, data);
    const ma60 = calculateMA(60, data);

    // 配置图表
    const option: echarts.EChartsOption = {
      animation: false,
      legend: {
        bottom: 10,
        left: 'center',
        data: ['K线', 'MA5', 'MA10', 'MA20', 'MA60'],
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
        },
        borderWidth: 1,
        borderColor: '#ccc',
        padding: 10,
        textStyle: {
          color: '#000',
        },
        formatter: function (params: any) {
          const dataIndex = params[0].dataIndex;
          const d = data[dataIndex];
          
          let html = `<div style="font-weight: bold;">${d.date}</div>`;
          html += `<div>开盘: ${d.open.toFixed(2)}</div>`;
          html += `<div>收盘: ${d.close.toFixed(2)}</div>`;
          html += `<div>最高: ${d.high.toFixed(2)}</div>`;
          html += `<div>最低: ${d.low.toFixed(2)}</div>`;
          html += `<div>成交量: ${formatVolume(d.volume)}</div>`;
          
          if (d.pct_change !== undefined) {
            html += `<div>涨跌幅: ${d.pct_change.toFixed(2)}%</div>`;
          }
          
          return html;
        },
      },
      axisPointer: {
        link: [{ xAxisIndex: 'all' }],
        label: {
          backgroundColor: '#777',
        },
      },
      grid: [
        {
          left: '10%',
          right: '8%',
          height: '50%',
        },
        {
          left: '10%',
          right: '8%',
          top: '70%',
          height: '15%',
        },
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          boundaryGap: false,
          axisLine: { onZero: false },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax',
        },
        {
          type: 'category',
          gridIndex: 1,
          data: dates,
          boundaryGap: false,
          axisLine: { onZero: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          min: 'dataMin',
          max: 'dataMax',
        },
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true,
          },
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: { show: false },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { show: false },
        },
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 0,
          end: 100,
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          bottom: 60,
          start: 0,
          end: 100,
        },
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: klineData,
          itemStyle: {
            color: '#ef5350',
            color0: '#26a69a',
            borderColor: '#ef5350',
            borderColor0: '#26a69a',
          },
        },
        {
          name: 'MA5',
          type: 'line',
          data: ma5,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1,
          },
          showSymbol: false,
        },
        {
          name: 'MA10',
          type: 'line',
          data: ma10,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1,
          },
          showSymbol: false,
        },
        {
          name: 'MA20',
          type: 'line',
          data: ma20,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1,
          },
          showSymbol: false,
        },
        {
          name: 'MA60',
          type: 'line',
          data: ma60,
          smooth: true,
          lineStyle: {
            opacity: 0.8,
            width: 1,
          },
          showSymbol: false,
        },
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumes,
          itemStyle: {
            color: function (params: any) {
              const dataIndex = params.dataIndex;
              const kline = klineData[dataIndex];
              return kline[1] >= kline[0] ? '#ef5350' : '#26a69a';
            },
          },
        },
      ],
    };

    chartInstance.current.setOption(option);

    // 响应式调整
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [data]);

  // 清理图表实例
  useEffect(() => {
    return () => {
      chartInstance.current?.dispose();
      chartInstance.current = null;
    };
  }, []);

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <span>时间范围：</span>
        <Button
          type={timeRange === '1M' ? 'primary' : 'default'}
          size="small"
          onClick={() => onTimeRangeChange('1M')}
        >
          1个月
        </Button>
        <Button
          type={timeRange === '3M' ? 'primary' : 'default'}
          size="small"
          onClick={() => onTimeRangeChange('3M')}
        >
          3个月
        </Button>
        <Button
          type={timeRange === '6M' ? 'primary' : 'default'}
          size="small"
          onClick={() => onTimeRangeChange('6M')}
        >
          6个月
        </Button>
        <Button
          type={timeRange === '1Y' ? 'primary' : 'default'}
          size="small"
          onClick={() => onTimeRangeChange('1Y')}
        >
          1年
        </Button>
        <Button
          type={timeRange === 'ALL' ? 'primary' : 'default'}
          size="small"
          onClick={() => onTimeRangeChange('ALL')}
        >
          全部
        </Button>
      </Space>

      <div ref={chartRef} style={{ width: '100%', height: '600px' }} />
    </div>
  );
}

// 计算移动平均线
function calculateMA(period: number, data: DailyData[]): (number | null)[] {
  const result: (number | null)[] = [];
  
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
      continue;
    }
    
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += data[i - j].close;
    }
    result.push(sum / period);
  }
  
  return result;
}

// 格式化成交量
function formatVolume(volume: number): string {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿';
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万';
  }
  return volume.toFixed(0);
}

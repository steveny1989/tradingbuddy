/**
 * 交易站专业深色主题配置
 * 基于 Ant Design 5.0 Design Token 系统
 */
import { ThemeConfig } from 'antd';
import { theme } from 'antd';

/**
 * 交易颜色常量 - 语义化颜色
 */
export const TRADING_COLORS = {
  UP: '#cf1322',     // 涨（中国习惯：红涨）
  DOWN: '#3f8600',   // 跌（中国习惯：绿跌）
  STABLE: '#8c8c8c', // 平
  // 可选：国际习惯
  UP_INTL: '#389e0d',   // 涨（国际习惯：绿涨）
  DOWN_INTL: '#f5222d', // 跌（国际习惯：红跌）
};

/**
 * 交易站深色主题
 */
export const tradingTheme: ThemeConfig = {
  // 启用深色模式并增加信息密度
  algorithm: [theme.darkAlgorithm, theme.compactAlgorithm],
  
  token: {
    // 基础色调：采用深航海蓝，而非死板的纯黑
    colorBgBase: '#0d1117',
    colorTextBase: '#e6edf3',
    
    // 品牌主色：金融蓝
    colorPrimary: '#177ddc',
    
    // 降低圆角：增强界面的严谨与精密感
    borderRadius: 2,
    
    // 字体配置：为数字采用等宽字体
    fontFamily: "'JetBrains Mono', 'Roboto Mono', 'Segoe UI', sans-serif",
    
    // 调整间距以提高信息密度
    marginXS: 4,
    marginSM: 8,
    margin: 12,
    marginMD: 16,
    marginLG: 20,
    
    // 调整字体大小 - 保持可读性
    fontSize: 14,      // 基础字体从 13 调整到 14
    fontSizeSM: 12,
    fontSizeLG: 16,    // 大字体从 14 调整到 16
    fontSizeXL: 20,    // 添加超大字体用于关键数据
    
    // 标题字体大小
    fontSizeHeading1: 32,
    fontSizeHeading2: 26,
    fontSizeHeading3: 20,
    fontSizeHeading4: 18,
    fontSizeHeading5: 16,
  },
  
  components: {
    // 表格：交易者核心区域
    Table: {
      headerBg: '#161b22',
      headerColor: '#8b949e',
      headerBorderRadius: 0,
      colorBgContainer: '#0d1117',
      borderColor: '#21262d',
      rowHoverBg: '#161b22',
      fontSize: 14,           // 表格字体大小
      fontSizeSM: 13,         // 小号表格字体
    },
    
    // 布局
    Layout: {
      headerBg: '#161b22',
      siderBg: '#010409',
      bodyBg: '#0d1117',
      footerBg: '#010409',
    },
    
    // 卡片
    Card: {
      colorBgContainer: '#161b22',
      colorBorderSecondary: '#21262d',
      fontSize: 14,           // 卡片内容字体
    },
    
    // 统计数字
    Statistic: {
      contentFontSize: 24,    // 统计数字从 20 调整到 24
      titleFontSize: 14,      // 统计标题字体
    },
    
    // 按钮
    Button: {
      borderRadius: 2,
    },
    
    // 输入框
    Input: {
      borderRadius: 2,
      colorBgContainer: '#0d1117',
    },
    
    // 标签
    Tag: {
      borderRadiusSM: 2,
    },
    
    // 菜单
    Menu: {
      itemBg: '#010409',
      itemSelectedBg: '#161b22',
      itemHoverBg: '#161b22',
      fontSize: 15,           // 菜单项字体大小
      itemHeight: 44,         // 菜单项高度（更大的点击区域）
      iconSize: 18,           // 图标大小
    },
  },
};

/**
 * ECharts 主题配置（与 Ant Design 主题同步）
 */
export const echartsTheme = {
  backgroundColor: '#0d1117',
  textColor: '#e6edf3',
  borderColor: '#21262d',
  textStyle: {
    color: '#e6edf3',
    fontFamily: "'JetBrains Mono', 'Roboto Mono', 'Segoe UI', sans-serif",
    fontSize: 13,  // ECharts 文字大小
  },
  title: {
    textStyle: {
      color: '#e6edf3',
      fontSize: 16,
    },
  },
  legend: {
    textStyle: {
      color: '#8b949e',
      fontSize: 13,
    },
  },
  grid: {
    borderColor: '#21262d',
  },
  categoryAxis: {
    axisLine: {
      lineStyle: {
        color: '#21262d',
      },
    },
    axisLabel: {
      color: '#8b949e',
    },
    splitLine: {
      lineStyle: {
        color: '#21262d',
      },
    },
  },
  valueAxis: {
    axisLine: {
      lineStyle: {
        color: '#21262d',
      },
    },
    axisLabel: {
      color: '#8b949e',
    },
    splitLine: {
      lineStyle: {
        color: '#21262d',
      },
    },
  },
  // K线图颜色
  candlestick: {
    itemStyle: {
      color: TRADING_COLORS.UP,      // 涨
      color0: TRADING_COLORS.DOWN,   // 跌
      borderColor: TRADING_COLORS.UP,
      borderColor0: TRADING_COLORS.DOWN,
    },
  },
};

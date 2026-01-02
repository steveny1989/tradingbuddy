/**
 * 极简选股助手工具函数
 * 
 * 提供信号强度映射、技术术语过滤、价格格式化等通用功能
 */

/**
 * 信号强度类型
 */
export type SignalStrength = 'strong' | 'medium' | 'weak';

/**
 * 信号类型
 */
export type SignalType = 'buy' | 'sell' | 'hold';

/**
 * 信号强度到颜色的映射
 * 
 * 根据信号强度返回对应的颜色代码
 * - strong (强): 绿色 (#52c41a)
 * - medium (中): 黄色 (#faad14)
 * - weak (弱): 灰色 (#d9d9d9)
 * 
 * @param strength 信号强度
 * @returns 颜色代码
 * 
 * @example
 * getSignalColor('strong') // '#52c41a'
 * getSignalColor('medium') // '#faad14'
 * getSignalColor('weak') // '#d9d9d9'
 */
export function getSignalColor(strength: SignalStrength): string {
  const colorMap: Record<SignalStrength, string> = {
    strong: '#52c41a',  // 绿色
    medium: '#faad14',  // 黄色
    weak: '#d9d9d9',    // 灰色
  };
  
  return colorMap[strength] || '#d9d9d9';
}

/**
 * 根据信号强度分数计算信号强度等级
 * 
 * @param score 信号强度分数 (0-100)
 * @returns 信号强度等级
 * 
 * @example
 * calculateSignalStrength(80) // 'strong'
 * calculateSignalStrength(60) // 'medium'
 * calculateSignalStrength(40) // 'weak'
 */
export function calculateSignalStrength(score: number): SignalStrength {
  if (score >= 70) {
    return 'strong';
  } else if (score >= 50) {
    return 'medium';
  } else {
    return 'weak';
  }
}

/**
 * 信号类型到颜色的映射
 * 
 * @param signal 信号类型
 * @returns 颜色代码
 * 
 * @example
 * getSignalTypeColor('buy') // '#52c41a'
 * getSignalTypeColor('sell') // '#ff4d4f'
 * getSignalTypeColor('hold') // '#faad14'
 */
export function getSignalTypeColor(signal: SignalType): string {
  const colorMap: Record<SignalType, string> = {
    buy: '#52c41a',   // 绿色
    sell: '#ff4d4f',  // 红色
    hold: '#faad14',  // 黄色
  };
  
  return colorMap[signal] || '#d9d9d9';
}

/**
 * 信号类型到中文标签的映射
 * 
 * @param signal 信号类型
 * @returns 中文标签
 * 
 * @example
 * getSignalLabel('buy') // '买入'
 * getSignalLabel('sell') // '卖出'
 * getSignalLabel('hold') // '观望'
 */
export function getSignalLabel(signal: SignalType): string {
  const labelMap: Record<SignalType, string> = {
    buy: '买入',
    sell: '卖出',
    hold: '观望',
  };
  
  return labelMap[signal] || '观望';
}

/**
 * 技术术语列表
 * 
 * 这些术语应该在用户界面中被过滤或替换为大白话
 */
const TECHNICAL_TERMS = [
  'MA5', 'MA10', 'MA20', 'MA30', 'MA60',
  'RSI', 'MACD', 'KDJ', 'BOLL',
  'EMA', 'SMA', 'DIF', 'DEA',
  'API', 'HTTP', 'SQL', 'database',
  '均线', '指标', '参数', '配置',
];

/**
 * 检查文本是否包含技术术语
 * 
 * @param text 要检查的文本
 * @returns 是否包含技术术语
 * 
 * @example
 * containsTechnicalTerms('MA5上穿MA20') // true
 * containsTechnicalTerms('成交量放大') // false
 */
export function containsTechnicalTerms(text: string): boolean {
  return TECHNICAL_TERMS.some(term => 
    text.toUpperCase().includes(term.toUpperCase())
  );
}

/**
 * 过滤技术术语
 * 
 * 将文本中的技术术语替换为更友好的表达
 * 
 * @param text 原始文本
 * @returns 过滤后的文本
 * 
 * @example
 * filterTechnicalTerms('MA5上穿MA20') // '短期均线上穿长期均线'
 * filterTechnicalTerms('RSI指标超买') // '超买信号'
 */
export function filterTechnicalTerms(text: string): string {
  let filtered = text;
  
  // 替换常见技术术语
  const replacements: Record<string, string> = {
    'MA5': '短期均线',
    'MA10': '短期均线',
    'MA20': '长期均线',
    'MA30': '长期均线',
    'MA60': '长期均线',
    'RSI': '强弱指标',
    'MACD': '趋势指标',
    'KDJ': '随机指标',
    'BOLL': '布林带',
    'API': '接口',
    'HTTP': '网络',
    'SQL': '数据库',
    'database': '数据库',
  };
  
  Object.entries(replacements).forEach(([term, replacement]) => {
    const regex = new RegExp(term, 'gi');
    filtered = filtered.replace(regex, replacement);
  });
  
  return filtered;
}

/**
 * 格式化价格
 * 
 * 将价格格式化为带有货币符号和小数位的字符串
 * 
 * @param price 价格
 * @param decimals 小数位数，默认2位
 * @param showSymbol 是否显示货币符号，默认true
 * @returns 格式化后的价格字符串
 * 
 * @example
 * formatPrice(12.345) // '¥12.35'
 * formatPrice(12.345, 3) // '¥12.345'
 * formatPrice(12.345, 2, false) // '12.35'
 */
export function formatPrice(
  price: number, 
  decimals: number = 2, 
  showSymbol: boolean = true
): string {
  const formatted = price.toFixed(decimals);
  return showSymbol ? `¥${formatted}` : formatted;
}

/**
 * 格式化百分比
 * 
 * 将数值格式化为百分比字符串
 * 
 * @param value 数值 (例如: 0.05 表示 5%)
 * @param decimals 小数位数，默认2位
 * @param showSign 是否显示正负号，默认true
 * @returns 格式化后的百分比字符串
 * 
 * @example
 * formatPercentage(0.0523) // '+5.23%'
 * formatPercentage(-0.0312) // '-3.12%'
 * formatPercentage(0.0523, 1) // '+5.2%'
 * formatPercentage(0.0523, 2, false) // '5.23%'
 */
export function formatPercentage(
  value: number, 
  decimals: number = 2, 
  showSign: boolean = true
): string {
  const percentage = (value * 100).toFixed(decimals);
  const sign = value > 0 ? '+' : '';
  return showSign ? `${sign}${percentage}%` : `${percentage}%`;
}

/**
 * 格式化市值
 * 
 * 将市值格式化为易读的字符串（亿元）
 * 
 * @param marketCap 市值（元）
 * @returns 格式化后的市值字符串
 * 
 * @example
 * formatMarketCap(5000000000) // '50.00亿'
 * formatMarketCap(123456789012) // '1234.57亿'
 */
export function formatMarketCap(marketCap: number): string {
  const yi = marketCap / 100000000; // 转换为亿
  return `${yi.toFixed(2)}亿`;
}

/**
 * 格式化成交量
 * 
 * 将成交量格式化为易读的字符串（万手）
 * 
 * @param volume 成交量（手）
 * @returns 格式化后的成交量字符串
 * 
 * @example
 * formatVolume(12345) // '1.23万手'
 * formatVolume(123456789) // '12345.68万手'
 */
export function formatVolume(volume: number): string {
  const wan = volume / 10000; // 转换为万
  return `${wan.toFixed(2)}万手`;
}

/**
 * 计算涨跌幅颜色
 * 
 * 根据涨跌幅返回对应的颜色（中国股市习惯：涨红跌绿）
 * 
 * @param pctChange 涨跌幅（小数，例如 0.05 表示 5%）
 * @returns 颜色代码
 * 
 * @example
 * getPriceChangeColor(0.05) // '#ff4d4f' (红色)
 * getPriceChangeColor(-0.03) // '#52c41a' (绿色)
 * getPriceChangeColor(0) // '#8c8c8c' (灰色)
 */
export function getPriceChangeColor(pctChange: number): string {
  if (pctChange > 0) {
    return '#ff4d4f'; // 红色（涨）
  } else if (pctChange < 0) {
    return '#52c41a'; // 绿色（跌）
  } else {
    return '#8c8c8c'; // 灰色（平）
  }
}

/**
 * 计算数据更新警告级别
 * 
 * 根据最后更新时间计算警告级别
 * - none: 24小时内
 * - yellow: 24-72小时
 * - red: 超过72小时
 * 
 * @param lastUpdate 最后更新时间（ISO字符串或Date对象）
 * @returns 警告级别
 * 
 * @example
 * getUpdateWarningLevel('2024-01-01T10:00:00Z') // 'red' (假设现在是2024-01-05)
 */
export function getUpdateWarningLevel(
  lastUpdate: string | Date
): 'none' | 'yellow' | 'red' {
  const lastUpdateTime = typeof lastUpdate === 'string' 
    ? new Date(lastUpdate) 
    : lastUpdate;
  
  const now = new Date();
  const hoursDiff = (now.getTime() - lastUpdateTime.getTime()) / (1000 * 60 * 60);
  
  if (hoursDiff > 72) {
    return 'red';
  } else if (hoursDiff > 24) {
    return 'yellow';
  } else {
    return 'none';
  }
}

/**
 * 格式化相对时间
 * 
 * 将时间格式化为相对于当前时间的描述
 * 
 * @param date 日期（ISO字符串或Date对象）
 * @returns 相对时间描述
 * 
 * @example
 * formatRelativeTime('2024-01-01T10:00:00Z') // '3天前'
 * formatRelativeTime('2024-01-01T23:00:00Z') // '1小时前'
 */
export function formatRelativeTime(date: string | Date): string {
  const targetTime = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - targetTime.getTime();
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffMinutes < 1) {
    return '刚刚';
  } else if (diffMinutes < 60) {
    return `${diffMinutes}分钟前`;
  } else if (diffHours < 24) {
    return `${diffHours}小时前`;
  } else if (diffDays < 30) {
    return `${diffDays}天前`;
  } else {
    return targetTime.toLocaleDateString('zh-CN');
  }
}

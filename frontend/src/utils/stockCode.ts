/**
 * 股票代码格式化工具
 * Stock Code Formatting Utilities
 */

/**
 * 格式化股票代码显示
 * 将 "sh.600519" 或 "sz.000001" 格式转换为纯数字代码
 * 
 * @param code - 原始股票代码（可能包含市场前缀）
 * @returns 格式化后的代码（纯数字）
 * 
 * @example
 * formatStockCode("sh.600519") // "600519"
 * formatStockCode("sz.000001") // "000001"
 * formatStockCode("600519") // "600519"
 */
export function formatStockCode(code: string): string {
  if (!code) return '';
  
  // 如果包含点号，提取点号后面的部分
  if (code.includes('.')) {
    return code.split('.')[1];
  }
  
  return code;
}

/**
 * 格式化股票代码显示（带市场标识）
 * 将 "sh.600519" 转换为 "SH600519"
 * 
 * @param code - 原始股票代码
 * @returns 格式化后的代码（带大写市场前缀）
 * 
 * @example
 * formatStockCodeWithMarket("sh.600519") // "SH600519"
 * formatStockCodeWithMarket("sz.000001") // "SZ000001"
 */
export function formatStockCodeWithMarket(code: string): string {
  if (!code) return '';
  
  if (code.includes('.')) {
    const [market, number] = code.split('.');
    return `${market.toUpperCase()}${number}`;
  }
  
  return code;
}

/**
 * 获取股票市场名称
 * 
 * @param code - 股票代码
 * @returns 市场名称（中文）
 * 
 * @example
 * getMarketName("sh.600519") // "上海"
 * getMarketName("sz.000001") // "深圳"
 */
export function getMarketName(code: string): string {
  if (!code) return '';
  
  if (code.includes('.')) {
    const market = code.split('.')[0].toLowerCase();
    return market === 'sh' ? '上海' : market === 'sz' ? '深圳' : '';
  }
  
  // 根据代码数字判断
  if (code.startsWith('6')) return '上海';
  if (code.startsWith('0') || code.startsWith('3')) return '深圳';
  
  return '';
}

/**
 * 构建完整的股票代码（带市场前缀）
 * 
 * @param code - 纯数字代码
 * @returns 完整代码（如 "sh.600519"）
 * 
 * @example
 * buildFullCode("600519") // "sh.600519"
 * buildFullCode("000001") // "sz.000001"
 */
export function buildFullCode(code: string): string {
  if (!code) return '';
  
  // 如果已经包含前缀，直接返回
  if (code.includes('.')) return code;
  
  // 根据代码数字判断市场
  if (code.startsWith('6')) return `sh.${code}`;
  if (code.startsWith('0') || code.startsWith('3')) return `sz.${code}`;
  
  return code;
}

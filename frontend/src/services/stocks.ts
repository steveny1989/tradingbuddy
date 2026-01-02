/**
 * 股票数据API服务
 */
import api from './api';

export interface Stock {
  code: string;
  name: string;
  market: 'sh' | 'sz';
  full_code: string;
  industry?: string;
  market_cap?: number;  // 保留兼容性
  total_cap?: number;   // 总市值
  float_cap?: number;   // 流通市值
  list_date?: string;
  pe_ttm?: number;      // 市盈率
  pb?: number;          // 市净率
  pct_chg?: number;     // 涨跌幅
}

export interface DailyData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
  turnover?: number;
  pct_change?: number;
}

export interface IndicatorData {
  date: string;
  ma5?: number;
  ma10?: number;
  ma20?: number;
  ma60?: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface StockListParams extends PaginationParams {
  market?: 'sh' | 'sz';
  min_cap?: number;
  max_cap?: number;
}

export interface StockListResponse {
  success: boolean;
  data: Stock[];
  pagination: {
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  };
}

export interface StockDetailResponse {
  success: boolean;
  data: Stock;
}

export interface DailyDataResponse {
  success: boolean;
  data: DailyData[];
}

export interface IndicatorDataResponse {
  success: boolean;
  data: IndicatorData[];
}

/**
 * 获取股票列表
 */
export const getStockList = async (params?: StockListParams): Promise<StockListResponse> => {
  const response = await api.get<StockListResponse>('/stocks', { params });
  return response as StockListResponse;
};

/**
 * 获取股票详情
 */
export const getStockDetail = async (code: string): Promise<Stock> => {
  const response = await api.get<StockDetailResponse>(`/stocks/${code}`);
  return response.data;
};

/**
 * 获取日线数据
 */
export const getStockDaily = async (
  code: string,
  params?: { start_date?: string; end_date?: string }
): Promise<DailyData[]> => {
  const response = await api.get<DailyDataResponse>(`/stocks/${code}/daily`, { params });
  return response.data;
};

/**
 * 获取技术指标
 */
export const getIndicators = async (
  code: string,
  indicators?: string,
  startDate?: string,
  endDate?: string
): Promise<IndicatorDataResponse> => {
  return await api.get(`/stocks/${code}/indicators`, {
    params: {
      indicators,
      start_date: startDate,
      end_date: endDate,
    },
  });
};

export default {
  getStockList,
  getStockDetail,
  getStockDaily,
  getIndicators,
};

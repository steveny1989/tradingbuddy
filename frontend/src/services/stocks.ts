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
  market_cap?: number;
  list_date?: string;
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
  pct_chg?: number;
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
  return await api.get('/stocks', { params });
};

/**
 * 获取股票详情
 */
export const getStockDetail = async (code: string): Promise<StockDetailResponse> => {
  return await api.get(`/stocks/${code}`);
};

/**
 * 获取日线数据
 */
export const getDailyData = async (
  code: string,
  startDate?: string,
  endDate?: string
): Promise<DailyDataResponse> => {
  return await api.get(`/stocks/${code}/daily`, {
    params: { start_date: startDate, end_date: endDate },
  });
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
  getDailyData,
  getIndicators,
};

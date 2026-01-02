/**
 * 指数数据API服务
 */
import api from './api';

export interface IndexData {
  code: string;
  name: string;
  close: number;
  change: number;
  pct_chg: number;
  open: number;
  high: number;
  low: number;
  volume: number;
  amount: number;
  date: string;
  available: boolean;
}

export interface IndicesResponse {
  success: boolean;
  data: IndexData[];
}

/**
 * 获取主要指数行情
 */
export const getIndices = async (): Promise<IndexData[]> => {
  const response = await api.get<IndicesResponse>('/indices');
  return response.data;
};

export default {
  getIndices,
};

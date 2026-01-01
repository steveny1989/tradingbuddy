/**
 * 仪表板API服务
 */
import api from './api';

export interface DatabaseStatus {
  total_stocks: number;
  last_update: string;
  data_completeness: number;
}

export interface PaperTradingStatus {
  running: boolean;
  total_value: number;
  daily_pnl: number;
}

export interface BacktestSummary {
  id: string;
  strategy_name: string;
  total_return: number;
  max_drawdown: number;
  created_at: string;
}

export interface DashboardSummary {
  database: DatabaseStatus;
  paper_trading: PaperTradingStatus;
  recent_backtests: BacktestSummary[];
}

/**
 * 获取仪表板摘要数据
 */
export const getDashboardSummary = async (): Promise<DashboardSummary> => {
  const response = await api.get('/dashboard/summary');
  return response.data;
};

export default {
  getDashboardSummary,
};

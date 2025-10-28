import { apiClient } from './client';
import { API_ENDPOINTS } from '@/constants';
import type { BacktestRequest, BacktestResponse } from '@/types';

export async function runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
  const response = await apiClient.post<BacktestResponse>(
    API_ENDPOINTS.BACKTEST,
    request
  );
  return response.data;
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await apiClient.get<{ status: string }>(API_ENDPOINTS.HEALTH);
  return response.data;
}

import { request } from '../utils/request';
import { apiPaths } from '../constants/apiPaths';
import type { FuelRecord } from '../types';

export interface MonthlyFuelSummary {
  month: string | null;
  liters: number;
  totalAmount: number;
}

export const fuelApi = {
  list: () => request<FuelRecord[]>(apiPaths.fuel),
  monthlySummary: () => request<MonthlyFuelSummary[]>(apiPaths.fuelSummary)
};

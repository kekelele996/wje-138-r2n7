import { request } from '../utils/request';
import { apiPaths } from '../constants/apiPaths';
import type { CreateDriverPayload, Driver } from '../types';

export const driverApi = {
  list: (status?: string) =>
    request<Driver[]>(
      status ? `${apiPaths.drivers}?status=${encodeURIComponent(status)}` : apiPaths.drivers
    ),
  create: (payload: CreateDriverPayload) =>
    request<Driver>(apiPaths.drivers, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
};

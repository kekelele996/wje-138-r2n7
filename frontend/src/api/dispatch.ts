import { request } from '../utils/request';
import { apiPaths, dispatchActionPath } from '../constants/apiPaths';
import type { DispatchCreatePayload, DispatchOrder } from '../types';

export const dispatchApi = {
  list: (status?: string) =>
    request<DispatchOrder[]>(`${apiPaths.dispatch}${status ? `?status=${status}` : ''}`),
  create: (payload: DispatchCreatePayload) =>
    request<DispatchOrder>(apiPaths.dispatch, { method: 'POST', body: JSON.stringify(payload) }),
  start: (id: number) =>
    request<DispatchOrder>(dispatchActionPath.start(id), { method: 'POST' }),
  complete: (id: number) =>
    request<DispatchOrder>(dispatchActionPath.complete(id), { method: 'POST' }),
  cancel: (id: number) =>
    request<DispatchOrder>(dispatchActionPath.cancel(id), { method: 'POST' })
};

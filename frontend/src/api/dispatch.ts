import { request } from '../utils/request';
import { apiPaths, dispatchActionPaths } from '../constants/apiPaths';
import type { CreateDispatchPayload, DispatchOrder, ReassignPayload } from '../types';

export const dispatchApi = {
  list: (status?: string) =>
    request<DispatchOrder[]>(
      status ? `${apiPaths.dispatch}?status=${encodeURIComponent(status)}` : apiPaths.dispatch
    ),
  detail: (id: number) => request<DispatchOrder>(dispatchActionPaths.detail(id)),
  create: (payload: CreateDispatchPayload) =>
    request<DispatchOrder>(apiPaths.dispatch, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),
  start: (id: number) =>
    request<DispatchOrder>(dispatchActionPaths.start(id), { method: 'POST' }),
  complete: (id: number) =>
    request<DispatchOrder>(dispatchActionPaths.complete(id), { method: 'POST' }),
  cancel: (id: number) =>
    request<DispatchOrder>(dispatchActionPaths.cancel(id), { method: 'POST' }),
  reassign: (id: number, payload: ReassignPayload) =>
    request<DispatchOrder>(dispatchActionPaths.reassign(id), {
      method: 'POST',
      body: JSON.stringify(payload)
    })
};

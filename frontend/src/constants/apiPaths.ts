export const apiPaths = {
  vehicles: '/api/vehicles/',
  drivers: '/api/drivers/',
  dispatch: '/api/dispatch-orders/',
  maintenance: '/api/maintenance-records/',
  fuel: '/api/fuel-records/',
  fuelSummary: '/api/fuel-records/monthly-summary/'
} as const;

export const dispatchActionPaths = {
  detail: (id: number) => `/api/dispatch-orders/${id}/`,
  start: (id: number) => `/api/dispatch-orders/${id}/start/`,
  complete: (id: number) => `/api/dispatch-orders/${id}/complete/`,
  cancel: (id: number) => `/api/dispatch-orders/${id}/cancel/`,
  reassign: (id: number) => `/api/dispatch-orders/${id}/reassign/`
} as const;

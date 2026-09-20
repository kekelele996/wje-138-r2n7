export const apiPaths = {
  vehicles: '/api/vehicles/',
  drivers: '/api/drivers/',
  dispatch: '/api/dispatch-orders/',
  maintenance: '/api/maintenance-records/',
  fuel: '/api/fuel-records/'
} as const;

export const dispatchActionPath = {
  start: (id: number) => `/api/dispatch-orders/${id}/start/`,
  complete: (id: number) => `/api/dispatch-orders/${id}/complete/`,
  cancel: (id: number) => `/api/dispatch-orders/${id}/cancel/`
};

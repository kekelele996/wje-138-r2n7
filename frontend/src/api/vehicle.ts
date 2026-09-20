import { request } from '../utils/request';
import { apiPaths } from '../constants/apiPaths';
import type { CreateVehiclePayload, Vehicle } from '../types';

export const vehicleApi = {
  list: (status?: string) =>
    request<Vehicle[]>(
      status ? `${apiPaths.vehicles}?status=${encodeURIComponent(status)}` : apiPaths.vehicles
    ),
  create: (payload: CreateVehiclePayload) =>
    request<Vehicle>(apiPaths.vehicles, {
      method: 'POST',
      body: JSON.stringify(payload)
    })
};

import { DispatchStatus } from './enums';
import type { Driver } from './driver';
import type { Vehicle } from './vehicle';

export type DispatchStatusEvent = {
  id: number;
  fromStatus: DispatchStatus | '';
  toStatus: DispatchStatus;
  remark: string;
  createdAt: string;
};

export type DispatchOrder = {
  id: number;
  orderNo: string;
  vehicleId: number;
  driverId: number;
  origin: string;
  destination: string;
  planDepartAt: string | null;
  planArriveAt: string | null;
  actualDepartAt?: string | null;
  actualArriveAt?: string | null;
  cargo: string;
  weight: number;
  freight: number;
  status: DispatchStatus;
  creatorId: number;
  note?: string;
  createdAt: string;
  assignedAt?: string | null;
  startedAt?: string | null;
  completedAt?: string | null;
  cancelledAt?: string | null;
  vehicle?: Vehicle;
  driver?: Driver;
  events?: DispatchStatusEvent[];
};

export type DispatchCreatePayload = {
  vehicleId: number;
  driverId: number;
  origin: string;
  destination: string;
  planDepartAt?: string;
  planArriveAt?: string;
  cargo: string;
  weight: number;
  freight?: number;
  note?: string;
};

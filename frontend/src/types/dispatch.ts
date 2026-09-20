import { DispatchStatus } from './enums';

export interface DispatchTimelineItem {
  eventType: 'Created' | 'Assigned' | 'Reassigned' | 'Started' | 'Completed' | 'Cancelled';
  fromStatus: string;
  toStatus: string;
  detail: string;
  time: string;
}

export type DispatchOrder = {
  id: number;
  orderNo: string;
  vehicleId?: number | null;
  driverId?: number | null;
  vehicle?: number | null;
  driver?: number | null;
  vehiclePlateNo?: string;
  vehicleType?: string;
  driverName?: string;
  driverPhone?: string;
  origin: string;
  destination: string;
  planDepartAt?: string | null;
  planArriveAt?: string | null;
  actualDepartAt?: string | null;
  actualArriveAt?: string | null;
  cargo: string;
  weight: number;
  freight: number;
  status: DispatchStatus;
  creatorId: number;
  note?: string;
  createdAt?: string;
  assignedAt?: string | null;
  startedAt?: string | null;
  completedAt?: string | null;
  cancelledAt?: string | null;
  timeline?: DispatchTimelineItem[];
};

export interface CreateDispatchPayload {
  vehicleId: number;
  driverId: number;
  origin: string;
  destination:
  string;
  weight: number;
  freight?: number;
  cargo?: string;
  note?: string;
  planDepartAt?: string | null;
  planArriveAt?: string | null;
}

export interface ReassignPayload {
  vehicleId: number;
  driverId: number;
}

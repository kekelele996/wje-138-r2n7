import { VehicleStatus } from './enums';

export type Vehicle = {
  id: number;
  plateNo: string;
  type: string;
  vehicleType: string;
  brandModel: string;
  purchaseDate: string | null;
  insuranceExpireDate: string | null;
  inspectionExpireDate: string | null;
  status: VehicleStatus;
  mileage: number;
  tankCapacity: number;
  payloadCapacity: number;
  fuelConsumption: number;
  statusChangedAt?: string | null;
};

export type CreateVehiclePayload = {
  plateNo: string;
  vehicleType: string;
  brandModel: string;
  insuranceExpireDate?: string | null;
  inspectionExpireDate?: string | null;
  payloadCapacity?: number;
  tankCapacity?: number;
  fuelConsumption?: number;
  mileage?: number;
};

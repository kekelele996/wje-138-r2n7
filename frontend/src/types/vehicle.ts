import { VehicleStatus } from './enums';
export type Vehicle = { id: number; plateNo: string; type: string; brandModel: string; purchaseDate: string | null; insuranceExpireDate: string | null; inspectionExpireDate: string | null; status: VehicleStatus; mileage: number; tankCapacity: number; fuelConsumption: number; loadCapacity: number };

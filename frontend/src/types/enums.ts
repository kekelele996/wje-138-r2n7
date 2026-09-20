export enum VehicleStatus { Available = 'Available', OnTrip = 'OnTrip', Maintenance = 'Maintenance', Retired = 'Retired' }
export enum DispatchStatus { Pending = 'Pending', Assigned = 'Assigned', InProgress = 'InProgress', Completed = 'Completed', Cancelled = 'Cancelled' }
export enum MaintenanceType { Routine = 'Routine', Repair = 'Repair', Emergency = 'Emergency', Inspection = 'Inspection' }
export enum DriverStatus { Available = 'Available', OnTrip = 'OnTrip', Leave = 'Leave', Suspended = 'Suspended' }
export enum PaymentMethod { Cash = 'Cash', Card = 'Card', Company = 'Company' }

// 后端业务错误码（与 backend/fleet_app/exceptions.py、dispatch_service.py 对应）
export enum DispatchErrorCode {
  VehicleUnavailable = 'vehicle_unavailable',
  VehicleInsuranceExpired = 'vehicle_insurance_expired',
  LoadExceeded = 'load_exceeded',
  DriverUnavailable = 'driver_unavailable',
  DriverLicenseExpired = 'driver_license_expired',
  VehicleBusy = 'vehicle_busy',
  DriverBusy = 'driver_busy',
  IllegalTransition = 'illegal_transition',
  DuplicateOperation = 'duplicate_operation',
  AlreadyFinished = 'already_finished',
  NotFound = 'not_found',
}

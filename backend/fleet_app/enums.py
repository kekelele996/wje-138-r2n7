"""后端共享枚举/常量（前后端枚举保持一致，见 README「枚举位置」）。"""


class VehicleStatus:
    AVAILABLE = 'Available'
    ON_TRIP = 'OnTrip'
    MAINTENANCE = 'Maintenance'
    RETIRED = 'Retired'
    CHOICES = [
        (AVAILABLE, '可用'),
        (ON_TRIP, '运输中'),
        (MAINTENANCE, '维保中'),
        (RETIRED, '已报废'),
    ]


class DriverStatus:
    AVAILABLE = 'Available'
    ON_TRIP = 'OnTrip'
    LEAVE = 'Leave'
    SUSPENDED = 'Suspended'
    CHOICES = [
        (AVAILABLE, '可用'),
        (ON_TRIP, '运输中'),
        (LEAVE, '休假'),
        (SUSPENDED, '停用'),
    ]


class DispatchStatus:
    PENDING = 'Pending'
    ASSIGNED = 'Assigned'
    IN_PROGRESS = 'InProgress'
    COMPLETED = 'Completed'
    CANCELLED = 'Cancelled'

    # 未结束：占用车辆与司机，禁止再被分配
    ACTIVE_STATUSES = (ASSIGNED, IN_PROGRESS)
    # 终态
    FINISHED_STATUSES = (COMPLETED, CANCELLED)


class MaintenanceType:
    ROUTINE = 'Routine'
    REPAIR = 'Repair'
    EMERGENCY = 'Emergency'
    INSPECTION = 'Inspection'


# 调度单状态流转白名单：当前状态 -> 允许进入的状态
DISPATCH_TRANSITIONS = {
    DispatchStatus.ASSIGNED: (DispatchStatus.IN_PROGRESS, DispatchStatus.CANCELLED),
    DispatchStatus.IN_PROGRESS: (DispatchStatus.COMPLETED, DispatchStatus.CANCELLED),
}

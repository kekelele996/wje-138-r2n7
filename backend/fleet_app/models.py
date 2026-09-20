from django.db import models
from django.db.models import Q


# ============================================================
# 共享枚举（与 frontend/src/types/enums.ts 保持一致）
# ============================================================
class VehicleStatus(models.TextChoices):
    AVAILABLE = 'Available', '可用'
    ON_TRIP = 'OnTrip', '运输中'
    MAINTENANCE = 'Maintenance', '维保中'
    RETIRED = 'Retired', '已报废'


class DriverStatus(models.TextChoices):
    AVAILABLE = 'Available', '可用'
    ON_TRIP = 'OnTrip', '运输中'
    LEAVE = 'Leave', '休假'
    SUSPENDED = 'Suspended', '停职'


class DispatchStatus(models.TextChoices):
    PENDING = 'Pending', '待指派'
    ASSIGNED = 'Assigned', '已指派'
    IN_PROGRESS = 'InProgress', '运输中'
    COMPLETED = 'Completed', '已完成'
    CANCELLED = 'Cancelled', '已取消'


class MaintenanceType(models.TextChoices):
    ROUTINE = 'Routine', '常规保养'
    REPAIR = 'Repair', '维修'
    EMERGENCY = 'Emergency', '紧急维修'
    INSPECTION = 'Inspection', '年检'


class MaintenanceStatus(models.TextChoices):
    SCHEDULED = 'Scheduled', '已计划'
    IN_PROGRESS = 'InProgress', '进行中'
    COMPLETED = 'Completed', '已完成'


class PaymentMethod(models.TextChoices):
    CASH = 'Cash', '现金'
    CARD = 'Card', '油卡'
    COMPANY = 'Company', '公司结算'


# 尚未结束的调度单状态：车辆/司机在此状态集合内视为被占用
ACTIVE_DISPATCH_STATUSES = (DispatchStatus.ASSIGNED, DispatchStatus.IN_PROGRESS)


# ============================================================
# 实体 1：车辆 Vehicle
# ============================================================
class Vehicle(models.Model):
    plate_no = models.CharField('车牌号', max_length=32, unique=True)
    vehicle_type = models.CharField('车辆类型', max_length=32)
    brand_model = models.CharField('品牌型号', max_length=80)
    purchase_date = models.DateField('购买日期', null=True, blank=True)
    insurance_expire_date = models.DateField('保险到期日', null=True, blank=True)
    inspection_expire_date = models.DateField('年检到期日', null=True, blank=True)
    status = models.CharField(
        '当前状态', max_length=24, choices=VehicleStatus.choices, default=VehicleStatus.AVAILABLE
    )
    mileage = models.IntegerField('累计里程(km)', default=0)
    tank_capacity = models.FloatField('油箱容量(L)', default=0)
    payload_capacity = models.FloatField('额定载重(kg)', default=0)
    fuel_consumption = models.FloatField('当前油耗(L/100km)', default=0)

    # 状态时间戳：持久化状态变化发生的时间，服务重启后仍可查询
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_changed_at = models.DateTimeField('状态变更时间', null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.plate_no} ({self.brand_model})'


# ============================================================
# 实体 2：司机 Driver
# ============================================================
class Driver(models.Model):
    name = models.CharField('姓名', max_length=40)
    phone = models.CharField('手机号', max_length=32, unique=True)
    license_type = models.CharField('驾照类型', max_length=8)
    license_expire_date = models.DateField('驾照到期日', null=True, blank=True)
    hire_date = models.DateField('入职日期', null=True, blank=True)
    status = models.CharField(
        '当前状态', max_length=24, choices=DriverStatus.choices, default=DriverStatus.AVAILABLE
    )
    driving_hours = models.IntegerField('累计驾驶时长(h)', default=0)
    violation_count = models.IntegerField('违章次数', default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_changed_at = models.DateTimeField('状态变更时间', null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.name} ({self.phone})'


# ============================================================
# 实体 3：调度单 DispatchOrder
# ============================================================
class DispatchOrder(models.Model):
    order_no = models.CharField('单号', max_length=40, unique=True)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.SET_NULL, null=True, related_name='dispatch_orders'
    )
    driver = models.ForeignKey(
        Driver, on_delete=models.SET_NULL, null=True, related_name='dispatch_orders'
    )
    origin = models.CharField('出发地', max_length=120)
    destination = models.CharField('目的地', max_length=120)
    plan_depart_at = models.DateTimeField('预计出发时间', null=True, blank=True)
    plan_arrive_at = models.DateTimeField('预计到达时间', null=True, blank=True)
    actual_depart_at = models.DateTimeField('实际出发时间', null=True, blank=True)
    actual_arrive_at = models.DateTimeField('实际到达时间', null=True, blank=True)
    cargo = models.CharField('货物描述', max_length=160, blank=True, default='')
    weight = models.FloatField('重量(kg)', default=0)
    freight = models.FloatField('运费', default=0)
    status = models.CharField(
        '状态', max_length=24, choices=DispatchStatus.choices, default=DispatchStatus.ASSIGNED
    )
    creator_id = models.IntegerField('创建人ID', default=1)
    note = models.TextField('备注', blank=True, default='')

    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField('指派时间', null=True, blank=True)
    started_at = models.DateTimeField('开始运输时间', null=True, blank=True)
    completed_at = models.DateTimeField('完成时间', null=True, blank=True)
    cancelled_at = models.DateTimeField('取消时间', null=True, blank=True)

    class Meta:
        ordering = ['-id']
        constraints = [
            # 同一车辆/司机最多只允许一张未结束单据（数据库层最终防线）
            models.UniqueConstraint(
                fields=['vehicle'],
                condition=Q(status__in=list(ACTIVE_DISPATCH_STATUSES)),
                name='uniq_active_dispatch_per_vehicle',
            ),
            models.UniqueConstraint(
                fields=['driver'],
                condition=Q(status__in=list(ACTIVE_DISPATCH_STATUSES)),
                name='uniq_active_dispatch_per_driver',
            ),
        ]

    def __str__(self):
        return self.order_no


# ============================================================
# 调度单事件流：状态变化保留时间（运输时间线），服务重启后仍可查询
# ============================================================
class DispatchEventType(models.TextChoices):
    CREATED = 'Created', '创建调度单'
    ASSIGNED = 'Assigned', '指派车辆与司机'
    REASSIGNED = 'Reassigned', '改派'
    STARTED = 'Started', '开始运输'
    COMPLETED = 'Completed', '完成运输'
    CANCELLED = 'Cancelled', '取消调度单'


class DispatchEvent(models.Model):
    order = models.ForeignKey(
        DispatchOrder, on_delete=models.CASCADE, related_name='events'
    )
    event_type = models.CharField(max_length=24, choices=DispatchEventType.choices)
    from_status = models.CharField(max_length=24, blank=True, default='')
    to_status = models.CharField(max_length=24, blank=True, default='')
    detail = models.CharField(max_length=255, blank=True, default='')
    operator_id = models.IntegerField(default=1)
    created_at = models.DateTimeField('发生时间', auto_now_add=True)

    class Meta:
        ordering = ['id']
        indexes = [models.Index(fields=['order', 'id'])]


# ============================================================
# 实体 4：维保记录 MaintenanceRecord
# ============================================================
class MaintenanceRecord(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='maintenance_records'
    )
    maintenance_type = models.CharField(max_length=24, choices=MaintenanceType.choices)
    items = models.JSONField(default=list, blank=True)
    cost = models.FloatField('维修费用', default=0)
    vendor = models.CharField('维修厂', max_length=120, blank=True, default='')
    date = models.DateField('维修日期', null=True, blank=True)
    next_mileage = models.IntegerField('下次保养里程', default=0)
    next_date = models.DateField('下次保养日期', null=True, blank=True)
    status = models.CharField(
        max_length=24, choices=MaintenanceStatus.choices, default=MaintenanceStatus.SCHEDULED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']


# ============================================================
# 实体 5：油耗记录 FuelRecord
# ============================================================
class FuelRecord(models.Model):
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name='fuel_records'
    )
    date = models.DateField('加油日期', null=True, blank=True)
    liters = models.FloatField('加油量(L)', default=0)
    unit_price = models.FloatField('单价', default=0)
    total_amount = models.FloatField('总金额', default=0)
    mileage = models.IntegerField('当前里程', default=0)
    station = models.CharField('加油站', max_length=120, blank=True, default='')
    payment_method = models.CharField(
        max_length=24, choices=PaymentMethod.choices, default=PaymentMethod.COMPANY
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']

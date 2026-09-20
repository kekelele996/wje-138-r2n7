from django.db import models


# ===== Vehicle =====
class Vehicle(models.Model):
    plate_no = models.CharField(max_length=32)
    vehicle_type = models.CharField(max_length=32)
    brand_model = models.CharField(max_length=80)
    purchase_date = models.DateField(null=True)
    insurance_expire_date = models.DateField(null=True)
    inspection_expire_date = models.DateField(null=True)
    status = models.CharField(max_length=24)
    mileage = models.IntegerField(default=0)
    tank_capacity = models.FloatField(default=0)
    fuel_consumption = models.FloatField(default=0)
    # 核定载重（kg），派单时货物重量不得超过该值
    load_capacity = models.FloatField(default=0)


# ===== Driver =====
class Driver(models.Model):
    name = models.CharField(max_length=40)
    phone = models.CharField(max_length=32)
    license_type = models.CharField(max_length=8)
    license_expire_date = models.DateField(null=True)
    hire_date = models.DateField(null=True)
    status = models.CharField(max_length=24)
    driving_hours = models.IntegerField(default=0)
    violation_count = models.IntegerField(default=0)


# ===== DispatchOrder =====
# 未结束（占用车辆/司机）的单据状态：Assigned、InProgress
class DispatchOrder(models.Model):
    order_no = models.CharField(max_length=40, unique=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    origin = models.CharField(max_length=120)
    destination = models.CharField(max_length=120)
    plan_depart_at = models.DateTimeField(null=True, blank=True)
    plan_arrive_at = models.DateTimeField(null=True, blank=True)
    actual_depart_at = models.DateTimeField(null=True, blank=True)
    actual_arrive_at = models.DateTimeField(null=True, blank=True)
    cargo = models.CharField(max_length=160)
    weight = models.FloatField(default=0)
    freight = models.FloatField(default=0)
    status = models.CharField(max_length=24, default='Assigned')
    creator_id = models.IntegerField(default=1)
    note = models.TextField(blank=True, default='')
    # 状态变化时间（持久化，重启后仍可查询）
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)


# ===== DispatchStatusEvent：状态流转事件（运输时间线数据源） =====
class DispatchStatusEvent(models.Model):
    order = models.ForeignKey(DispatchOrder, related_name='events', on_delete=models.CASCADE)
    from_status = models.CharField(max_length=24, blank=True, default='')
    to_status = models.CharField(max_length=24)
    remark = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']


# ===== MaintenanceRecord =====
class MaintenanceRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    maintenance_type = models.CharField(max_length=24)
    items = models.JSONField(default=list)
    cost = models.FloatField(default=0)
    vendor = models.CharField(max_length=120)
    date = models.DateField(null=True)
    next_mileage = models.IntegerField(default=0)
    next_date = models.DateField(null=True)
    status = models.CharField(max_length=24)


# ===== FuelRecord =====
class FuelRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    liters = models.FloatField(default=0)
    unit_price = models.FloatField(default=0)
    total_amount = models.FloatField(default=0)
    mileage = models.IntegerField(default=0)
    station = models.CharField(max_length=120)
    payment_method = models.CharField(max_length=24)

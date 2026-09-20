"""调度派单闭环核心服务。

规则：
- 创建时校验：车辆存在、状态 Available、载重足够、保险有效；
  司机存在、证件（驾照）未过期；车辆/司机无未结束（Assigned/InProgress）单据。
- 开始运输：仅 Assigned -> InProgress，同步车辆/司机为 OnTrip。
- 完成运输：仅 InProgress -> Completed，恢复车辆/司机为 Available。
- 取消：Assigned/InProgress -> Cancelled，恢复车辆/司机为 Available。
- 运输中（InProgress）的单据禁止改派、禁止重复操作。
- 每次状态变化写入时间戳与 DispatchStatusEvent，随数据库持久化。
"""

from django.db import transaction
from django.utils import timezone

from fleet_app.enums import (
    DISPATCH_TRANSITIONS,
    DispatchStatus,
    DriverStatus,
    VehicleStatus,
)
from fleet_app.exceptions import BusinessError, ConflictError
from fleet_app.models import DispatchOrder, DispatchStatusEvent, Driver, Vehicle
from fleet_app.serializers.dispatch_serializer import (
    DispatchCreateSerializer,
    DispatchSerializer,
)


def list_orders(status=None):
    queryset = DispatchOrder.objects.select_related('vehicle', 'driver').prefetch_related('events')
    if status:
        queryset = queryset.filter(status=status)
    return DispatchSerializer(queryset.order_by('-id'), many=True).data


def get_order_or_404(order_id):
    try:
        return DispatchOrder.objects.select_related('vehicle', 'driver').get(pk=order_id)
    except DispatchOrder.DoesNotExist:
        raise BusinessError('调度单不存在', code='not_found', status_code=404)


def _has_active_order(*, vehicle_id=None, driver_id=None, exclude_order_id=None):
    """返回占用该车辆或司机的未结束单据（Assigned / InProgress）。"""
    queryset = DispatchOrder.objects.filter(status__in=DispatchStatus.ACTIVE_STATUSES)
    if exclude_order_id is not None:
        queryset = queryset.exclude(pk=exclude_order_id)
    if vehicle_id is not None and queryset.filter(vehicle_id=vehicle_id).exists():
        return queryset.get(vehicle_id=vehicle_id)
    if driver_id is not None and queryset.filter(driver_id=driver_id).exists():
        return queryset.get(driver_id=driver_id)
    return None


def _generate_order_no(now):
    day = now.strftime('%Y%m%d')
    prefix = f'DSP-{day}-'
    same_day = DispatchOrder.objects.filter(order_no__startswith=prefix).count()
    return f'{prefix}{same_day + 1:04d}'


def _validate_create(vehicle, driver, weight, today):
    """创建派单的全部前置条件，冲突时抛出带原因的 BusinessError。"""
    if vehicle.status != VehicleStatus.AVAILABLE:
        raise ConflictError(
            f'车辆 {vehicle.plate_no} 当前状态为 {vehicle.status}，仅可用（Available）车辆允许派单',
            code='vehicle_unavailable',
        )
    if vehicle.insurance_expire_date is None or vehicle.insurance_expire_date < today:
        expire = vehicle.insurance_expire_date or '未登记'
        raise BusinessError(
            f'车辆 {vehicle.plate_no} 保险已失效（到期日：{expire}），不允许派单',
            code='vehicle_insurance_expired',
        )
    if weight > vehicle.load_capacity:
        raise BusinessError(
            f'货物重量 {weight:g}kg 超过车辆 {vehicle.plate_no} 的核定载重 {vehicle.load_capacity:g}kg',
            code='load_exceeded',
        )
    if driver.license_expire_date is None or driver.license_expire_date < today:
        expire = driver.license_expire_date or '未登记'
        raise BusinessError(
            f'司机 {driver.name} 的驾照已过期（到期日：{expire}），不允许派单',
            code='driver_license_expired',
        )
    if driver.status != DriverStatus.AVAILABLE:
        raise ConflictError(
            f'司机 {driver.name} 当前状态为 {driver.status}，暂不可分配',
            code='driver_unavailable',
        )


@transaction.atomic
def create_order(payload):
    serializer = DispatchCreateSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    today = timezone.localdate()

    # 行锁锁定车辆/司机，避免并发重复分配
    try:
        vehicle = Vehicle.objects.select_for_update().get(pk=data['vehicle_id'])
    except Vehicle.DoesNotExist:
        raise BusinessError('所选车辆不存在', code='vehicle_not_found', status_code=404)
    try:
        driver = Driver.objects.select_for_update().get(pk=data['driver_id'])
    except Driver.DoesNotExist:
        raise BusinessError('所选司机不存在', code='driver_not_found', status_code=404)

    _validate_create(vehicle, driver, data['weight'], today)

    busy = _has_active_order(vehicle_id=vehicle.id)
    if busy is not None:
        raise ConflictError(
            f'车辆 {vehicle.plate_no} 已有未结束单据 {busy.order_no}（{busy.status}），拒绝重复分配',
            code='vehicle_busy',
        )
    busy = _has_active_order(driver_id=driver.id)
    if busy is not None:
        raise ConflictError(
            f'司机 {driver.name} 已有未结束单据 {busy.order_no}（{busy.status}），拒绝重复分配',
            code='driver_busy',
        )

    now = timezone.now()
    order = DispatchOrder.objects.create(
        order_no=_generate_order_no(now),
        vehicle=vehicle,
        driver=driver,
        origin=data['origin'],
        destination=data['destination'],
        plan_depart_at=data.get('plan_depart_at'),
        plan_arrive_at=data.get('plan_arrive_at'),
        cargo=data['cargo'],
        weight=data['weight'],
        freight=data.get('freight', 0),
        status=DispatchStatus.ASSIGNED,
        creator_id=data.get('creator_id', 1),
        note=data.get('note', ''),
        assigned_at=now,
    )
    DispatchStatusEvent.objects.create(
        order=order, from_status='', to_status=DispatchStatus.ASSIGNED,
        remark='调度单创建并指派车辆与司机',
    )
    return DispatchSerializer(get_order_or_404(order.id)).data


@transaction.atomic
def _transit(order_id, target, *, remark, sync_status=None, actual_depart=False,
             actual_arrive=False, timestamp_attr):
    """通用状态流转：校验白名单 -> 加锁 -> 写时间戳/事件 -> 同步车辆司机状态。"""
    try:
        order = DispatchOrder.objects.select_for_update().select_related('vehicle', 'driver').get(pk=order_id)
    except DispatchOrder.DoesNotExist:
        raise BusinessError('调度单不存在', code='not_found', status_code=404)
    allowed = DISPATCH_TRANSITIONS.get(order.status, ())
    if target not in allowed:
        if order.status == target:
            raise ConflictError(f'单据 {order.order_no} 已处于 {target} 状态，请勿重复操作',
                                code='duplicate_operation')
        if order.status in DispatchStatus.FINISHED_STATUSES:
            raise ConflictError(f'单据 {order.order_no} 已{order.status}，为终态单据，不能再操作',
                                code='already_finished')
        raise ConflictError(
            f'单据 {order.order_no} 当前状态为 {order.status}，不允许{remark}',
            code='illegal_transition',
        )

    now = timezone.now()
    setattr(order, timestamp_attr, now)
    if actual_depart:
        order.actual_depart_at = now
    if actual_arrive:
        order.actual_arrive_at = now
    old_status = order.status
    order.status = target
    order.save(update_fields=['status', timestamp_attr] +
               (['actual_depart_at'] if actual_depart else []) +
               (['actual_arrive_at'] if actual_arrive else []))

    if sync_status is not None:
        Vehicle.objects.filter(pk=order.vehicle_id).update(status=sync_status)
        Driver.objects.filter(pk=order.driver_id).update(status=sync_status)

    DispatchStatusEvent.objects.create(
        order=order, from_status=old_status, to_status=target, remark=remark,
    )
    return DispatchSerializer(get_order_or_404(order.id)).data


def start_order(order_id):
    # Assigned -> InProgress；运输中的单据不得重复开始或改派
    return _transit(
        order_id, DispatchStatus.IN_PROGRESS,
        remark='开始运输', sync_status=VehicleStatus.ON_TRIP,
        actual_depart=True, timestamp_attr='started_at',
    )


def complete_order(order_id):
    # InProgress -> Completed；车辆/司机恢复 Available
    return _transit(
        order_id, DispatchStatus.COMPLETED,
        remark='完成运输', sync_status=VehicleStatus.AVAILABLE,
        actual_arrive=True, timestamp_attr='completed_at',
    )


def cancel_order(order_id):
    # Assigned/InProgress -> Cancelled；车辆/司机恢复 Available
    return _transit(
        order_id, DispatchStatus.CANCELLED,
        remark='取消调度单', sync_status=VehicleStatus.AVAILABLE,
        timestamp_attr='cancelled_at',
    )

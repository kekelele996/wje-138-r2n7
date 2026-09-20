"""派单闭环领域服务。

创建规则：
  - 车辆必须 Available、载重 >= 货物重量、保险未过期
  - 司机必须 Available、驾照未过期
  - 同一车辆或司机已有未结束单据（Assigned/InProgress）时拒绝分配
流转规则：
  - Assigned --start--> InProgress，同步车辆/司机 -> OnTrip
  - InProgress --complete--> Completed，恢复车辆/司机 -> Available
  - Assigned/InProgress --cancel--> Cancelled，恢复车辆/司机 -> Available
  - InProgress 单据不得改派；任何状态不得重复操作
所有状态变化写入 DispatchEvent 并落库，重启后仍可查询。
"""
import time

from django.db import IntegrityError, OperationalError, transaction
from django.utils import timezone

from fleet_app.models import (
    ACTIVE_DISPATCH_STATUSES,
    DispatchEvent,
    DispatchEventType,
    DispatchOrder,
    DispatchStatus,
    Driver,
    DriverStatus,
    Vehicle,
    VehicleStatus,
)
from fleet_app.serializers.dispatch_serializer import DispatchSerializer
from fleet_app.services.driver_service import get_driver
from fleet_app.services.exceptions import (
    BusinessError,
    DispatchConflictError,
    InvalidStatusError,
    NotFoundError,
)
from fleet_app.services.vehicle_service import get_vehicle


def list_orders(status: str | None = None):
    queryset = DispatchOrder.objects.select_related('vehicle', 'driver').prefetch_related('events')
    if status:
        queryset = queryset.filter(status=status)
    return DispatchSerializer(queryset, many=True).data


def retrieve_order(pk: int):
    return DispatchSerializer(_get_order(pk)).data


def _get_order(pk: int) -> DispatchOrder:
    try:
        return DispatchOrder.objects.select_related('vehicle', 'driver').get(pk=pk)
    except DispatchOrder.DoesNotExist:
        raise NotFoundError(f'调度单不存在：id={pk}')


def _log_event(order, event_type, from_status, to_status, detail=''):
    DispatchEvent.objects.create(
        order=order,
        event_type=event_type,
        from_status=from_status or '',
        to_status=to_status or '',
        detail=detail,
    )


def _generate_order_no(today) -> str:
    prefix = f'DSP-{today:%Y%m%d}-'
    seq = DispatchOrder.objects.filter(order_no__startswith=prefix).count() + 1
    for _ in range(10):
        candidate = f'{prefix}{seq:04d}'
        if not DispatchOrder.objects.filter(order_no=candidate).exists():
            return candidate
        seq += 1
    raise BusinessError('单号生成冲突，请稍后重试')


def _validate_vehicle(vehicle: Vehicle, weight: float):
    """车辆状态可用、载重足够、保险有效。"""
    if vehicle.status != VehicleStatus.AVAILABLE:
        raise DispatchConflictError(
            f'车辆 {vehicle.plate_no} 当前状态为 {vehicle.status}，仅 Available 车辆可派单'
        )
    if not vehicle.insurance_expire_date:
        raise BusinessError(f'车辆 {vehicle.plate_no} 未登记保险到期日，保险无效')
    if vehicle.insurance_expire_date < timezone.localdate():
        raise BusinessError(
            f'车辆 {vehicle.plate_no} 保险已于 {vehicle.insurance_expire_date:%Y-%m-%d} 过期',
            code='VEHICLE_INSURANCE_EXPIRED',
        )
    if weight and vehicle.payload_capacity and vehicle.payload_capacity < weight:
        raise BusinessError(
            f'车辆 {vehicle.plate_no} 额定载重 {vehicle.payload_capacity:g}kg，'
            f'不足以装载 {weight:g}kg 货物',
            code='VEHICLE_PAYLOAD_INSUFFICIENT',
        )


def _validate_driver(driver: Driver):
    """司机状态可用、证件（驾照）未过期。"""
    if driver.status != DriverStatus.AVAILABLE:
        raise DispatchConflictError(
            f'司机 {driver.name} 当前状态为 {driver.status}，仅 Available 司机可派单'
        )
    if not driver.license_expire_date:
        raise BusinessError(f'司机 {driver.name} 未登记驾照到期日，证件无效')
    if driver.license_expire_date < timezone.localdate():
        raise BusinessError(
            f'司机 {driver.name} 驾照已于 {driver.license_expire_date:%Y-%m-%d} 过期',
            code='DRIVER_LICENSE_EXPIRED',
        )


def _ensure_not_occupied(vehicle: Vehicle, driver: Driver, exclude_order_id: int | None = None):
    """同一车辆或司机存在未结束单据时拒绝分配。"""
    base = DispatchOrder.objects.filter(status__in=ACTIVE_DISPATCH_STATUSES)
    if exclude_order_id is not None:
        base = base.exclude(id=exclude_order_id)

    vehicle_conflict = base.filter(vehicle=vehicle).first()
    if vehicle_conflict:
        raise DispatchConflictError(
            f'车辆 {vehicle.plate_no} 已有未结束单据 {vehicle_conflict.order_no}'
            f'（{vehicle_conflict.get_status_display()}），不能重复分配'
        )
    driver_conflict = base.filter(driver=driver).first()
    if driver_conflict:
        raise DispatchConflictError(
            f'司机 {driver.name} 已有未结束单据 {driver_conflict.order_no}'
            f'（{driver_conflict.get_status_display()}），不能重复分配'
        )


def create_order(payload: dict) -> dict:
    serializer = DispatchSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if data.get('vehicle') is None:
        raise BusinessError('请选择指派车辆')
    if data.get('driver') is None:
        raise BusinessError('请选择指派司机')
    weight = data.get('weight') or 0
    vehicle_pk = data['vehicle'].pk
    driver_pk = data['driver'].pk

    now = timezone.now()
    order = None
    # 整个校验+落库放进 savepoint 重试：
    #   PostgreSQL 由 SELECT FOR UPDATE 串行化；SQLite 写锁冲突时退避重试
    for attempt in range(6):
        try:
            with transaction.atomic():
                vehicle = Vehicle.objects.select_for_update().get(pk=vehicle_pk)
                driver = Driver.objects.select_for_update().get(pk=driver_pk)
                _validate_vehicle(vehicle, weight)
                _validate_driver(driver)
                _ensure_not_occupied(vehicle, driver)

                order_no = _generate_order_no(now.date())
                order = DispatchOrder.objects.create(
                    order_no=order_no,
                    vehicle=vehicle,
                    driver=driver,
                    origin=data['origin'],
                    destination=data['destination'],
                    plan_depart_at=data.get('plan_depart_at'),
                    plan_arrive_at=data.get('plan_arrive_at'),
                    cargo=data.get('cargo', ''),
                    weight=weight,
                    freight=data.get('freight', 0),
                    status=DispatchStatus.ASSIGNED,
                    creator_id=data.get('creator_id') or 1,
                    note=data.get('note', ''),
                    assigned_at=now,
                )
            break
        except OperationalError as exc:
            order = None
            if 'locked' in str(exc).lower() and attempt < 5:
                time.sleep(0.15 * (attempt + 1))
                continue
            raise
        except IntegrityError:
            # 并发穿透时由部分唯一约束兜底：事务外重试一次即可检测到占用
            order = None
            if attempt < 5:
                time.sleep(0.05)
                continue
            raise

    if order is None:
        raise DispatchConflictError('资源繁忙，请稍后重试')

    with transaction.atomic():
        # 重新取出关联用于事件文案
        vehicle = Vehicle.objects.get(pk=vehicle_pk)
        driver = Driver.objects.get(pk=driver_pk)
        _log_event(
            DispatchOrder.objects.get(pk=order.pk),
            DispatchEventType.CREATED, '', DispatchStatus.ASSIGNED,
            f'创建调度单并指派车辆 {vehicle.plate_no}、司机 {driver.name}',
        )
        order.refresh_from_db()
    return DispatchSerializer(order).data


@transaction.atomic
def start_order(pk: int) -> dict:
    order = _lock_order(pk)
    if order.status != DispatchStatus.ASSIGNED:
        raise InvalidStatusError(
            _illegal_action_reason(order, '开始运输')
        )

    vehicle = Vehicle.objects.select_for_update().get(pk=order.vehicle_id)
    driver = Driver.objects.select_for_update().get(pk=order.driver_id)

    # 防御性校验：车辆/司机被其他单据占用或转为不可用状态时拒绝
    other_trip = DispatchOrder.objects.filter(
        status=DispatchStatus.IN_PROGRESS
    ).exclude(id=order.id)
    if other_trip.filter(vehicle=vehicle).exists():
        raise DispatchConflictError(f'车辆 {vehicle.plate_no} 正在执行其他运输任务')
    if other_trip.filter(driver=driver).exists():
        raise DispatchConflictError(f'司机 {driver.name} 正在执行其他运输任务')
    if vehicle.status not in (VehicleStatus.AVAILABLE, VehicleStatus.ON_TRIP):
        raise DispatchConflictError(
            f'车辆 {vehicle.plate_no} 当前状态为 {vehicle.status}，无法开始运输'
        )
    if driver.status not in (DriverStatus.AVAILABLE, DriverStatus.ON_TRIP):
        raise DispatchConflictError(
            f'司机 {driver.name} 当前状态为 {driver.status}，无法开始运输'
        )

    now = timezone.now()
    previous = order.status
    order.status = DispatchStatus.IN_PROGRESS
    order.started_at = now
    order.actual_depart_at = now
    order.save(update_fields=['status', 'started_at', 'actual_depart_at', 'updated_at'])

    vehicle.status = VehicleStatus.ON_TRIP
    vehicle.status_changed_at = now
    vehicle.save(update_fields=['status', 'status_changed_at', 'updated_at'])
    driver.status = DriverStatus.ON_TRIP
    driver.status_changed_at = now
    driver.save(update_fields=['status', 'status_changed_at', 'updated_at'])

    _log_event(
        order, DispatchEventType.STARTED, previous, DispatchStatus.IN_PROGRESS,
        '车辆与司机切换为 OnTrip，运输开始',
    )
    return DispatchSerializer(order).data


@transaction.atomic
def complete_order(pk: int) -> dict:
    order = _lock_order(pk)
    if order.status != DispatchStatus.IN_PROGRESS:
        raise InvalidStatusError(_illegal_action_reason(order, '完成运输'))

    now = timezone.now()
    previous = order.status
    order.status = DispatchStatus.COMPLETED
    order.completed_at = now
    order.actual_arrive_at = now
    order.save(update_fields=['status', 'completed_at', 'actual_arrive_at', 'updated_at'])

    _release_assets(order, now)
    _log_event(
        order, DispatchEventType.COMPLETED, previous, DispatchStatus.COMPLETED,
        '运输完成，车辆与司机恢复 Available',
    )
    return DispatchSerializer(order).data


@transaction.atomic
def cancel_order(pk: int) -> dict:
    order = _lock_order(pk)
    if order.status not in (DispatchStatus.ASSIGNED, DispatchStatus.IN_PROGRESS):
        raise InvalidStatusError(_illegal_action_reason(order, '取消'))

    now = timezone.now()
    previous = order.status
    order.status = DispatchStatus.CANCELLED
    order.cancelled_at = now
    order.save(update_fields=['status', 'cancelled_at', 'updated_at'])

    _release_assets(order, now)
    _log_event(
        order, DispatchEventType.CANCELLED, previous, DispatchStatus.CANCELLED,
        '调度单已取消，车辆与司机恢复 Available',
    )
    return DispatchSerializer(order).data


@transaction.atomic
def reassign_order(pk: int, payload: dict) -> dict:
    order = _lock_order(pk)
    if order.status == DispatchStatus.IN_PROGRESS:
        raise InvalidStatusError(f'单据 {order.order_no} 运输中，不得改派')
    if order.status != DispatchStatus.ASSIGNED:
        raise InvalidStatusError(_illegal_action_reason(order, '改派'))

    new_vehicle_id = payload.get('vehicleId') or payload.get('vehicle')
    new_driver_id = payload.get('driverId') or payload.get('driver')
    if not new_vehicle_id or not new_driver_id:
        raise BusinessError('改派必须同时提供新的车辆和司机')

    old_vehicle = get_vehicle(order.vehicle_id)
    old_driver = get_driver(order.driver_id)
    vehicle = Vehicle.objects.select_for_update().get(pk=new_vehicle_id)
    driver = Driver.objects.select_for_update().get(pk=new_driver_id)

    _validate_vehicle(vehicle, order.weight)
    _validate_driver(driver)
    _ensure_not_occupied(vehicle, driver, exclude_order_id=order.id)

    now = timezone.now()
    order.vehicle = vehicle
    order.driver = driver
    order.assigned_at = now
    order.save(update_fields=['vehicle', 'driver', 'assigned_at', 'updated_at'])

    _log_event(
        order, DispatchEventType.REASSIGNED, DispatchStatus.ASSIGNED,
        DispatchStatus.ASSIGNED,
        f'车辆 {old_vehicle.plate_no}→{vehicle.plate_no}；'
        f'司机 {old_driver.name}→{driver.name}',
    )
    return DispatchSerializer(order).data


def _lock_order(pk: int) -> DispatchOrder:
    try:
        return DispatchOrder.objects.select_for_update().select_related(
            'vehicle', 'driver'
        ).get(pk=pk)
    except DispatchOrder.DoesNotExist:
        raise NotFoundError(f'调度单不存在：id={pk}')


def _release_assets(order: DispatchOrder, now):
    """完成/取消后将车辆、司机恢复 Available。"""
    if order.vehicle_id:
        Vehicle.objects.filter(pk=order.vehicle_id, status=VehicleStatus.ON_TRIP).update(
            status=VehicleStatus.AVAILABLE, status_changed_at=now
        )
    if order.driver_id:
        Driver.objects.filter(pk=order.driver_id, status=DriverStatus.ON_TRIP).update(
            status=DriverStatus.AVAILABLE, status_changed_at=now
        )


def _illegal_action_reason(order: DispatchOrder, action: str) -> str:
    if order.status == DispatchStatus.IN_PROGRESS:
        return f'单据 {order.order_no} 正在运输中，不能重复{action}'
    if order.status == DispatchStatus.COMPLETED:
        return f'单据 {order.order_no} 已完成，不能{action}'
    if order.status == DispatchStatus.CANCELLED:
        return f'单据 {order.order_no} 已取消，不能{action}'
    if order.status == DispatchStatus.PENDING:
        return f'单据 {order.order_no} 尚未指派车辆与司机，不能{action}'
    return f'单据 {order.order_no} 当前状态为 {order.status}，不能{action}'

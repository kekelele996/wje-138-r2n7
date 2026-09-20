"""写入演示数据（幂等）：覆盖 Available/OnTrip/Maintenance、保险过期、载重不足等场景。"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from fleet_app.models import (
    DispatchEvent,
    DispatchEventType,
    DispatchOrder,
    DispatchStatus,
    Driver,
    DriverStatus,
    FuelRecord,
    MaintenanceRecord,
    MaintenanceStatus,
    MaintenanceType,
    PaymentMethod,
    Vehicle,
    VehicleStatus,
)


class Command(BaseCommand):
    help = '初始化演示数据（已存在车辆/司机时跳过）'

    def handle(self, *args, **options):
        if Vehicle.objects.exists() or Driver.objects.exists():
            self.stdout.write('演示数据已存在，跳过 seed_demo')
            return

        today = timezone.localdate()

        # ---------------- 车辆 ----------------
        vehicles_spec = [
            # plate_no, type, brand, payload, insurance_offset, status
            ('沪A-7821', '冷链车', '东风天锦 KR', 10000, 60, VehicleStatus.AVAILABLE),
            ('沪B-3301', '轻卡', '江铃顺达', 4500, 90, VehicleStatus.AVAILABLE),
            ('苏E-5520', '重卡', '解放 J6P', 18000, 200, VehicleStatus.AVAILABLE),
            ('浙C-9012', '中卡', '福田欧马可', 8000, 45, VehicleStatus.AVAILABLE),
            ('沪D-6677', '危化车', '重汽豪沃', 20000, -10, VehicleStatus.AVAILABLE),  # 保险已过期
            ('苏F-2208', '重卡', '陕汽德龙', 12000, 120, VehicleStatus.MAINTENANCE),
            ('浙G-1188', '中卡', '东风多利卡', 6000, 20, VehicleStatus.AVAILABLE),
            ('沪H-9009', '冷链车', '江淮格尔发', 9000, -1, VehicleStatus.AVAILABLE),  # 保险昨天到期
        ]
        vehicles = []
        for idx, (plate, vtype, brand, payload, ins_off, vstatus) in enumerate(vehicles_spec, start=1):
            vehicle = Vehicle.objects.create(
                plate_no=plate,
                vehicle_type=vtype,
                brand_model=brand,
                purchase_date=date(2022, (idx % 12) + 1, 5),
                insurance_expire_date=today + timedelta(days=ins_off),
                inspection_expire_date=today + timedelta(days=ins_off + 120),
                status=vstatus,
                mileage=50000 + idx * 13700,
                tank_capacity=300 + idx * 25,
                payload_capacity=payload,
                fuel_consumption=round(18 + idx * 1.8, 1),
                status_changed_at=timezone.now(),
            )
            vehicles.append(vehicle)

        # ---------------- 司机 ----------------
        drivers_spec = [
            ('赵强', '13800000001', 'B2', 700, DriverStatus.AVAILABLE),
            ('孙晨', '13800000002', 'A2', 900, DriverStatus.AVAILABLE),
            ('李梅', '13800000003', 'C1', 400, DriverStatus.AVAILABLE),
            ('周涛', '13800000004', 'A2', -30, DriverStatus.AVAILABLE),  # 驾照过期
            ('吴磊', '13800000005', 'B2', 500, DriverStatus.LEAVE),
            ('郑爽', '13800000006', 'A1', 800, DriverStatus.AVAILABLE),
        ]
        drivers = []
        for idx, (name, phone, license_type, lic_off, dstatus) in enumerate(drivers_spec, start=1):
            driver = Driver.objects.create(
                name=name,
                phone=phone,
                license_type=license_type,
                license_expire_date=today + timedelta(days=lic_off),
                hire_date=date(2021, idx + 1, 10),
                status=dstatus,
                driving_hours=1000 + idx * 620,
                violation_count=idx % 3,
                status_changed_at=timezone.now(),
            )
            drivers.append(driver)

        # ---------------- 历史调度单（已完成/已取消，用于时间线演示） ----------------
        completed = self._make_order(
            vehicles[0], drivers[0], '上海青浦仓', '杭州萧山仓',
            6200, DispatchStatus.COMPLETED, days_ago=6
        )
        self._log_full_timeline(completed, vehicles[0], drivers[0])

        cancelled = self._make_order(
            vehicles[2], drivers[1], '苏州园区', '南京江宁',
            15000, DispatchStatus.CANCELLED, days_ago=3
        )
        DispatchEvent.objects.create(
            order=cancelled, event_type=DispatchEventType.CREATED,
            to_status=DispatchStatus.ASSIGNED,
            detail=f'创建调度单并指派车辆 {vehicles[2].plate_no}、司机 {drivers[1].name}',
        )
        DispatchEvent.objects.create(
            order=cancelled, event_type=DispatchEventType.CANCELLED,
            from_status=DispatchStatus.ASSIGNED, to_status=DispatchStatus.CANCELLED,
            detail='货主临时取消发货',
        )

        # ---------------- 维保 ----------------
        MaintenanceRecord.objects.create(
            vehicle=vehicles[5], maintenance_type=MaintenanceType.ROUTINE,
            items=['机油', '轮胎检查', '刹车调校'], cost=2100,
            vendor='青浦维保站', date=today - timedelta(days=2),
            next_mileage=vehicles[5].mileage + 10000,
            next_date=today + timedelta(days=88),
            status=MaintenanceStatus.IN_PROGRESS,
        )
        MaintenanceRecord.objects.create(
            vehicle=vehicles[0], maintenance_type=MaintenanceType.INSPECTION,
            items=['年检准备'], cost=980,
            vendor='上海车检中心', date=today - timedelta(days=30),
            next_mileage=vehicles[0].mileage + 15000,
            next_date=today + timedelta(days=335),
            status=MaintenanceStatus.COMPLETED,
        )

        # ---------------- 油耗 ----------------
        for i, (vehicle, liters) in enumerate([
            (vehicles[0], 240), (vehicles[2], 360), (vehicles[1], 180),
            (vehicles[3], 260), (vehicles[0], 235),
        ]):
            FuelRecord.objects.create(
                vehicle=vehicle, date=today - timedelta(days=i * 7 + 2),
                liters=liters, unit_price=7.35 + (i % 3) * 0.08,
                total_amount=round(liters * (7.35 + (i % 3) * 0.08), 2),
                mileage=vehicle.mileage - i * 1200,
                station=['青浦服务区', '苏州东站', '嘉定加油站'][i % 3],
                payment_method=PaymentMethod.COMPANY if i % 2 == 0 else PaymentMethod.CARD,
            )

        self.stdout.write(self.style.SUCCESS('演示数据初始化完成'))

    def _make_order(self, vehicle, driver, origin, destination, weight, status, days_ago):
        now = timezone.now()
        created = now - timezone.timedelta(days=days_ago)
        order = DispatchOrder.objects.create(
            order_no=f'DSP-{created:%Y%m%d}-{vehicle.id:04d}',
            vehicle=vehicle, driver=driver,
            origin=origin, destination=destination,
            plan_depart_at=created, plan_arrive_at=created + timezone.timedelta(hours=4),
            cargo='冷链食品', weight=weight, freight=6800,
            status=status, creator_id=1, note='',
            assigned_at=created,
        )
        DispatchOrder.objects.filter(pk=order.pk).update(created_at=created)
        return order

    def _log_full_timeline(self, order, vehicle, driver):
        created = order.created_at
        started = created + timezone.timedelta(hours=1)
        finished = started + timezone.timedelta(hours=3, minutes=40)
        e1 = DispatchEvent.objects.create(
            order=order, event_type=DispatchEventType.CREATED,
            to_status=DispatchStatus.ASSIGNED,
            detail=f'创建调度单并指派车辆 {vehicle.plate_no}、司机 {driver.name}',
        )
        e2 = DispatchEvent.objects.create(
            order=order, event_type=DispatchEventType.STARTED,
            from_status=DispatchStatus.ASSIGNED, to_status=DispatchStatus.IN_PROGRESS,
            detail='车辆与司机切换为 OnTrip，运输开始',
        )
        e3 = DispatchEvent.objects.create(
            order=order, event_type=DispatchEventType.COMPLETED,
            from_status=DispatchStatus.IN_PROGRESS, to_status=DispatchStatus.COMPLETED,
            detail='运输完成，车辆与司机恢复 Available',
        )
        DispatchEvent.objects.filter(pk=e1.pk).update(created_at=created)
        DispatchEvent.objects.filter(pk=e2.pk).update(created_at=started)
        DispatchEvent.objects.filter(pk=e3.pk).update(created_at=finished)
        DispatchOrder.objects.filter(pk=order.pk).update(
            started_at=started, actual_depart_at=started,
            completed_at=finished, actual_arrive_at=finished,
        )

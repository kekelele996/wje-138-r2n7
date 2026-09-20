"""初始化演示数据：覆盖可用/运输中/载重不足/保险过期车辆，
可用/运输中/证件过期司机，以及占用冲突与历史单据。"""

from django.db import migrations
from django.utils import timezone
from datetime import timedelta


def seed(apps, schema_editor):
    Vehicle = apps.get_model('fleet_app', 'Vehicle')
    Driver = apps.get_model('fleet_app', 'Driver')
    DispatchOrder = apps.get_model('fleet_app', 'DispatchOrder')
    DispatchStatusEvent = apps.get_model('fleet_app', 'DispatchStatusEvent')

    if Vehicle.objects.exists():
        return

    today = timezone.localdate()

    vehicles = [
        Vehicle(
            id=1, plate_no='沪A-7821', vehicle_type='冷链车', brand_model='东风天锦 KR',
            purchase_date=today - timedelta(days=1200),
            insurance_expire_date=today + timedelta(days=90),
            inspection_expire_date=today + timedelta(days=120),
            status='Available', mileage=88210, tank_capacity=380,
            fuel_consumption=24.6, load_capacity=10000,
        ),
        Vehicle(
            id=2, plate_no='苏E-5520', vehicle_type='重卡', brand_model='解放 J6P',
            purchase_date=today - timedelta(days=1800),
            insurance_expire_date=today + timedelta(days=60),
            inspection_expire_date=today + timedelta(days=30),
            status='OnTrip', mileage=210430, tank_capacity=520,
            fuel_consumption=31.2, load_capacity=25000,
        ),
        Vehicle(
            id=3, plate_no='浙B-3309', vehicle_type='轻卡', brand_model='江铃顺达',
            purchase_date=today - timedelta(days=900),
            insurance_expire_date=today + timedelta(days=200),
            inspection_expire_date=today + timedelta(days=150),
            status='Available', mileage=52300, tank_capacity=180,
            fuel_consumption=15.8, load_capacity=3000,
        ),
        Vehicle(
            id=4, plate_no='沪D-9012', vehicle_type='中卡', brand_model='福田欧马可',
            purchase_date=today - timedelta(days=1500),
            # 保险已过期
            insurance_expire_date=today - timedelta(days=10),
            inspection_expire_date=today + timedelta(days=80),
            status='Available', mileage=130600, tank_capacity=300,
            fuel_consumption=22.1, load_capacity=12000,
        ),
        Vehicle(
            id=5, plate_no='皖A-6608', vehicle_type='重卡', brand_model='重汽豪沃',
            purchase_date=today - timedelta(days=2200),
            insurance_expire_date=today + timedelta(days=45),
            inspection_expire_date=today - timedelta(days=5),
            status='Maintenance', mileage=268000, tank_capacity=500,
            fuel_consumption=33.4, load_capacity=24000,
        ),
    ]
    Vehicle.objects.bulk_create(vehicles)

    drivers = [
        Driver(
            id=1, name='赵强', phone='13800000001', license_type='B2',
            license_expire_date=today + timedelta(days=600),
            hire_date=today - timedelta(days=1500),
            status='Available', driving_hours=3200, violation_count=1,
        ),
        Driver(
            id=2, name='孙晨', phone='13800000002', license_type='A2',
            license_expire_date=today + timedelta(days=900),
            hire_date=today - timedelta(days=1700),
            status='OnTrip', driving_hours=4810, violation_count=0,
        ),
        Driver(
            id=3, name='李娜', phone='13800000003', license_type='C1',
            # 驾照已过期
            license_expire_date=today - timedelta(days=30),
            hire_date=today - timedelta(days=800),
            status='Available', driving_hours=1200, violation_count=2,
        ),
        Driver(
            id=4, name='周涛', phone='13800000004', license_type='A2',
            license_expire_date=today + timedelta(days=300),
            hire_date=today - timedelta(days=2000),
            status='Available', driving_hours=5600, violation_count=0,
        ),
    ]
    Driver.objects.bulk_create(drivers)

    now = timezone.now()

    # 进行中的单据：占用车辆2 / 司机2（创建即冲突的演示数据）
    active = DispatchOrder.objects.create(
        id=1, order_no='DSP-SEED-0001',
        vehicle_id=2, driver_id=2,
        origin='苏州园区', destination='宁波北仑',
        plan_depart_at=now - timedelta(hours=2),
        plan_arrive_at=now + timedelta(hours=4),
        actual_depart_at=now - timedelta(hours=1),
        cargo='建筑材料', weight=16000, freight=9800,
        status='InProgress', creator_id=1, note='占用演示数据',
        created_at=now - timedelta(hours=3), assigned_at=now - timedelta(hours=3),
        started_at=now - timedelta(hours=1),
    )
    DispatchStatusEvent.objects.bulk_create([
        DispatchStatusEvent(order=active, from_status='', to_status='Assigned',
                            remark='调度单创建并指派', created_at=now - timedelta(hours=3)),
        DispatchStatusEvent(order=active, from_status='Assigned', to_status='InProgress',
                            remark='开始运输', created_at=now - timedelta(hours=1)),
    ])

    # 已完成的历史单据（不占资源，可验证重启后仍可查询）
    done = DispatchOrder.objects.create(
        id=2, order_no='DSP-SEED-0002',
        vehicle_id=1, driver_id=1,
        origin='上海青浦仓', destination='杭州萧山仓',
        plan_depart_at=now - timedelta(days=2),
        plan_arrive_at=now - timedelta(days=2, hours=5),
        actual_depart_at=now - timedelta(days=2, minutes=10),
        actual_arrive_at=now - timedelta(days=2, hours=5, minutes=20),
        cargo='冷链食品', weight=8200, freight=7200,
        status='Completed', creator_id=1, note='历史完成单据',
        created_at=now - timedelta(days=3), assigned_at=now - timedelta(days=3),
        started_at=now - timedelta(days=2), completed_at=now - timedelta(days=2, hours=5, minutes=20),
    )
    DispatchStatusEvent.objects.bulk_create([
        DispatchStatusEvent(order=done, from_status='', to_status='Assigned',
                            remark='调度单创建并指派', created_at=now - timedelta(days=3)),
        DispatchStatusEvent(order=done, from_status='Assigned', to_status='InProgress',
                            remark='开始运输', created_at=now - timedelta(days=2)),
        DispatchStatusEvent(order=done, from_status='InProgress', to_status='Completed',
                            remark='完成运输', created_at=now - timedelta(days=2, hours=5, minutes=20)),
    ])


def rollback(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('fleet_app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed, rollback),
    ]

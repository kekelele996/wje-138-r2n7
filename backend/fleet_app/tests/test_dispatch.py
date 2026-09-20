"""派单闭环后端测试：创建校验、占用冲突、状态流转、同步状态与持久化时间。"""
from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from fleet_app.models import DispatchOrder, DispatchStatusEvent, Driver, Vehicle


class DispatchClosedLoopTests(APITestCase):
    def setUp(self):
        today = timezone.localdate()
        self.available_truck = Vehicle.objects.create(
            plate_no='沪A-0001', vehicle_type='中卡', brand_model='测试车A',
            insurance_expire_date=today + timedelta(days=30),
            status='Available', mileage=0, tank_capacity=300,
            fuel_consumption=20, load_capacity=10000,
        )
        self.small_truck = Vehicle.objects.create(
            plate_no='沪B-0002', vehicle_type='轻卡', brand_model='测试车B',
            insurance_expire_date=today + timedelta(days=30),
            status='Available', mileage=0, tank_capacity=120,
            fuel_consumption=14, load_capacity=2000,
        )
        self.expired_insurance_truck = Vehicle.objects.create(
            plate_no='沪C-0003', vehicle_type='中卡', brand_model='保险过期车',
            insurance_expire_date=today - timedelta(days=1),
            status='Available', mileage=0, tank_capacity=300,
            fuel_consumption=20, load_capacity=10000,
        )
        self.ontrip_truck = Vehicle.objects.create(
            plate_no='沪D-0004', vehicle_type='重卡', brand_model='在途车',
            insurance_expire_date=today + timedelta(days=30),
            status='OnTrip', mileage=0, tank_capacity=500,
            fuel_consumption=30, load_capacity=20000,
        )

        self.available_driver = Driver.objects.create(
            name='张三', phone='13900000001', license_type='B2',
            license_expire_date=today + timedelta(days=300),
            status='Available', driving_hours=10, violation_count=0,
        )
        self.other_driver = Driver.objects.create(
            name='李四', phone='13900000002', license_type='A2',
            license_expire_date=today + timedelta(days=300),
            status='Available', driving_hours=20, violation_count=0,
        )
        self.expired_license_driver = Driver.objects.create(
            name='王五', phone='13900000003', license_type='C1',
            license_expire_date=today - timedelta(days=1),
            status='Available', driving_hours=5, violation_count=0,
        )

        self.payload = {
            'vehicleId': self.available_truck.id,
            'driverId': self.available_driver.id,
            'origin': '上海仓', 'destination': '南京仓',
            'cargo': '电子设备', 'weight': 5000, 'freight': 3000,
        }

    def create_order(self, **overrides):
        payload = dict(self.payload)
        payload.update(overrides)
        return self.client.post('/api/dispatch-orders/', payload, format='json')

    # ---------- 创建 ----------
    def test_create_success(self):
        response = self.create_order()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.json())
        body = response.json()
        self.assertEqual(body['status'], 'Assigned')
        self.assertTrue(body['orderNo'].startswith('DSP-'))
        self.assertIsNotNone(body['assignedAt'])
        self.assertEqual(len(body['events']), 1)

    def test_create_rejects_non_available_vehicle(self):
        response = self.create_order(vehicleId=self.ontrip_truck.id, driverId=self.other_driver.id)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()['code'], 'vehicle_unavailable')

    def test_create_rejects_expired_insurance(self):
        response = self.create_order(vehicleId=self.expired_insurance_truck.id, driverId=self.other_driver.id)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['code'], 'vehicle_insurance_expired')

    def test_create_rejects_overload(self):
        response = self.create_order(vehicleId=self.small_truck.id, driverId=self.other_driver.id, weight=9000)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['code'], 'load_exceeded')

    def test_create_rejects_expired_driver_license(self):
        response = self.create_order(vehicleId=self.small_truck.id, driverId=self.expired_license_driver.id, weight=100)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['code'], 'driver_license_expired')

    def test_create_rejects_busy_vehicle(self):
        first = self.create_order()
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        response = self.create_order(driverId=self.other_driver.id)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()['code'], 'vehicle_busy')
        self.assertIn('未结束', response.json()['message'])

    def test_create_rejects_busy_driver(self):
        first = self.create_order()
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        response = self.create_order(vehicleId=self.small_truck.id, weight=100)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()['code'], 'driver_busy')

    def test_create_rejects_missing_vehicle(self):
        response = self.create_order(vehicleId=99999)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()['code'], 'vehicle_not_found')

    # ---------- 开始 / 完成 / 取消 ----------
    def test_start_syncs_ontrip_and_complete_restores_available(self):
        order_id = self.create_order().json()['id']

        response = self.client.post(f'/api/dispatch-orders/{order_id}/start/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'InProgress')
        self.assertIsNotNone(response.json()['actualDepartAt'])
        self.available_truck.refresh_from_db()
        self.available_driver.refresh_from_db()
        self.assertEqual(self.available_truck.status, 'OnTrip')
        self.assertEqual(self.available_driver.status, 'OnTrip')

        # 重复开始 -> 409
        duplicate = self.client.post(f'/api/dispatch-orders/{order_id}/start/')
        self.assertEqual(duplicate.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(duplicate.json()['code'], 'duplicate_operation')

        # Assigned 之外不能直接完成（InProgress 完成是合法的）
        response = self.client.post(f'/api/dispatch-orders/{order_id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'Completed')
        self.assertIsNotNone(response.json()['actualArriveAt'])
        self.available_truck.refresh_from_db()
        self.available_driver.refresh_from_db()
        self.assertEqual(self.available_truck.status, 'Available')
        self.assertEqual(self.available_driver.status, 'Available')

        # 终态任何操作都拒绝
        self.assertEqual(self.client.post(f'/api/dispatch-orders/{order_id}/complete/').status_code, 409)
        self.assertEqual(self.client.post(f'/api/dispatch-orders/{order_id}/cancel/').status_code, 409)
        self.assertEqual(self.client.post(f'/api/dispatch-orders/{order_id}/start/').status_code, 409)

    def test_cancel_assigned_restores_available(self):
        order_id = self.create_order().json()['id']
        response = self.client.post(f'/api/dispatch-orders/{order_id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'Cancelled')
        self.assertIsNotNone(response.json()['cancelledAt'])
        self.available_truck.refresh_from_db()
        self.available_driver.refresh_from_db()
        self.assertEqual(self.available_truck.status, 'Available')
        self.assertEqual(self.available_driver.status, 'Available')

    def test_cancel_inprogress_allowed(self):
        order_id = self.create_order().json()['id']
        self.assertEqual(self.client.post(f'/api/dispatch-orders/{order_id}/start/').status_code, 200)
        response = self.client.post(f'/api/dispatch-orders/{order_id}/cancel/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'Cancelled')

    def test_assigned_cannot_complete(self):
        order_id = self.create_order().json()['id']
        response = self.client.post(f'/api/dispatch-orders/{order_id}/complete/')
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['code'], 'illegal_transition')

    def test_action_unknown_order_404(self):
        self.assertEqual(self.client.post('/api/dispatch-orders/99999/start/').status_code, 404)

    def test_timestamps_and_events_persisted(self):
        order_id = self.create_order().json()['id']
        self.client.post(f'/api/dispatch-orders/{order_id}/start/')
        self.client.post(f'/api/dispatch-orders/{order_id}/complete/')

        order = DispatchOrder.objects.get(pk=order_id)
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.assigned_at)
        self.assertIsNotNone(order.started_at)
        self.assertIsNotNone(order.completed_at)
        transitions = list(DispatchStatusEvent.objects.filter(order_id=order_id).values_list('to_status', flat=True))
        self.assertEqual(transitions, ['Assigned', 'InProgress', 'Completed'])

    def test_finished_resource_can_be_reassigned(self):
        order_id = self.create_order().json()['id']
        self.client.post(f'/api/dispatch-orders/{order_id}/start/')
        self.client.post(f'/api/dispatch-orders/{order_id}/complete/')
        # 完成后车辆/司机可再次派单
        response = self.create_order()
        self.assertEqual(response.status_code, 201, response.json())

    def test_list_filter_by_status(self):
        self.create_order()
        response = self.client.get('/api/dispatch-orders/?status=Assigned')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(o['status'] == 'Assigned' for o in response.json()))

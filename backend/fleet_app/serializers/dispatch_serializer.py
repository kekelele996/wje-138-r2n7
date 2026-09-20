from rest_framework import serializers

from fleet_app.serializers.vehicle_serializer import VehicleSerializer
from fleet_app.serializers.driver_serializer import DriverSerializer


class DispatchStatusEventSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    fromStatus = serializers.CharField(source='from_status')
    toStatus = serializers.CharField(source='to_status')
    remark = serializers.CharField()
    createdAt = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M')


class DispatchSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    orderNo = serializers.CharField(source='order_no', read_only=True)
    vehicleId = serializers.IntegerField(source='vehicle_id', required=False, allow_null=True)
    driverId = serializers.IntegerField(source='driver_id', required=False, allow_null=True)
    origin = serializers.CharField()
    destination = serializers.CharField()
    planDepartAt = serializers.DateTimeField(source='plan_depart_at', required=False,
                                             allow_null=True, input_formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'])
    planArriveAt = serializers.DateTimeField(source='plan_arrive_at', required=False,
                                             allow_null=True, input_formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'])
    actualDepartAt = serializers.DateTimeField(source='actual_depart_at', read_only=True, format='%Y-%m-%d %H:%M')
    actualArriveAt = serializers.DateTimeField(source='actual_arrive_at', read_only=True, format='%Y-%m-%d %H:%M')
    cargo = serializers.CharField()
    weight = serializers.FloatField(min_value=0)
    freight = serializers.FloatField(default=0, min_value=0)
    status = serializers.CharField(read_only=True)
    creatorId = serializers.IntegerField(source='creator_id', default=1)
    note = serializers.CharField(required=False, allow_blank=True, default='')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True, format='%Y-%m-%d %H:%M')
    assignedAt = serializers.DateTimeField(source='assigned_at', read_only=True, format='%Y-%m-%d %H:%M')
    startedAt = serializers.DateTimeField(source='started_at', read_only=True, format='%Y-%m-%d %H:%M')
    completedAt = serializers.DateTimeField(source='completed_at', read_only=True, format='%Y-%m-%d %H:%M')
    cancelledAt = serializers.DateTimeField(source='cancelled_at', read_only=True, format='%Y-%m-%d %H:%M')

    # 嵌套车辆/司机摘要，前端下拉与详情无需再拼装
    vehicle = VehicleSerializer(read_only=True)
    driver = DriverSerializer(read_only=True)
    events = DispatchStatusEventSerializer(read_only=True, many=True)


class DispatchCreateSerializer(serializers.Serializer):
    vehicleId = serializers.IntegerField(source='vehicle_id')
    driverId = serializers.IntegerField(source='driver_id')
    origin = serializers.CharField(max_length=120)
    destination = serializers.CharField(max_length=120)
    planDepartAt = serializers.DateTimeField(source='plan_depart_at', required=False, allow_null=True,
                                             input_formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'])
    planArriveAt = serializers.DateTimeField(source='plan_arrive_at', required=False, allow_null=True,
                                             input_formats=['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'])
    cargo = serializers.CharField(max_length=160)
    weight = serializers.FloatField(min_value=0)
    freight = serializers.FloatField(default=0, min_value=0)
    note = serializers.CharField(required=False, allow_blank=True, default='')

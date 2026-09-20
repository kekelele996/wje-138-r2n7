from rest_framework import serializers
from fleet_app.models import DispatchEvent, DispatchOrder
from fleet_app.serializers.common import CamelModelSerializer


class DispatchEventSerializer(CamelModelSerializer):
    class Meta:
        model = DispatchEvent
        fields = [
            'id', 'event_type', 'from_status', 'to_status',
            'detail', 'operator_id', 'created_at',
        ]
        read_only_fields = fields


class DispatchSerializer(CamelModelSerializer):
    # 嵌套车辆/司机摘要，前端无需额外请求即可展示
    vehicle_plate_no = serializers.CharField(source='vehicle.plate_no', read_only=True, default=None)
    vehicle_type = serializers.CharField(source='vehicle.vehicle_type', read_only=True, default=None)
    driver_name = serializers.CharField(source='driver.name', read_only=True, default=None)
    driver_phone = serializers.CharField(source='driver.phone', read_only=True, default=None)
    timeline = serializers.SerializerMethodField()

    class Meta:
        model = DispatchOrder
        fields = [
            'id', 'order_no', 'vehicle', 'driver',
            'vehicle_plate_no', 'vehicle_type', 'driver_name', 'driver_phone',
            'origin', 'destination',
            'plan_depart_at', 'plan_arrive_at',
            'actual_depart_at', 'actual_arrive_at',
            'cargo', 'weight', 'freight', 'status',
            'creator_id', 'note',
            'created_at', 'updated_at',
            'assigned_at', 'started_at', 'completed_at', 'cancelled_at',
            'timeline',
        ]
        read_only_fields = [
            'order_no', 'status', 'creator_id',
            'actual_depart_at', 'actual_arrive_at',
            'created_at', 'updated_at',
            'assigned_at', 'started_at', 'completed_at', 'cancelled_at',
        ]

    def get_timeline(self, obj):
        events = obj.events.all()
        return [
            {'eventType': e.event_type,
             'fromStatus': e.from_status,
             'toStatus': e.to_status,
             'detail': e.detail,
             'time': e.created_at.isoformat()}
            for e in events
        ]

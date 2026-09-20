from rest_framework import serializers
from fleet_app.models import MaintenanceRecord
from fleet_app.serializers.common import CamelModelSerializer


class MaintenanceSerializer(CamelModelSerializer):
    vehicle_plate_no = serializers.CharField(source='vehicle.plate_no', read_only=True, default=None)

    class Meta:
        model = MaintenanceRecord
        fields = [
            'id', 'vehicle', 'vehicle_plate_no', 'maintenance_type', 'items',
            'cost', 'vendor', 'date', 'next_mileage', 'next_date', 'status',
            'created_at',
        ]
        read_only_fields = ['created_at']

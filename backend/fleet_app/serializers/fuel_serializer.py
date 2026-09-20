from rest_framework import serializers
from fleet_app.models import FuelRecord
from fleet_app.serializers.common import CamelModelSerializer


class FuelSerializer(CamelModelSerializer):
    vehicle_plate_no = serializers.CharField(source='vehicle.plate_no', read_only=True, default=None)

    class Meta:
        model = FuelRecord
        fields = [
            'id', 'vehicle', 'vehicle_plate_no', 'date', 'liters',
            'unit_price', 'total_amount', 'mileage', 'station',
            'payment_method', 'created_at',
        ]
        read_only_fields = ['created_at']

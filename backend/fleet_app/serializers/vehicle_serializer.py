from fleet_app.models import Vehicle
from fleet_app.serializers.common import CamelModelSerializer


class VehicleSerializer(CamelModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            'id', 'plate_no', 'vehicle_type', 'brand_model', 'purchase_date',
            'insurance_expire_date', 'inspection_expire_date', 'status',
            'mileage', 'tank_capacity', 'payload_capacity', 'fuel_consumption',
            'created_at', 'updated_at', 'status_changed_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'status_changed_at']

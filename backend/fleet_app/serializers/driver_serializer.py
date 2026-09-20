from fleet_app.models import Driver
from fleet_app.serializers.common import CamelModelSerializer


class DriverSerializer(CamelModelSerializer):
    class Meta:
        model = Driver
        fields = [
            'id', 'name', 'phone', 'license_type', 'license_expire_date',
            'hire_date', 'status', 'driving_hours', 'violation_count',
            'created_at', 'updated_at', 'status_changed_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'status_changed_at']

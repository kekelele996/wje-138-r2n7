from fleet_app.models import MaintenanceRecord
from fleet_app.serializers.maintenance_serializer import MaintenanceSerializer


def list_records():
    records = MaintenanceRecord.objects.select_related('vehicle').all()
    return MaintenanceSerializer(records, many=True).data

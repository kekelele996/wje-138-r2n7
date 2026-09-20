from fleet_app.models import Driver
from fleet_app.serializers.driver_serializer import DriverSerializer


def list_drivers():
    return DriverSerializer(Driver.objects.all().order_by('id'), many=True).data

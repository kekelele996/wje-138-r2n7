from fleet_app.models import Vehicle
from fleet_app.serializers.vehicle_serializer import VehicleSerializer


def list_vehicles():
    return VehicleSerializer(Vehicle.objects.all().order_by('id'), many=True).data

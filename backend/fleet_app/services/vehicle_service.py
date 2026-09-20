from django.db import transaction
from django.utils import timezone
from fleet_app.models import Vehicle, VehicleStatus
from fleet_app.serializers.vehicle_serializer import VehicleSerializer
from fleet_app.services.exceptions import BusinessError, NotFoundError


def list_vehicles(status: str | None = None):
    queryset = Vehicle.objects.all()
    if status:
        queryset = queryset.filter(status=status)
    return VehicleSerializer(queryset, many=True).data


def get_vehicle(pk: int) -> Vehicle:
    try:
        return Vehicle.objects.get(pk=pk)
    except Vehicle.DoesNotExist:
        raise NotFoundError(f'车辆不存在：id={pk}')


def retrieve_vehicle(pk: int):
    return VehicleSerializer(get_vehicle(pk)).data


@transaction.atomic
def create_vehicle(payload: dict) -> dict:
    serializer = VehicleSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    vehicle = serializer.save(
        status=VehicleStatus.AVAILABLE, status_changed_at=timezone.now()
    )
    return VehicleSerializer(vehicle).data


@transaction.atomic
def update_vehicle_status(pk: int, new_status: str) -> dict:
    if new_status not in VehicleStatus.values:
        raise BusinessError(
            f'非法车辆状态：{new_status}', code='INVALID_STATUS'
        )
    vehicle = get_vehicle(pk)
    if vehicle.status == new_status:
        raise BusinessError(f'车辆已处于 {new_status} 状态，无需重复变更')
    vehicle.status = new_status
    vehicle.status_changed_at = timezone.now()
    vehicle.save(update_fields=['status', 'status_changed_at', 'updated_at'])
    return VehicleSerializer(vehicle).data

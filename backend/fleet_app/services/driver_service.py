from django.db import transaction
from django.utils import timezone
from fleet_app.models import Driver, DriverStatus
from fleet_app.serializers.driver_serializer import DriverSerializer
from fleet_app.services.exceptions import BusinessError, NotFoundError


def list_drivers(status: str | None = None):
    queryset = Driver.objects.all()
    if status:
        queryset = queryset.filter(status=status)
    return DriverSerializer(queryset, many=True).data


def get_driver(pk: int) -> Driver:
    try:
        return Driver.objects.get(pk=pk)
    except Driver.DoesNotExist:
        raise NotFoundError(f'司机不存在：id={pk}')


def retrieve_driver(pk: int):
    return DriverSerializer(get_driver(pk)).data


@transaction.atomic
def create_driver(payload: dict) -> dict:
    serializer = DriverSerializer(data=payload)
    serializer.is_valid(raise_exception=True)
    driver = serializer.save(
        status=DriverStatus.AVAILABLE, status_changed_at=timezone.now()
    )
    return DriverSerializer(driver).data


@transaction.atomic
def update_driver_status(pk: int, new_status: str) -> dict:
    if new_status not in DriverStatus.values:
        raise BusinessError(f'非法司机状态：{new_status}', code='INVALID_STATUS')
    driver = get_driver(pk)
    if driver.status == new_status:
        raise BusinessError(f'司机已处于 {new_status} 状态，无需重复变更')
    driver.status = new_status
    driver.status_changed_at = timezone.now()
    driver.save(update_fields=['status', 'status_changed_at', 'updated_at'])
    return DriverSerializer(driver).data

from django.db.models import Sum
from django.db.models.functions import TruncMonth

from fleet_app.models import FuelRecord
from fleet_app.serializers.fuel_serializer import FuelSerializer


def list_fuel_records():
    records = FuelRecord.objects.select_related('vehicle').all()
    return FuelSerializer(records, many=True).data


def monthly_summary():
    """按月汇总加油量与金额，供油耗分析柱状图使用。"""
    rows = (
        FuelRecord.objects
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(liters=Sum('liters'), total_amount=Sum('total_amount'))
        .order_by('month')
    )
    return [
        {
            'month': row['month'].strftime('%Y-%m') if row['month'] else None,
            'liters': row['liters'] or 0,
            'totalAmount': row['total_amount'] or 0,
        }
        for row in rows
    ]

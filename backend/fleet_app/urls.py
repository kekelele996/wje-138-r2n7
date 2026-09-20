from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

from fleet_app.views.dispatch_views import (
    DispatchCancelView,
    DispatchCompleteView,
    DispatchOrderDetailView,
    DispatchOrderListView,
    DispatchReassignView,
    DispatchStartView,
)
from fleet_app.views.driver_views import DriverDetailView, DriverListView
from fleet_app.views.fuel_views import FuelMonthlySummaryView, FuelRecordListView
from fleet_app.views.maintenance_views import MaintenanceRecordListView
from fleet_app.views.vehicle_views import VehicleDetailView, VehicleListView


@api_view(['GET'])
def health(request):
    return Response({'status': 'ok', 'service': 'fleet-dispatch'})


urlpatterns = [
    path('health/', health),

    # 车辆
    path('vehicles/', VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/<int:pk>/', VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicles/<int:pk>/status/', VehicleDetailView.as_view(), name='vehicle-status'),

    # 司机
    path('drivers/', DriverListView.as_view(), name='driver-list'),
    path('drivers/<int:pk>/', DriverDetailView.as_view(), name='driver-detail'),
    path('drivers/<int:pk>/status/', DriverDetailView.as_view(), name='driver-status'),

    # 调度单：创建/开始/完成/取消/改派 闭环
    path('dispatch-orders/', DispatchOrderListView.as_view(), name='dispatch-list'),
    path('dispatch-orders/<int:pk>/', DispatchOrderDetailView.as_view(), name='dispatch-detail'),
    path('dispatch-orders/<int:pk>/start/', DispatchStartView.as_view(), name='dispatch-start'),
    path('dispatch-orders/<int:pk>/complete/', DispatchCompleteView.as_view(), name='dispatch-complete'),
    path('dispatch-orders/<int:pk>/cancel/', DispatchCancelView.as_view(), name='dispatch-cancel'),
    path('dispatch-orders/<int:pk>/reassign/', DispatchReassignView.as_view(), name='dispatch-reassign'),

    # 维保
    path('maintenance-records/', MaintenanceRecordListView.as_view(), name='maintenance-list'),

    # 油耗
    path('fuel-records/', FuelRecordListView.as_view(), name='fuel-list'),
    path('fuel-records/monthly-summary/', FuelMonthlySummaryView.as_view(), name='fuel-summary'),
]

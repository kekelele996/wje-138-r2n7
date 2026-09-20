from rest_framework.response import Response
from rest_framework.views import APIView

from fleet_app.services import fuel_analytics_service


class FuelRecordListView(APIView):
    def get(self, request):
        return Response(fuel_analytics_service.list_fuel_records())


class FuelMonthlySummaryView(APIView):
    def get(self, request):
        return Response(fuel_analytics_service.monthly_summary())

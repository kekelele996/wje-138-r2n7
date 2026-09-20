from rest_framework.response import Response
from rest_framework.views import APIView

from fleet_app.services import maintenance_service


class MaintenanceRecordListView(APIView):
    def get(self, request):
        return Response(maintenance_service.list_records())

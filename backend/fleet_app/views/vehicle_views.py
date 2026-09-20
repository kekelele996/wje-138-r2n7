from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from fleet_app.services import vehicle_service


class VehicleListView(APIView):
    def get(self, request):
        return Response(vehicle_service.list_vehicles(request.query_params.get('status')))

    def post(self, request):
        data = vehicle_service.create_vehicle(request.data)
        return Response(data, status=status.HTTP_201_CREATED)


class VehicleDetailView(APIView):
    def get(self, request, pk):
        return Response(vehicle_service.retrieve_vehicle(pk))

    def patch(self, request, pk):
        new_status = request.data.get('status')
        if not new_status:
            from fleet_app.services.exceptions import BusinessError
            raise BusinessError('缺少 status 参数')
        return Response(vehicle_service.update_vehicle_status(pk, new_status))

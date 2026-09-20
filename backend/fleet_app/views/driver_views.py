from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from fleet_app.services import driver_service
from fleet_app.services.exceptions import BusinessError


class DriverListView(APIView):
    def get(self, request):
        return Response(driver_service.list_drivers(request.query_params.get('status')))

    def post(self, request):
        data = driver_service.create_driver(request.data)
        return Response(data, status=status.HTTP_201_CREATED)


class DriverDetailView(APIView):
    def get(self, request, pk):
        return Response(driver_service.retrieve_driver(pk))

    def patch(self, request, pk):
        new_status = request.data.get('status')
        if not new_status:
            raise BusinessError('缺少 status 参数')
        return Response(driver_service.update_driver_status(pk, new_status))

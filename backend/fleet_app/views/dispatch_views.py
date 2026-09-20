from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from fleet_app.services import dispatch_service


class DispatchOrderListView(APIView):
    def get(self, request):
        return Response(dispatch_service.list_orders(request.query_params.get('status')))

    def post(self, request):
        data = dispatch_service.create_order(request.data)
        return Response(data, status=status.HTTP_201_CREATED)


class DispatchOrderDetailView(APIView):
    def get(self, request, pk):
        return Response(dispatch_service.retrieve_order(pk))


class DispatchStartView(APIView):
    def post(self, request, pk):
        return Response(dispatch_service.start_order(pk))


class DispatchCompleteView(APIView):
    def post(self, request, pk):
        return Response(dispatch_service.complete_order(pk))


class DispatchCancelView(APIView):
    def post(self, request, pk):
        return Response(dispatch_service.cancel_order(pk))


class DispatchReassignView(APIView):
    def post(self, request, pk):
        return Response(dispatch_service.reassign_order(pk, request.data))

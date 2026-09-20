from rest_framework.decorators import api_view
from rest_framework.response import Response

from fleet_app.enums import DispatchStatus
from fleet_app.services import dispatch_service


@api_view(['GET', 'POST'])
def dispatch_orders(request):
    if request.method == 'POST':
        # 创建：车辆/司机校验不通过或存在未结束单据时返回 4xx + 原因
        return Response(dispatch_service.create_order(request.data), status=201)
    status = request.query_params.get('status')
    if status and status not in (
        DispatchStatus.PENDING, DispatchStatus.ASSIGNED, DispatchStatus.IN_PROGRESS,
        DispatchStatus.COMPLETED, DispatchStatus.CANCELLED,
    ):
        status = None
    return Response(dispatch_service.list_orders(status=status))


@api_view(['POST'])
def dispatch_order_start(request, order_id):
    return Response(dispatch_service.start_order(order_id))


@api_view(['POST'])
def dispatch_order_complete(request, order_id):
    return Response(dispatch_service.complete_order(order_id))


@api_view(['POST'])
def dispatch_order_cancel(request, order_id):
    return Response(dispatch_service.cancel_order(order_id))

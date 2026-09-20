from fleet_app.exceptions import BusinessError


class ErrorHandlerMiddleware:
    """非 DRF 视图抛出的业务异常兜底（正常流程由 exception_handler 处理）。"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except BusinessError as exc:
            from django.http import JsonResponse
            return JsonResponse(
                {'code': exc.code, 'message': exc.message},
                status=exc.status_code,
            )

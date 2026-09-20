import logging

from fleet_app.services.exceptions import BusinessError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """统一异常兜底：DRF 之外逃逸的异常也返回 {code, reason}。"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except BusinessError as exc:
            from django.http import JsonResponse
            return JsonResponse(
                {'code': exc.code, 'reason': exc.reason},
                status=exc.http_status,
            )
        except Exception:  # pragma: no cover - 兜底保护
            logger.exception('unhandled server error')
            from django.http import JsonResponse
            return JsonResponse(
                {'code': 'INTERNAL_ERROR', 'reason': '服务器内部错误'},
                status=500,
            )

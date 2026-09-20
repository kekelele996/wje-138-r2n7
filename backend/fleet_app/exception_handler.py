"""DRF 统一异常处理：业务异常返回 {code, message}，冲突携带 409 与具体原因。"""

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status as http_status

from fleet_app.exceptions import BusinessError


def custom_exception_handler(exc, context):
    if isinstance(exc, BusinessError):
        return Response(
            {'code': exc.code, 'message': exc.message},
            status=exc.status_code,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        detail = response.data
        if isinstance(detail, dict) and 'detail' in detail:
            message = str(detail['detail'])
            errors = {k: v for k, v in detail.items() if k != 'detail'}
        else:
            message = '请求参数不合法'
            errors = detail if isinstance(detail, dict) else None
        payload = {'code': 'invalid_request', 'message': message}
        if errors:
            payload['errors'] = errors
        response.data = payload
        if response.status_code == http_status.HTTP_405_METHOD_NOT_ALLOWED:
            response.data = {'code': 'method_not_allowed', 'message': '不支持的操作'}
    return response

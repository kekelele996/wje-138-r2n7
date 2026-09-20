"""DRF 统一异常处理：所有错误返回 {code, reason} 结构。"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from fleet_app.services.exceptions import BusinessError


def custom_exception_handler(exc, context):
    if isinstance(exc, BusinessError):
        return Response(
            {'code': exc.code, 'reason': exc.reason},
            status=exc.http_status,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        detail = response.data
        if isinstance(detail, dict) and 'detail' in detail and len(detail) == 1:
            reason = str(detail['detail'])
        else:
            reason = _flatten_errors(detail)
        response.data = {
            'code': _code_for_status(response.status_code),
            'reason': reason,
        }
    return response


def _code_for_status(http_status: int) -> str:
    return {
        status.HTTP_400_BAD_REQUEST: 'VALIDATION_ERROR',
        status.HTTP_401_UNAUTHORIZED: 'UNAUTHENTICATED',
        status.HTTP_403_FORBIDDEN: 'PERMISSION_DENIED',
        status.HTTP_404_NOT_FOUND: 'NOT_FOUND',
        status.HTTP_405_METHOD_NOT_ALLOWED: 'METHOD_NOT_ALLOWED',
        status.HTTP_409_CONFLICT: 'CONFLICT',
    }.get(http_status, 'ERROR')


def _flatten_errors(detail) -> str:
    if isinstance(detail, dict):
        parts = []
        for field, messages in detail.items():
            if isinstance(messages, (list, tuple)):
                messages = '；'.join(str(m) for m in messages)
            parts.append(f'{field}: {messages}')
        return '；'.join(parts)
    if isinstance(detail, (list, tuple)):
        return '；'.join(str(m) for m in detail)
    return str(detail)

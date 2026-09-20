"""业务异常：service 层抛出，exception_handler 统一转换为带原因的 JSON。"""
from rest_framework import status


class BusinessError(Exception):
    """业务规则不满足（400）。"""

    code = 'BUSINESS_ERROR'
    http_status = status.HTTP_400_BAD_REQUEST

    def __init__(self, reason: str, code: str | None = None):
        self.reason = reason
        if code:
            self.code = code
        super().__init__(reason)


class DispatchConflictError(BusinessError):
    """资源冲突：车辆/司机已有未结束单据，或状态被并发占用（409）。"""

    code = 'DISPATCH_CONFLICT'
    http_status = status.HTTP_409_CONFLICT


class InvalidStatusError(BusinessError):
    """非法状态流转：重复开始/完成/取消、运输中改派等（409）。"""

    code = 'INVALID_STATUS'
    http_status = status.HTTP_409_CONFLICT


class NotFoundError(BusinessError):
    """资源不存在（404）。"""

    code = 'NOT_FOUND'
    http_status = status.HTTP_404_NOT_FOUND

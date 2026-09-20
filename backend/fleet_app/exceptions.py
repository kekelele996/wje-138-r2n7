"""业务异常：携带错误码、可读原因与 HTTP 状态码。"""


class BusinessError(Exception):
    """所有可预期的业务冲突/非法状态都抛出该异常。"""

    def __init__(self, message: str, code: str = 'business_error', status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class ConflictError(BusinessError):
    """资源冲突或非法状态流转（车辆/司机已被占用、重复操作等）。"""

    def __init__(self, message: str, code: str = 'conflict'):
        super().__init__(message, code=code, status_code=409)

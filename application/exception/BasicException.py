from typing import Any
from fastapi import Request
from fastapi.exceptions import HTTPException
from application.util.ResponseUtil import ResponseUtil
from application.initial.BaseEnum import StatusCodeEnum


class BasicException(HTTPException):
    """
    自定义异常处理
    """
    def __init__(self, status_code: StatusCodeEnum = StatusCodeEnum.ERROR,
                 message: str = "服务器繁忙，请稍后重试！",
                 detail: Any = None):
        self.status_code: StatusCodeEnum = status_code
        self.message: str = message
        self.detail: Any = detail

    @staticmethod
    async def exception_handler(request: Request, exception: Any):
        """
        自定义异常处理器
        :param request: 请求对象
        :param exception: 异常类
        :return:
        """
        return ResponseUtil(code=exception.status_code, message=exception.message).fail()

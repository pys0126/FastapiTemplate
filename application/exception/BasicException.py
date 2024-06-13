from typing import Any
from fastapi import Request
from traceback import format_exc
from fastapi.exceptions import HTTPException
from application.util.LogUtil import write_error_log
from application.util.ResponseUtil import ResponseUtil
from application.enumeration.StatusCodeEnum import StatusCodeEnum


class BasicException(HTTPException):
    """
    自定义异常处理
    """
    def __init__(self, status_code=StatusCodeEnum.BAD_REQUEST_ERROR, message="请求异常！"):
        self.status_code = status_code
        self.message = message
        self.detail = message

    @staticmethod
    async def exception_handler(request: Request, exception: Any):
        """
        自定义异常处理器
        :param request: 请求对象
        :param exception: 异常类
        :return:
        """
        write_error_log(log_message=f"请求方法：{request.method} - 请求地址：{request.url} - 异常信息：{exception.message}",
                        traceback=format_exc())
        return ResponseUtil(code=exception.status_code, message=exception.message).fail()

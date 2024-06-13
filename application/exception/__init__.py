from fastapi import Request
from traceback import format_exc
from application.util.LogUtil import write_error_log
from application.util.ResponseUtil import ResponseUtil
from application.enumeration.StatusCodeEnum import StatusCodeEnum


async def low_exception_handler(request: Request, exception: Exception):
    """
    自定义异常处理器
    :param request: 请求对象
    :param exception: 异常类
    :return:
    """
    write_error_log(log_message=f"请求方法：{request.method} - 请求地址：{request.url} - 系统异常：{exception}",
                    traceback=format_exc())
    return ResponseUtil(code=StatusCodeEnum.ERROR.value, message="系统异常，请稍后再试！").fail()

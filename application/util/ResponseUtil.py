from application.initial.BaseEnum import StatusCodeEnum
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional, Any
from starlette import status


class ResponseUtil:
    """
    返回Response类
    """
    def __init__(self, code: int = StatusCodeEnum.SUCCESS.value, data: Optional[Any] = None, message: str = "ok"):
        """
        构造方法
        :param code: 状态码
        :param data: 返回数据
        :param message: 返回信息
        """
        self.code: int = code
        self.data: Optional[Any] = data
        self.message: str = message

    def success(self) -> JSONResponse:
        """
        成功Response
        :return: Response对象
        """
        response: dict = dict(code=self.code, data=self.data, message=self.message)
        return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(response))

    def fail(self) -> JSONResponse:
        """
        失败Response
        :return: Response对象
        """
        response: dict = dict(code=self.code, data=self.data, message=self.message)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(response))

from application.initial.BaseEnum import StatusCodeEnum
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Optional, Any
from starlette import status


class ResponseUtil:
    """
    返回Response类
    """
    def __init__(self, status_code: StatusCodeEnum = StatusCodeEnum.SUCCESS,
                 data: Optional[Any] = None, message: Optional[str] = None):
        """
        构造方法
        :param status_code: 状态码枚举
        :param data: 返回数据
        :param message: 返回信息
        """
        self.code: int = status_code.code
        self.data: Optional[Any] = data
        self.message: str = message or status_code.description

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

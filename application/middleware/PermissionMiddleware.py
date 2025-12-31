from typing import Optional
from fastapi import Request, Response
from application.service.user.Model import UserModel
from application.util.TokenUtil import get_user_id
from application.util.ResponseUtil import ResponseUtil
from application.initial.BaseEnum import StatusCodeEnum
from starlette.middleware.base import RequestResponseEndpoint, BaseHTTPMiddleware


class PermissionMiddleware(BaseHTTPMiddleware):
    """权限处理中间件类"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        请求响应中间件处理器
        :param request: 请求对象
        :param call_next: 请求处理器
        :return: 响应对象
        """
        # 获取用户ID
        user_id: Optional[int] = await get_user_id(token=dict(request.headers).get("authorization"))
        # 获取用户ORM模型
        user_model: Optional[UserModel] = await UserModel.filter(id=user_id).first()
        # 如果用户存在
        if user_model is not None:
            # 验证是否禁用
            if user_model.is_disabled:
                return ResponseUtil(code=StatusCodeEnum.AUTHORITY_ERROR.value, message="该用户已被封禁！").fail()
        # 继续执行请求
        return await call_next(request)

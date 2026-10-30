from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from application.initial.BaseEnum import StatusCodeEnum
from application.service.user.Model import UserModel
from application.util.ResponseUtil import ResponseUtil
from application.util.TokenUtil import get_user_id


class PermissionMiddleware(BaseHTTPMiddleware):
    """权限处理中间件类"""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        请求响应中间件处理器
        :param request: 请求对象
        :param call_next: 请求处理器
        :return: 响应对象
        """
        # 匿名请求不访问 Redis 或数据库，受保护接口仍由鉴权依赖拒绝。
        token = request.headers.get("authorization")
        user_id = await get_user_id(token=token) if token else 0
        request.state.auth_user_id = user_id
        request.state.auth_user_exists = False
        if user_id:
            # 只读取权限检查所需字段，供后续鉴权依赖复用。
            is_disabled = await UserModel.filter(id=user_id, is_disabled=True).exists()
            request.state.auth_user_exists = is_disabled is not None
            if is_disabled:
                return ResponseUtil(status_code=StatusCodeEnum.USER_DISABLED).fail()
        return await call_next(request)

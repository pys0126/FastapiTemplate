from typing import Literal
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from application.util.ResponseUtil import ResponseUtil
from application.service.common import Logic

# 创建路由
router: APIRouter = APIRouter(prefix="/common", tags=["通用"])


@router.post("/send_captcha", summary="发送验证码")
async def send_captcha(target: str, send_type: Literal["email", "phone"]) -> JSONResponse:
    """
    发送验证码
    :param target: 目标邮箱/手机号
    :param send_type: 发送类型（email/phone）
    :return: JSONResponse
    """
    await Logic.send_captcha(target=target, send_type=send_type)
    return ResponseUtil().success()

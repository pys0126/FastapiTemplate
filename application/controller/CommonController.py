from fastapi import APIRouter
from fastapi.responses import JSONResponse
from application.util.ResponseUtil import ResponseUtil
from application.logic import CommonLogic

# 创建路由
router: APIRouter = APIRouter(prefix="/common", tags=["通用"])


@router.post("/email_captcha", summary="发送邮箱验证码")
def email_captcha(email: str) -> JSONResponse:
    """
    发送邮箱验证码
    :param email: 邮箱
    :return: JSONResponse
    """
    CommonLogic.email_captcha(email=email)
    return ResponseUtil().success()

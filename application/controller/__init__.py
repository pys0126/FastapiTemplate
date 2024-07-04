from application.util.ResponseUtil import ResponseUtil
from fastapi.responses import JSONResponse
from fastapi import APIRouter

router: APIRouter = APIRouter(prefix="", tags=["根路径"])


@router.get("/")
@router.get("/index")
async def root() -> JSONResponse:
    """
    主页/根路径，测试API是否正常
    """
    return ResponseUtil().success()

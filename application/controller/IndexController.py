from fastapi import APIRouter
from starlette.responses import JSONResponse
from application.util.ResponseUtil import ResponseUtil

# 创建路由
router: APIRouter = APIRouter(tags=["杂项"])


@router.get("/")
@router.get("/index")
async def root() -> JSONResponse:
    """
    主页/根路径，测试API是否正常
    """
    return ResponseUtil().success()

from fastapi import APIRouter, status
from starlette.responses import JSONResponse
from application.model.UserModel import UserModel
from application.util.ResponseUtil import ResponseUtil

# 创建路由
router: APIRouter = APIRouter(tags=["index"],
                              responses={status.HTTP_404_NOT_FOUND: {"description": "Not Found"}})


@router.get("/")
@router.get("/index")
async def root() -> JSONResponse:
    """
    主页/根路径
    :return:
    """
    user_model: UserModel = await UserModel.filter(id=1).first()

    return ResponseUtil().success()

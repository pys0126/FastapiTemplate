from application.entity.UserEntity import UserAdd, UserOut, UserLogin
from application.depend.TokenDepend import verify_token
from application.util.ResponseUtil import ResponseUtil
from fastapi.responses import JSONResponse
from application.logic import UserLogic
from fastapi import APIRouter, Depends
from pydantic import PositiveInt

# 设置路由
router: APIRouter = APIRouter(prefix="/user", tags=["用户"])


@router.get("/all", response_model=UserOut, summary="获取所有用户信息")
async def get_all_data(page: PositiveInt = 1, page_size: PositiveInt = 10) -> JSONResponse:
    return ResponseUtil(data=await UserLogic.get_all_data(page=page, page_size=page_size)).success()


@router.post("/register", summary="注册用户")
async def register(user_add: UserAdd) -> JSONResponse:
    await UserLogic.register(user_add=user_add)
    return ResponseUtil().success()


@router.post("/login", summary="登录用户")
async def login(user_login: UserLogin) -> JSONResponse:
    token: str = await UserLogic.login(user_login=user_login)
    return ResponseUtil(data=token).success()


@router.get("/info/{user_id:int}", summary="根据ID获取用户信息", dependencies=[Depends(verify_token)])
async def get_user_by_id(user_id: int) -> JSONResponse:
    return ResponseUtil(data=await UserLogic.get_user_by_id(user_id=user_id)).success()

from application.service.user.Entity import UserAdd, UserLogin
from application.dependency.AuthDependency import get_current_user
from application.service.user.Model import UserModel
from application.util.ResponseUtil import ResponseUtil
from fastapi.responses import JSONResponse
from application.service.user import Logic
from fastapi import APIRouter, Depends

# 设置路由
router: APIRouter = APIRouter(prefix="/user", tags=["用户"])


@router.post("/register", summary="注册用户")
async def register(user_add: UserAdd) -> JSONResponse:
    await Logic.register(user_add=user_add)
    return ResponseUtil().success()


@router.post("/login", summary="登录用户")
async def login(user_login: UserLogin) -> JSONResponse:
    return ResponseUtil(data=await Logic.login(user_login=user_login)).success()


@router.get("/profile", summary="获取当前登录用户信息")
async def get_profile(user_model: UserModel = Depends(get_current_user)) -> JSONResponse:
    return ResponseUtil(data=await Logic.get_profile(user_model=user_model)).success()

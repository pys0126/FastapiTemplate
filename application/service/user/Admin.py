from uuid import UUID
from application.initial.BaseAdmin import BaseAdmin
from application.service.user.Model import UserModel
from application.service.user.Util import encode_password
from fastadmin import (register, widget_action, WidgetActionType, WidgetActionChartProps, WidgetActionFilter,
                       WidgetType, WidgetActionInputSchema, WidgetActionResponseSchema)


@register(UserModel)
class UserAdmin(BaseAdmin):
    """
    用户管理
    """
    list_display_links = ["username"]
    list_display = ["id", "username", "nickname", "email", "phone", "sex", "is_disabled", "is_employee",
                    "is_superuser", "create_datetime", "update_datetime"]
    list_filter = ["sex", "is_disabled", "is_employee", "is_superuser"]
    search_fields = ["username", "nickname", "email", "phone"]
    ordering = ["-id"]
    actions = ["delete_selected"]
    formfield_overrides = {
        "password": (WidgetType.PasswordInput, {"label": "密码"}),
        "email": (WidgetType.EmailInput, {"label": "邮箱"}),
        "intro": (WidgetType.TextArea, {"label": "个人简介"}),
    }
    readonly_fields = ["id", "create_datetime"]

    async def authenticate(self, username: str, password: str) -> UUID | int | None:
        """
        自定义认证
        :param username: 用户名
        :param password: 密码
        :return:
        """
        user_model: UserModel = await self.model_cls.filter(username=username,
                                                            password=encode_password(password=password),
                                                            is_superuser=True).first()
        return user_model.id if user_model else None

    async def change_password(self, id: UUID | int, password: str) -> None:
        """
        自定义修改密码
        :param id: 用户ID
        :param password: 密码
        :return:
        """
        user_model: UserModel = await self.model_cls.filter(id=id).first()
        user_model.password = encode_password(password=password)
        await user_model.save()

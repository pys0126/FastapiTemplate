from uuid import UUID
from application.initial.BaseAdmin import BaseAdmin
from application.service.user.Model import UserModel
from application.service.user.Util import encode_password
from fastadmin import (register, widget_action, WidgetActionType, WidgetActionChartProps, WidgetType,
                       WidgetActionInputSchema, WidgetActionResponseSchema)
from application.util.CommonUtil import group_by_list


@register(UserModel)
class UserAdmin(BaseAdmin):
    """
    用户管理
    """
    menu_section = "业务管理"
    list_display_links = ["id", "username"]
    list_display = ["id", "avatar", "username", "nickname", "email", "phone", "sex", "is_disabled", "is_employee",
                    "is_superuser", "create_datetime", "update_datetime"]
    list_filter = ["sex", "is_disabled", "is_employee", "is_superuser"]
    search_fields = ["username", "nickname", "email", "phone"]
    ordering = ["-id"]
    formfield_overrides = {
        "username": (WidgetType.SlugInput, {"required": True}),
        "nickname": (WidgetType.Input, {"required": True}),
        "password": (WidgetType.PasswordInput, {"required": True, "passwordModalForm": True}),
        "email": (WidgetType.EmailInput, {"required": False}),
        "phone": (WidgetType.Input, {"required": False}),
        "intro": (WidgetType.TextArea, {"required": False}),
        "avatar": (WidgetType.UploadImage, {"required": False}),
    }
    readonly_fields = ["id", "create_datetime", "update_datetime"]
    radio_fields = ["sex"]
    widget_actions = ["users_chart"]

    @widget_action(
        widget_action_type=WidgetActionType.ChartPie,
        widget_action_props=WidgetActionChartProps(
            x_field="性别", y_field="用户数",
            series_color=["#5B8FF9", "#5AD8A6", "#5D7092"]
        ),
        tab="基础统计",
        title="用户统计",
        description="根据用户性别分类统计",
        width=12
    )
    async def users_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        sex_group: dict[str, list] = group_by_list(await self.model_cls.all().values_list("sex", flat=True))
        return WidgetActionResponseSchema(
            data=[{"性别": sex_key, "用户数": len(sex_value)} for sex_key, sex_value in sex_group.items()]
        )

    async def upload_file(self, field_name: str, file_name: str, file_content: bytes,
                          obj: UserModel | None = None) -> str:
        """
        自定义上传文件
        :param field_name: 字段名称
        :param file_name: 文件名称
        :param file_content: 文件内容
        :param obj: 当前ORM模型
        :return:
        """
        # TODO 模拟上传文件到OSS
        return "https://img.tuxiangyan.com/uploads/allimg/210908/1_0ZP344115191.jpg"

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

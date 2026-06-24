from uuid import UUID
from typing import Optional
from datetime import datetime
from application.initial.BaseAdmin import BaseAdmin
from application.service.user.Model import UserModel
from application.util.CommonUtil import group_by_list
from application.util.TimeUtil import get_date_list, format_date
from application.service.system.Model import SystemRequestLogModel, SystemResponseLogModel
from fastadmin import (register, widget_action, WidgetActionType, WidgetActionChartProps, WidgetActionInputSchema,
                       WidgetActionResponseSchema, display)


@register(SystemRequestLogModel)
class SystemRequestLogAdmin(BaseAdmin):
    """
    请求日志管理
    """
    menu_section = "系统管理"
    list_display_links = ["id", "request_id"]
    list_display = ["id", "request_id", "用户", "request_ip", "request_path", "request_method", "request_body",
                    "request_method", "request_path", "request_headers", "request_query"]
    list_filter = ["request_method", "request_path"]
    search_fields = ["request_ip", "request_path"]
    ordering = ["-id"]
    readonly_fields = list_display
    widget_actions = ["request_chart"]

    @widget_action(
        widget_action_type=WidgetActionType.ChartLine,
        widget_action_props=WidgetActionChartProps(
            x_field="日期",
            y_field="请求数量"
        ),
        tab="基础统计",
        title="请求统计",
        description="近7天请求统计",
        width=12
    )
    async def request_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        date_list: list[str] = get_date_list(days=7)  # 获取最近7天的日期列表（包含今天）
        # 查询指定时间段的数据
        query_list: list[datetime] = await SystemRequestLogModel.filter(
            create_datetime__gte=date_list[0] + " 00:00:00",
            create_datetime__lte=date_list[-1] + " 23:59:59"
        ).values_list("create_datetime", flat=True)
        # 获取日期列表，并且根据日期进行分组
        result: dict[str, list] = group_by_list([format_date(item.date()) for item in query_list])
        return WidgetActionResponseSchema(
            data=[{"日期": key, "请求数量": len(value)} for key, value in result.items()]
        )

    @display(sorter="user__username")
    async def 用户(self, obj: SystemRequestLogModel) -> str:
        """
        获取用户名
        :param obj: 当前请求日志ORM模型
        :return:
        """
        user_model: Optional[UserModel] = await obj.user
        return user_model.username if user_model else "-"

    async def has_add_permission(self, user_id: UUID | int | None = None) -> bool:
        return False


@register(SystemResponseLogModel)
class SystemResponseLogAdmin(BaseAdmin):
    """
    响应日志管理
    """
    menu_section = "系统管理"
    list_display = ["id", "request_id", "response_headers", "response_body"]
    search_fields = ["request_id"]
    ordering = ["-id"]
    readonly_fields = list_display

    async def has_add_permission(self, user_id: UUID | int | None = None) -> bool:
        return False

from pydantic import BaseModel, StrictInt, field_serializer
from datetime import datetime
from typing import Optional


class BaseOutEntity(BaseModel):
    """
    输出实体基类
    """
    id: StrictInt
    update_datetime: datetime
    create_datetime: datetime

    @field_serializer("create_datetime")
    def create_datetime_fmt(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")

    @field_serializer("update_datetime")
    def update_datetime_fmt(self, value: datetime) -> str:
        return value.strftime("%Y-%m-%d %H:%M:%S")


class PagingEntity(BaseModel):
    """
    分页实体
    """
    page: StrictInt
    page_size: StrictInt
    total: StrictInt
    items: list


class BaseQueryEntity(BaseModel):
    """
    基础查询实体
    """
    page: Optional[int] = 1  # 当前页码
    page_size: Optional[int] = 10  # 每页数量

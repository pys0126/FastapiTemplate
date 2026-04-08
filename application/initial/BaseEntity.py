from pydantic import BaseModel, StrictInt
from typing import Any, Optional
from datetime import datetime


class BaseOutEntity(BaseModel):
    """
    输出实体基类
    """
    id: StrictInt
    update_datetime: datetime
    create_datetime: datetime

    def model_dump(self, **kwargs) -> dict[str, Any]:
        result: dict = super().model_dump(**kwargs)
        for key, value in result.items():
            # 尝试将时间转换为可读的字符串
            if isinstance(value, datetime):
                result[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        return result


class PagingEntity(BaseModel):
    """
    分页实体
    """
    page: StrictInt
    page_size: StrictInt
    total_count: StrictInt
    items: list


class BaseQueryEntity(BaseModel):
    """
    基础查询实体
    """
    page: Optional[int] = 1  # 当前页码
    page_size: Optional[int] = 10  # 每页数量

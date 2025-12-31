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
            # 尝试将日期转换为可读的字符串
            try:
                time_obj: datetime = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
                result[key] = time_obj.strftime("%Y-%m-%d %H:%M:%S")
            except (TypeError, ValueError):
                result[key] = value
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

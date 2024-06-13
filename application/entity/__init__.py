from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class BaseEntity(BaseModel):
    """
    实体基类
    """
    id: Optional[int]
    update_datetime: Optional[datetime]
    create_datetime: Optional[datetime]

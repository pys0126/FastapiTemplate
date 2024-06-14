from pydantic import BaseModel, StrictInt
from datetime import datetime
from typing import Optional


class BaseOutEntity(BaseModel):
    """
    输出实体基类
    """
    id: StrictInt
    update_datetime: datetime
    create_datetime: datetime
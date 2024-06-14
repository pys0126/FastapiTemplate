"""
数据表模型基类
"""
from datetime import datetime
from tortoise.models import Model
from tortoise.fields import DatetimeField, BigIntField


class TortoiseBaseModel(Model):
    """
    Tortoise模型基类
    """
    id: int = BigIntField(primary_key=True, unique=True, null=False, description="主键，自增")
    # 更新时间，自动生成
    update_datetime: datetime = DatetimeField(auto_now=True, null=True, description="更新时间")
    # 创建时间，只在第一次创建的时候自动生成
    create_datetime: datetime = DatetimeField(auto_now_add=True, null=True, description="创建时间")

    class Meta:
        abstract = True  # 抽象类，不会创建表

    def to_dict(self) -> dict:
        """
        转为字典
        :return:
        """
        remove_keys: list = ["_custom_generated_pk", "_await_when_save", "_partial", "_saved_in_db"]
        for key in remove_keys:
            if key in self.__dict__:
                self.__dict__.pop(key)
        return self.__dict__

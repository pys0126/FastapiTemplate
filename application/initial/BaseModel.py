"""
数据表模型基类
"""
from typing import Any, Union
from datetime import datetime
from tortoise.models import Model
from tortoise.functions import Sum
from tortoise.fields import DatetimeField, BigIntField
from application.initial.BaseEntity import PagingEntity


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
        result: dict = {}
        # 提取当前模型的字段的值
        for key in self.__dict__.keys():
            if key in self._meta.fields:
                # 尝试转为可读的时间字符串
                value: Any = self.__dict__.get(key)
                if isinstance(value, datetime):
                    value: str = value.strftime("%Y-%m-%d %H:%M:%S")
                result.update({key: value})
        return result

    @classmethod
    async def get_sum_by_fields(cls, sum_field: str, **kwargs) -> int:
        """
        统计某个字段值的总数
        :param sum_field: 需要统计的字段
        :param kwargs: 其他筛选条件
        :return: 统计结果
        """
        result: Any = await cls.filter(**kwargs).annotate(sum=Sum(sum_field)).first()
        return int(result.sum) if result.sum else 0

    @classmethod
    async def get_data_list_by_fields(cls, page: int = None, page_size: int = None, return_model: bool = False,
                                      order_field: str = "-id",
                                      **kwargs) -> Union[PagingEntity, list]:
        """
        获取数据列表（不传分页返回所有ORM模型）
        :param page: 第几页
        :param page_size: 每页多少条数据
        :param return_model: 是否返回ORM模型（返回所有数据无效）
        :param order_field: 排序条件字段（默认根据ID倒序）
        :param kwargs: 筛选条件
        :return: 分页对象 | 所有ORM对象列表
        """
        # 如果没有分页，则直接返回所有数据
        if not all([page, page_size]):
            return await cls.filter(**kwargs).order_by(order_field)
        model_list: list = await cls.filter(**kwargs).order_by(order_field).limit(page_size).offset(
            (page - 1) * page_size)
        if not return_model:
            return PagingEntity(page=page,
                                page_size=page_size,
                                total_count=await cls.filter(**kwargs).count(),
                                items=[item.to_dict() for item in model_list])
        return PagingEntity(page=page,
                            page_size=page_size,
                            total_count=await cls.filter(**kwargs).count(),
                            items=model_list)
"""
数据表模型基类
"""
from itertools import groupby
from datetime import datetime
from tortoise.models import Model
from tortoise.functions import Sum
from typing import Any, Optional, Self
from tortoise.fields import DatetimeField, BigIntField
from application.initial.BaseEntity import PagingEntity


class TortoiseBaseModel(Model):
    """
    Tortoise模型基类
    """
    id: int = BigIntField(primary_key=True, unique=True, null=False, description="主键")
    # 更新时间，自动生成
    update_datetime: datetime = DatetimeField(auto_now=True, null=True, description="更新时间")
    # 创建时间，只在第一次创建的时候自动生成
    create_datetime: datetime = DatetimeField(auto_now_add=True, null=True, description="创建时间")

    class Meta:
        abstract = True  # 抽象类，不会创建表

    def to_dict(self, exclude: Optional[tuple[str]] = None) -> dict:
        """
        转为字典
        :param exclude: 需要排除的字段
        :return:
        """
        result: dict = {}
        # 提取当前模型的字段的值
        for key in self.__dict__.keys():
            # 排除指定字段
            if exclude and key in exclude:
                continue
            result.update({key: self.__dict__.get(key)})
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
    async def get_data_list_by_fields(cls, page: int, page_size: int, return_model: bool = False,
                                      order_field: str = "-id",
                                      **kwargs) -> PagingEntity:
        """
        获取数据列表（不传分页返回所有ORM模型）
        :param page: 第几页
        :param page_size: 每页多少条数据
        :param return_model: 是否返回ORM模型（返回所有数据无效）
        :param order_field: 排序条件字段（默认根据ID倒序）
        :param kwargs: 筛选条件
        :return: 分页对象 | 所有ORM对象列表
        """
        model_list: list = await cls.filter(**kwargs).order_by(order_field).limit(page_size).offset(
            (page - 1) * page_size)
        if not return_model:
            return PagingEntity(page=page,
                                page_size=page_size,
                                total=await cls.filter(**kwargs).count(),
                                items=[item.to_dict() for item in model_list])
        return PagingEntity(page=page,
                            page_size=page_size,
                            total=await cls.filter(**kwargs).count(),
                            items=model_list)

    @classmethod
    async def group_by(cls, group_field: str, **kwargs) -> dict[Any, Self]:
        """
        根据字段分组（单个数据）
        :param group_field: 分组字段
        :param kwargs: 筛选条件
        :return: 分组结果（字典+ORM模型）
        """
        return {getattr(item, group_field): item async for item in cls.filter(**kwargs)}

    @classmethod
    async def batch_group_by(cls, group_field: str, result_fields: Optional[tuple] = None, **kwargs) -> dict[Any, list]:
        """
        根据字段分组（多个数据）
        :param group_field: 分组字段
        :param result_fields: 结果字段
        :param kwargs: 筛选条件
        :return: 分组结果（字典+列表数据）
        """
        if result_fields:
            queryset = await cls.filter(**kwargs).values(*result_fields)
            group_data = groupby(queryset, key=lambda x: x[group_field])
            return {key: list(group) for key, group in group_data}
        else:
            queryset = await cls.filter(**kwargs).all()
            group_data = groupby(queryset, key=lambda x: getattr(x, group_field))
            return {key: list([item.to_dict() for item in group]) for key, group in group_data}

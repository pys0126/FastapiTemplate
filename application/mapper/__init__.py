import traceback
from typing import Optional, Type, Any
from tortoise.functions import Sum
from application.model import TortoiseBaseModel
from application.util.LogUtil import write_error_log


class BaseMapper:
    """
    DAO层基类，提供基础的增删改查方法
    """
    orm_model: Type[TortoiseBaseModel] = None

    @classmethod
    async def insert(cls, data: dict) -> bool:
        """
        插入数据
        :param data: 数据字典
        :return:
        """
        try:
            # 移除id字段
            if "id" in data.keys():
                data.pop("id")
            # 插入数据
            new_model: TortoiseBaseModel = await cls.orm_model.create(**data)
            await new_model.save()
            return True
        except Exception:
            write_error_log(log_message=f"此数据插入失败：{data}", traceback=traceback.format_exc())
            return False

    @classmethod
    async def update(cls, data: dict) -> None:
        """
        更新数据
        :param data: 数据字典
        :return:
        """
        try:
            new_model: TortoiseBaseModel = await cls.orm_model.filter(id=data.get("id")).first()
            await new_model.update_from_dict(data=data)
        except Exception:
            write_error_log(log_message=f"此数据更新失败：{data}", traceback=traceback.format_exc())

    @classmethod
    async def delete(cls, orm_model: TortoiseBaseModel) -> None:
        """
        删除数据
        :param orm_model: ORM模型
        :return:
        """
        try:
            await orm_model.delete()
        except Exception:
            write_error_log(log_message=f"此Type[TortoiseBaseModel]删除失败：{orm_model.to_dict()}",
                            traceback=traceback.format_exc())

    @classmethod
    async def get_data_by_id(cls, data_id: int) -> Optional[Type[TortoiseBaseModel]]:
        """
        根据数据ID获取数据
        :param data_id: 数据ID
        :return: 数据ORM模型
        """
        return await cls.orm_model.filter(id=data_id).get_or_none()
    
    @classmethod
    async def get_data_by_fields(cls, **kwargs) -> Optional[Type[TortoiseBaseModel]]:
        """
        根据筛选条件获取数据
        :param kwargs: 筛选条件（and关系）
        :return: 数据ORM模型
        """
        return await cls.orm_model.filter(**kwargs).get_or_none()

    @classmethod
    async def get_data_list_by_fields(cls, page: int = None, page_size: int = None,
                                      **kwargs) -> list[Type[TortoiseBaseModel]]:
        """
        获取数据列表
        :param page: 第几页
        :param page_size: 每页多少条数据
        :param kwargs: 筛选条件
        :return: 数据ORM模型列表
        """
        # 如果没有分页，则直接返回所有数据
        if not all([page, page_size]):
            return await cls.orm_model.filter(**kwargs).all()
        return await cls.orm_model.filter(**kwargs).all().limit(page_size).offset((page - 1) * page_size)

    @classmethod
    async def get_data_count_by_fields(cls, **kwargs) -> int:
        """
        获取数据数量
        :param kwargs: 筛选条件
        :return: 数据ORM模型列表
        """
        return await cls.orm_model.filter(**kwargs).count()

    @classmethod
    async def get_sum_by_fields(cls, sum_field: str, **kwargs) -> int:
        """
        获取某个字段值的总数量
        :param sum_field: 某个字段
        :param kwargs: 筛选条件
        :return: 数据ORM模型列表
        """
        result: Any = await cls.orm_model.filter(**kwargs).annotate(sum=Sum(sum_field)).first()
        return result.sum

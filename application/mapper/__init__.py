import traceback
from typing import Optional
from tortoise.models import Model
from application.util.LogUtil import write_error_log


class BaseMapper:
    """
    DAO层基类，提供基础的增删改查方法
    """
    orm_model: Model = None

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
            new_model: Model = await cls.orm_model.create(**data)
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
            await cls.orm_model.update_from_dict(data=data)
        except Exception:
            write_error_log(log_message=f"此数据更新失败：{data}", traceback=traceback.format_exc())

    @classmethod
    async def delete(cls, orm_model: Model) -> None:
        """
        删除数据
        :param orm_model: ORM模型
        :return:
        """
        try:
            await orm_model.delete()
        except Exception:
            write_error_log(log_message=f"此Model删除失败：{orm_model.to_dict()}", traceback=traceback.format_exc())


    @classmethod
    async def get_data_by_id(cls, data_id: int) -> Optional[Model]:
        """
        根据数据ID获取数据
        :param data_id: 数据ID
        :return: 数据ORM模型
        """
        return await cls.orm_model.filter(id=data_id).get_or_none()
    
    @classmethod
    async def get_data_list(cls, page: int, page_size: int) -> list[Optional[Model]]:
        """
        获取数据列表
        :param page: 第几页
        :param page_size: 每页多少条数据
        :return: 数据ORM模型列表
        """
        return await cls.orm_model.all().limit(page_size).offset((page - 1) * page_size)
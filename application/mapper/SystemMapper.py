from application.model.SystemModel import SystemRequestLogModel, SystemResponseLogModel
from application.mapper import BaseMapper


class SystemRequestLogMapper(BaseMapper):
    """
    请求日志DAO
    """
    orm_model: SystemRequestLogModel = SystemRequestLogModel


class SystemResponseLogMapper(BaseMapper):
    """
    响应日志DAO
    """
    orm_model: SystemResponseLogModel = SystemResponseLogModel

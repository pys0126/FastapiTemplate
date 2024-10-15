"""
后端服务相关表ORM
"""
from tortoise.fields import CharField, TextField, BigIntField
from application.util.StringUtil import random_uuid
from application.model import TortoiseBaseModel


class SystemRequestLogModel(TortoiseBaseModel):
    """
    请求日志表
    """
    user_id: int = BigIntField(null=True, description="用户ID")
    request_body: str = TextField(null=True, description="请求体")
    request_headers: str = TextField(null=True, description="请求头")
    request_ip: str = CharField(max_length=32, null=True, description="请求IP")
    request_method: str = CharField(max_length=8, null=True, description="请求方法")
    request_path: str = CharField(max_length=128, null=True, description="请求路径")
    request_query: str = TextField(null=True, description="请求参数")
    request_id: str = CharField(max_length=36, default=random_uuid(), null=True, description="请求ID")

    class Meta:
        table: str = "system_request_log"
        table_description: str = "请求日志表"


class SystemResponseLogModel(TortoiseBaseModel):
    """
    响应日志表
    """
    response_body: str = TextField(null=True, description="响应体")
    response_headers: str = TextField(null=True, description="响应头")
    request_id: str = CharField(max_length=36, default=random_uuid(), null=True, description="请求ID")

    class Meta:
        table: str = "system_response_log"
        table_description: str = "响应日志表"

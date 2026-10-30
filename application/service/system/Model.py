"""
后端服务相关表ORM
"""
from tortoise.fields import (
    CASCADE,
    CharField,
    ForeignKeyField,
    ForeignKeyNullableRelation,
    TextField,
)
from application.util.StringUtil import random_uuid
from application.service.user.Model import UserModel
from application.initial.BaseModel import TortoiseBaseModel


class SystemRequestLogModel(TortoiseBaseModel):
    """
    请求日志表
    """
    user: ForeignKeyNullableRelation[UserModel] = ForeignKeyField(
        to="models.UserModel", on_delete=CASCADE, null=True, description="用户ID"
    )
    request_body: str | None = TextField(null=True, description="请求体")
    request_headers: str | None = TextField(null=True, description="请求头")
    request_ip: str | None = CharField(max_length=32, null=True, description="请求IP")
    request_method: str | None = CharField(max_length=8, null=True, description="请求方法")
    request_path: str | None = CharField(max_length=128, null=True, description="请求路径")
    request_query: str | None = TextField(null=True, description="请求参数")
    request_id: str | None = CharField(max_length=36, default=random_uuid, null=True, description="请求ID")

    class Meta:
        table: str = "system_request_log"
        table_description: str = "请求日志表"
        indexes: tuple = ("request_id", "request_path", "request_method", "request_ip")

    def __str__(self) -> str:
        return self.request_id or ""


class SystemResponseLogModel(TortoiseBaseModel):
    """
    响应日志表
    """
    response_body: str | None = TextField(null=True, description="响应体")
    response_headers: str | None = TextField(null=True, description="响应头")
    request_id: str | None = CharField(max_length=36, default=random_uuid, null=True, description="请求ID")

    class Meta:
        table: str = "system_response_log"
        table_description: str = "响应日志表"
        indexes: tuple = ("request_id",)

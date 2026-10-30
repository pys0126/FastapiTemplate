from tortoise.fields import CharField, TextField, BooleanField
from application.initial.BaseModel import TortoiseBaseModel


class UserModel(TortoiseBaseModel):
    """
    用户表
    """
    username: str | None = CharField(
        max_length=16, null=True, unique=True, description="用户名"
    )
    nickname: str | None = CharField(max_length=8, null=True, description="昵称")
    password: str | None = CharField(max_length=40, null=True, description="密码")
    avatar: str = TextField(null=False,
                            default="https://c-ssl.duitang.com/uploads/blog/202206/12/20220612164733_72d8b.jpg",
                            description="头像URL")
    intro: str = CharField(default="简短介绍一下自己吧~", max_length=250, null=False, description="个人简介")
    is_disabled: bool = BooleanField(null=False, default=False, description="是否禁用")
    is_employee: bool = BooleanField(null=False, default=False, description="是否员工账号")
    is_superuser: bool = BooleanField(null=False, default=False, description="是否超级管理员")

    class Meta:
        table: str = "application_user"  # 表名
        table_description: str = "用户表"  # 表描述
        indexes: tuple = ("username", "nickname", "is_disabled", "is_employee", "is_superuser")

    def __str__(self) -> str:
        return self.username or ""

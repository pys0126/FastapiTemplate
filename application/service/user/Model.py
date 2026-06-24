from tortoise.fields import CharField, TextField, BooleanField, IntField, CharEnumField
from application.initial.BaseModel import TortoiseBaseModel
from application.service.user.Enum import UserSexEnum


class UserModel(TortoiseBaseModel):
    """
    用户表
    """
    username: str = CharField(max_length=16, null=True, unique=True, description="用户名")
    nickname: str = CharField(max_length=8, null=True, description="昵称")
    password: str = CharField(max_length=40, null=True, description="密码")
    email: str = CharField(max_length=32, null=True, unique=True, description="邮箱")
    phone: str = CharField(max_length=11, null=True, unique=True, description="手机号")
    avatar: str = TextField(null=False,
                            default="https://c-ssl.duitang.com/uploads/blog/202206/12/20220612164733_72d8b.jpg",
                            description="头像URL")
    age: int = IntField(default=18, max_length=3, null=False, description="年龄")
    sex: str = CharEnumField(enum_type=UserSexEnum, max_length=3, null=False, default=UserSexEnum.OTHER.value,
                             description="性别枚举")
    intro: str = CharField(default="简短介绍一下自己吧~", max_length=250, null=False, description="个人简介")
    occupation: str = CharField(default="未知", max_length=20, null=False, description="职业")
    address: str = CharField(default="未知", max_length=50, null=False, description="地址")
    follow_ids: str = TextField(default="", null=True, description="关注用户ID列表，用英文逗号分隔")
    fans_ids: str = TextField(default="", null=True, description="粉丝用户ID列表，用英文逗号分隔")
    is_disabled: bool = BooleanField(null=False, default=False, description="是否禁用")
    is_employee: bool = BooleanField(null=False, default=False, description="是否员工账号")
    is_superuser: bool = BooleanField(null=False, default=False, description="是否超级管理员")

    class Meta:
        table: str = "application_user"  # 表名
        table_description: str = "用户表"  # 表描述
        indexes: tuple = ("username", "nickname", "email", "phone", "sex", "is_disabled", "is_employee", "is_superuser")

    def __str__(self):
        return self.username

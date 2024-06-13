from tortoise.fields import CharField, TextField, BooleanField
from application.model import TortoiseBaseModel


class UserModel(TortoiseBaseModel):
    """
    用户表
    """
    nickname: str = CharField(max_length=8, null=True, description="昵称，长度为8")
    username: str = CharField(max_length=16, null=True, unique=True, description="用户名，长度为16，唯一")
    password: str = CharField(max_length=40, null=True, description="密码，sha1(md5)，长度40")
    email: str = CharField(max_length=32, null=True, description="邮箱，长度为32")
    avatar: str = TextField(null=True, default="https://c-ssl.duitang.com/uploads/blog/202206/12/"
                                               "20220612164733_72d8b.jpg", description="头像URL")
    is_active: bool = BooleanField(null=True, default=True, description="是否激活")

    class Meta:
        table: str = "users"  # 表名
        table_description: str = "用户表"  # 表描述

from tortoise.fields import CharField, TextField, BooleanField, BigIntField, IntField, CharEnumField
from application.enumeration.UserSexEnum import UserSexEnum
from application.model import TortoiseBaseModel


class UserModel(TortoiseBaseModel):
    """
    用户表
    """    
    # 登陆/注册用
    username: str = CharField(max_length=16, null=True, unique=True, description="用户名，长度为16，唯一")
    nickname: str = CharField(max_length=8, null=True, description="昵称，长度为8")
    password: str = CharField(max_length=40, null=True, description="密码，sha1(md5)，长度40")
    email: str = CharField(max_length=32, null=True, description="邮箱，长度为32")
    phone: int = BigIntField(max_length=11, null=True, description="手机号，长度为11")
    # 其他信息
    avatar: str = TextField(null=True, default="https://c-ssl.duitang.com/uploads/blog/202206/12/"
                            "20220612164733_72d8b.jpg", description="头像URL")
    age: int = IntField(default=18, max_length=3, null=True, description="年龄，长度为3")
    sex: str = CharEnumField(enum_type=UserSexEnum, max_length=3, null=True, default=UserSexEnum.OTHER.value, 
                             description="性别枚举，男/女/其他")
    follow: list = TextField(null=True, description="关注用户ID列表，用,分隔")
    # 限制信息    
    is_active: bool = BooleanField(null=True, default=True, description="是否激活")       

    class Meta:
        table: str = "users"  # 表名
        table_description: str = "用户表"  # 表描述

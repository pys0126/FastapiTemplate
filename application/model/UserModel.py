from tortoise.fields import CharField, TextField, BooleanField, BigIntField, IntField, CharEnumField
from application.enumeration.UserSexEnum import UserSexEnum
from application.model import TortoiseBaseModel


class UserModel(TortoiseBaseModel):
    """
    用户表
    """
    username: str = CharField(max_length=16, null=True, unique=True, description="用户名，长度为16，唯一")
    nickname: str = CharField(max_length=8, null=True, description="昵称，长度为8")
    password: str = CharField(max_length=40, null=True, description="密码，sha1(md5)，长度40")
    email: str = CharField(max_length=32, null=True, unique=True, description="邮箱，长度为32，唯一")
    phone: int = BigIntField(max_length=11, null=True, unique=True, description="手机号，长度为11，唯一")
    avatar: str = TextField(null=True,
                            default="https://c-ssl.duitang.com/uploads/blog/202206/12/20220612164733_72d8b.jpg",
                            description="头像URL")
    age: int = IntField(default=18, max_length=3, null=True, description="年龄，长度为3")
    sex: str = CharEnumField(enum_type=UserSexEnum, max_length=3, null=True, default=UserSexEnum.OTHER.value, 
                             description="性别枚举，男/女/其他")
    describe: str = CharField(max_length=250, null=True, description="个人简介，250字符")
    occupation: str = CharField(max_length=20, null=True, description="职业，20字符")
    address: str = CharField(max_length=50, null=True, description="地址，50字符")
    follow_ids: str = TextField(null=True, description="关注用户ID列表，用英文逗号分隔")
    fans_ids: str = TextField(null=True, description="粉丝用户ID列表，用英文逗号分隔")
    is_disabled: bool = BooleanField(null=True, default=False, description="是否禁用")

    class Meta:
        table: str = "users"  # 表名
        table_description: str = "用户表"  # 表描述

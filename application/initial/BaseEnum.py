from enum import Enum


class StatusCodeEnum(Enum):
    """
    状态码枚举
    """
    SUCCESS = (2000, "ok")
    ERROR = (5000, "fail")
    SERVER_BUSY = (5001, "服务器繁忙，请稍后重试")
    SYSTEM_ERROR = (5002, "系统异常，请稍后再试")

    CAPTCHA_SEND_ERROR = (3009, "验证码发送失败，请稍后再试")
    LOGIN_STATUS_EXPIRED = (3010, "登陆状态失效")

    # 常见错误
    BAD_REQUEST_ERROR = (4000, "错误请求")
    ILLEGALITY_ERROR = (4001, "非法请求")
    PHONE_FORMAT_ERROR = (4002, "手机号格式错误")
    EMAIL_FORMAT_ERROR = (4003, "邮箱格式错误")
    PASSWORD_FORMAT_ERROR = (4004, "密码最少6位，包含字母与数字，且不能包含特殊字符")
    EMAIL_CAPTCHA_ALREADY_SENT = (4005, "已发送验证码，未找到请查看垃圾箱")
    PHONE_CAPTCHA_ALREADY_SENT = (4006, "已发送验证码，未收到请重试")

    # 权限相关
    AUTHORITY_ERROR = (4030, "无权限访问")
    CAPTCHA_ERROR = (4031, "验证码错误")
    PASSWORD_ERROR = (4032, "密码错误")
    USER_DISABLED = (4033, "该用户已被封禁")

    NOT_FOUND_ERROR = (4040, "未找到")
    USER_NOT_REGISTERED = (4041, "该用户未注册")
    USER_NOT_FOUND = (4042, "该用户不存在")

    METHOD_ERROR = (4050, "请求方法错误")

    ALREADY_EXIST_ERROR = (4090, "已存在")
    PHONE_ALREADY_EXIST = (4091, "手机号已被注册")
    EMAIL_ALREADY_EXIST = (4092, "邮箱已被注册")

    # 媒体相关
    MEDIA_TYPE_ERROR = (4130, "不支持的媒体类型")
    IMAGE_VIOLATION = (4230, "图片违规")
    FILE_SIZE_ERROR = (4140, "文件大小错误")
    FILE_UPLOAD_ERROR = (4150, "文件上传错误")
    FILE_DELETE_ERROR = (4160, "文件删除错误")

    # 微信相关
    WECHAT_MINI_LOGIN_ERROR = (6000, "微信小程序登录错误")
    WECHAT_MINI_USER_EXIST = (6002, "微信小程序用户已绑定")

    # 支付、权益相关
    UNKNOWN_PAY_MODE = (7000, "未知支付方式")
    PAY_ORDER_CREATE_ERROR = (7040, "订单创建失败")
    PAY_ORDER_CANCEL_ERROR = (7050, "订单取消失败")

    @property
    def code(self) -> int:
        """
        获取状态码
        :return:
        """
        return self.value[0]

    @property
    def description(self) -> str:
        """
        获取状态码描述
        :return:
        """
        return self.value[1]


class WebsocketNoticeTypeEnum(Enum):
    """
    websocket通知类型枚举
    """
    # 普通通知
    MESSAGE = "message"
    # 试衣通知
    FITTING = "fitting"
    # 积分更新通知
    POINTS = "points"
    # 邀请通知
    SHARE = "share"

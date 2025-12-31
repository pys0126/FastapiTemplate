from enum import Enum


class StatusCodeEnum(Enum):
    """
    状态码枚举
    """
    SUCCESS = 2000  # 成功
    ERROR = 5000  # 失败
    LOGIN_STATUS_EXPIRED = 3010  # 登录状态失效
    # 通用
    ILLEGALITY_ERROR = 4001  # 非法请求
    AUTHORITY_ERROR = 4030  # 权限错误
    NOT_FOUND_ERROR = 4040  # 未找到
    METHOD_ERROR = 4050  # 请求方法错误
    BAD_REQUEST_ERROR = 4000  # 错误请求
    ALREADY_EXIST_ERROR = 4090  # 已存在
    # 媒体相关
    MEDIA_TYPE_ERROR = 4130  # 不支持的媒体类型
    IMAGE_VIOLATION = 4230  # 图片违规
    FILE_SIZE_ERROR = 4140  # 文件大小错误
    FILE_UPLOAD_ERROR = 4150  # 文件上传错误
    FILE_DELETE_ERROR = 4160  # 文件删除错误
    # 换装相关
    DRESS_UP_ERROR = 4250  # 换装失败
    DRESS_UP_ALREADY_EXIST = 4290  # 已有换装任务
    DRESS_UP_NOT_EXIST = 4251  # 换装任务不存在
    DRESS_UP_NOT_ROOM_ERROR = 4253  # 试衣间不存在或被禁用
    DRESS_UP_NOT_ENOUGH = 4254  # 试衣间试衣次数不足
    # 衣橱相关
    CLOSET_LIMIT_ERROR = 4301  # 衣橱数量超出限制
    SINGLES_LIMIT_ERROR = 4300  # 单品数量超出限制
    SINGLES_NOT_FOUND = 4304  # 单品不存在
    CLOSET_DELETE_ERROR = 4302  # 衣橱删除失败
    OUTFITS_LIMIT_ERROR = 4303  # 搭配数量超出限制
    # 微信相关
    WECHAT_MINI_LOGIN_ERROR = 6000  # 微信小程序登录错误
    WECHAT_MINI_USER_EXIST = 6002  # 微信小程序用户已绑定
    # 支付、权益相关
    UNKNOWN_PAY_MODE = 7000  # 未知支付方式
    PAY_ORDER_CREATE_ERROR = 7040  # 订单创建失败
    PAY_ORDER_CANCEL_ERROR = 7050  # 订单取消失败
    INTEGRAL_NOT_ENOUGH = 7100  # 积分不足
    # 其他
    DAILY_CHECK_IN_ALREADY = 9040  # 今日已签到


class SeasonEnum(Enum):
    """
    季节枚举
    """
    SPRING = "春季"
    SUMMER = "夏季"
    AUTUMN = "秋季"
    WINTER = "冬季"


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

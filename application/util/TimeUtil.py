import time
from datetime import datetime, timedelta, date


def now_format_datetime() -> str:
    """
    获取当前格式化时间字符串
    :return: 当前格式化时间字符串
    """
    # 获取当前时间
    current_time = datetime.now()
    # 格式化时间
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_time

def format_datetime(_datetime: datetime) -> str:
    """
    格式化时间
    :param _datetime: 时间
    :return: 格式化后的时间字符串
    """
    return _datetime.strftime("%Y-%m-%d %H:%M:%S")


def now_format_date() -> str:
    """
    获取当前格式化日期字符串
    :return: 当前格式化日期字符串
    """
    # 获取当前时间
    current_time = datetime.now()
    # 格式化时间
    formatted_time = current_time.strftime("%Y-%m-%d")
    return formatted_time

def format_date(_date: date) -> str:
    """
    格式化日期
    :param _date: 日期
    :return: 格式化后的日期字符串
    """
    return _date.strftime("%Y-%m-%d")


def now_timestamp() -> int:
    """
    获取当前时间戳
    :return: 当前时间戳整数
    """
    return int(time.time())


def timestamp_to_datetime(timestamp: int) -> datetime:
    """
    时间戳转时间
    :param timestamp: 时间戳整数
    :return: 时间
    """
    return datetime.fromtimestamp(timestamp)


def date_difference(start_date: datetime, end_date: datetime) -> int:
    """
    日期差
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return: 日期差
    """
    return (end_date - start_date).days


def get_date_list(days: int) -> list[str]:
    """
    获取从今天往前推 days 天的所有日期字符串列表（包含当天）
    :param days: 向前推的天数
    :return: 日期字符串列表 (格式: YYYY-MM-DD)
    """
    # 获取当前时间作为结束日期
    end_date = datetime.now()
    # 计算开始日期：当前时间减去 (days - 1) 天
    # 例如 days=3，则是今天、昨天、前天
    start_date = end_date - timedelta(days=days - 1)
    # 计算时间间隔，生成日期列表
    delta = (end_date - start_date).days
    return [(start_date + timedelta(d)).strftime("%Y-%m-%d") for d in range(delta + 1)]

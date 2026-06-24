"""
通用工具包
"""
from itertools import groupby


def group_by_list(array: list) -> dict[str, list]:
    """
    列表分组（兼容枚举类型）
    :param array: 列表
    :return:
    """
    try:
        array.sort(key=lambda x: x)
    except TypeError:
        array.sort(key=lambda x: x.value)
    return {key: list(group) for key, group in groupby(array)}

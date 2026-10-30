"""模型字段标注和默认值测试，不连接数据库。"""

import unittest
from datetime import datetime
from typing import get_args, get_type_hints

from application.initial.BaseModel import TortoiseBaseModel
from application.service.system.Model import SystemRequestLogModel, SystemResponseLogModel
from application.service.user.Model import UserModel


class ModelFieldTest(unittest.TestCase):
    """检查可空字段与模型标注一致。"""

    def test_nullable_fields_are_annotated(self) -> None:
        """显式声明的可空字段可以返回 None。"""
        for model in (
            TortoiseBaseModel,
            UserModel,
            SystemRequestLogModel,
            SystemResponseLogModel,
        ):
            annotations = get_type_hints(model)
            for field_name in model.__annotations__:
                field = model._meta.fields_map[field_name]
                if field.null:
                    with self.subTest(model=model.__name__, field=field_name):
                        self.assertIn(type(None), get_args(annotations[field_name]))

    def test_log_request_ids_have_per_instance_defaults(self) -> None:
        """请求日志和响应日志的新记录分别生成请求 ID。"""
        for model in (SystemRequestLogModel, SystemResponseLogModel):
            with self.subTest(model=model.__name__):
                first_id = model().request_id
                second_id = model().request_id
                self.assertIsInstance(first_id, str)
                self.assertNotEqual(first_id, second_id)

    def test_base_timestamps_accept_none_before_save(self) -> None:
        """自动生成的时间字段在保存前可能为空。"""
        annotations = get_type_hints(TortoiseBaseModel)
        for field_name in ("create_datetime", "update_datetime"):
            with self.subTest(field=field_name):
                self.assertIn(datetime, get_args(annotations[field_name]))
                self.assertIn(type(None), get_args(annotations[field_name]))


if __name__ == "__main__":
    unittest.main()

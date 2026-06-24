import inspect
from copy import copy
from decimal import Decimal
from contextlib import contextmanager
from asgiref.sync import sync_to_async
from fastadmin import TortoiseModelAdmin, action
from typing import Any, Iterator, Optional, Sequence
from fastadmin.models.schemas import ModelFieldWidgetSchema, WidgetType


class BaseAdmin(TortoiseModelAdmin):
    """
    基础后台管理类
    """
    actions_on_top = True
    actions_on_bottom = False

    @action(description="批量删除")
    async def batch_delete(self, obj_ids: list[int]) -> None:
        """
        批量删除
        :param obj_ids: 需要删除的ID列表
        :return:
        """
        await self.model_cls.filter(id__in=obj_ids).delete()

    @property
    def field_label_map(self) -> dict[str, str]:
        """
        ORM字段名到后台展示名的映射。
        :return:
        """
        label_map: dict[str, str] = {}
        used_labels: set[str] = set()
        for field_name, field in self.model_cls._meta.fields_map.items():
            description: str = getattr(field, "description", None) or field_name
            if description in used_labels:
                description = field_name
            label_map[field_name] = description
            used_labels.add(description)
        return label_map

    @property
    def label_field_map(self) -> dict[str, str]:
        """
        后台展示名到ORM字段名的映射。
        :return:
        """
        return {label: field for field, label in self.field_label_map.items()}

    def get_column_name(self, column: str) -> str:
        """
        获取列中文名称
        :param column: 列名
        :return: 列中文名称
        """
        return self.field_label_map.get(column, column)

    def get_field_name(self, label: str) -> str:
        """
        获取展示名对应的真实字段名
        :param label: 展示名
        :return: 真实字段名
        """
        return self.label_field_map.get(label, label)

    def get_column_sequence(self, columns: Sequence[str]) -> list[str]:
        """
        字段名列表转为展示名列表
        :param columns: 字段名列表
        :return:
        """
        return [self.get_column_name(column=column) for column in columns]

    def get_field_sequence(self, labels: Sequence[str]) -> list[str]:
        """
        展示名列表转为字段名列表
        :param labels: 展示名列表
        :return:
        """
        return [self.get_field_name(label=label) for label in labels]

    @contextmanager
    def use_real_field_configs(self) -> Iterator[None]:
        """
        fastadmin底层解析字段时仍需要真实字段名，这里临时把展示名配置还原。
        :return:
        """
        attrs = (
            "list_display",
            "list_display_links",
            "list_filter",
            "search_fields",
            "sortable_by",
            "fields",
            "exclude",
            "readonly_fields",
            "ordering",
            "formfield_overrides",
            "list_display_widths",
        )
        snapshots: dict[str, Any] = {attr: getattr(self, attr) for attr in attrs}
        try:
            for attr in attrs[:8]:
                setattr(self, attr, self.get_field_sequence(labels=getattr(self, attr)))
            self.ordering = [
                f"-{self.get_field_name(label=field[1:])}" if field.startswith("-") else self.get_field_name(label=field)
                for field in self.ordering
            ]
            self.formfield_overrides = {
                self.get_field_name(label=field): config
                for field, config in self.formfield_overrides.items()
            }
            self.list_display_widths = {
                self.get_field_name(label=field): width
                for field, width in self.list_display_widths.items()
            }
            yield
        finally:
            for attr, value in snapshots.items():
                setattr(self, attr, value)

    async def pre_generate_models_schema(self) -> None:
        """
        生成后台配置前，把字段配置切换成展示名，使fastadmin前端按description展示。
        :return:
        """
        # 顺带增加批量删除操作
        self.actions += ("batch_delete",)
        # 顺带更新当前管理模块名称
        table_description: Optional[str] = getattr(self.model_cls._meta, "table_description", None)
        if table_description:
            model_name: str = table_description.replace("表", "")
            self.verbose_name = self.verbose_name or f"{model_name}管理"
            self.verbose_name_plural = self.verbose_name_plural or f"{model_name}管理列表"

        self.list_display = self.get_column_sequence(columns=self.list_display)
        self.list_display_links = self.get_column_sequence(columns=self.list_display_links)
        self.list_filter = self.get_column_sequence(columns=self.list_filter)
        self.search_fields = self.get_column_sequence(columns=self.search_fields)
        self.sortable_by = self.get_column_sequence(columns=self.sortable_by)
        self.fields = self.get_column_sequence(columns=self.fields)
        self.exclude = self.get_column_sequence(columns=self.exclude)
        self.readonly_fields = self.get_column_sequence(columns=self.readonly_fields)
        self.ordering = [
            f"-{self.get_column_name(column=field[1:])}" if field.startswith("-") else self.get_column_name(column=field)
            for field in self.ordering
        ]
        self.formfield_overrides = {
            self.get_column_name(column=field): config
            for field, config in self.formfield_overrides.items()
        }
        self.list_display_widths = {
            self.get_column_name(column=field): width
            for field, width in self.list_display_widths.items()
        }

    def get_model_fields_with_widget_types(
            self,
            with_m2m: Optional[bool] = None,
    ) -> list[ModelFieldWidgetSchema]:
        """
        重写获取模型字段和Widget类型，读取每列中文描述
        :param with_m2m: 是否包含多对多字段
        :return: 模型字段和Widget类型列表
        """
        with self.use_real_field_configs():
            super_results: list[ModelFieldWidgetSchema] = super().get_model_fields_with_widget_types(with_m2m=with_m2m)
        results: list[ModelFieldWidgetSchema] = []
        for result in super_results:
            field = copy(result)
            field.name = self.get_column_name(column=field.name)
            results.append(field)
        return results

    def get_fields_for_serialize(self) -> set[str]:
        """
        This method is used to get fields for serialize.
        :return: A set of fields.
        """
        fields = self.get_model_fields_with_widget_types()
        fields_for_serialize = {field.name for field in fields}
        if self.fields:
            fields_for_serialize &= set(self.fields)
        if self.exclude:
            fields_for_serialize -= set(self.exclude)
        if self.list_display:
            fields_for_serialize |= set(self.list_display)
        return fields_for_serialize

    def resolve_sort_by(self, sort_by: str) -> str:
        """
        展示名排序字段转为真实字段名
        :param sort_by: 排序字段
        :return:
        """
        if not sort_by:
            return sort_by
        prefix: str = "-" if sort_by.startswith("-") else ""
        field_name: str = sort_by.lstrip("-")
        return super().resolve_sort_by(f"{prefix}{self.get_field_name(label=field_name)}")

    async def orm_get_list(
            self,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            search: Optional[str] = None,
            sort_by: Optional[str] = None,
            filters: Optional[dict] = None,
    ) -> tuple[list[Any], int]:
        """
        展示名查询条件转为真实字段名后再查询
        :param offset: 偏移量
        :param limit: 限制数量
        :param search: 搜索关键词
        :param sort_by: 排序字段
        :param filters: 筛选条件
        :return:
        """
        real_filters = None
        if filters:
            real_filters = {
                (self.get_field_name(label=field), condition): value
                for (field, condition), value in filters.items()
            }

        with self.use_real_field_configs():
            return await super().orm_get_list(
                offset=offset,
                limit=limit,
                search=search,
                sort_by=sort_by,
                filters=real_filters,
            )

    async def save_model(self, id: Any = None, payload: dict = None) -> Optional[dict]:
        """
        保存时统一使用展示名字段，兼容前端传展示名和手动传真实字段名两种场景。
        :param id: 对象ID
        :param payload: 请求载荷
        :return:
        """
        payload = payload or {}
        real_payload: dict = {self.get_field_name(label=field): value for field, value in payload.items()}
        if id is not None:
            readonly_fields: set[str] = set(self.get_field_sequence(labels=self.readonly_fields))
            readonly_fields.add(self.get_model_pk_name(self.model_cls))
            real_payload = {
                field: value
                for field, value in real_payload.items()
                if field not in readonly_fields
            }
        display_payload: dict = {
            self.get_column_name(column=field): value
            for field, value in real_payload.items()
        }
        return await super().save_model(id, display_payload)

    async def serialize_obj_attributes(
            self, obj: Any, attributes_to_serialize: list[ModelFieldWidgetSchema], list_view: bool = False
    ) -> dict[str, Any]:
        """
        Serialize orm model obj attribute to dict.
        :params obj: an object.
        :params attributes_to_serialize: a list of attributes to serialize.
        :return: A dict of serialized attributes.
        """
        serialized_dict: dict[str, Any] = {}
        for field in attributes_to_serialize:
            value = getattr(obj, field.column_name)
            if isinstance(value, Decimal):
                value = format(value, "f")
            serialized_dict[field.name] = value
            if not list_view and field.form_widget_type in (WidgetType.UploadFile, WidgetType.UploadImage) and value:
                serialized_dict[f"{field.name}__url"] = await self.get_file_url(field.name, value, obj)
        if inspect.iscoroutinefunction(obj.__str__):
            str_fn = obj.__str__
        else:
            str_fn = sync_to_async(obj.__str__)
        serialized_dict["__str__"] = await str_fn()
        return serialized_dict

    async def serialize_obj(self, obj: Any, list_view: bool = False) -> dict:
        """
        Serialize orm model obj to dict.
        :params obj: an object.
        :params exclude_fields: a list of fields to exclude.
        :return: A dict.
        """
        fields = self.get_model_fields_with_widget_types()
        fields_for_serialize = self.get_fields_for_serialize()

        obj_dict = {}
        attributes_to_serialize = []
        for field in fields:
            if field.name not in fields_for_serialize:
                continue
            if field.is_m2m and list_view:
                continue
            if field.is_m2m:
                obj_dict[field.name] = await self.orm_get_m2m_ids(obj, field.column_name)
            else:
                attributes_to_serialize.append(field)

        obj_dict.update(await self.serialize_obj_attributes(obj, attributes_to_serialize, list_view=list_view))

        for field_name in fields_for_serialize:
            real_field_name: str = self.get_field_name(label=field_name)
            display_field_function = getattr(self, real_field_name, None)
            if not display_field_function or not hasattr(display_field_function, "is_display"):
                continue

            if inspect.iscoroutinefunction(display_field_function):
                display_field_function_fn = display_field_function
            else:
                display_field_function_fn = sync_to_async(display_field_function)

            obj_dict[field_name] = await display_field_function_fn(obj)

        pk_name: str = self.get_model_pk_name(self.model_cls)
        if pk_name not in obj_dict:
            obj_dict[pk_name] = getattr(obj, pk_name)

        return obj_dict

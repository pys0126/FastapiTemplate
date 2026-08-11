from fastadmin import TortoiseModelAdmin, action
from typing import Optional


class BaseAdmin(TortoiseModelAdmin):
    """
    基础后台管理类
    """
    ordering = ["-id"]
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

    async def pre_generate_models_schema(self) -> None:
        await super().pre_generate_models_schema()
        # 顺带更新当前管理模块名称
        table_description: Optional[str] = getattr(self.model_cls._meta, "table_description", None)
        if table_description:
            model_name: str = table_description.replace("表", "")
            self.verbose_name = self.verbose_name or f"{model_name}管理"
            self.verbose_name_plural = self.verbose_name_plural or f"{model_name}管理列表"
        # 顺带更新字段展示名
        self.list_display_labels = self.field_label_map

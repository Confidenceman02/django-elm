from dataclasses import dataclass
from typing import Annotated, Any
from django.db import models
from django.forms.boundfield import BoundField
from pydantic import TypeAdapter, ValidationError
from pydantic.functional_validators import BeforeValidator
from djelm.flags.form.helpers import ModelChoiceFieldVariant, ModelChoiceFlagHelper
from djelm.flags.primitives import Flag
from django.forms.models import ModelChoiceField


@dataclass(slots=True)
class ModelChoiceFieldFlag(Flag):
    variants: list[type[models.Model]] | None = None

    def anno(self) -> Annotated:
        return Annotated[
            ModelChoiceFlagHelper.object_annotation(self._get_variants()),  # type:ignore
            BeforeValidator(self.serializer),
        ]

    def adapter(self):
        return TypeAdapter(self.anno())

    def obj(self) -> Flag:
        return ModelChoiceFlagHelper.object_flag(self._get_variants())

    def _get_variants(self) -> list[ModelChoiceFieldVariant]:
        if self.variants:
            return [ModelChoiceFieldVariant(mod) for mod in self.variants]
        else:
            return []

    def serializer(self, field: Any):
        """
        Serialize a BoundField to a structure pydantic can validate.
        """
        try:
            assert isinstance(field, BoundField) and isinstance(
                field.field, ModelChoiceField
            )
        except Exception as err:
            raise ValidationError(err)

        return ModelChoiceFlagHelper.field_to_dict(field, self._get_variants())


class ModelMultipleChoiceFieldFlag(ModelChoiceFieldFlag):
    def __init__(self, variants: list[type[models.Model]] | None = None):
        super().__init__(variants)

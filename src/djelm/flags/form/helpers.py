from dataclasses import dataclass
from types import UnionType
from typing import Any, NotRequired, Optional
import typing
from typing_extensions import TypedDict
from django.db import models
from django.forms.boundfield import BoundField, BoundWidget
from django.db.models.fields import CharField, BooleanField, IntegerField, FloatField
from pydantic import BaseModel
from djelm.flags.primitives import (
    BoolFlag,
    CustomTypeFlag,
    Flag,
    IntFlag,
    ListFlag,
    NullableFlag,
    ObjectFlag,
    StringFlag,
    FloatFlag,
)

SUPPORTED_VARIANT_FIELDS = [CharField, BooleanField, IntegerField, FloatField]

DEFAULT_OPTION_TYPES = [
    ("choice_label", str),
    ("value", str),
    ("selected", bool),
]

DEFAULT_OPTION_ROOT_TYPES = [
    ("help_text", str),
    ("auto_id", str),
    ("id_for_label", str),
    ("label", str),
    ("name", str),
    ("widget_type", str),
]

OPTION_BASE_MODEL = type(
    "OptionBaseModel",
    (BaseModel,),
    {"__annotations__": dict(DEFAULT_OPTION_TYPES)},
)

MODEL_CHOICE_FIELD_BASE_MODEL = type(
    "ModelChoiceFieldBaseModelAnno",
    (BaseModel,),
    {
        "__annotations__": dict(
            [*DEFAULT_OPTION_ROOT_TYPES, ("options", list[OPTION_BASE_MODEL])]
        )
    },
)

ModelChoiceFieldObjects = TypedDict(
    "ModelChoiceFieldObjects",
    {
        "fields": list[str],
        "flag": Flag,
        "annotations": dict[
            str, typing.Union[type[str], type[int], type[float], type[bool]] | UnionType
        ],
    },
)

ModelChoiceFieldOptions = TypedDict(
    "ModelChoiceFieldOptions",
    {
        "choice_label": str,
        "value": str,
        "selected": bool,
        "instance": NotRequired[dict[str, Any]],
    },
)

ModelChoiceFieldType = TypedDict(
    "ModelChoiceFieldType",
    {
        "help_text": str,
        "auto_id": str,
        "id_for_label": str,
        "label": Optional[str],
        "name": str,
        "widget_type": str,
        "options": list[ModelChoiceFieldOptions],
    },
)


@dataclass(slots=True)
class ModelChoiceFieldVariant:
    model: type[models.Model]

    def get_field_objects(self) -> ModelChoiceFieldObjects:
        resolved_field_names: list[str] = []
        resolved_flags: list[Flag] = []
        resolved_annotations: list[
            typing.Union[type[str], type[int], type[float], type[bool] | UnionType]
        ] = []
        fields = self.model._meta.get_fields()

        for field in fields:
            if any([isinstance(field, f) for f in SUPPORTED_VARIANT_FIELDS]):
                resolved_field_names.append(field.name)
                resolved_flags.append(self.field_to_flag(field))
                resolved_annotations.append(self.field_to_annotation(field))

        return {
            "fields": resolved_field_names,
            "flag": ObjectFlag(dict(zip(resolved_field_names, resolved_flags))),
            "annotations": dict(zip(resolved_field_names, resolved_annotations)),
        }

    def get_classname(self) -> str:
        return self.model.__name__

    def get_instance_values(self, model: models.Model) -> dict[str, Any]:
        field_names = self.get_field_objects()["fields"]
        resolved_fields = {}

        for field in field_names:
            resolved_fields[field] = getattr(model, field)

        return resolved_fields

    def field_to_flag(self, field) -> Flag:
        is_null: bool = field.null
        if isinstance(field, CharField):
            if is_null:
                return NullableFlag(StringFlag())
            else:
                return StringFlag()
        if isinstance(field, BooleanField):
            if is_null:
                return NullableFlag(BoolFlag())
            else:
                return BoolFlag()
        if isinstance(field, IntegerField):
            if is_null:
                return NullableFlag(IntFlag())
            else:
                return IntFlag()
        if isinstance(field, FloatField):
            if is_null:
                return NullableFlag(FloatFlag())
            else:
                return FloatFlag()
        raise Exception(
            f"The model field type {field.__class__.__name__} is not supported."
        )

    def field_to_annotation(
        self, field
    ) -> typing.Union[type[str], type[int], type[float], type[bool]] | UnionType:
        is_null: bool = field.null
        if isinstance(field, CharField):
            if is_null:
                return typing.Optional[str]
            else:
                return str
        if isinstance(field, BooleanField):
            if is_null:
                return typing.Optional[bool]
            else:
                return bool
        if isinstance(field, IntegerField):
            # TODO Handle AutoField, BigAutoField and BigIntegerField
            if is_null:
                return typing.Optional[int]
            else:
                return int
        if isinstance(field, FloatField):
            if is_null:
                return typing.Optional[float]
            else:
                return float
        raise Exception(
            f"The model field type {field.__class__.__name__} is not supported."
        )


class ModelChoiceFlagHelper:
    @staticmethod
    def field_to_dict(
        field: BoundField, variants: list[ModelChoiceFieldVariant]
    ) -> ModelChoiceFieldType:
        return {
            "help_text": str(field.help_text),
            "auto_id": field.auto_id,
            "id_for_label": field.id_for_label,
            "label": field.label,  # type:ignore
            "name": field.name,
            "widget_type": field.widget_type,
            "options": [
                ModelChoiceFlagHelper.widget_to_options(opt, variants=variants)
                for opt in field.subwidgets
            ],
        }

    @staticmethod
    def widget_to_options(
        option: BoundWidget, variants: list[ModelChoiceFieldVariant]
    ) -> ModelChoiceFieldOptions:
        base_option: ModelChoiceFieldOptions = {
            "choice_label": option.choice_label,
            "value": str(option.data["value"]),
            "selected": option.data["selected"],
        }

        if variants:
            bound_instance = option.data["value"].instance

            assert isinstance(bound_instance, models.Model)

            variant = None
            for v in variants:
                if isinstance(bound_instance, v.model):
                    variant = v

            if variant:
                base_option["instance"] = variant.get_instance_values(bound_instance)

        return base_option

    @staticmethod
    def object_annotation(variants: list[ModelChoiceFieldVariant]):
        """Annotations for the ModelChoiceField field"""

        variant_annotations = []

        if variants:
            for variant in variants:
                instance_root = [*DEFAULT_OPTION_ROOT_TYPES]
                option_with_instance = [*DEFAULT_OPTION_TYPES]
                option_with_instance.append(
                    (
                        "instance",
                        type(
                            variant.get_classname() + "InstanceBaseModel",
                            (BaseModel,),
                            {
                                "__annotations__": variant.get_field_objects()[
                                    "annotations"
                                ]
                            },
                        ),
                    )
                )
                instance_root.append(
                    (
                        "options",
                        list[
                            type(
                                variant.get_classname() + "BaseModel",
                                (BaseModel,),
                                {"__annotations__": dict(option_with_instance)},
                            )
                        ],
                    )
                )

                variant_annotations.append(
                    type(
                        variant.get_classname() + "VariantBaseModel",
                        (BaseModel,),
                        {"__annotations__": dict(instance_root)},
                    )  # type:ignore
                )

        if variant_annotations:
            return typing.Union[*variant_annotations]  # type:ignore
        else:
            return MODEL_CHOICE_FIELD_BASE_MODEL

    @staticmethod
    def object_flag(variants: list[ModelChoiceFieldVariant] | None = None) -> Flag:
        """A Flag analogue for the ModelChoiceField field"""

        # The default option when no variants exist
        resolved_option: Flag = ObjectFlag(
            {
                "choice_label": StringFlag(),
                "value": StringFlag(),
                "selected": BoolFlag(),
            }
        )

        if variants:
            options: list[tuple[str, Flag]] = [
                (
                    variant.get_classname(),
                    ObjectFlag(
                        {
                            "choice_label": StringFlag(),
                            "value": StringFlag(),
                            "selected": BoolFlag(),
                            "instance": variant.get_field_objects()["flag"],
                        }
                    ),
                )
                for variant in variants
            ]

            resolved_option = CustomTypeFlag(options)

        return ObjectFlag(
            {
                "help_text": StringFlag(),
                "auto_id": StringFlag(),
                "id_for_label": StringFlag(),
                "label": NullableFlag(StringFlag()),
                "name": StringFlag(),
                "widget_type": StringFlag(),
                "options": ListFlag(resolved_option),
            }
        )

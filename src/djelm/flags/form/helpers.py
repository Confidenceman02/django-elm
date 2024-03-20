from typing import Optional
from typing_extensions import TypedDict

from django.forms.boundfield import BoundField

from djelm.flags.primitives import (
    BoolFlag,
    Flag,
    ListFlag,
    NullableFlag,
    ObjectFlag,
    StringFlag,
)


ModelChoiceFieldOptions = TypedDict(
    "ModelChoiceFieldOptions", {"choice_label": str, "value": str, "selected": bool}
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


class ModelChoiceFlagHelper:
    @staticmethod
    def field_to_dict(field: BoundField) -> ModelChoiceFieldType:
        return {
            "help_text": str(field.help_text),
            "auto_id": field.auto_id,
            "id_for_label": field.id_for_label,
            "label": field.label,  # type:ignore
            "name": field.name,
            "widget_type": field.widget_type,
            "options": [
                {
                    "choice_label": opt.choice_label,
                    "value": str(opt.data["value"]),
                    "selected": opt.data["selected"],
                }
                for opt in field.subwidgets
            ],
        }

    @staticmethod
    def object_flag() -> Flag:
        return ObjectFlag(
            {
                "help_text": StringFlag(),
                "auto_id": StringFlag(),
                "id_for_label": StringFlag(),
                "label": NullableFlag(StringFlag()),
                "name": StringFlag(),
                "widget_type": StringFlag(),
                "options": ListFlag(
                    ObjectFlag(
                        {
                            "choice_label": StringFlag(),
                            "value": StringFlag(),
                            "selected": BoolFlag(),
                        }
                    )
                ),
            }
        )

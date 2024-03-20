from typing_extensions import Any
from django.forms.boundfield import BoundField
from django.forms.models import ModelChoiceField
from pydantic import ValidationError

from djelm.flags.form.helpers import ModelChoiceFlagHelper


def model_choice_serializer(field: Any):
    """
    Serialize a BoundField to a structure pydantic can validate.
    """
    try:
        assert isinstance(field, BoundField) and isinstance(
            field.field, ModelChoiceField
        )
    except Exception as err:
        raise ValidationError(err)

    return ModelChoiceFlagHelper.field_to_dict(field)

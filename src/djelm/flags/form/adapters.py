from typing_extensions import Annotated

from pydantic import BaseModel, PlainValidator
from pydantic.functional_validators import BeforeValidator
from pydantic.type_adapter import TypeAdapter

from djelm.flags.form.serializer import model_choice_serializer


class ModelChoiceFieldOptionsAnno(BaseModel):
    choice_label: str
    value: str
    selected: bool


class ModelChoiceFieldModel(BaseModel):
    help_text: str
    auto_id: str
    id_for_label: str
    label: str
    name: str
    widget_type: str
    options: list[ModelChoiceFieldOptionsAnno]


annotated_model_choice_field = Annotated[
    ModelChoiceFieldModel,
    BeforeValidator(model_choice_serializer),
    PlainValidator(model_choice_serializer),
]

ModelChoiceFieldAdapter = TypeAdapter(
    annotated_model_choice_field  # type:ignore
)

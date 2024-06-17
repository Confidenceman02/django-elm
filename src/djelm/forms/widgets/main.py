import typing

from djelm.flags.form.primitives import ModelChoiceFieldFlag
from djelm.flags.primitives import Flag

WIDGET_NAMES_T = typing.Union[
    typing.Literal["ModelChoiceField"], typing.Literal["ModelMultipleChoiceField"]
]


WIDGET_NAMES: list[WIDGET_NAMES_T] = [
    "ModelChoiceField",
    "ModelMultipleChoiceField",
]

WIDGET_NAME_TO_DEFAULT_FLAG: dict[WIDGET_NAMES_T, type[Flag]] = {
    "ModelChoiceField": ModelChoiceFieldFlag,
    "ModelMultipleChoiceField": ModelChoiceFieldFlag,
}

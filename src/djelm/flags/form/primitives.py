from dataclasses import dataclass
from typing import Annotated
from djelm.flags.form.helpers import ModelChoiceFlagHelper
from djelm.flags.primitives import Flag
from djelm.flags.form.adapters import annotated_model_choice_field


@dataclass(slots=True)
class ModelChoiceFieldFlag(Flag):
    def anno(self) -> Annotated:
        return annotated_model_choice_field

    def obj(self) -> Flag:
        return ModelChoiceFlagHelper.object_flag()

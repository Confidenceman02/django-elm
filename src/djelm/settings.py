from dataclasses import dataclass, field
from typing import Dict, Self, TypedDict, Union

Name = TypedDict("Name", {"name": str})
SingleTon = TypedDict("SingleTon", {"singleton": bool})


@dataclass(slots=True)
class ProgramSettings:
    _settings: Dict = field(default_factory=lambda: {"name": None, "singleton": False})

    def with_setting(self, setting: Union[Name, SingleTon]) -> Self:
        self._settings = self._settings | setting
        return self

    def get_settings(self) -> dict:
        return self._settings

from dataclasses import dataclass


@dataclass(slots=True)
class ModuleName:
    names: list[str]

from dataclasses import dataclass


class Pattern:
    pass


@dataclass(slots=True)
class VarPattern(Pattern):
    value: str

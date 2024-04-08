from dataclasses import dataclass


@dataclass(slots=True)
class Range:
    row: int
    column: int

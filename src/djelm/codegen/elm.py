from dataclasses import dataclass

from .annotation import Annotation


class Variant:
    def __init__(self, name: str, annotations: list[Annotation] | None = None) -> None:
        self.name = name
        self.annotations = annotations


def variant(name: str) -> Variant:
    return Variant(name)


def variantWith(name: str, annotations: list[Annotation]) -> Variant:
    return Variant(name, annotations)


@dataclass(slots=True)
class CustomType:
    name: str
    variants: list[Variant]

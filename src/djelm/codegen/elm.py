from dataclasses import dataclass

import djelm.codegen.compiler as Compiler


class Variant:
    def __init__(
        self, name: str, annotations: list[Compiler.Annotation] | None = None
    ) -> None:
        self.name = name
        self.annotations = annotations


def variant(name: str) -> Variant:
    return Variant(name)


def variantWith(name: str, annotations: list[Compiler.Annotation]) -> Variant:
    return Variant(name, annotations)


def alias(name: str, annotation: Compiler.Annotation):
    return Compiler.Declaration(name, Compiler.Alias(annotation))


@dataclass(slots=True)
class CustomType:
    name: str
    variants: list[Variant]

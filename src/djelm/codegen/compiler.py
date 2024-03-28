from dataclasses import dataclass
from typing import List


class TypeAnnotation:
    pass


class DeclarationKind:
    pass


class Declaration:
    def __init__(self, name: str, kind: DeclarationKind) -> None:
        self.name = name
        self.kind = kind


@dataclass(slots=True)
class Typed(TypeAnnotation):
    def __init__(self, name: str, args: List[TypeAnnotation]) -> None:
        self.name: str = name
        self.args: List[TypeAnnotation] = args


class Annotation:
    def __init__(
        self,
        annotation: TypeAnnotation,
        aliases: dict[str, TypeAnnotation],
    ) -> None:
        self.annotation = annotation
        self.aliases: dict[str, TypeAnnotation] = aliases


class Variant:
    def __init__(self, name: str, annotations: list[Annotation]) -> None:
        self.name = name
        self.annotations = annotations


@dataclass(slots=True)
class Record(TypeAnnotation):
    def __init__(self, fields: List[tuple[str, Annotation]]) -> None:
        self.fields = fields


@dataclass(slots=True)
class AliasDeclaration(DeclarationKind):
    name: str
    anno: Annotation


@dataclass(slots=True)
class CustomTypeDeclaration(DeclarationKind):
    name: str
    variants: list[Variant]


def get_declaration_name(declaration: Declaration) -> str:
    match declaration.kind:
        case AliasDeclaration(name=name, anno=_):
            return name
        case CustomTypeDeclaration(name=name, variants=_):
            return name
        case _:
            raise Exception("I don't recognise that declaration type")

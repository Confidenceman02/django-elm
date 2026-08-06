from abc import ABC, abstractmethod
from dataclasses import dataclass

import djelm.codegen.range as Range


class TypeAnnotation:
    pass


class Expression(ABC):
    @abstractmethod
    def annotation_type(self) -> TypeAnnotation | None:
        pass

    @abstractmethod
    def set_range(self, rng: Range.Range) -> None:
        pass

    def set_range_column(self, start: int) -> None:
        pass

    @abstractmethod
    def get_range(self) -> Range.Range:
        pass


class DeclarationKind:
    pass


@dataclass(slots=True)
class Signature:
    name: str
    type_annotation: TypeAnnotation


class Declaration:
    def __init__(self, name: str, kind: DeclarationKind) -> None:
        self.name = name
        self.kind = kind


@dataclass(slots=True)
class Typed(TypeAnnotation):
    name: str
    args: list[TypeAnnotation]


@dataclass(slots=True)
class Generic(TypeAnnotation):
    value: str


@dataclass(slots=True)
class Unit(TypeAnnotation):
    pass


@dataclass(slots=True)
class Annotation:
    annotation: TypeAnnotation
    aliases: dict[str, TypeAnnotation]


@dataclass(slots=True)
class Variant:
    name: str
    annotations: list[Annotation]


@dataclass(slots=True)
class Record(TypeAnnotation):
    fields: list[tuple[str, Annotation]]


@dataclass(slots=True)
class AliasDeclaration(DeclarationKind):
    name: str
    generics: list[str]
    anno: Annotation


@dataclass(slots=True)
class CustomTypeDeclaration(DeclarationKind):
    name: str
    generics: list[str]
    variants: list[Variant]


@dataclass(slots=True)
class FunctionDeclaration(DeclarationKind):
    name: str
    expression: Expression
    signature: Signature


def get_declaration_name(declaration: Declaration) -> str:
    match declaration.kind:
        case AliasDeclaration(name=name, anno=_):
            return name
        case CustomTypeDeclaration(name=name, variants=_):
            return name
        case _:
            raise Exception("I don't recognise that declaration type")

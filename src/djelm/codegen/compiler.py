from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
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
    def __init__(self, name: str, args: List[TypeAnnotation]) -> None:
        self.name: str = name
        self.args: List[TypeAnnotation] = args


@dataclass(slots=True)
class Generic(TypeAnnotation):
    def __init__(self, value: str) -> None:
        self.value: str = value


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

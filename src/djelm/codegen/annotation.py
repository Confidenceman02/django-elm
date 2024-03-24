from dataclasses import dataclass
import functools
from typing import List, Protocol
import djelm.codegen.format as Format


def foldl(func, acc, xs):
    return functools.reduce(func, xs, acc)


class TypeAnnotation:
    pass


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


@dataclass(slots=True)
class Record(TypeAnnotation):
    def __init__(self, fields: List[tuple[str, Annotation]]) -> None:
        self.fields = fields


def getAliases(anno: Annotation) -> dict[str, TypeAnnotation]:
    return anno.aliases


def mergeAliases(
    x: dict[str, TypeAnnotation], anno: Annotation
) -> dict[str, TypeAnnotation]:
    z = x.copy()
    z.update(getAliases(anno))
    return z


def toAliasKey(k: str) -> str:
    return f"{k[0].upper()}{k[1:]}"


def addAlias(
    name: str, target: Annotation, alias_cache: dict[str, TypeAnnotation]
) -> dict[str, TypeAnnotation]:
    aliasKey: str = toAliasKey(name)
    alias_cache.update({f"{aliasKey}": target.annotation})
    return alias_cache


def typed(name: str, args: List[Annotation]) -> Annotation:
    args_anno: List[TypeAnnotation] = []
    for arg in args:
        args_anno.append(arg.annotation)

    return Annotation(
        Typed(name, args_anno),
        foldl(mergeAliases, {}, args),
    )


class SupportsRecord(Protocol):
    fields: List[tuple[str, Annotation]]


def string():
    """Elm String annotation"""
    return typed("String", [])


def int():
    """Elm Int annotation"""
    return typed("Int", [])


def float():
    """Elm Float annotation"""
    return typed("Float", [])


def bool() -> Annotation:
    """Elm Bool annotation"""
    return typed("Bool", [])


def maybe(anno: Annotation):
    """Elm Maybe annotation"""
    return typed("Maybe", [anno])


def list(anno: Annotation):
    """Elm List annotation"""
    return typed("List", [anno])


def alias(name: str, anno: Annotation):
    """Elm alias annotation"""
    return Annotation(Typed(Format.alias_type(name), []), addAlias(name, anno, {}))


def record(fields: List[tuple[str, Annotation]]) -> Annotation:
    """Elm Dict annotation"""
    return Annotation(
        Record(fields),
        foldl(lambda acc, field: mergeAliases(acc, field[1]), {}, fields),
    )


def writeTypeAnnotation(anno: TypeAnnotation) -> str:
    match anno:
        case Typed(name=name, args=args):
            anno_names = []
            for arg in args:
                anno_names.append(writeTypeAnnotation(arg))
            return " ".join([name, *anno_names])
        case Record(fields=fields):
            return "Record fields"
        case _:
            raise Exception("Can't handle that type of annotation")


def toString(anno: Annotation) -> str:
    return writeTypeAnnotation(anno.annotation)

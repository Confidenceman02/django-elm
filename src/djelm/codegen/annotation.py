from typing import List
import djelm.codegen.compiler as Compiler
import djelm.codegen.writer as Writer
import djelm.codegen.format as Format
from djelm.codegen.utils import foldl


def getAliases(anno: Compiler.Annotation) -> dict[str, Compiler.TypeAnnotation]:
    return anno.aliases


def mergeAliases(
    x: dict[str, Compiler.TypeAnnotation], anno: Compiler.Annotation
) -> dict[str, Compiler.TypeAnnotation]:
    z = x.copy()
    z.update(getAliases(anno))
    return z


def toAliasKey(k: str) -> str:
    return f"{k[0].upper()}{k[1:]}"


def addAlias(
    name: str,
    target: Compiler.Annotation,
    alias_cache: dict[str, Compiler.TypeAnnotation],
) -> dict[str, Compiler.TypeAnnotation]:
    aliasKey: str = toAliasKey(name)
    alias_cache.update({f"{aliasKey}": target.annotation})
    return alias_cache


def typed(name: str, args: List[Compiler.Annotation]) -> Compiler.Annotation:
    args_anno: List[Compiler.TypeAnnotation] = []
    for arg in args:
        args_anno.append(arg.annotation)

    return Compiler.Annotation(
        Compiler.Typed(name, args_anno),
        foldl(mergeAliases, {}, args),
    )


def string():
    """Elm String annotation"""
    return typed("String", [])


def int():
    """Elm Int annotation"""
    return typed("Int", [])


def float():
    """Elm Float annotation"""
    return typed("Float", [])


def bool() -> Compiler.Annotation:
    """Elm Bool annotation"""
    return typed("Bool", [])


def maybe(anno: Compiler.Annotation):
    """Elm Maybe annotation"""
    return typed("Maybe", [anno])


def list(anno: Compiler.Annotation):
    """Elm List annotation"""
    return typed("List", [anno])


def alias(name: str, anno: Compiler.Annotation):
    """Elm alias annotation"""
    return Compiler.Annotation(
        Compiler.Typed(Format.alias_type(name), []), addAlias(name, anno, {})
    )


def record(fields: List[tuple[str, Compiler.Annotation]]) -> Compiler.Annotation:
    """Elm Dict annotation"""
    return Compiler.Annotation(
        Compiler.Record(fields),
        foldl(lambda acc, field: mergeAliases(acc, field[1]), {}, fields),
    )


def toString(anno: Compiler.Annotation) -> str:
    return Writer.writeTypeAnnotation(anno.annotation).write()

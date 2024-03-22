from dataclasses import dataclass
from typing import List

import djelm.codegen.compiler as Compiler
import djelm.codegen.format as Format
import djelm.codegen.expression as Expression
import djelm.codegen.module_name as Mod
import djelm.codegen.range as Range


def variantWith(name: str, annotations: List[Compiler.Annotation]) -> Compiler.Variant:
    return Compiler.Variant(Format.safe_capitalize(name), annotations)


def variant(name: str) -> Compiler.Variant:
    return variantWith(name, [])


def alias(name: str, annotation: Compiler.Annotation) -> Compiler.Declaration:
    return Compiler.Declaration(
        name, Compiler.AliasDeclaration(Format.alias_type(name), annotation)
    )


def customType(name: str, variants: List[Compiler.Variant]) -> Compiler.Declaration:
    return Compiler.Declaration(
        name, Compiler.CustomTypeDeclaration(Format.alias_type(name), variants)
    )


def value(
    name: str,
    rng: Range.Range | None = None,
    annotation: Compiler.Annotation | None = None,
) -> Compiler.Expression:
    return Expression.FunctionOrValue(Mod.ModuleName([]), name, rng, annotation)


def apply(
    fnExp: Compiler.Expression,
    argExp: List[Compiler.Expression],
    rng: Range.Range | None = None,
) -> Compiler.Expression:
    return Expression.Application([fnExp, *argExp], fnExp.annotation_type(), rng)


def list(members: List[Compiler.Expression]) -> Compiler.Expression:
    return Expression.List(members, None)


def literal(value: str) -> Compiler.Expression:
    return Expression.Literal(value, None)


def declaration(
    name: str, expression: Compiler.Expression, signature: Compiler.Signature
) -> Compiler.Declaration:
    """Top level declaration"""
    expression.set_range_column(4)
    return Compiler.Declaration(
        name,
        Compiler.FunctionDeclaration(
            name,
            expression,
            signature,
        ),
    )


def int(value: int, rng: Range.Range | None = None) -> Compiler.Expression:
    return Expression.Int(value, rng)


@dataclass(slots=True)
class CustomType:
    name: str
    variants: List[Compiler.Variant]

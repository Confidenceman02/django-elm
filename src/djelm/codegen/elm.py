from dataclasses import dataclass
import builtins

import djelm.codegen.compiler as Compiler
import djelm.codegen.expression as Expression
import djelm.codegen.format as Format
import djelm.codegen.module_name as Mod
import djelm.codegen.range as Range


def variantWith(
    name: str, annotations: builtins.list[Compiler.Annotation]
) -> Compiler.Variant:
    return Compiler.Variant(Format.safe_capitalize(name), annotations)


def variant(name: str) -> Compiler.Variant:
    return variantWith(name, [])


def alias(name: str, annotation: Compiler.Annotation) -> Compiler.Declaration:
    return aliasWith(name, [], annotation)


def aliasWith(
    name: str, generics: builtins.list[str], annotation: Compiler.Annotation
) -> Compiler.Declaration:
    return Compiler.Declaration(
        name, Compiler.AliasDeclaration(Format.alias_type(name), generics, annotation)
    )


def customType(
    name: str, variants: builtins.list[Compiler.Variant]
) -> Compiler.Declaration:
    return customTypeWith(name, [], variants)


def customTypeWith(
    name: str, generics: builtins.list[str], variants: list[Compiler.Variant]
) -> Compiler.Declaration:
    return Compiler.Declaration(
        name,
        Compiler.CustomTypeDeclaration(Format.alias_type(name), generics, variants),
    )


def value(
    name: str,
    rng: Range.Range | None = None,
    annotation: Compiler.Annotation | None = None,
) -> Compiler.Expression:
    return Expression.FunctionOrValue(Mod.ModuleName([]), name, rng, annotation)


def apply(
    fnExp: Compiler.Expression,
    argExp: builtins.list[Compiler.Expression],
    rng: Range.Range | None = None,
) -> Compiler.Expression:
    return Expression.Application([fnExp, *argExp], fnExp.annotation_type(), rng)


def list(members: builtins.list[Compiler.Expression]) -> Compiler.Expression:
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
    variants: builtins.list[Compiler.Variant]

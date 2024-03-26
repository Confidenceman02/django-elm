from dataclasses import dataclass

import djelm.codegen.compiler as Compiler
import djelm.codegen.format as Format


def variantWith(name: str, annotations: list[Compiler.Annotation]) -> Compiler.Variant:
    return Compiler.Variant(name, annotations)


def variant(name: str) -> Compiler.Variant:
    return variantWith(name, [])


def alias(name: str, annotation: Compiler.Annotation) -> Compiler.Declaration:
    return Compiler.Declaration(
        name, Compiler.AliasDeclaration(Format.alias_type(name), annotation)
    )


def customType(name: str, variants: list[Compiler.Variant]) -> Compiler.Declaration:
    return Compiler.Declaration(
        name, Compiler.CustomTypeDeclaration(Format.alias_type(name), variants)
    )


@dataclass(slots=True)
class CustomType:
    name: str
    variants: list[Compiler.Variant]

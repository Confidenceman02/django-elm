from dataclasses import dataclass
from typing import List, Protocol
import djelm.codegen.compiler as Compiler


class Writer(Protocol):
    def write(self, indent: int = 0) -> str:
        ...

    def writeIndented(self, indent: int = 0) -> str:
        if indent == 0:
            return ""
        repeated = " "

        for _ in range(indent):
            repeated += " "
        return repeated


@dataclass(slots=True)
class Spaced(Writer):
    items: List[Writer]

    def write(self, indent: int = 0) -> str:
        return " ".join([w.write(indent) for w in self.items])


@dataclass(slots=True)
class String(Writer):
    val: str

    def write(self, indent: int = 0) -> str:
        return self.val


@dataclass(slots=True)
class Paren(Writer):
    writer: Writer

    def write(self, indent: int = 0) -> str:
        return f"({self.writer.write()})"


@dataclass(slots=True)
class Sep(Writer):
    new_line: bool
    separators: tuple[str, str, str]
    items: List[Writer]

    def write(self, indent: int = 0) -> str:
        pre, sep, post = self.separators

        post = self.writeIndented(indent) + post

        if self.new_line:
            post = "\n" + post
            separator = "\n" + self.writeIndented(indent) + sep
        else:
            separator = sep

        return f"{pre}{separator.join([w.write() for w in self.items])}{post}"


@dataclass(slots=True)
class Breaked(Writer):
    writers: List[Writer]

    def write(self, indent: int = 0) -> str:
        return "\n".join([w.write() for w in self.writers])


@dataclass(slots=True)
class Indent(Writer):
    indent: int
    writer: Writer

    def write(self, indent: int = 0) -> str:
        return f"{self.writeIndented(self.indent)}{self.writer.write(self.indent)}"


def string(val: str) -> Writer:
    return String(val)


def spaced(items: List[Writer]) -> Writer:
    return Spaced(items)


def paren(writer: Writer) -> Writer:
    return Paren(writer)


def breaked(writers: List[Writer]) -> Writer:
    return Breaked(writers)


def indent(indent: int, writer: Writer) -> Writer:
    return Indent(indent, writer)


def multiFieldRecord(new_line: bool, items: List[Writer]) -> Writer:
    return Sep(new_line, ("{ ", ", ", "}"), items)


def bracesComma(new_line: bool, items: List[Writer]) -> Writer:
    return Sep(new_line, ("{", ", ", "}"), items)


def sepBy(separators: tuple[str, str, str], newlines: bool, writers: list[Writer]):
    return Sep(newlines, separators, writers)


def parensIfContainsSpaces(writer: Writer) -> Writer:
    if " " in writer.write():
        return paren(writer)
    else:
        return writer


def writeTypeAnnotation(anno: Compiler.TypeAnnotation) -> Writer:
    match anno:
        case Compiler.Typed(name=name, args=args):
            spaced_writer = Spaced(
                [
                    string(name),
                    *[parensIfContainsSpaces(writeTypeAnnotation(w)) for w in args],
                ]
            )

            return spaced_writer

        case Compiler.Record(fields=fields):
            writer_fields = []
            for field in fields:
                writer_fields.append(
                    spaced(
                        [
                            string(field[0]),
                            string(":"),
                            writeTypeAnnotation(field[1].annotation),
                        ]
                    )
                )
            if 1 < len(writer_fields):
                return multiFieldRecord(True, writer_fields)
            else:
                return bracesComma(False, writer_fields)

        case _:
            raise Exception("Can't handle that type of annotation")


def writeVariantConstructors(variant: Compiler.Variant) -> Writer:
    writers: list[Writer] = [string(variant.name)]
    writers.extend(
        [
            parensIfContainsSpaces(writeTypeAnnotation(v.annotation))
            for v in variant.annotations
        ]
    )
    return spaced(writers)


def writeDeclartion(declaration: Compiler.Declaration) -> Writer:
    match declaration.kind:
        case Compiler.AliasDeclaration(name=name, anno=anno):
            return breaked(
                [
                    spaced(
                        [
                            string("type"),
                            string("alias"),
                            string(name),
                            string("="),
                        ]
                    ),
                    indent(3, writeTypeAnnotation(anno.annotation)),
                ]
            )
        case Compiler.CustomTypeDeclaration(name=name, variants=variants):
            return breaked(
                [
                    spaced([string("type"), string(name)]),
                    indent(
                        3,
                        sepBy(
                            ("= ", "| ", ""),
                            True,
                            [writeVariantConstructors(v) for v in variants],
                        ),
                    ),
                ]
            )
        case _:
            raise Exception("Cant handle that type of annotation")

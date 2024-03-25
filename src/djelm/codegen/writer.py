from dataclasses import dataclass
from typing import List, Protocol
import djelm.codegen.compiler as Compiler


class Writer(Protocol):
    def write(self) -> str:
        ...

    def writeIndented(self, indent: int = 0) -> str:
        repeated = " "

        for _ in range(indent):
            repeated += " "
        return repeated


@dataclass(slots=True)
class Spaced(Writer):
    items: List[Writer]

    def write(self) -> str:
        return " ".join([w.write() for w in self.items])


@dataclass(slots=True)
class String(Writer):
    val: str

    def write(self) -> str:
        return self.val


@dataclass(slots=True)
class Paren(Writer):
    writer: Writer

    def write(self) -> str:
        return f"({self.writer.write()})"


@dataclass(slots=True)
class Sep(Writer):
    new_line: bool
    separators: tuple[str, str, str]
    items: List[Writer]

    def write(self, indent: int = 0) -> str:
        pre, sep, post = self.separators

        if self.new_line:
            separator = "\n" + self.writeIndented(indent) + sep
        else:
            separator = sep

        return f"{pre}{separator.join([w.write() for w in self.items])}{post}"


def string(val: str) -> Writer:
    return String(val)


def spaced(items: List[Writer]) -> Writer:
    return Spaced(items)


def paren(writer: Writer) -> Writer:
    return Paren(writer)


def multiFieldRecord(new_line: bool, items: List[Writer]) -> Writer:
    return Sep(new_line, ("{ ", "\n, ", "\n}"), items)


def bracesComma(new_line: bool, items: List[Writer]) -> Writer:
    return Sep(new_line, ("{ ", ", ", " }"), items)


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
                return multiFieldRecord(False, writer_fields)
            else:
                return bracesComma(False, writer_fields)

        case _:
            raise Exception("Can't handle that type of annotation")


def writeDeclartion(declaration: Compiler.Declaration) -> Writer:
    pass

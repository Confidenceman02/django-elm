from dataclasses import dataclass
from typing import List

import djelm.codegen.writer as Writer


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


def writeRecordField(anno: List[tuple[str, Annotation]]) -> Writer.Writer:
    return Writer.spaced([])


def parensIfContainsSpaces(writer: Writer.Writer) -> Writer.Writer:
    if " " in writer.write():
        return Writer.paren(writer)
    else:
        return writer


def writeTypeAnnotation(anno: TypeAnnotation) -> Writer.Writer:
    match anno:
        case Typed(name=name, args=args):
            spaced_writer = Writer.Spaced(
                [
                    Writer.string(name),
                    *[parensIfContainsSpaces(writeTypeAnnotation(w)) for w in args],
                ]
            )

            return spaced_writer

        case Record(fields=fields):
            writer_fields = []
            for field in fields:
                writer_fields.append(
                    Writer.spaced(
                        [
                            Writer.string(field[0]),
                            Writer.string(":"),
                            writeTypeAnnotation(field[1].annotation),
                        ]
                    )
                )

            return Writer.bracesComma(False, writer_fields)
        case _:
            raise Exception("Can't handle that type of annotation")

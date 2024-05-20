from dataclasses import dataclass
from typing import List, Protocol
import djelm.codegen.compiler as Compiler
import djelm.codegen.expression as Exp
import djelm.codegen.module_name as Mod
from djelm.codegen.pattern import Pattern, VarPattern


class Writer(Protocol):
    def write(self, indent: int = 0) -> str: ...

    def writeIndented(self, indent: int = 0) -> str:
        if indent == 0:
            return ""
        repeated = ""

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
class Literal(Writer):
    val: str

    def write(self, indent: int = 0) -> str:
        return f'"{ self.val }"'


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

        if post != "":
            post = self.writeIndented(indent) + post

        if self.new_line:
            post = "\n" + post
            separator = "\n" + self.writeIndented(indent) + sep
        else:
            separator = sep

        return f"{pre}{separator.join([w.write() for w in self.items])}{post}"


@dataclass(slots=True)
class SepInline(Writer):
    separators: tuple[str, str, str]
    items: List[Writer]

    def write(self, indent: int = 0) -> str:
        pre, sep, post = self.separators

        return f"{pre}{sep.join([w.write() for w in self.items])}{post}"


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


@dataclass(slots=True)
class Joined(Writer):
    writer: List[Writer]

    def write(self, indent: int = 0) -> str:
        return "".join([w.write() for w in self.writer])


def string(val: str) -> Writer:
    return String(val)


def literal(val: str) -> Writer:
    return Literal(val)


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


def bracketsComma(new_line: bool, items: List[Writer]) -> Writer:
    return Sep(new_line, ("[", ", ", "]"), items)


def singleRecordField(items: List[Writer]) -> Writer:
    return SepInline(("{ ", ", ", " }"), items)


def sepBy(separators: tuple[str, str, str], newlines: bool, writers: list[Writer]):
    return Sep(newlines, separators, writers)


def join(writers: list[Writer]):
    return Joined(writers)


def epsilon():
    return string("")


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

        case Compiler.Generic(value=value):
            return string(value)

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
                return singleRecordField(writer_fields)

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


def writeModuleName(module: Mod.ModuleName) -> Writer:
    return string(".".join(module.names))


def writePattern(pattern: Pattern) -> Writer:
    match pattern:
        case VarPattern(value=v):
            return string(v)
        case _:
            raise Exception("Cant handle that type of pattern")


def writeExpression(expression: Compiler.Expression) -> Writer:
    match expression:
        case (
            Exp.OperatorApplication(
                symbol=symbol,
                infix_direction=direction,
                left=left,
                right=right,
                range=_,
            ) as op
        ):
            op_range = op.get_range()
            right_range = right.get_range()
            left_range = left.get_range()
            break_right = 0 < right_range.row
            break_left = 0 < left_range.row

            if break_right:
                right_writer = indent(
                    4 + op_range.column,
                    spaced(
                        [
                            string(symbol),
                            writeExpression(right),
                        ]
                    ),
                )
            else:
                right_writer = spaced(
                    [
                        string(symbol),
                        writeExpression(right),
                    ]
                )

            if break_left:
                left_writer = indent(4 + op_range.column, writeExpression(left))
            else:
                left_writer = writeExpression(left)

            match direction:
                case "Left":
                    if break_right or break_left:
                        return breaked(
                            [
                                left_writer,
                                right_writer,
                            ]
                        )
                    else:
                        return spaced(
                            [
                                writeExpression(left),
                                string(symbol),
                                writeExpression(right),
                            ]
                        )

                case "Right":
                    return spaced(
                        [
                            writeExpression(left),
                            writeExpression(right),
                            string(symbol),
                        ]
                    )
                case "Non":
                    return spaced(
                        [
                            writeExpression(left),
                            string(symbol),
                            writeExpression(right),
                        ]
                    )
        case Exp.FunctionOrValue(moduleName=module, name=name):
            match module.names:
                case []:
                    return string(name)
                case _:
                    return join([writeModuleName(module), string("."), string(name)])
        case Exp.Int(value=v, range=name):
            return string(str(v))
        case Exp.Literal(value=v, range=name):
            return literal(v)
        case Exp.Application(expressions=exp):
            match exp:
                case []:
                    return epsilon()
                case [x]:
                    return writeExpression(x)
                case [x, *x_rest]:
                    return spaced(
                        [
                            writeExpression(x),
                            sepBy(
                                ("", " ", ""),
                                False,
                                [writeExpression(ex) for ex in x_rest],
                            ),
                        ]
                    )
                case _:
                    raise Exception("Can't handle that type of espression")

        case Exp.Parenthesized(expression=e):
            return paren(writeExpression(e))

        case Exp.List(members=members, range=_):
            return bracketsComma(False, [writeExpression(m) for m in members])
        case Exp.Lambda(args=args, expression=ex):
            return spaced(
                [
                    join([string("\\"), spaced([writePattern(pat) for pat in args])]),
                    string("->"),
                    writeExpression(ex),
                ]
            )
        case Exp.IfBlock(condition=cond, then_case=then, else_case=els):
            return spaced(
                [
                    string("if"),
                    writeExpression(cond),
                    string("then"),
                    writeExpression(then),
                    string("else"),
                    writeExpression(els),
                ]
            )

        case _:
            raise Exception("Can't handle that expression type")


def writeDeclartion(declaration: Compiler.Declaration) -> Writer:
    """Writer for top level declarations"""
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
                    indent(4, writeTypeAnnotation(anno.annotation)),
                ]
            )
        case Compiler.CustomTypeDeclaration(name=name, variants=variants):
            return breaked(
                [
                    spaced([string("type"), string(name)]),
                    indent(
                        4,
                        # TODO rstrip string to remove trailing spaces
                        sepBy(
                            ("= ", "| ", ""),
                            True,
                            [writeVariantConstructors(v) for v in variants],
                        ),
                    ),
                ]
            )
        case Compiler.FunctionDeclaration(name=name, signature=sig, expression=exp):
            return breaked(
                [
                    writeSignature(sig),
                    spaced(
                        [
                            string(name),
                            string("="),
                        ]
                    ),
                    indent(4, writeExpression(exp)),
                ]
            )
        case _:
            raise Exception("Cant handle that type of annotation")


def writeSignature(sig: Compiler.Signature) -> Writer:
    return spaced(
        [string(sig.name), string(":"), writeTypeAnnotation(sig.type_annotation)]
    )

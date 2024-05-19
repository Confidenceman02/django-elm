from dataclasses import dataclass
import typing as Typ
import djelm.codegen.module_name as Mod
from djelm.codegen.pattern import Pattern
import djelm.codegen.range as Range
import djelm.codegen.compiler as Compiler


@dataclass(slots=True)
class OperatorApplication(Compiler.Expression):
    """Operators are constructed bottom up or right to left"""

    symbol: str
    infix_direction: Typ.Literal["Left"] | Typ.Literal["Right"] | Typ.Literal["Non"]
    left: Compiler.Expression
    right: Compiler.Expression
    range: Range.Range | None

    def annotation_type(self) -> Compiler.TypeAnnotation | None:
        return None

    def set_range(self, rng: Range.Range) -> None:
        self.range = rng
        self.left.set_range(rng)

    def set_range_column(self, start: int) -> None:
        """
        Set the start column for an operator application

        This trickles in to the left hand side of the operator and allows
        for correct indentation when lines are "breaked"

        e.g.
                someFunc =
                    hello
                        |> world
                    ^   ^
                    |   |
                    |   start column + indentation
                    start column

        """
        new_range = self.get_range()
        new_range.column = start
        self.range = new_range
        self.left.set_range_column(start)

    def get_range(self) -> Range.Range:
        return self.range or Range.Range(0, 0)


@dataclass(slots=True)
class FunctionOrValue(Compiler.Expression):
    moduleName: Mod.ModuleName
    name: str
    range: Range.Range | None
    annotation: Compiler.Annotation | None

    def annotation_type(self) -> Compiler.TypeAnnotation | None:
        if self.annotation:
            return self.annotation.annotation
        else:
            return None

    def set_range(self, rng: Range.Range) -> None:
        self.range = rng

    def set_range_column(self, start: int) -> None:
        new_range = self.get_range()
        new_range.column = start
        self.range = new_range

    def get_range(self) -> Range.Range:
        return self.range or Range.Range(0, 0)


@dataclass(slots=True)
class Int(Compiler.Expression):
    value: int
    range: Range.Range | None

    def annotation_type(self) -> Compiler.TypeAnnotation | None:
        return Compiler.Typed("Int", [])

    def set_range(self, rng: Range.Range) -> None:
        self.range = rng

    def set_range_column(self, start: int) -> None:
        new_range = self.get_range()
        new_range.column = start
        self.range = new_range

    def get_range(self) -> Range.Range:
        return self.range or Range.Range(0, 0)


@dataclass(slots=True)
class List(Compiler.Expression):
    members: list[Compiler.Expression]
    range: Range.Range | None

    def annotation_type(self) -> Compiler.TypeAnnotation | None:
        match self.members:
            case []:
                return Compiler.Typed("List", [Compiler.Generic("a")])
            case [head, _]:
                head_anno: Compiler.TypeAnnotation | None = head.annotation_type()
                if head_anno:
                    return Compiler.Typed("List", [head_anno])
                else:
                    return Compiler.Typed("List", [Compiler.Generic("a")])
            case _:
                return None

    def set_range(self, rng: Range.Range) -> None:
        self.range = rng

    def set_range_column(self, start: int) -> None:
        new_range = self.get_range()
        new_range.column = start
        self.range = new_range

    def get_range(self) -> Range.Range:
        return self.range or Range.Range(0, 0)


@dataclass(slots=True)
class Literal(Compiler.Expression):
    value: str
    range: Range.Range | None

    def annotation_type(self) -> Compiler.TypeAnnotation | None:
        return Compiler.Typed("String", [])

    def set_range(self, rng: Range.Range) -> None:
        self.range = rng

    def set_range_column(self, start: int) -> None:
        new_range = self.get_range()
        new_range.column = start
        self.range = new_range

    def get_range(self) -> Range.Range:
        return self.range or Range.Range(0, 0)


@dataclass(slots=True)
class Application(Compiler.Expression):
    expressions: list[Compiler.Expression]
    annotation: Compiler.TypeAnnotation | None
    range: Range.Range | None

    def annotation_type(self) -> Compiler.TypeAnnotation | None:
        return None

    def set_range(self, rng: Range.Range) -> None:
        self.range = rng

    def set_range_column(self, start: int) -> None:
        new_range = self.get_range()
        new_range.column = start
        self.range = new_range

    def get_range(self) -> Range.Range:
        return self.range or Range.Range(0, 0)


@dataclass(slots=True)
class Parenthesized(Compiler.Expression):
    expression: Compiler.Expression
    range: Range.Range | None

    def annotation_type(self) -> Compiler.TypeAnnotation | None:
        return None

    def set_range(self, rng: Range.Range) -> None:
        self.range = rng

    def set_range_column(self, start: int) -> None:
        new_range = self.get_range()
        new_range.column = start
        self.range = new_range

    def get_range(self) -> Range.Range:
        return self.range or Range.Range(0, 0)


@dataclass(slots=True)
class Lambda(Compiler.Expression):
    args: list[Pattern]
    expression: Compiler.Expression

    def annotation_type(self) -> Compiler.TypeAnnotation | None:
        return None

    def set_range(self, rng: Range.Range) -> None:
        self.range = rng

    def set_range_column(self, start: int) -> None:
        new_range = self.get_range()
        new_range.column = start
        self.range = new_range

    def get_range(self) -> Range.Range:
        return self.range or Range.Range(0, 0)


@dataclass(slots=True)
class IfBlock(Compiler.Expression):
    condition: Compiler.Expression
    then_case: Compiler.Expression
    else_case: Compiler.Expression

    def annotation_type(self) -> Compiler.TypeAnnotation | None:
        return None

    def set_range(self, rng: Range.Range) -> None:
        self.range = rng

    def set_range_column(self, start: int) -> None:
        new_range = self.get_range()
        new_range.column = start
        self.range = new_range

    def get_range(self) -> Range.Range:
        return self.range or Range.Range(0, 0)

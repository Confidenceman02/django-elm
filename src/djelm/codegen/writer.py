from dataclasses import dataclass
from typing import List, Protocol


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

    def write(self, indent: int = 0) -> str:
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


def bracesComma(new_line: bool, items: List[Writer]) -> Writer:
    return Sep(new_line, ("{", ",", "}"), items)

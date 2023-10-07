from typing import Literal, TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')


@dataclass(slots=True)
class ExitSuccess(Generic[T]):
    value: T = None
    tag: Literal["Success"] = "Success"

    def __init__(self, v: T):
        self.value = v


@dataclass(slots=True)
class ExitFailure(Generic[T, E]):
    err: E
    meta: T
    tag: Literal["Failure"] = "Failure"

    def __init__(self, meta: T, err: E):
        self.meta = meta
        self.err = err

from typing import Literal, TypeVar, Generic

T = TypeVar('T')
E = TypeVar('E')


class ExitSuccess(Generic[T]):
    _tag: Literal["Success"] = "Success"
    value: T = None

    def __init__(self, v: T):
        self.value = v


class ExitFailure(Generic[T, E]):
    _tag: Literal["Failure"] = "Failure"
    err: E
    meta: T

    def __init__(self, meta: T, err: E):
        self.meta = meta
        self.err = err

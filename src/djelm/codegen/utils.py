import functools


def foldl(func, acc, xs):
    return functools.reduce(func, xs, acc)

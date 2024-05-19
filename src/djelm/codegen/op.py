from typing import Iterator
import djelm.codegen.expression as Exp
import djelm.codegen.compiler as Compiler


def equals(
    left: Compiler.Expression, right: Compiler.Expression
) -> Compiler.Expression:
    return Exp.OperatorApplication("==", "Left", left, right, None)


def plus(left: Compiler.Expression, right: Compiler.Expression) -> Compiler.Expression:
    return Exp.OperatorApplication("+", "Left", left, right, None)


def pipe(right: Compiler.Expression, left: Compiler.Expression) -> Compiler.Expression:
    """Construct a pipe operator"""
    return Exp.OperatorApplication("|>", "Left", left, right, None)


def pipes(
    top_pipe: Compiler.Expression, other_pipes: Iterator[Compiler.Expression]
) -> Compiler.Expression:
    """
    Supply an iterator of expressions to build a pipe expression bottom to top

    top_pipe = Should be the top most pipe in the chain.
    e.g.
            Decode.succeed Something
            ^   |> required "something" Decode.string
            |
            top_pipe

    other_pipes = The pipe tree will be constructed bottom to top so the iterator should reflect
                  that order
    e.g.
            pipes(top_pipe, iter[1, 2, 3])

            ==
                top_pipe
                   |> 3
                   |> 2
                   |> 1
    """
    try:
        right_pipe = next(other_pipes)
    except StopIteration:
        return top_pipe

    return pipe(right=right_pipe, left=pipes(top_pipe, other_pipes))

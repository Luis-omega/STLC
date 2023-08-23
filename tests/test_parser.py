from typing import Optional, TypeVar, Callable

from STLC.Parser.Lexer import Token, lexer

from STLC.Parser.Parser import Parser, expression

from STLC.Parser.AST import Function, Variable, IntLiteral, Application

import pytest

T = TypeVar("T")


def make_positive_test(stream: str, parser: Parser[T], expected: T) -> None:
    lexed = lexer(stream)
    assert isinstance(lexed, list)
    result = parser(lexed)
    assert isinstance(result, tuple)
    _, value = result
    assert value == expected


@pytest.mark.parametrize(
    "stream,parser,expected",
    [
        ("(a b)", expression, Application(Variable("a"), Variable("b"))),
        ("\\ x -> 2", expression, Function(Variable("x"), IntLiteral(2))),
        (
            "\\ y -> (z @)",
            expression,
            Function(Variable("y"), Application(Variable("z"), IntLiteral(4))),
        ),
    ],
)
def test_function(stream, parser, expected):
    make_positive_test(stream, parser, expected)

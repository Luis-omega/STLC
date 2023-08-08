from typing import Optional, TypeVar, Callable

from STLC.Parser.Lexer import (
    TokenVariable,
    variable,
    TokenInt,
    int_,
    Operator,
    operator,
)

import pytest

T = TypeVar("T")


def make_positive_test(
    stream: str,
    lexer_function: Callable[[str], Optional[tuple[str, T]]],
    expected: T,
) -> None:
    lexed = lexer_function(stream)
    assert isinstance(lexed, tuple)
    _, value = lexed
    assert value == expected


def make_negative_test(
    stream: str, lexer_function: Callable[[str], Optional[tuple[str, T]]]
) -> None:
    lexed = lexer_function(stream)
    assert lexed is None


@pytest.mark.parametrize(
    "stream,expected",
    [
        ("_", TokenVariable("_")),
        ("_a", TokenVariable("_a")),
        ("a", TokenVariable("a")),
        ("abdcd434", TokenVariable("abdcd")),
        ("ab_dcd434", TokenVariable("ab")),
    ],
)
def test_variable_positive(stream: str, expected: TokenVariable):
    make_positive_test(stream, variable, expected)


@pytest.mark.parametrize(
    "stream",
    [
        "",
        "=",
        "2",
        "2123",
        "-2334",
    ],
)
def test_variable_negative(stream: str):
    make_negative_test(stream, variable)


@pytest.mark.parametrize(
    "stream,expected",
    [
        ("0", TokenInt(0)),
        ("1", TokenInt(1)),
        ("190", TokenInt(190)),
        ("-1", TokenInt(-1)),
        ("-923_", TokenInt(-923)),
        ("-924asf", TokenInt(-924)),
    ],
)
def test_int_positive(stream: str, expected: TokenInt):
    make_positive_test(stream, int_, expected)


@pytest.mark.parametrize(
    "stream",
    [
        "",
        "=",
        "-",
        "asd",
        "--23",
    ],
)
def test_int_negative(stream: str):
    make_negative_test(stream, int_)


@pytest.mark.parametrize(
    "stream,expected",
    [
        ("+", Operator("+")),
        ("-", Operator("-")),
        ("*", Operator("*")),
        ("/", Operator("/")),
        ("<=", Operator("<=")),
        (">=", Operator(">=")),
        ("<", Operator("<")),
        (">", Operator(">")),
        ("==", Operator("==")),
        ("&", Operator("&")),
        ("|", Operator("|")),
        ("~", Operator("~")),
    ],
)
def test_operator_positive(stream: str, expected: Operator):
    make_positive_test(stream, operator, expected)


@pytest.mark.parametrize(
    "stream",
    [
        "",
        "=",
        "asd",
    ],
)
def test_operator_negative(stream: str):
    make_negative_test(stream, operator)

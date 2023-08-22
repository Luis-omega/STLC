from typing import Optional, Callable, TypeVar, Type
from dataclasses import dataclass

from STLC.Parser.Lexer import Token
import STLC.Parser.Lexer as Lexer
from STLC.Parser.AST import (
    Variable,
    BoolLiteral,
    IntLiteral,
    UnitLiteral,
    Expression,
    Application,
    Function,
)

T = TypeVar("T")
T2 = TypeVar("T2")


@dataclass
class ParserError:
    msg: str


Parser = Callable[[list[Token]], Optional[tuple[list[Token], T]]]
ParserResult = Optional[tuple[list[Token], T]]


def bind(parser: Parser[T], transform: Callable[[T], Parser[T2]]) -> Parser[T2]:
    def new_parser(l1: list[Token]) -> Optional[tuple[list[Token], T2]]:
        result1 = parser(l1)
        if result1 is None:
            return None
        else:
            (l2, value1) = result1
            parser2 = transform(value1)
            return parser2(l2)

    return new_parser


def pure(element: T) -> Parser[T]:
    return lambda l: (l, element)


def variable(l: list[Token]) -> ParserResult[Variable]:
    match l:
        case [Lexer.TokenVariable(name=name), *remain]:
            return (remain, Variable(name))
        case _:
            return None


def boolLiteral(l: list[Token]) -> ParserResult[BoolLiteral]:
    match l:
        case [Lexer.TokenBool(value=value), *remain]:
            return (remain, BoolLiteral(value))
        case _:
            return None


def intLiteral(l: list[Token]) -> ParserResult[IntLiteral]:
    match l:
        case [Lexer.TokenInt(value=value), *remain]:
            return (remain, IntLiteral(value))
        case _:
            return None


def unitLiteral(l: list[Token]) -> ParserResult[UnitLiteral]:
    match l:
        case [Lexer.TokenUnit(), *remain]:
            return (remain, UnitLiteral())
        case _:
            return None


def constantLexer2Ast(cls: Type[T]) -> Parser[T]:
    def new_parser(l: list[Token]) -> ParserResult[T]:
        if len(l) >= 1:
            if isinstance(l[0], cls):
                return (l[1:], l[0])
            else:
                return None
        else:
            return None

    return new_parser


lparen: Parser[Lexer.LParen] = constantLexer2Ast(Lexer.LParen)
rparen: Parser[Lexer.RParen] = constantLexer2Ast(Lexer.RParen)
lambdaStar: Parser[Lexer.LambdaStart] = constantLexer2Ast(Lexer.LambdaStart)
arrow: Parser[Lexer.Arrow] = constantLexer2Ast(Lexer.Arrow)

application: Parser[Application] = bind(
    lparen,
    lambda _: bind(
        expression,
        lambda e1: bind(
            expression,
            lambda e2: bind(rparen, lambda _: pure(Application(e1, e2))),
        ),
    ),
)

function: Parser[Function] = bind(
    lambdaStar,
    lambda _: bind(
        variable,
        lambda arg: bind(
            arrow,
            lambda _: bind(expression, lambda exp: pure(Function(arg, exp))),
        ),
    ),
)


def make_expression_parser() -> Parser[Expression]:
    parser_list: list[Parser[Expression]] = [
        variable,
        boolLiteral,
        intLiteral,
        unitLiteral,
        application,
        function,
    ]

    def new_parser(l: list[Token]) -> ParserResult[Expression]:
        for parser in parser_list:
            r = parser(l)
            if r is not None:
                return r
        return None

    return new_parser


expression: Parser[Expression] = make_expression_parser()

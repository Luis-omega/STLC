from typing import Optional, Callable, TypeVar, Type, Union
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
    If,
)

T = TypeVar("T")
T2 = TypeVar("T2")


@dataclass
class ParserError:
    msg: str


ParserResult = Union[ParserError, tuple[list[Token], T]]
Parser = Callable[[list[Token]], ParserResult[T]]


def bind(parser: Parser[T], transform: Callable[[T], Parser[T2]]) -> Parser[T2]:
    def new_parser(l1: list[Token]) -> ParserResult[T2]:
        result1 = parser(l1)
        if isinstance(result1, ParserError):
            return result1
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
            return ParserError("Can't parse a variable")


def boolLiteral(l: list[Token]) -> ParserResult[BoolLiteral]:
    match l:
        case [Lexer.TokenBool(value=value), *remain]:
            return (remain, BoolLiteral(value))
        case _:
            return ParserError("Can't parse a boolean")


def intLiteral(l: list[Token]) -> ParserResult[IntLiteral]:
    match l:
        case [Lexer.TokenInt(value=value), *remain]:
            return (remain, IntLiteral(value))
        case _:
            return ParserError("Can't parse int")


def unitLiteral(l: list[Token]) -> ParserResult[UnitLiteral]:
    match l:
        case [Lexer.TokenUnit(), *remain]:
            return (remain, UnitLiteral())
        case _:
            return ParserError("Can't parse unit")


def constantLexer2Ast(cls: Type[T]) -> Parser[T]:
    def new_parser(l: list[Token]) -> ParserResult[T]:
        if len(l) >= 1:
            if isinstance(l[0], cls):
                return (l[1:], l[0])
            else:
                return ParserError("Can't parse a " + str(cls.__name__))
        else:
            return ParserError("Can't parse a " + str(cls.__name__))

    return new_parser


lparen: Parser[Lexer.LParen] = constantLexer2Ast(Lexer.LParen)
rparen: Parser[Lexer.RParen] = constantLexer2Ast(Lexer.RParen)
lambdaStar: Parser[Lexer.LambdaStart] = constantLexer2Ast(Lexer.LambdaStart)
arrow: Parser[Lexer.Arrow] = constantLexer2Ast(Lexer.Arrow)
if_lexer: Parser[Lexer.if_] = constantLexer2Ast(Lexer.If)
then: Parser[Lexer.then] = constantLexer2Ast(Lexer.Then)
else_: Parser[Lexer.else_] = constantLexer2Ast(Lexer.Else)

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

if_: Parser[If] = bind(
    if_lexer,
    lambda _: bind(
        expression,
        lambda predicate: bind(
            then,
            lambda _: bind(
                expression,
                lambda expression1: bind(
                    else_,
                    lambda _: bind(
                        expression,
                        lambda expression2: pure(
                            If(predicate, expression1, expression2)
                        ),
                    ),
                ),
            ),
        ),
    ),
)


def make_literal() -> Parser[Union[BoolLiteral, IntLiteral, UnitLiteral]]:
    parser_list = [boolLiteral, intLiteral, unitLiteral]

    def new_parser(
        l: list[Token],
    ) -> ParserResult[Union[BoolLiteral, IntLiteral, UnitLiteral]]:
        for parser in parser_list:
            maybe_result = parser(l)
            if not isinstance(maybe_result, ParserError):
                return maybe_result
        return ParserError("Can't parse a literal")

    return new_parser


literal = make_literal()


def expression(l: list[Token]) -> ParserResult[Expression]:
    match l:
        case [Lexer.LParen(), *_]:
            return expression_paren(l)
        case [Lexer.LambdaStart(), *_]:
            return function(l)
        case [Lexer.If(), *_]:
            return if_(l)
        case [Lexer.TokenError(msg=msg), *_]:
            return ParserError("Can't recognize symbol: " + msg)
        case _:
            maybe_variable = variable(l)
            if isinstance(maybe_variable, ParserError):
                maybe_literal = literal(l)
                if isinstance(maybe_literal, ParserError):
                    return ParserError("Can't parse a expression")
                else:
                    return maybe_literal
            else:
                return maybe_variable


def expression_paren(l: list[Token]) -> ParserResult[Expression]:
    return application(l)

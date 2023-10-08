from dataclasses import dataclass
from typing import Union

from STLC.Range import HasRange

Literal = Union["BoolLiteral", "IntLiteral", "UnitLiteral"]
Expression = Union[
    "Variable",
    "Literal",
    "Application",
    "OperatorApplication",
    "Function",
    "If",
    "Annotation",
]
Type = Union["BoolType", "IntType", "UnitType", "Arrow"]


@dataclass
class Variable(HasRange):
    name: str

    def pretty(self) -> str:
        return self.name


@dataclass
class BoolLiteral(HasRange):
    value: bool

    def pretty(self) -> str:
        return str(self.value)


@dataclass
class IntLiteral(HasRange):
    value: int

    def pretty(self) -> str:
        return str(self.value)


@dataclass
class UnitLiteral(HasRange):
    def pretty(self) -> str:
        return "unit"


@dataclass
class Application(HasRange):
    left: Expression
    right: Expression

    def pretty(self) -> str:
        if (
            isinstance(self.right, Function)
            or isinstance(self.right, If)
            or isinstance(self.right, Application)
        ):
            return f"{self.left.pretty()} ({self.right.pretty()})"
        return f"{self.left.pretty()} {self.right.pretty()}"


@dataclass
class OperatorApplication(HasRange):
    left: Expression
    right: Expression
    operator: str

    def pretty(self) -> str:
        return f"({self.left.pretty()} {self.operator} {self.right.pretty()})"


@dataclass
class Function(HasRange):
    argument: Variable
    expression: Expression

    def pretty(self) -> str:
        return f"\\ {self.argument.pretty()} -> {self.expression.pretty()}"


@dataclass
class If(HasRange):
    condition: Expression
    true_expression: Expression
    false_expression: Expression

    def pretty(self) -> str:
        return f"if {self.condition.pretty()} then {self.true_expression.pretty()} else {self.false_expression.pretty()}"


@dataclass
class Annotation(HasRange):
    expression: Expression
    annotation: Type

    def pretty(self) -> str:
        return f"({self.expression.pretty()} : {self.annotation.pretty()})"


@dataclass
class BoolType(HasRange):
    def pretty(self) -> str:
        return "Bool"


@dataclass
class IntType(HasRange):
    def pretty(self) -> str:
        return "Int"


@dataclass
class UnitType(HasRange):
    def pretty(self) -> str:
        return "Unit"


@dataclass
class Arrow(HasRange):
    left: Type
    right: Type

    def pretty(self) -> str:
        if isinstance(self.left, Arrow):
            return f"({self.left.pretty()}) -> {self.right.pretty()}"
        return f"{self.left.pretty()} -> {self.right.pretty()}"


@dataclass
class Definition(HasRange):
    name: str
    arguments: list[str]
    expression: Expression

    def pretty(self) -> str:
        arguments = " ".join(self.arguments)
        return f"{self.name} {arguments} = {self.expression.pretty()};"


@dataclass
class Declaration(HasRange):
    name: str
    _type: Type

    def pretty(self) -> str:
        return f"{self.name} : {self._type.pretty()};"

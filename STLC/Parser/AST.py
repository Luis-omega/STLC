from dataclasses import dataclass
from typing import Union

Literal = Union["BoolLiteral" | "IntLiteral" | "UnitLiteral"]
Expression = Union[
    "Variable" | "Literal" | "Application" | "Function" | "If" | "Annotation"
]
Type = Union["BoolType" | "IntType" | "UnitType" | "Arrow"]


@dataclass
class Variable:
    name: str


@dataclass
class BoolLiteral:
    value: bool


@dataclass
class IntLiteral:
    value: int


@dataclass
class UnitLiteral:
    pass


@dataclass
class Application:
    left: Expression
    right: Expression


@dataclass
class Function:
    argument: str
    expression: Expression


@dataclass
class If:
    condition: Expression
    true_expression: Expression
    false_expression: Expression


@dataclass
class Annotation:
    expression: Expression
    annotation: Type


@dataclass
class BoolType:
    pass


@dataclass
class IntType:
    pass


@dataclass
class UnitType:
    pass


@dataclass
class Arrow:
    left: Type
    right: Type


@dataclass
class Definition:
    name: str
    expression: Expression


@dataclass
class Declaration:
    name: str
    expression: Expression

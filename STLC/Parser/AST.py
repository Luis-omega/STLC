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

    def free_variables(self) -> list["Variable"]:
        return [self]

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.name == other.name


@dataclass
class BoolLiteral(HasRange):
    value: bool

    def pretty(self) -> str:
        return str(self.value)

    def free_variables(self) -> list["Variable"]:
        return []


@dataclass
class IntLiteral(HasRange):
    value: int

    def pretty(self) -> str:
        return str(self.value)

    def free_variables(self) -> list["Variable"]:
        return []


@dataclass
class UnitLiteral(HasRange):
    def pretty(self) -> str:
        return "unit"

    def free_variables(self) -> list["Variable"]:
        return []


def union(vars1: list[Variable], vars2: list[Variable]) -> list[Variable]:
    new_list = vars2.copy()
    for var in vars1:
        if var not in vars2:
            new_list.append(var)
    return new_list


def diference(vars1: list[Variable], vars2: list[Variable]) -> list[Variable]:
    return [i for i in vars1 if i not in vars2]


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

    def free_variables(self) -> list[Variable]:
        return union(self.left.free_variables(), self.right.free_variables())


@dataclass
class OperatorApplication(HasRange):
    left: Expression
    right: Expression
    operator: str

    def pretty(self) -> str:
        return f"({self.left.pretty()} {self.operator} {self.right.pretty()})"

    def free_variables(self) -> list[Variable]:
        return union(self.left.free_variables(), self.right.free_variables())


@dataclass
class Function(HasRange):
    argument: Variable
    expression: Expression

    def pretty(self) -> str:
        return f"\\ {self.argument.pretty()} -> {self.expression.pretty()}"

    def free_variables(self) -> list[Variable]:
        return diference(
            self.expression.free_variables(), self.argument.free_variables()
        )


@dataclass
class If(HasRange):
    condition: Expression
    true_expression: Expression
    false_expression: Expression

    def pretty(self) -> str:
        return f"if {self.condition.pretty()} then {self.true_expression.pretty()} else {self.false_expression.pretty()}"

    def free_variables(self) -> list[Variable]:
        return union(
            union(
                self.condition.free_variables(),
                self.true_expression.free_variables(),
            ),
            self.false_expression.free_variables(),
        )


@dataclass
class Annotation(HasRange):
    expression: Expression
    annotation: Type

    def pretty(self) -> str:
        return f"({self.expression.pretty()} : {self.annotation.pretty()})"

    def free_variables(self) -> list[Variable]:
        return self.expression.free_variables()


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
    arguments: list[Variable]
    expression: Expression

    def pretty(self) -> str:
        arguments = " ".join((i.name for i in self.arguments))
        return f"{self.name} {arguments} = {self.expression.pretty()};"

    def free_variables(self) -> list[Variable]:
        return diference(self.expression.free_variables(), self.arguments)


@dataclass
class Declaration(HasRange):
    name: str
    _type: Type

    def pretty(self) -> str:
        return f"{self.name} : {self._type.pretty()};"

from typing import Union, TypeVar, Generic, reveal_type, Literal
from dataclasses import dataclass

from STLC.Parser.AST import (
    Definition,
    Declaration,
    Variable,
    Expression,
    BoolLiteral,
    IntLiteral,
    UnitLiteral,
    Application,
    OperatorApplication,
    Function,
    If,
    Annotation,
)

from STLC.Range import Range

T = TypeVar("T")


parserResult = list[Definition | Declaration]

Definitions = dict[str, Definition]
Declarations = dict[str, Declaration]


def range2Report(r: Range) -> str:
    return f"""At line {r.line_start}, column {r.column_start}."""


@dataclass
class DeclarationNotFollowedByDefinition:
    declaration: Declaration

    def pretty(self) -> str:
        return f"""Declaration of "{self.declaration.name}" is not followed by it's definition, every declaration must be followed of it's  declaration.\n{range2Report(self.declaration._range)}."""


@dataclass
class DefinitionWithoutDeclaration:
    definition: Definition

    def pretty(self) -> str:
        return f"""Definition of "{self.definition.name}" must be preceded of it's declaration.\n{range2Report(self.definition._range)}."""


@dataclass
class MultipleDefinition:
    definitions: list[Definition]

    def pretty(self) -> str:
        places = "\n".join([range2Report(i._range) for i in self.definitions])
        return f"""Multiple definitions for "{self.definitions[0].name}" found.\n{places}"""


@dataclass
class MultipleDeclaration:
    declarations: list[Declaration]

    def pretty(self) -> str:
        places = "\n".join([range2Report(i._range) for i in self.declarations])
        return f"""Multiple declarations for "{self.declarations[0].name}" found.\n{places}"""


@dataclass
class UseOfUndefinedVariable:
    variable: Variable
    definition: Definition

    def pretty(self) -> str:
        return f"""Use of the undefined variable "{self.variable.name}" {range2Report(self.variable._range)} in declaration of "{self.definition.name}" {range2Report(self.definition._range)}"""


@dataclass
class Shadowing:
    variable: Variable
    place: list[Definition] | Variable

    def pretty(self) -> str:
        if isinstance(self.place, Variable):
            msg = "Bound " + range2Report(self.place._range)
        else:
            msg = "Defined " + "\n".join(
                [range2Report(i._range) for i in self.place]
            )
        return f"""The variable "{self.variable.name}" {range2Report(self.variable._range)} is shadowing the previous introduction of the variable: \n{msg}"""


def declaration_and_variable_are_together(
    statements: parserResult,
) -> (
    list[DeclarationNotFollowedByDefinition | DefinitionWithoutDeclaration]
    | None
):
    errors: list[
        DeclarationNotFollowedByDefinition | DefinitionWithoutDeclaration
    ] = []

    while statements:
        maybe_declaration = statements[0]
        if isinstance(maybe_declaration, Declaration):
            statements = statements[1:]
            if statements:
                maybe_definition = statements[0]
                if isinstance(maybe_definition, Definition):
                    if maybe_definition.name != maybe_declaration.name:
                        errors.append(
                            DeclarationNotFollowedByDefinition(
                                maybe_declaration
                            )
                        )
                        errors.append(
                            DefinitionWithoutDeclaration(maybe_definition)
                        )
                    statements = statements[1:]
                else:
                    errors.append(
                        DeclarationNotFollowedByDefinition(maybe_declaration)
                    )
            else:
                errors.append(
                    DeclarationNotFollowedByDefinition(maybe_declaration)
                )
        else:
            errors.append(DefinitionWithoutDeclaration(maybe_declaration))
            statements = statements[1:]
    if errors:
        return errors
    else:
        return None


def split_definitions_and_declarations(
    statements: parserResult,
) -> tuple[dict[str, list[Definition]], dict[str, list[Declaration]]]:
    definitions: dict[str, list[Definition]] = dict()
    declarations: dict[str, list[Declaration]] = dict()

    def add_to(d: dict[str, list[T]], name: str, value: T) -> None:
        old = d.get(name, None)
        if old is None:
            d[name] = [value]
        else:
            old.append(value)

    for statement in statements:
        if isinstance(statement, Declaration):
            add_to(declarations, statement.name, statement)
        elif isinstance(statement, Definition):
            add_to(definitions, statement.name, statement)
    return (definitions, declarations)


def multiple_declarations_or_definitions(
    definitions: dict[str, list[Definition]],
    declarations: dict[str, list[Declaration]],
) -> list[MultipleDeclaration | MultipleDefinition] | None:
    errors1 = [
        MultipleDefinition(v) for k, v in definitions.items() if len(v) > 1
    ]
    errors2 = [
        MultipleDeclaration(v) for k, v in declarations.items() if len(v) > 1
    ]

    return errors1 + errors2


def no_use_of_undefined_variables(
    definitions: dict[str, list[Definition]]
) -> list[UseOfUndefinedVariable] | None:
    errors = []
    for name, defs in definitions.items():
        for definition in defs:
            free: list[Variable] = definition.free_variables()
            for var in free:
                if var.name not in definitions:
                    errors.append(UseOfUndefinedVariable(var, definition))
    if errors:
        return errors
    else:
        return None


def no_shadowing_in_expression(
    expression: Expression,
    definitions: dict[str, list[Definition]],
    bounded_variables: list[Variable],
) -> list[Shadowing]:
    match expression:
        case Variable() | BoolLiteral() | IntLiteral() | UnitLiteral():
            return []
        case Application(left=left, right=right):
            return no_shadowing_in_expression(
                left, definitions, bounded_variables
            ) + no_shadowing_in_expression(
                right, definitions, bounded_variables
            )
        case OperatorApplication(left=left, right=right):
            return no_shadowing_in_expression(
                left, definitions, bounded_variables
            ) + no_shadowing_in_expression(
                right, definitions, bounded_variables
            )
        case Function(argument=var, expression=expression):
            errors: list[Shadowing] = []
            if var.name in definitions:
                errors.append(Shadowing(var, definitions[var.name]))
            for var2 in bounded_variables:
                if var.name == var2.name:
                    errors.append(Shadowing(var, var2))
            return errors + no_shadowing_in_expression(
                expression, definitions, bounded_variables + [var]
            )
        case If(
            condition=condition,
            true_expression=true_expression,
            false_expression=false_expression,
        ):
            return (
                no_shadowing_in_expression(
                    condition, definitions, bounded_variables
                )
                + no_shadowing_in_expression(
                    true_expression, definitions, bounded_variables
                )
                + no_shadowing_in_expression(
                    false_expression, definitions, bounded_variables
                )
            )
        case Annotation(expression=expression):
            return no_shadowing_in_expression(
                expression, definitions, bounded_variables
            )


def no_shadowing_in_definition(
    definition: Definition, definitions: dict[str, list[Definition]]
) -> list[Shadowing]:
    errors: list[Shadowing] = []
    for i in range(len(definition.arguments)):
        var = definition.arguments[i]
        if var.name in definitions:
            errors.append(Shadowing(var, definitions[var.name]))
        for var2 in definition.arguments[i + 1 :]:
            if var.name == var2.name:
                errors.append(Shadowing(var, var2))
    return errors + no_shadowing_in_expression(
        definition.expression, definitions, definition.arguments
    )


def no_shadowing(
    definitions: dict[str, list[Definition]]
) -> list[Shadowing] | None:
    errors: list[Shadowing] = []
    for name, defs in definitions.items():
        for definition in defs:
            errors += no_shadowing_in_definition(definition, definitions)
    if errors:
        return errors
    else:
        return None

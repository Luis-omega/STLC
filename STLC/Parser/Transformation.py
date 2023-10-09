from lark import Transformer, v_args, Token
from STLC.Parser.AST import (
    Variable,
    BoolLiteral,
    IntLiteral,
    UnitLiteral,
    Application,
    OperatorApplication,
    Function,
    If,
    Annotation,
    BoolType,
    IntType,
    UnitType,
    Arrow,
    Definition,
    Declaration,
    Literal,
    Expression,
    Type,
)
from STLC.Range import token2Range, mergeRanges


@v_args(inline=True)
class ToAST(Transformer):
    def variable(self, token: Token) -> Variable:
        return Variable(token2Range(token), token.value)

    def expression_atom_variable(self, value: Variable) -> Variable:
        return value

    def expression_atom_int(self, token: Token) -> IntLiteral:
        return IntLiteral(token2Range(token), int(token.value))

    def expression_atom_true(self, token: Token) -> BoolLiteral:
        return BoolLiteral(token2Range(token), True)

    def expression_atom_false(self, token: Token) -> BoolLiteral:
        return BoolLiteral(token2Range(token), False)

    def expression_atom_lambda(
        self,
        _lambda: Token,
        variable: Variable,
        arrow: Token,
        expression: Expression,
    ) -> Function:
        return Function(
            mergeRanges(token2Range(_lambda), expression._range),
            variable,
            expression,
        )

    def expression_atom_if(
        self,
        _if: Token,
        expression1: Expression,
        then: Token,
        expression2: Expression,
        _else: Token,
        expression3: Expression,
    ) -> If:
        return If(
            mergeRanges(token2Range(_if), expression3._range),
            expression1,
            expression2,
            expression3,
        )

    def expression_atom_parens(
        self, lparen: Token, expression: Expression, rparen: Token
    ) -> Expression:
        return expression

    def expression_atom_annotation(
        self,
        lparen: Token,
        expression: Expression,
        colon: Token,
        _type: Type,
        rparen: Token,
    ) -> Expression:
        return Annotation(
            mergeRanges(token2Range(lparen), token2Range(rparen)),
            expression,
            _type,
        )

    def expression_application_single(
        self, expression: Expression
    ) -> Expression:
        return expression

    def expression_application(
        self, expression: Expression, *expressions: Expression
    ) -> Expression:
        current: Expression = expression
        for exp in expressions:
            current = Application(
                mergeRanges(exp._range, current._range), current, exp
            )
        return current

    def expression_operator(
        self, start: Expression, *remain: Expression | Token
    ) -> Expression:
        current: Expression = start
        for i in range(len(remain), 2):
            # we can build a list with the right type for this, but
            # it would have a runtime overhead
            op: Token = remain[i]  # type:ignore
            right: Expression = remain[i + 1]  # type:ignore
            current = OperatorApplication(
                mergeRanges(current._range, right._range),
                current,
                right,
                op.value,
            )
        return current

    def _expression_order(
        self, left: Expression, op: Token, right: Expression
    ) -> Expression:
        return OperatorApplication(
            mergeRanges(left._range, right._range), left, right, op.value
        )

    def type_arrow(self, left: Type, arrow: Token, right: Type) -> Type:
        return Arrow(mergeRanges(left._range, right._range), left, right)

    def type_parens(self, lparen: Token, _type: Type, rparen: Token) -> Type:
        return _type

    def type_bool(self, value: Token) -> BoolType:
        return BoolType(token2Range(value))

    def type_int(self, value: Token) -> IntType:
        return IntType(token2Range(value))

    def type_unit(self, value: Token) -> UnitType:
        return UnitType(token2Range(value))

    def variable_declaration(
        self, variable: Variable, colon: Token, _type: Type, semicolon: Token
    ):
        return Declaration(
            mergeRanges(variable._range, token2Range(semicolon)),
            variable.name,
            _type,
        )

    def variables(self, *other: Variable) -> list[Variable]:
        return list(other)

    def variable_definition_alone(
        self,
        variable: Variable,
        equal: Token,
        expression: Expression,
        semicolon: Token,
    ) -> Definition:
        return Definition(
            mergeRanges(variable._range, token2Range(semicolon)),
            variable.name,
            [],
            expression,
        )

    def variable_definition(
        self,
        variable: Variable,
        arguments: list[Variable],
        equal: Token,
        expression: Expression,
        semicolon: Token,
    ) -> Definition:
        return Definition(
            mergeRanges(variable._range, token2Range(semicolon)),
            variable.name,
            arguments,
            expression,
        )

    def top(
        self, *values: Definition | Declaration
    ) -> list[Definition | Declaration]:
        return list(values)

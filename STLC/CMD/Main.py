from pathlib import Path
from argparse import ArgumentParser
from pprint import pprint


from lark import Lark

from STLC.Parser.Parser import (
    load_grammar,
    parse_string,
    ParserStageError,
    LarkLoadError,
    ParserError,
)

from STLC.Parser.Transformation import ToAST

from STLC.Checker.Checks import (
    declaration_and_variable_are_together,
    split_definitions_and_declarations,
    multiple_declarations_or_definitions,
    no_use_of_undefined_variables,
    no_shadowing,
)


def from_file(symbols: list[str], path: Path) -> None:
    try:
        with open(path, "r") as f:
            content = f.read()
    except OSError:
        print("Can't open or read file: ", path)
        return None
    from_string(symbols, content)


def from_string(symbols: list[str], value: str) -> None:
    lark = load_grammar(False, symbols)
    if not isinstance(lark, Lark):
        match lark:
            case LarkLoadError(msg):
                print(msg)
            case _:
                print(lark)
        return
    parsed = parse_string(lark, value)
    if isinstance(parsed, ParserError):
        print("Error trying to parse it!")
        print(parsed.exception)
        return
    print(40 * "-", "Lark Tree", 40 * "-", "\n")
    print(parsed.pretty())
    tranformed = ToAST().transform(parsed)
    print(40 * "-", "Transformed pprint", 40 * "-", "\n")
    pprint(tranformed)
    print(40 * "-", "Transformed pretty", 40 * "-", "\n")
    for i in tranformed:
        print(i.pretty())
    print(
        40 * "-", "Declarations and variables must be together", 40 * "-", "\n"
    )
    maybe_davat_errors = declaration_and_variable_are_together(tranformed)
    if maybe_davat_errors is None:
        print("Not found")
    else:
        for i in maybe_davat_errors:
            pprint(i)

    definitions, declarations = split_definitions_and_declarations(tranformed)
    print(40 * "-", "Multiple declarations", 40 * "-", "\n")
    maybe_multiples = multiple_declarations_or_definitions(
        definitions, declarations
    )
    if maybe_multiples is None:
        print("Not found")
    else:
        for i in maybe_multiples:
            pprint(i)
    print(40 * "-", "Undefined variables", 40 * "-", "\n")
    maybe_undefined = no_use_of_undefined_variables(definitions)
    if maybe_undefined is None:
        print("Not found")
    else:
        for i in maybe_undefined:
            pprint(i)
    print(40 * "-", "Shadowing", 40 * "-", "\n")
    maybe_shadowing = no_shadowing(definitions)
    if maybe_shadowing:
        for i in maybe_shadowing:
            pprint(i)
    else:
        print("Not found")


def generate_arg_parser():
    parser = ArgumentParser(
        prog="Simple typed lambda calculus with recursion",
        description="test tool",
        epilog="End of help, have a nice day =)",
    )
    parser.add_argument(
        "-s",
        "--symbol",
        nargs=1,
        type=str,
        required=False,
        metavar="Lark_rule",
        help="The rule to apply",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-i",
        "--inline",
        nargs=1,
        type=str,
        metavar="str",
        help="The text to parse",
    )
    group.add_argument(
        "-f",
        "--file",
        nargs=1,
        type=str,
        metavar="FILE",
        help="A file to parse",
    )
    return parser.parse_args()


def main():
    args = generate_arg_parser()

    if args.symbol is not None:
        symbols = args.symbol
    else:
        symbols = ["top"]

    if args.inline is not None:
        from_string(symbols, args.inline[0])
    else:
        from_file(symbols, args.file[0])

    return 0

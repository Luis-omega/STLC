from typing import Optional
from pathlib import Path
from dataclasses import dataclass

from lark import (
    Lark,
    Tree,
    UnexpectedInput,
    Token,
)

from STLC.STLCError import STLCError


class ParserStageError(STLCError):
    pass


class LoadGrammarError:
    pass


@dataclass
class LarkLoadError:
    msg: str


@dataclass
class FileLoadError(ParserStageError):
    pass


@dataclass
class ParserError(ParserStageError):
    exception: UnexpectedInput


def load_grammar(
    debug: Optional[bool] = None, start_symbols: Optional[list[str]] = ["top"]
) -> LoadGrammarError | LarkLoadError | Lark:
    if debug is None:
        debug = False
    grammarPath = "STLC/Parser/Grammar.lark"
    if start_symbols is None:
        start_symbols = ["top"]
    try:
        with open(grammarPath, "r") as grammarFile:
            grammar = grammarFile.read()
            try:
                parser = Lark(
                    grammar,
                    start=start_symbols,
                    debug=debug,
                    cache=None,
                    propagate_positions=False,
                    maybe_placeholders=True,
                    keep_all_tokens=True,
                    parser="lalr",
                    lexer="basic",
                )
            except Exception as e:
                return LarkLoadError(str(e))
    except OSError:
        return LoadGrammarError()
    return parser


def parse_string(lark: Lark, text: str) -> ParserError | Tree[Token]:
    try:
        result = lark.parse(text)
        return result
    except UnexpectedInput as uinput:
        return ParserError(uinput)


def parse(
    path: Path, lark: Lark, debug: bool
) -> FileLoadError | ParserError | Tree[Token]:
    try:
        with open(path, "r") as file:
            content = file.read()
            maybe_tree = parse_string(lark, content)
            return maybe_tree
    except OSError:
        return FileLoadError()

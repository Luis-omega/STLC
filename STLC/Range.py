from dataclasses import dataclass
from typing import NamedTuple

from lark import Token


Range = NamedTuple(
    "Range",
    [
        ("line_start", int),
        ("line_end", int),
        ("column_start", int),
        ("column_end", int),
        ("position_start", int),
        ("position_end", int),
    ],
)


@dataclass
class HasRange:
    _range: Range


def token2Range(token: Token) -> Range:
    # type: ignore
    return Range(
        token.line,  # type: ignore
        token.end_line,  # type: ignore
        token.column,  # type: ignore
        token.end_column,  # type: ignore
        token.start_pos,  # type: ignore
        token.end_pos,  # type: ignore
    )


def mergeRanges(range1: Range, range2: Range) -> Range:
    if range1.position_start <= range2.position_start:
        if range1.position_end <= range2.position_end:
            return Range(
                range1.line_start,
                range2.line_end,
                range1.column_start,
                range2.column_end,
                range1.position_start,
                range2.position_end,
            )
        else:
            return range1
    else:
        return mergeRanges(range2, range1)

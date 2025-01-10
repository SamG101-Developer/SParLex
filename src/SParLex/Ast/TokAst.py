from __future__ import annotations
from dataclasses import dataclass

from SParLex.Lexer.Tokens import Token, TokenType
from SParLex.Ast.Ast import Ast


@dataclass
class TokAst(Ast):
    token: Token

    @staticmethod
    def dummy(token_type: TokenType, info=None, pos=-1) -> TokAst:
        # Quick way to create a token ast for a given token type.
        return TokAst(pos, Token(info or token_type.value, token_type))

from __future__ import annotations
from dataclasses import dataclass

from SParLex.Lexer.Tokens import Token, TokenType
from SParLex.Ast.Ast import Ast


@dataclass
class TokenAst(Ast):
    token: Token

    @staticmethod
    def dummy(token_type: TokenType, info=None, pos=-1) -> TokenAst:
        # Quick way to create a token ast for a given token type.
        return TokenAst(pos, Token(info or token_type.value, token_type))

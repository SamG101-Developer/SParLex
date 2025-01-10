from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Type, TYPE_CHECKING
import functools

from SParLex.Lexer.Tokens import Token, TokenType, SpecialToken
from SParLex.Parser.ParserRuleHandler import ParserRuleHandler
from SParLex.Ast import *

if TYPE_CHECKING:
    from SParLex.Parser.ParserError import ParserError, ParserErrors
    from SParLex.Utils.ErrorFormatter import ErrorFormatter


# Decorator that wraps the function in a ParserRuleHandler
def parser_rule[T](func: Callable[..., T]) -> Callable[..., ParserRuleHandler]:
    @functools.wraps(func)
    def wrapper(self, *args) -> ParserRuleHandler[T]:
        return ParserRuleHandler(self, functools.partial(func, self, *args))
    return wrapper


class Parser(ABC):
    _tokens: List[Token]
    _token_set: Type[TokenType]
    _name: str
    _index: int
    _err_fmt: ErrorFormatter
    _error: Optional[ParserErrors.SyntaxError]

    def __init__(self, token_set: Type[TokenType], tokens: List[Token], file_name: str = "", error_formatter: Optional[ErrorFormatter] = None) -> None:
        from SParLex.Parser.ParserError import ParserErrors
        from SParLex.Utils.ErrorFormatter import ErrorFormatter

        self._token_set = token_set
        self._tokens = tokens
        self._name = file_name
        self._index = 0
        self._err_fmt = error_formatter or ErrorFormatter(token_set, self._tokens, file_name)
        self._error = ParserErrors.SyntaxError()

    def current_pos(self) -> int:
        return self._index

    def current_tok(self) -> Token:
        return self._tokens[self._index]

    # ===== PARSING =====

    def parse(self) -> RootAst:
        from SParLex.Parser.ParserError import ParserError

        try:
            c0 = self.current_pos()
            p1 = self.parse_root().parse_once()
            p2 = self.parse_eof().parse_once()
            return RootAst(c0, p1, p2)

        except ParserError as e:
            e.throw(self._err_fmt)

    @parser_rule
    @abstractmethod
    def parse_root(self) -> Ast:
        ...

    @parser_rule
    def parse_eof(self) -> TokAst:
        p1 = self.parse_token(SpecialToken.EOF).parse_once()
        return p1

    # ===== TOKENS, KEYWORDS, & LEXEMES =====

    @parser_rule
    def parse_lexeme(self, lexeme: TokenType) -> TokAst:
        p1 = self.parse_token(lexeme).parse_once()
        return p1

    @parser_rule
    def parse_token(self, token_type: TokenType) -> TokAst:
        # For the "no token", instantly return a new token.
        if token_type == SpecialToken.NO_TOK:
            return TokAst(self.current_pos(), Token("", SpecialToken.NO_TOK))

        # Check if the end of the file has been reached.
        if self._index > len(self._tokens) - 1:
            new_error = f"Expected '{token_type}', got <EOF>"
            self.store_error(self.current_pos(), new_error)
            raise self._error

        # Skip newlines and whitespace for non-newline parsing, and whitespace only for new-line parsing.
        if token_type != self._token_set.newline_token():
            while self._tokens[self._index].token_type == self._token_set.newline_token() or self._tokens[self._index].token_type == self._token_set.whitespace_token():
                self._index += 1
        if token_type == self._token_set.newline_token():
            while self._tokens[self._index].token_type == self._token_set.whitespace_token():
                self._index += 1

        # Handle an incorrectly placed token.
        if self._tokens[self._index].token_type != token_type:
            if self._error.pos == self._index:
                self._error.expected_tokens.append(token_type)
                raise self._error

            new_error = f"Expected $, got '{self._tokens[self._index].token_type.name}'"
            if self.store_error(self._index, new_error):
                self._error.expected_tokens.append(token_type)
            raise self._error

        # Otherwise, the parse was successful, so return a TokenAst as the correct position.
        r = TokAst(self._index, self._tokens[self._index])
        self._index += 1
        return r

    def store_error(self, pos: int, error: str) -> bool:
        if pos > self._error.pos:
            self._error.expected_tokens.clear()
            self._error.pos = pos
            self._error.args = (error,)
            return True
        return False


__all__ = ["Parser", "parser_rule"]

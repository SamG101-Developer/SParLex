from abc import abstractmethod
from typing import List

from src.Ast.ProgramAst import ProgramAst
from src.Ast.TokenAst import TokenAst
from src.Lexer.Tokens import TokenType, Token
from src.Parser.ParserError import ParserError
from src.Parser.ParserRuleHandler import parser_rule
from src.Utils.ErrorFormatter import ErrorFormatter


class Parser:
    _tokens: List[Token]
    _index: int
    _err_fmt: ErrorFormatter
    _errors: List[ParserError]
    _pos_shift: int

    def __init__(self, tokens: List[Token], file_name: str, pos_shift: int = 0) -> None:
        self._tokens = tokens
        self._index = 0
        self._err_fmt = ErrorFormatter(self._tokens, file_name)
        self._errors = []
        self._pos_shift = pos_shift

    def current_pos(self) -> int:
        return self._index + self._pos_shift

    def current_tok(self) -> Token:
        return self._tokens[self._index]

    @parser_rule
    def parse_token(self, token_type: TokenType) -> TokenAst:
        if token_type == TokenType.NO_TOK:
            return TokenAst(self.current_pos(), Token("", TokenType.NO_TOK))

        if self._index > len(self._tokens) - 1:
            new_error = ParserError(self.current_pos(), f"Expected '{token_type}', got <EOF>")
            self._errors.append(new_error)
            raise new_error

        c1 = self.current_pos()

        while token_type != TokenType.NEWLINE and self.current_tok().token_type in [TokenType.NEWLINE, TokenType.WHITE_SPACE]:
            self._index += 1
        while token_type == TokenType.NEWLINE and self.current_tok().token_type == TokenType.WHITE_SPACE:
            self._index += 1

        if self.current_tok().token_type != token_type:
            token_print = lambda t: f"<{t.name[2:]}>" if t.name.startswith("Lx") else t.value

            if any([error.pos == self.current_pos() for error in self._errors]):
                existing_error = next(error for error in self._errors if error.pos == self.current_pos())
                existing_error.expected_tokens.add(token_print(token_type))
                raise existing_error

            else:
                new_error = ParserError(f"Expected $, got '{token_print(self.current_tok().token_type)}'")
                new_error.pos = self.current_pos()
                new_error.expected_tokens.add(token_print(token_type))
                self._errors.append(new_error)
                raise new_error

        r = TokenAst(c1, self.current_tok())
        self._index += 1
        return r

    @abstractmethod
    def parse(self) -> ProgramAst:
        ...

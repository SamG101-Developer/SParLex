from abc import ABC, abstractmethod
from typing import List

from src.Ast.ProgramAst import ProgramAst
from src.Ast.TokenAst import TokenAst
from src.Lexer.Tokens import TokenType, Token
from src.Parser.ParserError import ParserError
from src.Parser.ParserRuleHandler import parser_rule
from src.Utils.ErrorFormatter import ErrorFormatter


class Parser(ABC):
    """
    The Parser class is an abstract class that defines the interface for all the rules. Each rule is a method that
    returns an AST node. The rules are called by the "parse" method, which is the entry point for the parser. Each rule
    defined must be decorated with the "@parse_rule" decorator (see "parse_token").

    The parser keeps track of the current token index and the list of tokens. It also keeps track of the errors that
    occurred during the parsing process. The "parse_token" method is used to parse a single token, and it checks if the
    token is the expected token. If the token is not the expected token, an error is raised.

    When inheriting from the Parser class, the "parse" method must be implemented. The "parse" method is the entry point
    for the parser and should return the root AST node - a "ProgramAst" type.
    """

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
        # Return the current position in the code.
        return self._index + self._pos_shift

    def current_tok(self) -> Token:
        # Return the current token.
        return self._tokens[self._index]

    @abstractmethod
    def parse(self) -> ProgramAst:
        # The entry point for the parser. This method should return the root AST node.
        ...

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

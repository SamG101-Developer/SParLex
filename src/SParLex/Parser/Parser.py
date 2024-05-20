from abc import ABC, abstractmethod
from enum import Enum
from type_intersections import Intersection
from typing import List

from SParLex.Ast.ProgramAst import ProgramAst
from SParLex.Ast.TokenAst import TokenAst
from SParLex.Lexer.Tokens import TokenType, Token, SpecialToken
from SParLex.Parser.ParserError import ParserError
from SParLex.Parser.ParserRuleHandler import parser_rule
from SParLex.Utils.ErrorFormatter import ErrorFormatter


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
    _token_set: Intersection[type[Enum], type[TokenType]]
    _index: int
    _err_fmt: ErrorFormatter
    _errors: List[ParserError]
    _pos_shift: int

    def __init__(self, tokens: List[Token], token_set: Intersection[type[Enum], type[TokenType]], file_name: str = "FILE", pos_shift: int = 0) -> None:
        self._tokens = tokens
        self._token_set = token_set
        self._index = 0
        self._err_fmt = ErrorFormatter(self._tokens, token_set, file_name)
        self._errors = []
        self._pos_shift = pos_shift

    def current_pos(self) -> int:
        # Return the current position in the code.
        return self._index + self._pos_shift

    def current_tok(self) -> Token:
        # Return the current token.
        return self._tokens[self._index]

    def parse(self) -> ProgramAst:
        try:
            return self.parse_root().parse_once()

        except ParserError as e:
            final_error = self._errors[0]

            for current_error in self._errors:
                if current_error.pos > final_error.pos:
                    final_error = current_error

            all_expected_tokens = "['" + "' | '".join(final_error.expected_tokens).replace("\n", "\\n") + "']"
            error_message = str(final_error).replace("$", all_expected_tokens)
            error_message = self._err_fmt.error(final_error.pos, message=error_message)
            raise SystemExit(error_message) from None

    @abstractmethod
    @parser_rule
    def parse_root(self) -> ProgramAst:
        ...

    @parser_rule
    def parse_token(self, token_type: Intersection[Enum, TokenType]) -> TokenAst:
        if token_type == SpecialToken.NO_TOK:
            return TokenAst(self.current_pos(), Token("", SpecialToken.NO_TOK))

        if self._index > len(self._tokens) - 1:
            new_error = ParserError(self.current_pos(), f"Expected '{token_type}', got <EOF>")
            self._errors.append(new_error)
            raise new_error

        c1 = self.current_pos()

        while token_type != self._token_set.newline_token() and self.current_tok().token_type in [self._token_set.newline_token(), self._token_set.whitespace_token()]:
            self._index += 1
        while token_type == self._token_set.newline_token() and self.current_tok().token_type == self._token_set.whitespace_token():
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

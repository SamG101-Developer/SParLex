from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING, Tuple

from SParLex.Lexer.Tokens import TokenType

from SParLex.Parser.ParserRuleHandler import ParserRuleHandler

if TYPE_CHECKING:
    from SParLex.Parser.ParserError import ParserError
    from SParLex.Parser.Parser import Parser


class ParserAlternateRulesHandler[T](ParserRuleHandler[T]):
    __slots__ = ["_parser_rule_handlers"]
    _parser_rule_handlers: List[ParserRuleHandler]

    def __init__(self, parser: Parser) -> None:
        super().__init__(parser, None)
        self._parser_rule_handlers = []

    def add_parser_rule_handler(self, parser_rule_handler: ParserRuleHandler) -> ParserAlternateRulesHandler:
        self._parser_rule_handlers.append(parser_rule_handler)
        return self

    def parse_once(self) -> T:
        from SParLex.Parser.ParserError import ParserError

        for parser_rule_handler in self._parser_rule_handlers:
            parser_index = self._parser._index
            try:
                ast = parser_rule_handler.parse_once()
                return ast
            except ParserError:
                self._parser._index = parser_index
                continue

        self._parser.store_error(self._parser._index, "Expected one of the alternatives.")
        raise self._parser._error

    def parse_optional(self) -> Optional[T]:
        from SParLex.Parser.ParserError import ParserError

        for parser_rule_handler in self._parser_rule_handlers:
            parser_index = self._parser._index
            try:
                ast = parser_rule_handler.parse_optional()
                return ast
            except ParserError:
                self._parser._index = parser_index
                continue
        return None

    def parse_zero_or_more(self, separator: TokenType, *, propagate_error: bool = False) -> List[T] | Tuple[List[T], ParserError]:
        raise NotImplementedError()

    def parse_one_or_more(self, separator: TokenType) -> List[T] | Tuple[List[T], ParserError]:
        raise NotImplementedError()

    def parse_two_or_more(self, separator: TokenType) -> List[T]:
        raise NotImplementedError()

    def __or__(self, that) -> ParserAlternateRulesHandler:
        return self.add_parser_rule_handler(that)

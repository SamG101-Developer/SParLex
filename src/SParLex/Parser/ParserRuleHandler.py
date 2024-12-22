from __future__ import annotations
from typing import Callable, Final, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from SParLex.Lexer.Tokens import TokenType
    from SParLex.Parser.Parser import Parser
    from SParLex.Parser.ParserAlternateRulesHandler import ParserAlternateRulesHandler
    from SParLex.Parser.ParserError import ParserError


class ParserRuleHandler[T]:
    type ParserRule = Callable[[], T]
    __slots__ = ["_rule", "_parser"]

    _rule: Final[ParserRule]
    _parser: Final[Parser]

    def __init__(self, parser: Parser, rule: ParserRule) -> None:
        self._parser = parser
        self._rule = rule

    def parse_once(self) -> T:
        ast = self._rule()
        return ast

    def parse_optional(self) -> Optional[T]:
        from SParLex.Parser.ParserError import ParserError

        parser_index = self._parser._index
        try:
            ast = self._rule()
            return ast
        except ParserError:
            self._parser._index = parser_index
            return None

    def parse_zero_or_more(self, separator: TokenType, *, propagate_error: bool = False) -> List[T] | Tuple[List[T], ParserError]:
        from SParLex.Lexer.Tokens import SpecialToken
        from SParLex.Parser.ParserError import ParserError

        successful_parses, result = 0, []
        parsed_sep, error = False, None
        while True:
            try:
                # If this is the second pass, then require the separator to be parsed.
                if successful_parses > 0:
                    self._parser.parse_token(separator).parse_once()
                    parsed_sep = True

                # Try to parse the AST, and mark the most recent parse as non-separator.
                ast = self.parse_once()
                parsed_sep = False

                # Save the AST to the result list and increment the number of ASTs parsed.
                result.append(ast)
                successful_parses += 1

            except ParserError as e:
                # If the most recent parse is a separator, backtrack it because there is no following AST.
                if parsed_sep:
                    self._parser._index -= 1 * (separator != SpecialToken.NO_TOK)

                # Save the error and break the loop.
                error = e
                break

        # Return the result, and the with the error if it is to be propagated.
        return result if not propagate_error else (result, error)

    def parse_one_or_more(self, separator: TokenType) -> List[T]:
        result = self.parse_zero_or_more(separator, propagate_error=True)
        if len(result[0]) < 1:
            raise result[1]
        return result[0]

    def parse_two_or_more(self, separator: TokenType) -> List[T]:
        result = self.parse_zero_or_more(separator, propagate_error=True)
        if len(result[0]) < 2:
            raise result[1]
        return result[0]

    def __or__[U](self, that: ParserRuleHandler[U]) -> ParserAlternateRulesHandler[T | U]:
        from SParLex.Parser.ParserAlternateRulesHandler import ParserAlternateRulesHandler
        return ParserAlternateRulesHandler(self._parser).add_parser_rule_handler(self).add_parser_rule_handler(that)


__all__ = ["ParserRuleHandler"]

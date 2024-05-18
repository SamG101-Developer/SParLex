from __future__ import annotations
from typing import Callable, List, Optional
import functools

from SParLex.Lexer.Tokens import TokenType
from SParLex.Parser.Parser import Parser
from SParLex.Parser.ParserError import ParserError
from SParLex.Ast.Ast import Ast


class ParserRuleHandler[T]:
    """
    The ParserRuleHandler class is used to handle the parsing of a rule. It is used to parse a rule once, zero or once,
    zero or more times, or one or more times. The result of the parsing is stored in the "_result" attribute. The
    "_rule" attribute is a function that returns the AST node.

    This class also implements the "__or__" operator, allowing for a alternate rule to be defined. The "__or__" operator
    is used to create a ParserAlternateRulesHandler object, which is used to parse one of the alternate rules. For a
    rule to be combined into an alternate rule, the "for_alt" method must be called on the rule, to prevent bugs.
    """

    ParserRule = Callable[[], T]

    _rule: ParserRule
    _parser: Parser
    _for_alternate: bool
    _result: Optional[T]

    def __init__(self, parser: Parser, rule: ParserRule) -> None:
        self._parser = parser
        self._rule = rule
        self._for_alternate = False
        self._result = None

    def parse_once(self) -> T:
        self._result = self._rule()
        return self._result

    def parse_optional(self, save=True) -> Optional[T]:
        parser_index = self._parser._index
        try:
            ast = self._rule()
            if save: self._result = ast
            return ast
        except ParserError:
            self._parser._index = parser_index
            return None

    def parse_zero_or_more(self, sep: TokenType = TokenType.NO_TOK) -> List[T]:
        self._result = []
        while ast := self.parse_optional(save=False):
            self._result.append(ast)
            sep_ast = self._parser.parse_token(sep).parse_optional()
            if not sep_ast: break
        return self._result

    def parse_one_or_more(self, sep: TokenType = TokenType.NO_TOK) -> List[T]:
        self.parse_zero_or_more(sep)
        if not self._result:
            new_error = ParserError(f"Expected one or more.")
            new_error.pos = self._parser._index
            self._parser._errors.append(new_error)
            raise new_error
        return self._result

    def for_alt(self) -> ParserRuleHandler:
        self._for_alternate = True
        return self

    def and_then(self, wrapper_function) -> ParserRuleHandler:
        new_parser_rule_handler = ParserRuleHandler(self._parser, self._rule)
        new_parser_rule_handler._rule = lambda: wrapper_function(self._rule())
        return new_parser_rule_handler

    def __or__(self, that: ParserRuleHandler) -> ParserAlternateRulesHandler:
        if not (self._for_alternate and that._for_alternate):
            raise SystemExit("Cannot use '|' operator on a non-alternate rule.")

        return (ParserAlternateRulesHandler(self._parser).for_alt()
                .add_parser_rule_handler(self)
                .add_parser_rule_handler(that))


class ParserAlternateRulesHandler(ParserRuleHandler):
    """
    The ParserAlternateRulesHandler class is used to handle the parsing of alternate rules. It is used to parse one of
    the alternate rules. The "_parser_rule_handlers" attribute is a list of ParserRuleHandler objects that represent the
    alternate rules.
    """

    _parser_rule_handlers: List[ParserRuleHandler]

    def __init__(self, parser: Parser) -> None:
        super().__init__(parser, None)
        self._parser_rule_handlers = []

    def add_parser_rule_handler(self, parser_rule_handler: ParserRuleHandler) -> ParserAlternateRulesHandler:
        self._parser_rule_handlers.append(parser_rule_handler)
        return self

    def parse_once(self) -> Ast:
        for parser_rule_handler in self._parser_rule_handlers:
            parser_index = self._parser._index
            try:
                self._result = parser_rule_handler.parse_once()
                return self._result
            except ParserError:
                self._parser._index = parser_index
                continue
        raise ParserError(self._parser._index, "Expected one of the alternatives.")

    def __or__(self, that) -> ParserAlternateRulesHandler:
        if not (self._for_alternate and that._for_alternate):
            raise SystemExit("Cannot use '|' operator on a non-alternate rule.")

        return self.add_parser_rule_handler(that)


# Decorator that wraps the function in a ParserRuleHandler
def parser_rule(func) -> Callable[..., ParserRuleHandler]:
    """
    Decorator that wraps the function in a ParserRuleHandler.
    :param func: The function to wrap.
    :return: The wrapped function.
    """

    @functools.wraps(func)
    def wrapper(self, *args) -> ParserRuleHandler:
        return ParserRuleHandler(self, functools.partial(func, self, *args))

    return wrapper

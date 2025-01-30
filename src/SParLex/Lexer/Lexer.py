from SParLex.Lexer.Tokens import Token, TokenType, SpecialToken
from fastenum import Enum
from type_intersections import Intersection
import re


class Lexer:
    """
    The Lexer class analyses the input code and returns a list of tokens. The code and the token set must be specified
    in the constructor. The lex method is called to perform the lexical analysis and return the list of tokens. Custom
    token sets can be created by subclassing TokenType and passing the subclass to the Lexer constructor.

    Example:
        - tokens = Lexer("let x = 5;", MyTokenType).lex()
    """

    _code: str
    _token_class: Intersection[type[Enum], type[TokenType]]

    def __init__(self, code: str, token_set: Intersection[type[Enum], type[TokenType]] = TokenType) -> None:
        self._code = code.replace("\t", "    ")
        self._token_class = token_set
        self._token_class._member_map_.update(SpecialToken._member_map_)

    def lex(self):
        current = 0
        output = []

        tokens   = [t for t in self._token_class._member_map_ if t[:2] == "Tk"]
        keywords = [t for t in self._token_class._member_map_ if t[:2] == "Kw"]
        lexemes  = [t for t in self._token_class._member_map_ if t[:2] == "Lx"]

        tokens.sort(key=lambda t: len(self._token_class[t].value), reverse=True)
        keywords.sort(key=lambda t: len(self._token_class[t].value), reverse=True)

        available_tokens = keywords + lexemes + tokens

        while current < len(self._code):
            for token in available_tokens:
                value = getattr(self._token_class, token).value
                upper = current + len(value)

                # Keywords: Match the keyword, and check that the next character isn't [A-Za-z_] (identifier).
                if token[:2] == "Kw" and self._code[current:upper] == value and not (self._code[upper].isalpha() or self._code[upper] == "_"):
                    output.append(Token(value, self._token_class[token]))
                    current += len(value)
                    break

                # Lexemes: Match a lexeme by attempting to get a regex match against the current code. Discard comments.
                elif token[:2] == "Lx" and (matched := re.match(value, self._code[current:])):
                    if self._token_class[token] not in [self._token_class.single_line_comment_token(), self._token_class.multi_line_comment_token()]:
                        output.append(Token(matched.group(0), self._token_class[token]))
                    if self._token_class[token] == self._token_class.multi_line_comment_token():
                        output.extend([Token("\n", self._token_class.newline_token())] * matched.group(0).count("\n"))
                    current += len(matched.group(0))
                    break

                # Tokens: Match the token and increment the counter by the length of the token.
                elif token[:2] == "Tk" and self._code[current:upper] == value:
                    output.append(Token(value, self._token_class[token]))
                    current += len(value)
                    break

            else:
                # Use n error token here, so that the error checker can use the same code to format the error when some
                # rule fails to parse, rather than trying to raise an error from here.
                output += [Token(self._code[current], SpecialToken.ERR)]
                current += 1

        return [Token("\n", self._token_class.newline_token())] + output + [Token("<EOF>", SpecialToken.EOF)]

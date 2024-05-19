from SParLex.Lexer.Tokens import Token, TokenType
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
    _token_class: type[TokenType]

    def __init__(self, code: str, token_set: type[TokenType] = TokenType) -> None:
        self._code = code.replace("\t", "    ")
        self._token_class = token_set

        if token_set is not TokenType:
            self._token_class._member_map_.update(TokenType._member_map_)

    def lex(self):
        current = 0
        output = []

        tokens   = [t for t in TokenType.__dict__["_member_names_"] if t.startswith("Tk")]
        keywords = [t for t in TokenType.__dict__["_member_names_"] if t.startswith("Kw")]
        lexemes  = [t for t in TokenType.__dict__["_member_names_"] if t.startswith("Lx")]

        tokens.sort(key=lambda t: len(TokenType[t].value), reverse=True)
        keywords.sort(key=lambda t: len(TokenType[t].value), reverse=True)

        available_tokens = keywords + lexemes + tokens

        while current < len(self._code):
            for token in available_tokens:
                value = getattr(TokenType, token).value
                upper = current + len(value)

                # Keywords: Match the keyword, and check that the next character isn't [A-Za-z_] (identifier).
                if token.startswith("Kw") and self._code[current:upper] == value and not (self._code[upper].isalpha() or self._code[upper] == "_"):
                    output.append(Token(value, TokenType[token]))
                    current += len(value)
                    break

                # Lexemes: Match a lexeme by attempting to get a regex match against the current code. Discard comments.
                elif token.startswith("Lx") and (matched := re.match(value, self._code[current:])):
                    if TokenType[token] not in [self._token_class.single_line_comment_token(), self._token_class.multi_line_comment_token()]:
                        output.append(Token(matched.group(0), TokenType[token]))
                    if TokenType[token] == self._token_class.multi_line_comment_token():
                        output.extend([Token("\n", TokenType.NEWLINE)] * matched.group(0).count("\n"))
                    current += len(matched.group(0))
                    break

                # Tokens: Match the token and increment the counter by the length of the token.
                elif token.startswith("Tk") and self._code[current:upper] == value:
                    output.append(Token(value, TokenType[token]))
                    current += len(value)
                    break

            else:
                # Use n error token here, so that the error checker can use the same code to format the error when some
                # rule fails to parse, rather than trying to raise an error from here.
                output += [Token(self._code[current], TokenType.ERR)]
                current += 1

        return [Token("\n", TokenType.NEWLINE)] + output + [Token("<EOF>", TokenType.EOF)]

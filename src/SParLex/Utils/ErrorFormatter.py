from typing import List
from colorama import Fore, Style

from SParLex.Lexer.Tokens import Token, TokenType, SpecialToken


class ErrorFormatter:
    _tokens: List[Token]
    _file_path: str

    def __init__(self, tokens: List[Token], file_path: str) -> None:
        self._tokens = tokens
        self._file_path = file_path[file_path.rfind("src\\") + 4:]

    def error(self, start_pos: int, message: str = "", tag_message: str = "", minimal: bool = False) -> str:
        while self._tokens[start_pos].token_type in [TokenType.newline_token(), TokenType.whitespace_token()]:
            start_pos += 1

        # Get the tokens at the start and end of the line containing the error. Skip the leading newline.
        error_line_start_pos = [i for i, x in enumerate(self._tokens[:start_pos]) if x.token_type == TokenType.newline_token()][-1] + 1
        error_line_end_pos = ([i for i, x in enumerate(self._tokens[start_pos:]) if x.token_type == TokenType.newline_token()] or [len(self._tokens) - 1])[0] + start_pos
        error_line_tokens = self._tokens[error_line_start_pos:error_line_end_pos]
        error_line_as_string = "".join([str(token) for token in error_line_tokens])

        # Get the line number of the error
        error_line_number = len([x for x in self._tokens[:start_pos] if x.token_type == TokenType.newline_token()])

        # The number of "^" is the length of the token data where the error is. Todo: Should span entire AST node.
        carets = "^" * len(self._tokens[start_pos].token_metadata)
        carets = " " * sum([len(str(token)) for token in self._tokens[error_line_start_pos : start_pos]]) + carets

        # Print the preceding spaces before the error line
        l1 = len(error_line_as_string)
        error_line_as_string = error_line_as_string.replace("  ", "")
        carets = carets[l1 - len(error_line_as_string):] + f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT} <- {tag_message}"

        left_padding = " " * len(str(error_line_number))
        bar_character = "|"
        final_error_message = "\n".join([
            f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT}",
            f"Error in file '{self._file_path}', on line {error_line_number}:" if not minimal else f"Context from file '{self._file_path}', on line {error_line_number}:",
            f"{Fore.LIGHTWHITE_EX}{left_padding} {bar_character}",
            f"{Fore.LIGHTRED_EX if not minimal else Fore.LIGHTGREEN_EX}{error_line_number} {bar_character} {error_line_as_string}",
            f"{Fore.LIGHTWHITE_EX}{left_padding} {bar_character} {Style.NORMAL}{Fore.LIGHTRED_EX if not minimal else Fore.LIGHTGREEN_EX}{carets}\n",
            f"{Style.RESET_ALL}{Fore.LIGHTRED_EX}{message}" * (not minimal)])

        return final_error_message

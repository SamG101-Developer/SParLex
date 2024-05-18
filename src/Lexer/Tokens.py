from __future__ import annotations
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    ERR = "Unknown"
    NO_TOK = ""
    EOF = "<EOF>"
    NEWLINE = "\n"
    WHITE_SPACE = " "

    @staticmethod
    @abstractmethod
    def single_line_comment_token() -> TokenType:
        ...

    @staticmethod
    @abstractmethod
    def multi_line_comment_token() -> TokenType:
        ...


@dataclass
class Token:
    token_metadata: str
    token_type: TokenType

    def __str__(self):
        return self.token_metadata

from dataclasses import dataclass

from src.Ast.Ast import Ast
from src.Ast.TokenAst import TokenAst


@dataclass
class ProgramAst(Ast):
    eof_token: TokenAst

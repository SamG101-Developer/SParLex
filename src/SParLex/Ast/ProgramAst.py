from dataclasses import dataclass

from SParLex.Ast.Ast import Ast
from SParLex.Ast.TokenAst import TokenAst


@dataclass
class ProgramAst(Ast):
    root_ast: Ast
    eof_token: TokenAst

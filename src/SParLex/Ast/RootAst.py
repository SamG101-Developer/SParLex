from dataclasses import dataclass

from SParLex.Ast.Ast import Ast
from SParLex.Ast.TokAst import TokAst


@dataclass
class RootAst(Ast):
    root_ast: Ast
    eof_token: TokAst

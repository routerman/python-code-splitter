import ast


class BlockType:
    IMPORT = "import"
    FUNCTION = "function"
    CLASS = "class"
    VALUE = "value"
    COMMENT = "comment"
    OTHER = "other"

    def ast2type(stmt: ast.AST):
        if isinstance(stmt, ast.Import) or isinstance(stmt, ast.ImportFrom):
            return BlockType.IMPORT
        if isinstance(stmt, ast.FunctionDef) or isinstance(stmt, ast.AsyncFunctionDef):
            return BlockType.FUNCTION
        if isinstance(stmt, ast.ClassDef):
            return BlockType.CLASS
        if isinstance(stmt, ast.Assign):
            return BlockType.VALUE
        return BlockType.OTHER

import ast
from dataclasses import dataclass
from pathlib import Path

from src.entities.block import Block
from src.entities.file import File
from src.enums.block_type import BlockType
from src.patterns import CLASS_PATTERN, FUNCTION_PATTERN, IMPORT_PATTERN, VALUE_PATTERN


@dataclass(frozen=True)
class LoadFileService:
    file_path: Path

    class ParseError(Exception):
        pass

    def execute(self) -> File:
        """Read the file and split it into classes, functions, and others"""
        assert self.file_path.is_file(), f"Error: File '{self.file_path}' does not exist."
        with self.file_path.open(mode="r") as file:
            lines = file.readlines()
        blocks: list[Block] = []
        tree = ast.parse("".join(lines))
        number = 0
        for node in ast.iter_child_nodes(tree):
            if not isinstance(
                node,
                (
                    ast.AsyncFunctionDef,
                    ast.FunctionDef,
                    ast.ClassDef,
                    ast.Module,
                    ast.Import,
                    ast.ImportFrom,
                    ast.Assign,
                ),
            ):
                continue
            blocks.append(self._generate_block(codes=lines[number : node.end_lineno]))
            number = node.end_lineno
        blocks.append(self._generate_block(codes=lines[number:]))
        # Check if the total number of lines in the split blocks matches the original number of lines
        assert len(lines) == sum([len(block.codes) for block in blocks])
        return File(path=self.file_path, blocks=blocks)

    def _generate_block(self, codes: list[str]) -> Block:
        for pattern in [CLASS_PATTERN, FUNCTION_PATTERN, VALUE_PATTERN, IMPORT_PATTERN]:
            for code in codes:
                if match := pattern.pattern.match(code):
                    name = match and match.groups()[-1]
                    if not name:
                        raise self.ParseError(f"{code=} {match=}")
                    return Block(
                        codes=codes,
                        name=name,
                        type=pattern.name,
                    )
        else:
            return Block(
                codes=codes,
                name="other",
                type=BlockType.OTHER,
            )

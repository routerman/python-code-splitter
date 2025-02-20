from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.entities.block import Block
from src.enums.block_type import BlockType
from src.utils import to_snake_case


@dataclass(frozen=True)
class GenerateImportStatementService:
    new_dir_path: Path
    moved_blocks: list[Block]
    non_moved_blocks: list[Block] = field(default_factory=list)
    exclude_block: Optional[Block] = None

    def execute(self) -> list[str]:
        # Generate import statements for moved and non-moved blocks
        new_dir_path = str(self.new_dir_path).replace("/", ".")
        import_statement = []
        # Add import statements from the original file
        for non_moved_block in filter(lambda block: block.type == BlockType.IMPORT, self.non_moved_blocks):
            import_statement += non_moved_block.codes
        # Add import statements for moved blocks
        for moved_block in self.moved_blocks:
            if self.exclude_block and moved_block.name == self.exclude_block.name:
                continue
            import_statement.append(
                f"from {new_dir_path}.{to_snake_case(moved_block.name)} import {moved_block.name}\n"
            )
        # Add import statements for non-moved blocks
        for non_moved_block in filter(
            lambda block: block.type not in [BlockType.IMPORT, BlockType.OTHER], self.non_moved_blocks
        ):
            import_statement.append(f"from {new_dir_path} import {non_moved_block.name}\n")
        return import_statement

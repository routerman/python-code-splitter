from dataclasses import dataclass
from pathlib import Path

from src.entities.block import Block
from src.services.generate_import_statement_service import (
    GenerateImportStatementService,
)


@dataclass(frozen=True)
class AttachImportStatements:
    moved_blocks: list[Block]
    non_moved_blocks: list[Block]
    new_dir_path: Path

    def execute(self):
        moved_blocks = sorted(self.moved_blocks, key=lambda block: (block.type, block.name))
        for moved_block in moved_blocks:
            with moved_block.path(parent=self.new_dir_path).open(mode="w") as f:
                import_statement = GenerateImportStatementService(
                    new_dir_path=self.new_dir_path,
                    moved_blocks=moved_blocks,
                    non_moved_blocks=self.non_moved_blocks,
                    exclude_block=moved_block,
                ).execute()
                f.writelines(import_statement)
                f.writelines(moved_block.codes)
